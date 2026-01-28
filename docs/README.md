# 🇧🇷 Lupa Política - Transparência em Gastos Parlamentares

**Status**: 🟢 **PRODUÇÃO - v1.0** | **Última atualização**: 28 Jan 2026

## O Projeto

Sistema que analisa e expõe gastos de deputados federais brasileiros com IA, integrando dados públicos da Câmara dos Deputados com análise de anomalias usando Gemini.

**Impacto**: Tornando a política brasileira mais transparente para cidadãos, jornalistas e pesquisadores.

---

## 🚀 Quick Start

### URLs de Acesso
```
Frontend:     https://<seu-vercel-url>
Backend API:  https://<seu-railway-url>
Docs API:     https://<seu-railway-url>/docs
```

### Setup Local (Dev)
```bash
# Backend
poetry install
poetry shell
uvicorn src.main:app --reload

# Frontend (em outro terminal)
cd frontend
npm install
npm run dev

# Celery Worker (em outro terminal)
celery -A src.core.celery_app worker --loglevel=info

# Celery Beat (em outro terminal - CRÍTICO!)
celery -A src.core.celery_app beat --loglevel=info
```

**⭐ IMPORTANTE**: Celery Beat faz rescanning automático de 90 dias. Ver detalhes em [TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md#rescanning-automático-de-90-dias).

---

## 📊 Status v1.0

| Componente | % | Notas |
|-----------|----|----|
| Backend API | 95% | ✅ 8 endpoints funcionando |
| Frontend | 90% | ✅ 5 páginas + modais |
| Database | 100% | ✅ 8 tabelas, 600+ deputados |
| IA (Gemini) | 100% | ✅ Análise de anomalias |
| DevOps | 100% | ✅ Railway + Vercel |
| **Testes** | 0% | ❌ MVP decision: skip testes |
| **Logging** | 0% | ❌ v2 feature |
| **Auth JWT** | 0% | ❌ v2 feature (endpoints públicos) |

---

## 🏗️ Arquitetura em 30 Segundos

```
┌─────────────┐                    ┌──────────────┐
│   Câmara    │                    │   Gemini IA  │
│ API Pública │                    │ (Análise)    │
└──────┬──────┘                    └──────┬───────┘
       │                                  │
       └──────────────┬───────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  FastAPI + Celery          │
        │  (Backend - Railway)       │
        └─────────────┬──────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  PostgreSQL + Redis        │
        │  (Database + Cache)        │
        └──────────────────────────┘
                      │
        ┌─────────────▼──────────────┐
        │  Next.js + React           │
        │  (Frontend - Vercel)       │
        └──────────────────────────┘
```

**Tech Stack**:
- Backend: FastAPI + SQLAlchemy 2.0 (async) + PostgreSQL
- Frontend: Next.js 16 + React 19 + TypeScript + Tailwind v4
- IA: Google Gemini com structured output
- Queue: Celery + Redis
- Deploy: Railway (backend) + Vercel (frontend)

---

## 📦 Dados em Produção

```
Deputados:        600 registros
Partidos:         30 registros
Gastos:           50.000+ registros (2025-2026)
Proposições:      500+ (últimos 90 dias)
Votações:         100+ (últimas 2 semanas)
Análises IA:      200+ (crescendo diariamente)
```

---

## 🔄 Ingestão Automática (Rescanning 90 Dias)

**CRÍTICO**: O sistema faz rescanning automático para capturar gastos que chegam com atraso.

**Por quê**: 
- Câmara tem defasagem até 30 dias
- Deputados podem demorar até 3 meses para lançar um gasto
- Sem rescanning: ~30-50% dos dados atrasados são perdidos

**Schedule** (Celery Beat - automático):
```
02:00 AM UTC  → Rescan 90 dias (DIÁRIO)      ⭐ CRÍTICO
03:00 AM UTC  → Full year sync (DOMINGO)     📊 Validação
04:00 AM UTC  → Proposições 30 dias (DIÁRIO) 📜 Novas
05:00 AM UTC  → Votações 14 dias (DIÁRIO)    🗳️ Recentes
```

**Se não ativar Celery Beat**: Gastos atrasados serão perdidos forever ❌

Ver [TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md#como-ativar-celery-beat) para instruções de ativação.

---

## 8️⃣ Endpoints API

```
GET    /                     # Health check
GET    /deputados/           # Lista com filtros
GET    /deputados/{id}       # Detalhes do deputado
GET    /deputados/partidos/  # Agregação por partido
GET    /proposicoes/         # Lista proposições
GET    /proposicoes/{id}     # Detalhes proposição
GET    /gastos/exploration   # Filtros avançados (10+ params)
GET    /stats/dashboard      # Dashboard agregado
POST   /ingest/deputados     # Ingestão manual
POST   /ingest/gastos/{id}   # Ingestão manual por deputado
```

Docs completa: `https://<api-url>/docs`

---

## 🔐 Segurança

✅ **Implementado**:
- HTTPS/TLS (Railway + Vercel)
- Rate limiting (5 req/min por IP)
- CORS configurado
- Validação Pydantic (strict)
- Secrets em environment variables
- DLQ para falhas de ingestão
- Rescanning automático (prevenção de perda de dados)

❌ **TODO (v2)**:
- JWT auth nos endpoints POST /ingest/*
- Logging estruturado (ELK stack)
- Monitoring com alertas (Sentry)
- Backup automatizado (AWS S3)

---

## 📈 Performance Esperada

| Métrica | Valor |
|---------|-------|
| API latency | <300ms (p95) |
| Frontend load | <2s (LCP) |
| Cache hit rate | 85%+ |
| Error rate | <1% |
| Uptime | 99.9%+ |

---

## 🛠️ Manutenção

### Diário
```bash
curl https://<api-url>/              # Health check
# Railway dashboard > Logs
# Vercel dashboard > Analytics
```

### Semanal
```bash
# Revisar performance
# Railway: Monitoring > Metrics
# Vercel: Analytics > Performance

# Check da fila Celery
# Flower: <api-url>/flower ou localhost:5555
```

### Mensal
```bash
# Backup DB (se necessário)
pg_dump postgresql://... > backup.sql

# Ingestão manual (se necessário)
curl -X POST https://<api-url>/ingest/deputados

# Revisar DLQ
SELECT COUNT(*) FROM gastos_dlq;
```

---

## 📚 Documentação Completa

| Doc | Propósito |
|-----|-----------|
| [README.md](docs/README.md) | Este arquivo - visão geral do projeto |
| [TECHNICAL_SPEC.md](docs/TECHNICAL_SPEC.md) | Specs completas, modelo de dados, rescanning, troubleshooting |
| [ROADMAP.md](docs/ROADMAP.md) | v2 features, timeline, quick wins |

---

## 🚨 Problemas Comuns

| Problema | Solução |
|----------|---------|
| Gastos não aparecem | Ativar Celery Beat (rescanning 90d) - ver TECHNICAL_SPEC.md |
| API lento | Check rate limiting, DB indexing, cache |
| Task não roda | Verificar: Redis ok? Worker rodando? Beat rodando? |
| Dados em duplicata | Deduplicação automática - check DLQ |

---

## 💡 Próximas Ações

**URGENTE (Esta semana)**:
- [ ] Ativar Celery Beat em produção (ver TECHNICAL_SPEC.md)
- [ ] Validar rescanning funciona (monitorar logs)
- [ ] Confirmação: dados sendo capturados diariamente

**v2 (Próximos 2-3 meses)**:
- [ ] Logging estruturado + monitoramento (Sentry)
- [ ] Análise de votações + integração TSE
- [ ] UI improvements (charts, dark mode)
- [ ] IA features (chat, email notifications)

Ver [ROADMAP.md](docs/ROADMAP.md) para detalhes.

---

## 📞 Suporte

**Redis not running?**
```bash
redis-server  # ou docker-compose up
redis-cli ping  # Verificar: PONG
```

**PostgreSQL connection error?**
```bash
psql -U user -d lupa_politica -c "SELECT 1"
# Check Railway: Services > Logs
```

**Celery tasks não executando?**
```bash
ps aux | grep celery  # Beat e Worker rodando?
celery -A src.core.celery_app inspect scheduled  # Tasks agendadas?
```

---

## 📝 Versão

**v1.0 Release**: 28 de Janeiro de 2026  
**Developer**: @johkker  
**License**: MIT (dados públicos)  
**Status**: ✅ PRONTO PARA PRODUÇÃO

---

🎊 **Lupa Política está viva. Transparência brasileira um passo mais perto!**

