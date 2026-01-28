"""
AI Worker - DEPRECATED (Analysis moved to separate scripts)

NOTA: Análises IA foram desacopladas do worker de ingestão.

Novo fluxo:
1. Ingestão de dados: resilience_ingestor.py (Worker Celery)
2. Análises IA: ai_analyzer.py + scripts/run_ai_analysis.py (Manual/Cron)

Benefícios:
- ✅ Controle granular de limite de IA por dia
- ✅ Sem timeout durante ingestão
- ✅ Reutilização de budget de API
- ✅ Fácil pausar/resumir análises

Uso:
    # Analisar 100 gastos
    python scripts/run_ai_analysis.py --type GASTO --limit 100
    
    # Análises diárias otimizadas
    python scripts/run_ai_analysis.py --daily
    
    # Cron: adicionar ao crontab
    0 6 * * * cd /path/to/project && python scripts/run_ai_analysis.py --daily
"""

# Arquivo mantido para compatibilidade/referência histórica
# TODO: Remover em v2.0 após migração completa
