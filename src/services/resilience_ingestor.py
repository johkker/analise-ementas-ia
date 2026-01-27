import traceback
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.models.gasto import Gasto, Empresa
from src.models.proposicao import Proposicao
from src.models.votacao import Votacao
from src.models.voto import Voto
from src.models.dlq import DLQ
from src.schemas.camara_api import StrictGastoSchema, ProposicaoSchema, VotacaoSchema, VotoSchema

class ResilienceIngestor:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_gastos_batch(self, politico_id: int, raw_data_list: list[dict]):
        valid_records = []
        valid_empresas = {} # cnpj: data
        dlq_records = []

        for raw_item in raw_data_list:
            try:
                validated_item = StrictGastoSchema(**raw_item)
                
                # 1. Prepara Empresa
                if validated_item.empresa_cnpj:
                    valid_empresas[validated_item.empresa_cnpj] = {
                        "cnpj": validated_item.empresa_cnpj,
                        "nome_fantasia": validated_item.empresa_nome
                    }

                # 2. Prepara Gasto
                item_dict = validated_item.model_dump(by_alias=False)
                item_dict['politico_id'] = politico_id
                
                # Remove campo que não existe na tabela de Gastos
                item_dict.pop('empresa_nome', None)
                
                valid_records.append(item_dict)

            except ValidationError as e:
                dlq_records.append({
                    "origin_source": f"camara_gastos_{politico_id}",
                    "payload": raw_item,
                    "error_message": str(e),
                    "error_type": "SchemaValidationError"
                })
            except Exception:
                dlq_records.append({
                    "origin_source": f"camara_gastos_{politico_id}",
                    "payload": raw_item,
                    "error_message": traceback.format_exc(),
                    "error_type": "UnhandledException"
                })

        # 3. Upsert Empresas primeiro (FK dependency)
        if valid_empresas:
            stmt = insert(Empresa).values(list(valid_empresas.values()))
            stmt = stmt.on_conflict_do_update(
                index_elements=['cnpj'],
                set_={"nome_fantasia": stmt.excluded.nome_fantasia}
            )
            await self.session.execute(stmt)

        # 4. Upsert Gastos
        if valid_records:
            await self._bulk_upsert_gastos(valid_records)
        
        if dlq_records:
            await self._bulk_insert_dlq(dlq_records)
            
        await self.session.commit()

    async def _bulk_upsert_gastos(self, records):
        stmt = insert(Gasto).values(records)
        # Sincroniza campos exceto a PK interna se houver conflito no ext_id
        update_dict = {
            c.name: c for c in stmt.excluded 
            if c.name not in ['id', 'ext_id', 'created_at']
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=['ext_id'],
            set_=update_dict
        )
        await self.session.execute(stmt)

    async def _bulk_insert_dlq(self, records):
        await self.session.execute(insert(DLQ).values(records))

    async def process_deputados_batch(self, raw_data_list: list[dict]):
        from src.models.politico import Politico, Partido
        from src.schemas.camara_api import PoliticoSchema
        from sqlalchemy import select
        
        valid_politicos = []
        valid_partidos = {} # Dict to deduplicate: {id: data}
        dlq_records = []

        for raw_item in raw_data_list:
            try:
                validated_item = PoliticoSchema(**raw_item)
                
                # Extrai ID do Partido da URI (ex: .../partidos/37903)
                partido_id = int(validated_item.uriPartido.split('/')[-1])
                
                # Prepara Partido
                valid_partidos[partido_id] = {
                    "id": partido_id,
                    "sigla": validated_item.siglaPartido,
                    "nome": validated_item.siglaPartido # API summary doesn't have full name
                }

                # Prepara Político
                item_dict = {
                    "id": validated_item.id,
                    "nome_civil": validated_item.nome,
                    "nome_parlamentar": validated_item.nome,
                    "uf": validated_item.siglaUf,
                    "email": validated_item.email,
                    "foto_url": validated_item.urlFoto,
                    "id_legislatura": validated_item.idLegislatura,
                    "partido_id": partido_id
                }
                valid_politicos.append(item_dict)

            except Exception as e:
                dlq_records.append({
                    "origin_source": "camara_deputados",
                    "payload": raw_item,
                    "error_message": str(e),
                    "error_type": type(e).__name__
                })

        # 1. Upsert Partidos
        if valid_partidos:
            stmt = insert(Partido).values(list(valid_partidos.values()))
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_={
                    "sigla": stmt.excluded.sigla,
                    "nome": stmt.excluded.nome
                }
            )
            await self.session.execute(stmt)

        # 2. Upsert Politicos
        if valid_politicos:
            stmt = insert(Politico).values(valid_politicos)
            update_dict = {
                c.name: c for c in stmt.excluded 
                if c.name not in ['id', 'created_at']
            }
            stmt = stmt.on_conflict_do_update(index_elements=['id'], set_=update_dict)
            await self.session.execute(stmt)
        
        if dlq_records:
            await self._bulk_insert_dlq(dlq_records)
            
        await self.session.commit()

    async def process_proposicoes_batch(self, raw_data_list: list[dict]):
        valid_records = []
        dlq_records = []
        all_authors = [] # (proposicao_id, politico_id)
        proposicao_ids_to_clean = []

        for raw_item in raw_data_list:
            try:
                validated_item = ProposicaoSchema(**raw_item)
                item_dict = validated_item.model_dump(by_alias=False)
                valid_records.append(item_dict)
                proposicao_ids_to_clean.append(validated_item.id)
                
                # Handle Authors
                # Expected format from API: list of simple objects, need to extract URI to find ID
                raw_autores = raw_item.get('autores', [])
                for autor in raw_autores:
                    # URI format: https://dadosabertos.camara.leg.br/api/v2/deputados/204536
                    if 'uri' in autor and '/deputados/' in autor['uri']:
                         try:
                             politico_id = int(autor['uri'].split('/deputados/')[-1])
                             all_authors.append({
                                 "proposicao_id": validated_item.id,
                                 "politico_id": politico_id
                             })
                         except Exception:
                             pass
                             
            except Exception as e:
                dlq_records.append({
                    "origin_source": "camara_proposicoes",
                    "payload": raw_item,
                    "error_message": str(e),
                    "error_type": type(e).__name__
                })

        if valid_records:
            await self._bulk_upsert_proposicoes(valid_records)
            
        if proposicao_ids_to_clean and all_authors:
            # Upsert authors association
            # First delete existing to support updates/idempotency
            from src.models.proposicao import autoria_proposicao
            from sqlalchemy import delete
            
            await self.session.execute(
                delete(autoria_proposicao).where(
                    autoria_proposicao.c.proposicao_id.in_(proposicao_ids_to_clean)
                )
            )
            
            # Insert new
            if all_authors:
                # Deduplicate tuples
                unique_authors = [dict(t) for t in {tuple(d.items()) for d in all_authors}]
                
                # SAFETY: Filter out politico_id not in DB to avoid FK violation
                from src.models.politico import Politico
                from sqlalchemy import select
                
                politico_ids = {a['politico_id'] for a in unique_authors}
                existing_politicos = await self.session.execute(
                    select(Politico.id).where(Politico.id.in_(politico_ids))
                )
                existing_ids = {row[0] for row in existing_politicos.all()}
                
                final_authors = [a for a in unique_authors if a['politico_id'] in existing_ids]
                
                if final_authors:
                    await self.session.execute(insert(autoria_proposicao).values(final_authors))

        if dlq_records:
            await self._bulk_insert_dlq(dlq_records)
            
        await self.session.commit()

    async def _bulk_upsert_proposicoes(self, records):
        stmt = insert(Proposicao).values(records)
        update_dict = {
            c.name: c for c in stmt.excluded 
            if c.name not in ['id', 'created_at']
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )
        await self.session.execute(stmt)

    async def process_votacoes_batch(self, raw_data_list: list[dict]):
        valid_records = []
        dlq_records = []

    async def process_votacoes_batch(self, raw_data_list: list[dict]):
        valid_records = []
        all_votos = []
        dlq_records = []
        votacao_ids_to_clean = []

        for raw_item in raw_data_list:
            try:
                # Validate main object
                validated_item = VotacaoSchema(**raw_item)
                item_dict = validated_item.model_dump(by_alias=False, exclude={'uri_proposicao'})
                
                # Extract proposicao_id from URI
                prop_uri = validated_item.uri_proposicao
                if prop_uri and '/proposicoes/' in prop_uri:
                    try:
                        item_dict['proposicao_id'] = int(prop_uri.split('/proposicoes/')[-1])
                    except (ValueError, IndexError):
                        pass
                
                # Handle nested Votos
                raw_votos = raw_item.get('votos', [])
                for rv in raw_votos:
                    try:
                        vv = VotoSchema(**rv)
                        # Extract politico_id from nested diputado object
                        # This assumes VotoSchema.deputado is a PoliticoSchema which has field 'id'
                        # But wait, VotoSchema.deputado is PoliticoSchema.
                        # PoliticoSchema has 'id' field.
                        
                        voto_dict = {
                            "votacao_id": validated_item.id,
                            "politico_id": vv.deputado.id,
                            "tipo_voto": vv.tipo_voto
                        }
                        all_votos.append(voto_dict)
                    except Exception as ev:
                        print(f"Skipping invalid voto: {ev}")

                valid_records.append(item_dict)
                votacao_ids_to_clean.append(validated_item.id)
                
            except Exception as e:
                dlq_records.append({
                    "origin_source": "camara_votacoes",
                    "payload": raw_item,
                    "error_message": str(e),
                    "error_type": type(e).__name__
                })

        if valid_records:
            await self._bulk_upsert_votacoes(valid_records)
            
        if votacao_ids_to_clean:
            # Clean old votes to ensure idempotency
            from sqlalchemy import delete
            await self.session.execute(delete(Voto).where(Voto.votacao_id.in_(votacao_ids_to_clean)))
            
        if all_votos:
            # SAFETY: Filter out politico_id not in DB
            from src.models.politico import Politico
            from sqlalchemy import select
            
            politico_ids = {v['politico_id'] for v in all_votos}
            existing_politicos = await self.session.execute(
                select(Politico.id).where(Politico.id.in_(politico_ids))
            )
            existing_ids = {row[0] for row in existing_politicos.all()}
            
            final_votos = [v for v in all_votos if v['politico_id'] in existing_ids]
            
            if final_votos:
                await self.session.execute(insert(Voto).values(final_votos))
        
        if dlq_records:
            await self._bulk_insert_dlq(dlq_records)
            
        await self.session.commit()

    async def _bulk_upsert_votacoes(self, records):
        stmt = insert(Votacao).values(records)
        update_dict = {
            c.name: c for c in stmt.excluded 
            if c.name not in ['id', 'created_at']
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=['id'],
            set_=update_dict
        )
        await self.session.execute(stmt)
