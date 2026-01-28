"""
AI Analysis Service - Desacoplado do Worker de Ingestão

Fornece diferentes tipos de análise IA com controle de limite diário.
Permite rodar via script CLI com parâmetros customizáveis.
"""

from enum import Enum
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import asyncio

from sqlalchemy import select, and_, not_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import AsyncSessionLocal
from src.services.llm_service import GeminiClient
from src.models.analise import AnaliseIA
from src.models.gasto import Gasto
from src.models.voto import Voto
from src.models.votacao import Votacao
from src.models.proposicao import Proposicao


class AnalysisType(str, Enum):
    """Tipos de análise suportados"""
    GASTO = "GASTO"
    VOTO = "VOTO"
    PROPOSICAO = "PROPOSICAO"
    CROSS_DATA = "CROSS_DATA"  # Análises cruzadas


class BaseAnalyzer:
    """Base class para analisadores específicos"""

    def __init__(self, llm_client: Optional[GeminiClient] = None):
        self.llm = llm_client or GeminiClient()

    async def get_pending_entities(
        self, 
        session: AsyncSession, 
        limit: int
    ) -> List:
        """
        Retorna entidades não analisadas, ordenadas por data do documento (descendente).
        
        Override em subclasses.
        """
        raise NotImplementedError

    async def prepare_analysis_text(self, entity) -> str:
        """Prepara texto para análise IA. Override em subclasses."""
        raise NotImplementedError

    async def analyze(self, session: AsyncSession, entity, entity_id: int) -> dict:
        """Executa análise e salva no banco. Override em subclasses."""
        raise NotImplementedError


class GastoAnalyzer(BaseAnalyzer):
    """Análise de gastos - detecta anomalias, padrões suspeitos"""

    analysis_type = AnalysisType.GASTO

    async def get_pending_entities(
        self,
        session: AsyncSession,
        limit: int
    ) -> List[Gasto]:
        """
        Busca gastos não analisados, ordenados por data do documento (mais recentes primeiro).
        Ignora gastos já analisados.
        """
        # Subquery: IDs de gastos já analisados
        analyzed_ids = select(AnaliseIA.entidade_id).where(
            AnaliseIA.entidade_tipo == self.analysis_type.value
        )

        # Query: Gastos não analisados, data decrescente, limit N
        stmt = select(Gasto).where(
            and_(
                Gasto.id.not_in(analyzed_ids),
                Gasto.data_emissao.isnot(None)  # Apenas com data válida
            )
        ).options(
            selectinload(Gasto.politico),
            selectinload(Gasto.empresa)
        ).order_by(
            Gasto.data_emissao.desc()  # Mais recentes primeiro
        ).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def prepare_analysis_text(self, gasto: Gasto) -> str:
        """Prepara texto descritivo do gasto para análise"""
        # Safely fetch related fields if loaded
        politico_nome = None
        empresa_nome = None
        try:
            politico_nome = getattr(gasto.politico, 'nome_parlamentar', None)
        except Exception:
            politico_nome = None
        try:
            empresa_nome = getattr(gasto.empresa, 'nome_fantasia', None)
        except Exception:
            empresa_nome = None

        detalhes = [
            f"id: {getattr(gasto, 'id', None)}",
            f"ext_id: {getattr(gasto, 'ext_id', None)}",
            f"politico_id: {getattr(gasto, 'politico_id', None)}",
            f"politico_nome: {politico_nome or 'N/A'}",
            f"empresa_cnpj: {getattr(gasto, 'empresa_cnpj', None)}",
            f"empresa_nome: {empresa_nome or 'N/A'}",
            f"valor: R$ {getattr(gasto, 'valor', 'N/A')}",
            f"data_emissao: {getattr(gasto, 'data_emissao', 'N/A')}",
            f"tipo_despesa: {getattr(gasto, 'tipo_despesa', 'N/A')}",
            f"url_documento: {getattr(gasto, 'url_documento', 'N/A')}"
        ]

        prompt = (
            "REGISTRO DE GASTO:\n" + "\n".join(detalhes) + "\n\n"
            "INSTRUÇÕES:\n"
            "Analise tecnicamente este gasto. Responda em JSON seguindo o schema fornecido.\n"
            "Perguntas úteis: existe indício de duplicidade, valor acima do padrão, pagamento a fornecedor repetido, uso indevido da verba ou ausência de evidências? Cite evidências objetivas.\n"
            "Forneça: resumo executivo (3 frases), impacto financeiro (ALTO/MEDIO/BAIXO/INCERTO), grupos beneficiados, riscos de corrupção, sentimento político (-1..1), score_anomalia (0..1), evidencias (lista) e recomendacoes (lista).\n"
        )

        return prompt

    async def analyze(
        self,
        session: AsyncSession,
        gasto: Gasto,
        entity_id: int
    ) -> dict:
        """Analisa gasto e salva AnaliseIA"""
        try:
            # Preparar texto
            texto = await self.prepare_analysis_text(gasto)

            # Chamar IA (async rate-limited)
            resultado = await self.llm.analisar_gasto_async(texto)

            # Extrair score (safe conversion)
            score = None
            if resultado.get('score_anomalia'):
                try:
                    score = Decimal(str(resultado['score_anomalia'])).quantize(
                        Decimal('0.01')
                    )
                except (ValueError, TypeError):
                    pass

            # Salvar no banco
            analise = AnaliseIA(
                entidade_tipo=self.analysis_type.value,
                entidade_id=gasto.id,
                score_anomalia=score,
                resumo_critico=resultado.get('resumo_executivo'),
                impacto_financeiro=resultado.get('impacto_financeiro'),
                grupos_beneficiados=resultado.get('grupos_beneficiados'),
                riscos_corrupcao=resultado.get('riscos_corrupcao'),
                raw_response=resultado
            )
            session.add(analise)
            await session.commit()

            return {
                "status": "success",
                "entity_id": gasto.id,
                "score": score,
                "type": self.analysis_type.value
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "entity_id": entity_id,
                "error": str(e),
                "type": self.analysis_type.value
            }


class VotoAnalyzer(BaseAnalyzer):
    """Análise de votos - padrões, coerência ideológica"""

    analysis_type = AnalysisType.VOTO

    async def get_pending_entities(
        self,
        session: AsyncSession,
        limit: int
    ) -> List[Voto]:
        """
        Busca votos não analisados, ordenados por data da votação (mais recentes).
        """
        # Subquery: IDs de votos já analisados
        analyzed_ids = select(AnaliseIA.entidade_id).where(
            AnaliseIA.entidade_tipo == self.analysis_type.value
        )

        # Query: Votos não analisados
        stmt = select(Voto).join(
            Votacao, Voto.votacao_id == Votacao.id
        ).where(
            and_(
                Voto.id.not_in(analyzed_ids),
                Votacao.data.isnot(None)
            )
        ).options(
            selectinload(Voto.politico),
            selectinload(Voto.votacao)
        ).order_by(
            Votacao.data.desc()  # Mais recentes primeiro
        ).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def prepare_analysis_text(self, voto: Voto) -> str:
        """Prepara texto descritivo do voto para análise"""
        # Try to include related votacao and politico info if available
        votacao_info = None
        politico_nome = None
        try:
            votacao_info = getattr(voto.votacao, 'descricao', None)
        except Exception:
            votacao_info = None
        try:
            politico_nome = getattr(voto.politico, 'nome_parlamentar', None)
        except Exception:
            politico_nome = None

        detalhes = [
            f"id: {getattr(voto, 'id', None)}",
            f"votacao_id: {getattr(voto, 'votacao_id', None)}",
            f"votacao_descricao: {votacao_info or 'N/A'}",
            f"politico_id: {getattr(voto, 'politico_id', None)}",
            f"politico_nome: {politico_nome or 'N/A'}",
            f"tipo_voto: {getattr(voto, 'tipo_voto', None)}"
        ]

        prompt = (
            "REGISTRO DE VOTO:\n" + "\n".join(detalhes) + "\n\n"
            "INSTRUÇÕES:\n"
            "Analise se o padrão de voto apresenta coerência ideológica com histórico, possíveis trocas de posição, ou sinais de coordenação indevida.\n"
            "Responda em JSON conforme schema: resumo_executivo, impacto_financeiro (se aplicável), grupos_beneficiados (setores afetados), riscos_corrupcao, sentimento_politico, score_anomalia, evidencias, recomendacoes.\n"
        )

        return prompt

    async def analyze(
        self,
        session: AsyncSession,
        voto: Voto,
        entity_id: int
    ) -> dict:
        """Analisa padrão de voto"""
        try:
            texto = await self.prepare_analysis_text(voto)
            resultado = await self.llm.analisar_voto_async(texto)

            score = None
            if resultado.get('score_anomalia'):
                try:
                    score = Decimal(str(resultado['score_anomalia'])).quantize(
                        Decimal('0.01')
                    )
                except (ValueError, TypeError):
                    pass

            analise = AnaliseIA(
                entidade_tipo=self.analysis_type.value,
                entidade_id=voto.id,
                score_anomalia=score,
                resumo_critico=resultado.get('resumo_executivo'),
                impacto_financeiro=resultado.get('impacto_financeiro'),
                grupos_beneficiados=resultado.get('grupos_beneficiados'),
                riscos_corrupcao=resultado.get('riscos_corrupcao'),
                raw_response=resultado
            )
            session.add(analise)
            await session.commit()

            return {
                "status": "success",
                "entity_id": voto.id,
                "score": score,
                "type": self.analysis_type.value
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "entity_id": entity_id,
                "error": str(e),
                "type": self.analysis_type.value
            }


class ProposicaoAnalyzer(BaseAnalyzer):
    """Análise de proposições - impacto, viabilidade, alinhamento ideológico"""

    analysis_type = AnalysisType.PROPOSICAO

    async def get_pending_entities(
        self,
        session: AsyncSession,
        limit: int
    ) -> List[Proposicao]:
        """
        Busca proposições não analisadas, ordenadas por data de apresentação (mais recentes).
        """
        analyzed_ids = select(AnaliseIA.entidade_id).where(
            AnaliseIA.entidade_tipo == self.analysis_type.value
        )

        stmt = select(Proposicao).where(
            and_(
                Proposicao.id.not_in(analyzed_ids),
                Proposicao.data_apresentacao.isnot(None)
            )
        ).options(
            selectinload(Proposicao.autores)
        ).order_by(
            Proposicao.data_apresentacao.desc()  # Mais recentes primeiro
        ).limit(limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    async def prepare_analysis_text(self, proposicao: Proposicao) -> str:
        """Prepara texto da proposição para análise"""
        # Collect authors if available
        autores = []
        try:
            for a in getattr(proposicao, 'autores', []) or []:
                nome = getattr(a, 'nome_parlamentar', None) or getattr(a, 'nome_civil', None)
                if nome:
                    autores.append(nome)
        except Exception:
            autores = []

        detalhes = [
            f"id: {getattr(proposicao, 'id', None)}",
            f"tipo: {getattr(proposicao, 'sigla_tipo', None)}",
            f"numero/ano: {getattr(proposicao, 'numero', None)}/{getattr(proposicao, 'ano', None)}",
            f"ementa: {getattr(proposicao, 'ementa', 'N/A')}",
            f"data_apresentacao: {getattr(proposicao, 'data_apresentacao', 'N/A')}",
            f"autores: {', '.join(autores) if autores else 'N/A'}"
        ]

        prompt = (
            "REGISTRO DE PROPOSIÇÃO:\n" + "\n".join(detalhes) + "\n\n"
            "INSTRUÇÕES:\n"
            "Analise impacto público, possí­vel favorecimento de grupos, viabilidade política e riscos institucionais.\n"
            "Responda em JSON conforme schema: resumo_executivo, impacto_financeiro, grupos_beneficiados, riscos_corrupcao, sentimento_politico, score_anomalia, evidencias, recomendacoes.\n"
        )

        return prompt

    async def analyze(
        self,
        session: AsyncSession,
        proposicao: Proposicao,
        entity_id: int
    ) -> dict:
        """Analisa impacto e viabilidade da proposição"""
        try:
            texto = await self.prepare_analysis_text(proposicao)
            resultado = await self.llm.analisar_proposicao_async(texto)

            score = None
            if resultado.get('score_anomalia'):
                try:
                    score = Decimal(str(resultado['score_anomalia'])).quantize(
                        Decimal('0.01')
                    )
                except (ValueError, TypeError):
                    pass

            analise = AnaliseIA(
                entidade_tipo=self.analysis_type.value,
                entidade_id=proposicao.id,
                score_anomalia=score,
                resumo_critico=resultado.get('resumo_executivo'),
                impacto_financeiro=resultado.get('impacto_financeiro'),
                grupos_beneficiados=resultado.get('grupos_beneficiados'),
                riscos_corrupcao=resultado.get('riscos_corrupcao'),
                raw_response=resultado
            )
            session.add(analise)
            await session.commit()

            return {
                "status": "success",
                "entity_id": proposicao.id,
                "score": score,
                "type": self.analysis_type.value
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "entity_id": entity_id,
                "error": str(e),
                "type": self.analysis_type.value
            }


class CrossDataAnalyzer(BaseAnalyzer):
    """Análise cruzada - correlações entre gastos, votos e proposições"""

    analysis_type = AnalysisType.CROSS_DATA

    async def get_pending_entities(
        self,
        session: AsyncSession,
        limit: int
    ) -> List[dict]:
        """
        Busca deputados com dados suficientes para análise cruzada.
        Retorna dicts com dados agregados.
        """
        from src.models.politico import Politico

        # Buscar deputados com gastos e votos
        stmt = select(Politico).limit(limit)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def prepare_analysis_text(self, politico_data: dict) -> str:
        """Prepara contexto cruzado para análise"""
        return (
            f"Deputado: {politico_data.get('nome')}\n"
            f"Total de gastos: {politico_data.get('gastos_total')}\n"
            f"Total de votos: {politico_data.get('votos_total')}\n"
            f"Padrão de voto: {politico_data.get('vote_pattern')}"
        )

    async def analyze(
        self,
        session: AsyncSession,
        politico_data: dict,
        entity_id: int
    ) -> dict:
        """Análise cruzada de padrões"""
        try:
            texto = await self.prepare_analysis_text(politico_data)
            resultado = await self.llm.analisar_cross_data_async(texto)

            score = None
            if resultado.get('score_anomalia'):
                try:
                    score = Decimal(str(resultado['score_anomalia'])).quantize(
                        Decimal('0.01')
                    )
                except (ValueError, TypeError):
                    pass

            # Para cross-data, usar politico_id como entidade_id
            analise = AnaliseIA(
                entidade_tipo=self.analysis_type.value,
                entidade_id=entity_id,
                score_anomalia=score,
                resumo_critico=resultado.get('resumo_executivo'),
                impacto_financeiro=resultado.get('impacto_financeiro'),
                grupos_beneficiados=resultado.get('grupos_beneficiados'),
                riscos_corrupcao=resultado.get('riscos_corrupcao'),
                raw_response=resultado
            )
            session.add(analise)
            await session.commit()

            return {
                "status": "success",
                "entity_id": entity_id,
                "score": score,
                "type": self.analysis_type.value
            }

        except Exception as e:
            await session.rollback()
            return {
                "status": "error",
                "entity_id": entity_id,
                "error": str(e),
                "type": self.analysis_type.value
            }


class AIAnalysisManager:
    """
    Manager para coordenar análises IA.
    
    Uso:
        manager = AIAnalysisManager()
        results = await manager.run_analysis(
            analysis_type=AnalysisType.GASTO,
            limit=100
        )
    """

    def __init__(self, llm_client: Optional[GeminiClient] = None):
        self.llm = llm_client or GeminiClient()
        self.analyzers = {
            AnalysisType.GASTO: GastoAnalyzer(self.llm),
            AnalysisType.VOTO: VotoAnalyzer(self.llm),
            AnalysisType.PROPOSICAO: ProposicaoAnalyzer(self.llm),
            AnalysisType.CROSS_DATA: CrossDataAnalyzer(self.llm),
        }

    async def run_analysis(
        self,
        analysis_type: AnalysisType,
        limit: int = 100,
    ) -> dict:
        """
        Executa análise do tipo especificado para até `limit` entidades.
        
        Args:
            analysis_type: Tipo de análise (GASTO, VOTO, PROPOSICAO, CROSS_DATA)
            limit: Número máximo de entidades a analisar
            
        Returns:
            {
                "type": "GASTO",
                "limit": 100,
                "analyzed": 95,
                "succeeded": 93,
                "failed": 2,
                "results": [...]
            }
        """
        analyzer = self.analyzers.get(analysis_type)
        if not analyzer:
            return {
                "status": "error",
                "message": f"Analysis type {analysis_type} not supported"
            }

        results = []
        analyzed_count = 0
        success_count = 0
        error_count = 0

        async with AsyncSessionLocal() as session:
            # Get pending entities
            entities = await analyzer.get_pending_entities(session, limit)
            
            if not entities:
                return {
                    "type": analysis_type.value,
                    "limit": limit,
                    "analyzed": 0,
                    "message": "No pending entities to analyze"
                }

            # Analyze each entity
            for entity in entities:
                # capture primary key before any DB state changes/rollbacks
                entity_id = getattr(entity, 'id', None)
                try:
                    result = await analyzer.analyze(
                        session,
                        entity,
                        entity_id
                    )
                    results.append(result)
                    analyzed_count += 1

                    if result.get("status") == "success":
                        success_count += 1
                    else:
                        error_count += 1

                    # Log progress
                    if analyzed_count % 10 == 0:
                        print(f"  [{analyzed_count}/{len(entities)}] Analyzed...")

                except Exception as e:
                    print(f"  ❌ Error analyzing entity {entity_id}: {str(e)}")
                    error_count += 1
                    results.append({
                        "status": "error",
                        "entity_id": entity_id,
                        "error": str(e),
                        "type": analysis_type.value
                    })

        return {
            "type": analysis_type.value,
            "limit": limit,
            "analyzed": analyzed_count,
            "succeeded": success_count,
            "failed": error_count,
            "results": results
        }

    async def run_daily_analyses(
        self,
        gasto_limit: int = 50,
        voto_limit: int = 30,
        proposicao_limit: int = 20
    ) -> dict:
        """
        Executa análises diárias de múltiplos tipos.
        
        Útil para um cron job diário que distribui o limite de API.
        
        Args:
            gasto_limit: Max gastos por dia
            voto_limit: Max votos por dia
            proposicao_limit: Max proposições por dia
            
        Returns:
            Sumário consolidado
        """
        results = {}

        print("🔍 Running daily AI analyses...\n")

        print(f"📊 Analyzing gastos (limit: {gasto_limit})...")
        results['gastos'] = await self.run_analysis(
            AnalysisType.GASTO,
            limit=gasto_limit
        )
        print(f"  ✅ {results['gastos'].get('succeeded', 0)} succeeded\n")

        print(f"🗳️ Analyzing votos (limit: {voto_limit})...")
        results['votos'] = await self.run_analysis(
            AnalysisType.VOTO,
            limit=voto_limit
        )
        print(f"  ✅ {results['votos'].get('succeeded', 0)} succeeded\n")

        print(f"📜 Analyzing proposições (limit: {proposicao_limit})...")
        results['proposicoes'] = await self.run_analysis(
            AnalysisType.PROPOSICAO,
            limit=proposicao_limit
        )
        print(f"  ✅ {results['proposicoes'].get('succeeded', 0)} succeeded\n")

        total_analyzed = sum(
            r.get('analyzed', 0) for r in results.values()
        )
        total_succeeded = sum(
            r.get('succeeded', 0) for r in results.values()
        )

        print(f"📈 Daily summary:")
        print(f"  Total analyzed: {total_analyzed}")
        print(f"  Total succeeded: {total_succeeded}")

        return {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "total_analyzed": total_analyzed,
            "total_succeeded": total_succeeded
        }
