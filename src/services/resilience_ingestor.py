import traceback
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from src.models.gasto import Gasto, Empresa
from src.models.dlq import DLQ
from src.schemas.camara_api import StrictGastoSchema

class ResilienceIngestor:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def process_gastos_batch(self, politico_id: int, raw_data_list: list[dict]):
        valid_records = []
        dlq_records = []

        for raw_item in raw_data_list:
            try:
                # 1. Tentativa de Validação Estrita
                validated_item = StrictGastoSchema(**raw_item)
                
                # Prepara para inserção
                item_dict = validated_item.model_dump(by_alias=False)
                item_dict['politico_id'] = politico_id
                
                # Vamos simplificar: se tiver CNPJ, a gente assume que a empresa existe ou cria.
                # Para fins de demonstração, vamos focar no Gasto.
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

        # 3. Commit em Batch
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
