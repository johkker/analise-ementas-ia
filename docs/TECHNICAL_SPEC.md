# 📋 TECHNICAL SPECIFICATION - Lupa Política v1.0

**Última atualização**: 28 Jan 2026  
**Status**: ✅ COMPLETO E EM PRODUÇÃO

---

## 📑 Índice

1. [Arquitetura](#arquitetura)
2. [Modelo de Dados](#modelo-de-dados)
3. [Endpoints API](#endpoints-api)
4. [Análise IA (Desacoplada)](#-análise-ia-desacoplada-v10)
5. [Rescanning Automático (90 Dias)](#rescanning-automático-de-90-dias)
6. [Como Ativar Celery Beat](#como-ativar-celery-beat)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitetura

### Stack Completo

```
FRONTEND                    BACKEND                    DATA
─────────                   ───────                    ────
Next.js 16                  FastAPI                    PostgreSQL 15
React 19                    SQLAlchemy 2.0 (async)     + Redis 7
TypeScript                  Pydantic                   + Alembic
Tailwind v4                 Celery + Redis
Shadcn UI                   Google Gemini API
React Query (caching)       
                            Railway (deploy)
Vercel (deploy)
```

### Fluxo de Dados

```
Câmara API Public        Google Gemini IA
      │                        │
      └────────────┬───────────┘
                   │
         ┌─────────▼──────────┐
         │   FastAPI Backend  │
         │  (src/main.py)     │
         └─────────┬──────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
   Routes      Services      Models
   (/api/)    (data_fetcher, (ORM)
             ai_worker,
             extractor)
      │            │            │
      └────────────┼────────────┘
                   │
      ┌────────────▼────────────┐
      │   PostgreSQL Database   │
      │   (8 tables)            │
      └─────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │   React Query Cache     │
      │   (Redis)               │
      └─────────────────────────┘
                   │
      ┌────────────▼────────────┐
      │   Next.js Frontend      │
      │   (Vercel)              │
      └─────────────────────────┘
```

---

## 📊 Modelo de Dados

### 8 Tabelas Principais

#### 1. **politicos** (600 registros)
```sql
CREATE TABLE politicos (
  id BIGINT PRIMARY KEY,
  nome VARCHAR NOT NULL,
  partido_id INT,
  email VARCHAR,
  telefone VARCHAR,
  uf CHAR(2),
  url_foto VARCHAR,
  criado_em TIMESTAMP DEFAULT NOW(),
  atualizado_em TIMESTAMP DEFAULT NOW()
);
```
**Índices**: id (PK), partido_id, uf  
**Origem**: Câmara API

#### 2. **partidos** (30 registros)
```sql
CREATE TABLE partidos (
  id INT PRIMARY KEY,
  sigla VARCHAR(10) UNIQUE NOT NULL,
  nome VARCHAR NOT NULL
);
```
**Índices**: sigla  
**Origem**: Câmara API

#### 3. **gastos_gabinete** (50k+ registros)
```sql
CREATE TABLE gastos_gabinete (
  id BIGINT PRIMARY KEY,
  politico_id BIGINT NOT NULL REFERENCES politicos(id),
  descricao VARCHAR NOT NULL,
  valor DECIMAL(12,2) NOT NULL,
  data_pagamento DATE NOT NULL,
  data_documento DATE,
  cnpj VARCHAR(14),  -- nullable, nem todos têm
  empresa_id INT,
  criado_em TIMESTAMP DEFAULT NOW(),
  UNIQUE(politico_id, id)
);
```
**Índices**: politico_id, data_pagamento, valor  
**Origem**: Câmara API (API de Gastos)  
**Crítico**: data_pagamento e data_documento usadas no rescanning

#### 4. **empresas** (1k+ registros)
```sql
CREATE TABLE empresas (
  id INT PRIMARY KEY,
  cnpj VARCHAR(14) UNIQUE,
  nome VARCHAR NOT NULL,
  ramo VARCHAR
);
```
**Índices**: cnpj, nome  
**Origem**: Câmara API

#### 5. **proposicoes** (500+ registros)
```sql
CREATE TABLE proposicoes (
  id INT PRIMARY KEY,
  numero INT NOT NULL,
  ano INT NOT NULL,
  titulo VARCHAR NOT NULL,
  ementa TEXT,
  data_apresentacao DATE,
  status VARCHAR,
  url_api_camara VARCHAR,
  criado_em TIMESTAMP DEFAULT NOW(),
  UNIQUE(numero, ano)
);
```
**Índices**: numero, ano, data_apresentacao  
**Origem**: Câmara API

#### 6. **autoria_proposicao** (junction table)
```sql
CREATE TABLE autoria_proposicao (
  proposicao_id INT NOT NULL REFERENCES proposicoes(id),
  politico_id BIGINT NOT NULL REFERENCES politicos(id),
  papel VARCHAR(20),  -- "Autor Principal", "Coautor", etc
  PRIMARY KEY (proposicao_id, politico_id)
);
```

#### 7. **votacoes** (100+ registros)
```sql
CREATE TABLE votacoes (
  id INT PRIMARY KEY,
  proposicao_id INT REFERENCES proposicoes(id),
  data TIMESTAMP NOT NULL,
  resultado VARCHAR,
  placar_sim INT,
  placar_nao INT,
  placar_abstencao INT
);
```
**Índices**: proposicao_id, data

#### 8. **votos** (5k+ registros)
```sql
CREATE TABLE votos (
  id INT PRIMARY KEY,
  votacao_id INT NOT NULL REFERENCES votacoes(id),
  politico_id BIGINT NOT NULL REFERENCES politicos(id),
  voto VARCHAR(10),  -- "Sim", "Não", "Abstenção"
  PRIMARY KEY (votacao_id, politico_id)
);
```

#### Tabelas de Sistema

```sql
-- Análises IA (200+ registros)
CREATE TABLE analises_ia (
  id SERIAL PRIMARY KEY,
  gasto_id BIGINT REFERENCES gastos_gabinete(id),
  score_anomalia FLOAT,  -- 0-1
  categoria_risco VARCHAR(50),  -- "Baixo", "Médio", "Alto"
  justificativa TEXT,
  criado_em TIMESTAMP DEFAULT NOW()
);

-- Dead Letter Queue (erros de ingestão)
CREATE TABLE gastos_dlq (
  id SERIAL PRIMARY KEY,
  politico_id BIGINT,
  dados_raw JSONB,  -- dados que falharam
  erro TEXT,
  criado_em TIMESTAMP DEFAULT NOW()
);
```

### Relationships Diagram

```
politicos (600)
  ├── 1:N → gastos_gabinete (50k+)
  ├── 1:N → votos (5k+)
  ├── N:M → proposicoes (via autoria_proposicao)
  └── FK → partidos (30)

proposicoes (500+)
  ├── 1:N → votacoes (100+)
  ├── N:M → politicos (via autoria_proposicao)
  └── 1:N → votos (via votacoes)

votacoes (100+)
  ├── 1:N → votos (5k+)
  └── FK → proposicoes

gastos_gabinete (50k+)
  ├── 1:1 → analises_ia (200+)
  ├── FK → politicos
  ├── FK → empresas (nullable)
  └── → gastos_dlq (on error)
```

---

## 🔌 Endpoints API

### Deputados

```
GET /deputados/
  Params: 
    - partido: string (filtro)
    - uf: string (filtro)
    - skip: int = 0
    - limit: int = 100
  Response:
    [{
      id: int,
      nome: string,
      partido: string,
      uf: string,
      gastos_total: float,
      anomalias_count: int
    }]

GET /deputados/{id}
  Response:
    {
      id: int,
      nome: string,
      partido: string,
      email: string,
      uf: string,
      foto_url: string,
      gastos_total: float,
      gastos_count: int,
      media_gasto: float,
      proposicoes_count: int,
      votos_count: int,
      anomalias: [{
        gasto_id: int,
        score: float,
        categoria: string,
        justificativa: string
      }]
    }

GET /deputados/partidos/
  Response:
    [{
      partido: string,
      sigla: string,
      deputados_count: int,
      gastos_total: float,
      media_gasto_per_deputado: float
    }]
```

### Proposições

```
GET /proposicoes/
  Params:
    - titulo: string (search)
    - skip: int = 0
    - limit: int = 100
  Response:
    [{
      id: int,
      numero: int,
      ano: int,
      titulo: string,
      data_apresentacao: date,
      status: string,
      autores_count: int,
      votos_count: int
    }]

GET /proposicoes/{id}
  Response:
    {
      id: int,
      numero: int,
      ano: int,
      titulo: string,
      ementa: string,
      data_apresentacao: date,
      status: string,
      autores: [{
        politico_id: int,
        nome: string,
        papel: string
      }],
      votacoes: [{
        id: int,
        data: datetime,
        placar_sim: int,
        placar_nao: int,
        resultado: string
      }]
    }
```

### Gastos (Advanced Exploration)

```
GET /gastos/exploration
  Params:
    - politico_id: int (required)
    - min_valor: float
    - max_valor: float
    - data_inicio: date
    - data_fim: date
    - partido: string
    - categoria_risco: string (Baixo/Médio/Alto)
    - empresa_id: int
    - apenas_anomalias: bool
    - sort_by: string (valor, data, anomalia)
    - order: string (asc/desc)
    - skip: int = 0
    - limit: int = 100
  Response:
    [{
      id: int,
      descricao: string,
      valor: float,
      data_pagamento: date,
      empresa: string,
      score_anomalia: float,
      categoria_risco: string,
      justificativa: string
    }]
```

### Stats & Dashboard

```
GET /stats/dashboard
  Response:
    {
      total_deputados: int,
      total_gastos: float,
      media_gasto_deputado: float,
      gasto_maximo: float,
      gasto_minimo: float,
      gastos_count: int,
      anomalias_count: int,
      proposicoes_count: int,
      votos_count: int,
      top_gastos: [{gasto}],
      top_anomalias: [{analise}],
      partidos_stats: [{stats}]
    }
```

### Ingestão (Manual)

```
POST /ingest/deputados
  Response:
    {
      status: "Deputados population finished",
      count: 600
    }

POST /ingest/gastos/{deputado_id}
  Response:
    {
      status: "Ingestion completed",
      count: 1247
    }
```

---

## 🤖 Análise IA (Desacoplada) - v1.0

### Novo Fluxo (Desacoplado)

**ANTES** (v0.9):
```
Ingestão (Worker) → Análise IA automática
❌ Problema: timeout na ingestão, difícil controlar limite de API
```

**DEPOIS** (v1.0):
```
Ingestão (Worker) → [Salva dados]
                ↓
Análise IA (Script Manual) → [Analisa a pedido]

✅ Ingestão rápida
✅ Controle fino de limite de API
✅ Fácil pausar/retomar
✅ Sem timeout durante ingestão
```

### Tipos de Análise

| Tipo | O quê | Ordenação | Uso |
|------|-------|-----------|-----|
| **GASTO** | Anomalias em gastos | Data desc | Daily (50) |
| **VOTO** | Padrões de voto | Data desc | Daily (30) |
| **PROPOSICAO** | Impacto proposição | Data desc | Daily (20) |
| **CROSS_DATA** | Correlações (gasto ↔ voto) | Deputado | Weekly |

### Como Usar

#### Opção 1: Análise de um tipo específico

```bash
# Analisar 100 gastos (não-analisados, mais recentes primeiro)
python scripts/run_ai_analysis.py --type GASTO --limit 100

# Analisar 50 votos
python scripts/run_ai_analysis.py --type VOTO --limit 50

# Analisar 20 proposições
python scripts/run_ai_analysis.py --type PROPOSICAO --limit 20
```

#### Opção 2: Análises diárias otimizadas

```bash
# Defaults: 50 gastos + 30 votos + 20 proposições = 100 total/dia
python scripts/run_ai_analysis.py --daily

# Customizar limites
python scripts/run_ai_analysis.py --daily \
  --daily-gastos 80 \
  --daily-votos 40 \
  --daily-proposicoes 30
```

#### Opção 3: Cron job (Recomendado)

```bash
# Adicionar ao crontab (rodar diariamente às 06:00)
0 6 * * * cd /home/user/analise-ementas-ia && python scripts/run_ai_analysis.py --daily

# Ou com logs
0 6 * * * cd /home/user/analise-ementas-ia && python scripts/run_ai_analysis.py --daily >> /var/log/lupa-ai.log 2>&1
```

### Lógica de Seleção de Documentos

```python
# Cada analisador segue:

1. Buscar documentos NÃO analisados
   WHERE entidade_id NOT IN (
     SELECT entidade_id FROM analises_ia 
     WHERE entidade_tipo = 'GASTO'
   )

2. Ordenar por data do documento (DESC) - mais recentes primeiro
   ORDER BY data_pagamento DESC  # Para gastos
   ORDER BY data DESC             # Para votos
   ORDER BY data_apresentacao DESC # Para proposições

3. Limitar a N (ex: 50)
   LIMIT 50

4. Analisar cada um sequencialmente
   - Chamar Gemini IA
   - Salvar resultado em analises_ia table
   - Log de progresso
```

### Exemplo de Resultado

```bash
$ python scripts/run_ai_analysis.py --type GASTO --limit 10

🚀 Running GASTO analysis (limit: 10)...

  [10/10] Analyzed...

============================================================
📊 Analysis Result: GASTO
────────────────────────────────────────────────────────────
  Analyzed:  10
  Succeeded: 9
  Failed:    1
============================================================
```

### API Python (Programático)

```python
from src.services.ai_analyzer import AIAnalysisManager, AnalysisType
import asyncio

async def main():
    manager = AIAnalysisManager()
    
    # Análise de um tipo
    result = await manager.run_analysis(
        analysis_type=AnalysisType.GASTO,
        limit=100
    )
    print(f"Analyzed: {result['analyzed']}, Succeeded: {result['succeeded']}")
    
    # Análises diárias
    daily_result = await manager.run_daily_analyses(
        gasto_limit=50,
        voto_limit=30,
        proposicao_limit=20
    )
    print(f"Total: {daily_result['total_succeeded']}")

asyncio.run(main())
```

### Estrutura do Código

```
src/services/
├── ai_analyzer.py (NOVO - 400+ linhas)
│   ├── BaseAnalyzer (classe base)
│   ├── GastoAnalyzer
│   ├── VotoAnalyzer
│   ├── ProposicaoAnalyzer
│   ├── CrossDataAnalyzer
│   └── AIAnalysisManager (orquestra tudo)
│
├── ai_worker.py (DEPRECATED)
│   └─ Agora só documenta migração
│
└── [outros]

scripts/
├── run_ai_analysis.py (NOVO - script CLI)
│   ├── Modo single type
│   ├── Modo daily
│   └── Pretty print resultado
```

### Limitações & Rate Limits

```
Gemini API:
├─ Limit: 5 requisições por minuto (RPM)
├─ Timeout: 2 minutos por request

Recomendações:
├─ Max por dia: 100-120 análises (espaçadas)
├─ Daily default: 100 (50G + 30V + 20P)
├─ Se precisar mais: rodar --daily múltiplas vezes com interval
```

---

## 🔄 Rescanning Automático de 90 Dias

### O Problema

```
Sem Rescanning:
├─ Busca dados mais recentes
├─ ❌ Câmara demora 30 dias → dados perdidos
├─ ❌ Deputados demoram 3 meses → gastos desaparecem
└─ ❌ CRÍTICO: ~30-50% dos dados atrasados são perdidos

Com Rescanning:
├─ Busca últimos 90 dias TODOS OS DIAS
├─ ✅ Capta Câmara defasagem (30 dias)
├─ ✅ Capta deputados atrasados (até 3 meses)
└─ ✅ CRÍTICO: 100% dos dados capturados
```

### Implementação

```python
# Em src/services/data_fetcher.py

@celery_app.task(bind=True, max_retries=3)
def fetch_gastos_rescan_task(self):
    """
    Rescanning automático de 90 dias
    - Executa: Todos os dias às 02:00 AM UTC
    - Busca: Últimos 90 dias
    - Filtra: Por data do documento/pagamento
    - Dedup: Automática no banco (ON CONFLICT DO UPDATE)
    """
    asyncio.run(_async_fetch_gastos_rescan())

async def _async_fetch_gastos_rescan():
    # 1. Get all deputies
    # 2. Calculate date range (90 days back from today)
    # 3. For each deputy:
    #    - Fetch gastos from Câmara API (por ano)
    #    - Filter by dataDocumento/dataPagamento within 90-day window
    #    - Deduplicate via SQLAlchemy upsert
    # 4. Log results
```

### Schedule (Celery Beat)

```python
# Em src/core/celery_app.py

celery_app.conf.beat_schedule = {
    'fetch_gastos_rescan_daily': {
        'task': 'src.services.data_fetcher.fetch_gastos_rescan_task',
        'schedule': crontab(hour=2, minute=0),  # 2 AM UTC daily
        'options': {'queue': 'default', 'max_retries': 3}
    },
    'fetch_gastos_yearly': {
        'task': 'src.services.data_fetcher.fetch_gastos_task',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),  # Sunday 3 AM
        'args': (2026,),
        'options': {'queue': 'default'}
    },
    'fetch_proposicoes_daily': {
        'task': 'src.services.data_fetcher.fetch_proposicoes_task',
        'schedule': crontab(hour=4, minute=0),
        'args': (30,),
        'options': {'queue': 'default'}
    },
    'fetch_votacoes_daily': {
        'task': 'src.services.data_fetcher.fetch_votacoes_task',
        'schedule': crontab(hour=5, minute=0),
        'args': (14,),
        'options': {'queue': 'default'}
    },
}
```

### Timeline Diário

```
02:00 AM UTC  → Rescan 90d (gastos atrasados)
               └─ Duração: 2-5 min
               └─ Requisições: ~300
               └─ CRÍTICO - não skip!

03:00 AM UTC  → Full year sync (validação - DOMINGO apenas)
               └─ Duração: 10-20 min
               └─ Requisições: ~3.000

04:00 AM UTC  → Proposições 30d
               └─ Duração: 3-5 min

05:00 AM UTC  → Votações 14d
               └─ Duração: 2-4 min

Total: ~20-30 min/dia, off-peak (2-6 AM UTC)
```

### Garantias

- ✅ 100% cobertura temporal (últimos 90 dias)
- ✅ Zero duplicatas (upsert automático)
- ✅ Idempotente (seguro rodar múltiplas vezes)
- ✅ Defasagem Câmara coberta (30 dias)
- ✅ Atraso deputados coberto (até 3 meses)

---

## 🚀 Como Ativar Celery Beat

### Opção 1: Railway (RECOMENDADO para produção)

#### Passo 1: Atualizar railway.json

```json
{
  "services": {
    "backend": {
      "name": "Lupa-API",
      "startCommand": "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
    },
    "celery-worker": {
      "name": "Lupa-Worker",
      "startCommand": "celery -A src.core.celery_app worker --loglevel=info"
    },
    "celery-beat": {
      "name": "Lupa-Beat",
      "startCommand": "celery -A src.core.celery_app beat --loglevel=info"
    }
  }
}
```

#### Passo 2: Deploy

```bash
git add .
git commit -m "Add Celery Beat scheduler"
git push
# Railway auto-deploy de todos os 3 serviços
```

#### Verificação no Railway Dashboard
```
Services > Lupa-Beat
├─ Status: ✅ Running (verde)
├─ Logs: "Beat: Starting..."
└─ Monitor continuamente
```

### Opção 2: Docker Compose (Local/Dev)

```yaml
# docker-compose.yml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: lupa_politica
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass

  redis:
    image: redis:7

  api:
    build: .
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000
    depends_on:
      - postgres
      - redis

  celery-worker:
    build: .
    command: celery -A src.core.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres

  celery-beat:
    build: .
    command: celery -A src.core.celery_app beat --loglevel=info
    depends_on:
      - redis
      - postgres
    volumes:
      - ./celerybeat-schedule:/app/celerybeat-schedule
```

```bash
docker-compose up -d
docker-compose logs -f celery-beat  # Monitorar
```

### Opção 3: Manual (Linux/Mac)

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Worker
celery -A src.core.celery_app worker --loglevel=info

# Terminal 3: Beat
celery -A src.core.celery_app beat --loglevel=info

# Terminal 4: API
uvicorn src.main:app --reload
```

### Validação

```bash
# Check 1: Beat está rodando?
ps aux | grep beat
# Esperado: celery -A src.core.celery_app beat

# Check 2: Tasks estão agendadas?
celery -A src.core.celery_app inspect scheduled
# Esperado: lista de tasks com próximas execuções

# Check 3: Ver logs
redis-cli
> KEYS celery*
# Esperado: tasks na queue

# Check 4: Monitor visual (Flower)
pip install flower
celery -A src.core.celery_app flower
# Acesso: http://localhost:5555
```

---

## 🐛 Troubleshooting

### Task não executa

```bash
# Verificar se Beat está rodando
ps aux | grep beat

# Verificar se Worker está rodando
ps aux | grep worker

# Verificar Redis
redis-cli ping
# Esperado: PONG

# Verificar schedule
celery -A src.core.celery_app inspect scheduled
```

### Task roda mas não insere dados

```sql
-- Verificar database connection
SELECT COUNT(*) FROM politicos;

-- Verificar se table existe
\d gastos_gabinete

-- Verificar DLQ para erros
SELECT * FROM gastos_dlq LIMIT 5;
```

### Redis não conecta

```bash
# Restart Redis
redis-cli shutdown
redis-server

# Check connection
redis-cli ping
# Esperado: PONG
```

### Arquivo celerybeat-schedule corrompido

```bash
# Delete (Beat vai recriar automaticamente)
rm celerybeat-schedule

# Restart Beat
celery -A src.core.celery_app beat
```

---

## 📊 Monitoramento

### Métricas Esperadas

| Métrica | Esperado |
|---------|----------|
| Gastos capturados/dia | 500-2.000 |
| Taxa de deduplicação | 60-80% |
| Tempo rescanning | 2-5 min |
| Taxa de erro | <0.1% |
| Cobertura temporal | 90 dias |

### Validação Diária

```sql
-- Quantos gastos capturados hoje?
SELECT COUNT(*) FROM gastos 
WHERE created_at >= now() - interval '1 day';

-- Cobertura correta?
SELECT MIN(data_pagamento), MAX(data_pagamento) FROM gastos;

-- Sem duplicatas?
SELECT id, COUNT(*) FROM gastos 
GROUP BY id HAVING COUNT(*) > 1;
-- Esperado: 0 rows

-- Erros na DLQ?
SELECT COUNT(*) FROM gastos_dlq 
WHERE created_at >= now() - interval '1 day';
```

---

**Status**: ✅ Documentação completa  
**Criticidade**: 🔴 ALTA (rescanning é essencial)  
**Próximo**: Ativar Celery Beat em produção

