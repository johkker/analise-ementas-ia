# 📊 Lente Cidadã - Visão Geral do Projeto

## 🎯 Objetivo Principal
**Análise transparente de gastos e proposições de políticos brasileiros usando IA**

Sistema integrado que coleta dados da Câmara dos Deputados, armazena em PostgreSQL, e utiliza Google Gemini para análises críticas de proposições legislativas e gastos de gabinete.

---

## 🏗️ Arquitetura do Projeto

### Stack Tecnológico

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Banco de Dados**: PostgreSQL com SQLAlchemy ORM async
- **Fila de Processamento**: Celery + Redis
- **IA**: Google Generative AI (Gemini)
- **Migrações**: Alembic
- **Validação**: Pydantic + Pydantic Settings

#### Frontend
- **Framework**: Next.js 16.1.5 (TypeScript)
- **Styling**: Tailwind CSS v4
- **Componentes**: Shadcn UI + Radix UI
- **Cache**: TanStack React Query
- **Ícones**: Lucide React

#### Infraestrutura
- **Containerização**: Docker Compose
- **Serviços**: Postgres, Redis, FastAPI, Celery Worker, Flower
- **Deployment**: Railway (backend), Vercel (frontend)

---

## 📁 Estrutura de Diretórios

### Backend (`/src`)
```
src/
├── core/                    # Configuração global
│   ├── config.py           # Variáveis de ambiente (Pydantic Settings)
│   ├── database.py         # AsyncSessionLocal, engine
│   ├── celery_app.py       # Configuração Celery
│   └── security.py         # Rate limiting
│
├── models/                 # ORM SQLAlchemy
│   ├── base.py            # TimestampMixin, Base class
│   ├── politico.py        # Politico, Partido
│   ├── gasto.py           # Gasto, Empresa
│   ├── proposicao.py      # Proposicao, autoria_proposicao (m2m)
│   ├── votacao.py         # Votacao, Voto
│   └── analise.py         # AnaliseIA (resultado da análise)
│
├── schemas/               # Pydantic DTOs
│   ├── camara_api.py      # Schemas para respostas da API Câmara
│   └── public_api.py      # Schemas para endpoints públicos
│
├── services/              # Lógica de negócio
│   ├── extractor/
│   │   ├── base.py        # BaseExtractor abstrato
│   │   └── camara.py      # CamaraExtractor concreto
│   ├── resilience_ingestor.py  # ResilienceIngestor com DLQ
│   ├── data_fetcher.py    # Celery tasks de fetch
│   ├── ai_worker.py       # Celery tasks de análise IA
│   └── llm_service.py     # GeminiClient wrapper
│
├── api/routes/            # Rotas FastAPI
│   ├── deputados.py       # GET /deputados, /deputados/{id}
│   ├── proposicoes.py     # GET /proposicoes, /proposicoes/{id}
│   ├── gastos.py          # GET /gastos/exploration (filtros avançados)
│   └── stats.py           # GET /stats/dashboard
│
├── main.py                # Entrypoint FastAPI + health checks
└── __init__.py
```

### Frontend (`/frontend`)
```
frontend/
├── app/                     # Next.js App Router
│   ├── layout.tsx          # Root layout com providers
│   ├── page.tsx            # Homepage (dashboard)
│   ├── deputados/
│   │   └── page.tsx        # Lista de deputados
│   ├── proposicoes/
│   │   └── page.tsx        # Lista de proposições
│   ├── gastos/
│   │   └── page.tsx        # Explorador de gastos
│   └── about/
│       └── page.tsx        # Página sobre
│
├── components/
│   ├── ui/                 # Shadcn UI components
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   ├── badge.tsx
│   │   ├── dialog.tsx
│   │   ├── input.tsx
│   │   ├── table.tsx
│   │   └── skeleton.tsx
│   ├── deputados/
│   │   └── DeputyDetailsModal.tsx  # Modal com perfil completo
│   ├── Navbar.tsx          # Navegação principal
│   └── providers.tsx       # React Query Provider
│
├── lib/
│   ├── api.ts              # Configuração fetch + endpoints
│   └── utils.ts            # Utilitários (cn, etc)
│
├── package.json            # Dependências frontend
├── next.config.ts          # Configuração Next.js
├── tsconfig.json           # Configuração TypeScript
└── tailwind.config.js      # Configuração Tailwind
```

---

## 💾 Modelo de Dados

### Tabelas Principais

#### Core Político
- **partidos**: sigla, nome, logo_url
- **politicos**: nome_civil, nome_parlamentar, partido_id (FK), uf, email, foto_url, id_legislatura

#### Financeiro
- **empresas**: cnpj (PK), nome_fantasia, razao_social
- **gastos_gabinete**: valor, data_emissao, tipo_despesa, politico_id (FK), empresa_cnpj (FK), url_documento

#### Legislativo
- **proposicoes**: sigla_tipo, numero, ano, ementa, data_apresentacao
- **autoria_proposicao**: many-to-many entre Politico e Proposicao
- **votacoes**: data, sigla_orgao, descricao, proposicao_id (FK)
- **votos**: voto (Sim/Não/Abstenção), politico_id (FK), votacao_id (FK)

#### IA & Análises
- **analises_ia**: entidade_tipo, entidade_id, score_anomalia, resumo_critico, impacto_financeiro, grupos_beneficiados, riscos_corrupcao, raw_response

---

## 🔗 Endpoints da API

### Deputados
```
GET  /deputados/                    # Lista com filtros (partido, uf, limit, offset)
GET  /deputados/{id}                # Detalhes completos
GET  /deputados/partidos/           # Lista de partidos disponíveis
```

### Proposições
```
GET  /proposicoes/                  # Lista com filtro por politico_id
GET  /proposicoes/{id}              # Detalhes da proposição
```

### Gastos
```
GET  /gastos/exploration            # Exploração avançada com múltiplos filtros:
                                    # - politico_id, politico_nome
                                    # - sigla_partido
                                    # - data_inicio, data_fim, ano, mes
                                    # - tipo_despesa
                                    # - min_valor, max_valor
                                    # - has_ai_analysis
                                    # - Paginação e ordenação
```

### Estatísticas
```
GET  /stats/dashboard               # Métricas globais:
                                    # - total_gastos, total_proposicoes
                                    # - top_gastos, top_proposicoes
                                    # - análises com anomalias
```

### Ingestão (Endpoints Internos)
```
POST /ingest/deputados              # Busca e salva todos os deputados
POST /ingest/gastos/{deputado_id}   # Busca gastos de um deputado
```

---

## 🔄 Fluxo de Dados

### 1️⃣ Extração (Câmara API)
```
CamaraExtractor
├── get_deputados()              → GET /deputados
├── get_gastos(id, ano)          → GET /deputados/{id}/despesas
├── get_proposicoes(data)        → GET /proposicoes
├── get_votacoes(data)           → GET /votacoes
└── get_votacao_votos(votacao_id) → GET /votacoes/{id}/votos
```

### 2️⃣ Ingestão (Resilience Pattern)
```
ResilienceIngestor
├── process_deputados_batch()
├── process_gastos_batch()
├── process_proposicoes_batch()
└── process_votos_batch()
    ├── Validação Strict (Pydantic)
    ├── Upsert no PostgreSQL
    └── DLQ Fallback se falhar
```

### 3️⃣ Análise IA (Celery Async)
```
Celery Tasks
├── processar_analise_ia(entidade_tipo, entidade_id, texto)
│   └── GeminiClient.analisar_gasto()
│       └── Structured Output (response_schema)
│           ├── score_anomalia
│           ├── resumo_critico
│           ├── impacto_financeiro
│           ├── grupos_beneficiados
│           └── riscos_corrupcao
└── mass_analyze_pending_gastos()
    └── Processa Gastos sem AnaliseIA em batch
```

### 4️⃣ Visualização (Frontend Next.js)
```
React Components
├── HomePage (Dashboard Stats)
├── DeputadosList → DeputyDetailsModal
├── ProposicoesList
└── GastosExploration (Filtros avançados)
```

---

## ⚙️ Funcionalidades Principais

### ✅ Implementadas

#### Backend
- ✅ Modelos ORM completos (Politico, Gasto, Proposicao, Votacao, AnaliseIA)
- ✅ Extrator da API Câmara (CamaraExtractor)
- ✅ Ingestão com padrão Resilience (DLQ)
- ✅ Rate limiting na API
- ✅ Endpoints RESTful para Deputados, Proposições, Gastos
- ✅ Filtros avançados em /gastos/exploration
- ✅ Celery tasks para fetch background
- ✅ Integração Gemini com análise de gastos
- ✅ Alembic migrations

#### Frontend
- ✅ Homepage com dashboard de stats
- ✅ Lista de deputados com filtros
- ✅ DeputyDetailsModal com perfil completo
- ✅ Explorador de proposições
- ✅ Explorador de gastos (com filtros avançados)
- ✅ React Query para caching global
- ✅ Navbar com navegação
- ✅ Responsive design (Tailwind + Shadcn)

### 🟡 Em Progresso / Futuro

- 📊 Dashboard de análises IA (visualização de anomalias)
- 📈 Gráficos de gastos por tipo/período
- 🔔 Alertas em tempo real para gastos suspeitos
- 💬 Chat com IA para perguntas sobre políticos
- 🗳️ Análise de votações e padrões de voto
- 🔐 Autenticação usuário (JWT)
- 📱 Aplicativo mobile (React Native)
- 🌐 Integração com TSE para dados de doações

---

## 🚀 Como Rodar Localmente

### Pré-requisitos
- Docker + Docker Compose
- Python 3.11+ (para desenvolvimento sem Docker)
- Node.js 18+ (para frontend)
- API Key do Google Gemini

### Passos

#### 1. Clone e Configure Env
```bash
git clone <repo>
cd analise-ementas-ia

# Backend env
cp .env.example .env
# Edite .env com suas keys (GEMINI_API_KEY, DATABASE_URL, etc)
```

#### 2. Rode com Docker Compose
```bash
docker-compose up -d
```

Serviços:
- Backend API: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- Postgres: `localhost:5432`
- Redis: `localhost:6379`
- Flower (Celery Monitor): `http://localhost:5555`

#### 3. Ou Rode Manualmente

**Backend:**
```bash
poetry install
alembic upgrade head
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

#### 4. Trigger Ingestão
```bash
# Via API (POST endpoints)
curl -X POST http://localhost:8000/ingest/deputados

# Ou via Celery beat (tasks agendadas)
```

---

## 📋 Checklist de Status

### Backend ✅
- [x] Estrutura base (FastAPI, SQLAlchemy, Celery)
- [x] Modelos de dados
- [x] Extrator Câmara API
- [x] Ingestão com Resilience
- [x] Endpoints CRUD
- [x] Rate limiting
- [x] Análise IA (Gemini)
- [x] Celery tasks
- [x] Migrações Alembic
- [ ] Testes unitários (pytest)
- [ ] Autenticação JWT
- [ ] Logs estruturados (loguru)

### Frontend ✅
- [x] Setup Next.js + TypeScript
- [x] Shadcn UI + Tailwind
- [x] React Query provider
- [x] API client (fetch wrapper)
- [x] Homepage com stats
- [x] Lista deputados
- [x] DeputyDetailsModal
- [x] Proposições list
- [x] Gastos explorer
- [ ] Charts (recharts/plotly)
- [ ] Dark mode
- [ ] PWA (Progressive Web App)
- [ ] i18n (internacionalização)

### Deployment 🚀
- [x] Docker Compose local
- [x] Railway backend config
- [x] Vercel frontend config
- [ ] CI/CD (GitHub Actions)
- [ ] Staging environment
- [ ] Monitoring & Alertas

---

## 📚 Documentação Adicional

- **context.md**: Arquitetura de dados e schema detalhado
- **implementation_plan.md**: Roadmap de features
- **api-docs.json**: Documentação OpenAPI da Câmara
- **walkthrough.md**: Tutorial completo de setup
- **README.md**: Instruções básicas

---

## 🔐 Segurança & Performance

### Rate Limiting
- API: `5 req/min` por IP (configurável)
- Gemini: `4 req/min` (limite oficial)

### Resilience
- DLQ (Dead Letter Queue) para falhas de ingestão
- Retry automático com backoff exponencial
- Validação Pydantic strict

### Performance
- Async/await em toda a stack
- Índices em `politico_id`, `data_emissao`, `empresa_cnpj`
- React Query para cache frontend
- Paginação em endpoints de lista

---

## 🤝 Contribuição

1. Crie uma branch: `git checkout -b feature/sua-feature`
2. Commit suas mudanças: `git commit -m 'Add feature'`
3. Push: `git push origin feature/sua-feature`
4. Abra Pull Request

---

## 📝 Licença & Créditos

- Dados públicos: Câmara dos Deputados (Dados Abertos)
- IA: Google Generative AI (Gemini)
- Framework: FastAPI + Next.js
- Componentes: Shadcn UI

---

**Última atualização**: 28 de Janeiro de 2026

