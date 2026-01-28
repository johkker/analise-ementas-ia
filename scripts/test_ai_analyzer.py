#!/usr/bin/env python
"""
Quick test para validar o novo sistema de análise IA.

Uso:
  python scripts/test_ai_analyzer.py --type GASTO --limit 5
  python scripts/test_ai_analyzer.py --info
"""

import asyncio
import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai_analyzer import AIAnalysisManager, AnalysisType
from src.core.database import AsyncSessionLocal
from src.models.analise import AnaliseIA
from sqlalchemy import select, func


async def test_analyzer(analysis_type: str, limit: int = 5):
    """Testar um analisador específico"""
    print(f"\n{'=' * 60}")
    print(f"🧪 Testing {analysis_type} Analyzer (limit: {limit})")
    print(f"{'=' * 60}\n")

    manager = AIAnalysisManager()

    try:
        result = await manager.run_analysis(
            analysis_type=AnalysisType[analysis_type],
            limit=limit
        )

        print(f"\n✅ Success!")
        print(f"  Analyzed: {result.get('analyzed', 0)}")
        print(f"  Succeeded: {result.get('succeeded', 0)}")
        print(f"  Failed: {result.get('failed', 0)}")

        if result.get('results'):
            print(f"\n  Results:")
            for r in result['results'][:3]:  # Show first 3
                print(f"    - Entity {r.get('entity_id')}: {r.get('status')}")

        return result

    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def show_info():
    """Mostrar informações sobre análises no banco"""
    print(f"\n{'=' * 60}")
    print(f"📊 AI Analysis Info")
    print(f"{'=' * 60}\n")

    async with AsyncSessionLocal() as session:
        # Total análises
        total = await session.execute(
            select(func.count(AnaliseIA.id))
        )
        total_count = total.scalar() or 0

        # Por tipo
        types_query = select(
            AnaliseIA.entidade_tipo,
            func.count(AnaliseIA.id).label('count')
        ).group_by(AnaliseIA.entidade_tipo)

        types_result = await session.execute(types_query)
        types_data = types_result.all()

        print(f"Total analyses: {total_count}\n")
        print(f"By type:")
        for tipo, count in types_data:
            print(f"  - {tipo}: {count}")

        # Análises recentes
        print(f"\nRecent (last 5):")
        recent = select(AnaliseIA).order_by(
            AnaliseIA.created_at.desc()
        ).limit(5)
        recent_result = await session.execute(recent)
        recent_analyses = recent_result.scalars().all()

        for analysis in recent_analyses:
            print(f"  - {analysis.entidade_tipo} {analysis.entidade_id}: "
                  f"score={analysis.score_anomalia}, "
                  f"created={analysis.created_at.strftime('%Y-%m-%d %H:%M')}")


async def list_pending(analysis_type: str):
    """Listar documentos pendentes de análise"""
    from src.models.gasto import Gasto
    from src.models.voto import Voto
    from src.models.proposicao import Proposicao

    print(f"\n{'=' * 60}")
    print(f"📋 Pending {analysis_type} for Analysis")
    print(f"{'=' * 60}\n")

    async with AsyncSessionLocal() as session:
        if analysis_type == "GASTO":
            analyzed_ids = select(AnaliseIA.entidade_id).where(
                AnaliseIA.entidade_tipo == 'GASTO'
            )
            pending = select(Gasto).where(
                Gasto.id.not_in(analyzed_ids)
            ).order_by(
                Gasto.data_pagamento.desc()
            ).limit(10)

        elif analysis_type == "VOTO":
            analyzed_ids = select(AnaliseIA.entidade_id).where(
                AnaliseIA.entidade_tipo == 'VOTO'
            )
            pending = select(Voto).where(
                Voto.id.not_in(analyzed_ids)
            ).limit(10)

        elif analysis_type == "PROPOSICAO":
            analyzed_ids = select(AnaliseIA.entidade_id).where(
                AnaliseIA.entidade_tipo == 'PROPOSICAO'
            )
            pending = select(Proposicao).where(
                Proposicao.id.not_in(analyzed_ids)
            ).order_by(
                Proposicao.data_apresentacao.desc()
            ).limit(10)

        else:
            print(f"❌ Unknown type: {analysis_type}")
            return

        result = await session.execute(pending)
        entities = result.scalars().all()

        if not entities:
            print(f"✅ All {analysis_type}s have been analyzed!")
            return

        print(f"Pending: {len(entities)}\n")
        for i, entity in enumerate(entities[:5], 1):
            if analysis_type == "GASTO":
                print(f"  {i}. ID {entity.id}: R${entity.valor} - {entity.descricao}")
            elif analysis_type == "VOTO":
                print(f"  {i}. ID {entity.id}: {entity.voto}")
            elif analysis_type == "PROPOSICAO":
                print(f"  {i}. ID {entity.id}: {entity.titulo[:50]}")


def main():
    parser = argparse.ArgumentParser(description="Test AI Analyzer")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--type",
        choices=["GASTO", "VOTO", "PROPOSICAO", "CROSS_DATA"],
        help="Test specific analyzer"
    )
    group.add_argument(
        "--info",
        action="store_true",
        help="Show analysis statistics"
    )
    group.add_argument(
        "--pending",
        choices=["GASTO", "VOTO", "PROPOSICAO"],
        help="List pending documents"
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        help="Limit for testing (default: 5)"
    )

    args = parser.parse_args()

    if args.info:
        asyncio.run(show_info())
    elif args.pending:
        asyncio.run(list_pending(args.pending))
    elif args.type:
        asyncio.run(test_analyzer(args.type, args.limit))


if __name__ == "__main__":
    main()
