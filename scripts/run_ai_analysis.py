#!/usr/bin/env python
"""
Script para rodar análises IA com controle de limite diário.

Uso:
  python scripts/run_ai_analysis.py --type GASTO --limit 100
  python scripts/run_ai_analysis.py --type VOTO --limit 50
  python scripts/run_ai_analysis.py --daily  # Rodar análises diárias com defaults

Opções:
  --type {GASTO,VOTO,PROPOSICAO,CROSS_DATA}  Tipo de análise
  --limit N                                    Máximo de análises (default: 50)
  --daily                                      Rodar análises diárias (default: 50+30+20)
  --daily-gastos N                             Gastos/dia se usar --daily
  --daily-votos N                              Votos/dia se usar --daily
  --daily-proposicoes N                        Proposições/dia se usar --daily
"""

import asyncio
import argparse
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.ai_analyzer import AIAnalysisManager, AnalysisType


def main():
    parser = argparse.ArgumentParser(
        description="Run AI analyses for Lente Cidadã"
    )

    # Modo: single type vs daily
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--type",
        type=str,
        choices=["GASTO", "VOTO", "PROPOSICAO", "CROSS_DATA"],
        help="Single analysis type"
    )
    mode_group.add_argument(
        "--daily",
        action="store_true",
        help="Run daily analyses (all types with optimized limits)"
    )

    # Limits para single analysis
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="Max number of entities to analyze (default: 50)"
    )

    # Limits customizáveis para daily mode
    parser.add_argument(
        "--daily-gastos",
        type=int,
        default=50,
        help="Max gastos per day in daily mode (default: 50)"
    )
    parser.add_argument(
        "--daily-votos",
        type=int,
        default=30,
        help="Max votos per day in daily mode (default: 30)"
    )
    parser.add_argument(
        "--daily-proposicoes",
        type=int,
        default=20,
        help="Max proposições per day in daily mode (default: 20)"
    )

    args = parser.parse_args()

    # Rodar análise
    if args.daily:
        result = asyncio.run(_run_daily(
            gasto_limit=args.daily_gastos,
            voto_limit=args.daily_votos,
            proposicao_limit=args.daily_proposicoes
        ))
    else:
        result = asyncio.run(_run_single(
            analysis_type=args.type,
            limit=args.limit
        ))

    # Print resultado
    _print_result(result)

    # Exit code based on success
    sys.exit(0 if result.get("status") != "error" else 1)


async def _run_single(analysis_type: str, limit: int):
    """Rodar análise de um tipo específico"""
    print(f"\n🚀 Running {analysis_type} analysis (limit: {limit})...\n")

    manager = AIAnalysisManager()
    result = await manager.run_analysis(
        analysis_type=AnalysisType[analysis_type],
        limit=limit
    )

    return result


async def _run_daily(
    gasto_limit: int = 50,
    voto_limit: int = 30,
    proposicao_limit: int = 20
):
    """Rodar análises diárias otimizadas"""
    print(f"\n📅 Running daily AI analyses\n")
    print(f"   Gastos:      {gasto_limit}")
    print(f"   Votos:       {voto_limit}")
    print(f"   Proposições: {proposicao_limit}")
    print(f"   {'─' * 40}\n")

    manager = AIAnalysisManager()
    result = await manager.run_daily_analyses(
        gasto_limit=gasto_limit,
        voto_limit=voto_limit,
        proposicao_limit=proposicao_limit
    )

    return result


def _print_result(result: dict):
    """Pretty print resultado"""
    print(f"\n{'═' * 60}")

    if result.get("status") == "error":
        print(f"❌ Error: {result.get('message')}")
        print(f"{'═' * 60}\n")
        return

    # Single analysis result
    if "type" in result and "analyzed" in result:
        print(f"📊 Analysis Result: {result['type']}")
        print(f"{'─' * 60}")
        print(f"  Analyzed:  {result.get('analyzed', 0)}")
        print(f"  Succeeded: {result.get('succeeded', 0)}")
        print(f"  Failed:    {result.get('failed', 0)}")
        if result.get('message'):
            print(f"  Message:   {result['message']}")

    # Daily analyses result
    elif "total_analyzed" in result:
        print(f"📅 Daily Analyses Summary")
        print(f"{'─' * 60}")
        print(f"  Timestamp: {result['timestamp']}")
        print(f"  Total:     {result['total_analyzed']} analyzed")
        print(f"  Succeeded: {result['total_succeeded']}")

        if "results" in result:
            print(f"\n  Breakdown:")
            for analysis_type, data in result['results'].items():
                status = "✅" if data.get("succeeded", 0) > 0 else "⏭️ "
                print(
                    f"    {status} {analysis_type.upper()}: "
                    f"{data.get('analyzed', 0)} analyzed, "
                    f"{data.get('succeeded', 0)} succeeded"
                )

    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
