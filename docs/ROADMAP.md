# 🛣️ ROADMAP v2+ - Lente Cidadã

**Última atualização**: 28 Jan 2026  
**Status v1.0**: ✅ COMPLETO | **Próxima fase**: v2 (Fevereiro 2026)

---

## 📋 Visão Geral

v1.0 é estável e em produção. v2 focará em features avançadas, monitoramento, e escalabilidade.

```
v1.0 (JAN 2026)
├─ Backend API ✅
├─ Frontend ✅
├─ IA básica ✅
├─ Deploy ✅
└─ Rescanning 90d ✅

v2 (FEV-MAI 2026)
├─ Logging + Monitoring
├─ Análise de votações
├─ UI improvements
├─ IA avançada
└─ Community features
```

---

## 📅 Timeline Proposto

### Fase 1: Logging & Monitoring (1 semana - Fevereiro)

**Objetivo**: Observabilidade completa do sistema

```python
# Backend: Logging estruturado
pip install loguru sentry-sdk

# Implementar:
# - Loguru para logs estruturados (JSON)
# - Sentry para error tracking
# - Prometheus metrics para API
# - Alert rules para anomalias
```

**Deliverables**:
- [ ] Logs JSON estruturados em todos os serviços
- [ ] Sentry integrado (error tracking)
- [ ] Prometheus metrics (API, DB, Celery)
- [ ] Grafana dashboard
- [ ] Alert rules configuradas

**Impacto**: Debugging 10x mais rápido, proativo

---

### Fase 2: Análise Votações + TSE (3 semanas - Março)

**Objetivo**: Análise de padrões de voto e integração com dados TSE

```python
# Novo service: vote_analyzer.py
# - Padrões de voto por assunto
# - Consenso/divergência por partido
# - Integração TSE (eleitorado, financiamento)

# Novas tabelas:
# - tse_financiamento_campanha
# - tse_eleitores_por_municipio
# - votacao_analise_padroes
```

**Deliverables**:
- [ ] API GET /votacoes/analise (padrões)
- [ ] Integração TSE (webcrawling ou open data)
- [ ] Dashboard de correlações (voto x financiamento)
- [ ] Feature: "Qual partido votou junto?"
- [ ] Feature: "Deputado muda posição?"

**Impacto**: Descobrir coalisões, padrões suspeitos

---

### Fase 3: UI Improvements (2 semanas - Abril)

**Objetivo**: Experiência visual e UX aprimorada

```typescript
// Frontend: Charts, dark mode, mobile

// Novas dependências:
npm install recharts
npm install next-themes

// Features:
// - Charts: gastos por time, evolução, categorias
// - Dark mode (toggle)
// - Mobile-first responsivo
// - Exportar dados (CSV, PDF)
// - Search full-text melhorado
```

**Deliverables**:
- [ ] Charts React (gastos, proposições, votos)
- [ ] Dark mode UI completo
- [ ] Mobile 100% responsivo
- [ ] Export (CSV, JSON, PDF)
- [ ] Search com autocomplete
- [ ] Comparador deputados (side-by-side)

**Impacto**: 3x melhor UX, viralização

---

### Fase 4: IA Avançada (3 semanas - Maio)

**Objetivo**: Features de IA para engajamento e insights

```python
# Novas features:
# - Chat: "Pergunte ao Lupa" (RAG com histórico)
# - Email alerts: "Novo gasto suspeito"
# - Recomendações: "Explore isso"
# - Summary IA: "TL;DR da semana política"

# Stack:
# - LangChain para RAG
# - SendGrid para emails
# - Twilio para SMS (futuro)
```

**Deliverables**:
- [ ] Chat RAG (histórico de deputados, proposições)
- [ ] Email alerts (suspicious activity)
- [ ] Weekly summary gerada por IA
- [ ] Recomendações personalizadas
- [ ] SMS alerts (tier premium - futuro)

**Impacto**: Engajamento recorrente, insights

---

## 🎯 Quick Wins (1-2 dias cada)

Implementar entre fases para momentum:

| Quick Win | Impacto | Esforço |
|-----------|--------|--------|
| Busca full-text (SQL LIKE) | 🟢 Alto | 1 dia |
| Comparador deputados | 🟢 Alto | 1 dia |
| Export CSV gastos | 🟢 Médio | 4h |
| API rate limit per user | 🟢 Médio | 4h |
| Sidebar navegação mobile | 🟢 Médio | 4h |
| Filter por "sem anomalia" | 🟢 Baixo | 2h |
| Trending proposições | 🟢 Médio | 1 dia |
| API cache headers | 🟢 Médio | 4h |
| Pagination tipo Instagram | 🟢 Médio | 1 dia |

---

## 🚀 Features Futuras (Roadmap Aberto)

### Community (v2.5?)

```python
# Features:
# - Comentários em gastos/proposições
# - Ratings/upvotes
# - Tags criadas por usuários
# - Denúncias/reports
# - Leaderboard (top reporters)

# Tabelas:
# - comentarios
# - ratings
# - denuncias
# - usuario_reputacao
```

### Analytics (v3?)

```python
# Features:
# - Painel para jornalistas
# - Alertas configuráveis
# - Export dados (CSV, JSON)
# - API para apps terceiros
# - Webhooks para notificações

# Stack:
# - PostgreSQL + TimescaleDB
# - ClickHouse para analytics
# - Apache Superset para dashboards
```

### Mobile App (v3?)

```typescript
// React Native app
// Features:
// - Push notifications
// - Offline mode (alguns dados)
// - Biometric auth
// - Shortcuts (home screen)

// Stack:
// - React Native + Expo
// - Firebase para push
// - SQLite local
```

---

## 📊 Priorização v2

```
PRIORITY MATRIX

Alta Urgência + Alto Impacto:
├─ Logging & Monitoring ⭐⭐⭐
├─ Análise Votações ⭐⭐⭐
├─ UI Improvements ⭐⭐
└─ Search Full-text ⭐⭐

Média Urgência + Alto Impacto:
├─ IA Chat ⭐⭐
├─ Email Alerts ⭐⭐
└─ Export CSV ⭐

Baixa Urgência + Médio Impacto:
├─ Dark mode ⭐
├─ Mobile tweaks ⭐
└─ Comparador deputados ⭐
```

---

## 💰 Estimativa de Esforço v2

| Fase | Esforço | Tempo | Dev Days |
|------|--------|-------|----------|
| 1. Logging | 40h | 1w | 1 dev |
| 2. Votações | 120h | 3w | 1-2 devs |
| 3. UI | 80h | 2w | 1-2 devs |
| 4. IA | 100h | 3w | 1-2 devs |
| **Total v2** | **340h** | **~9w** | **1-2 devs** |

**Timeline**: Fevereiro-Maio 2026 (4 meses)

---

## 🔧 Infraestrutura Melhorias

### Current (v1.0)

```
Railway: 1 API instance + 1 Worker + 1 Beat
PostgreSQL: Single instance
Redis: Single instance
Vercel: Auto-scaling
```

### Recomendado para v2

```
Railway:
├─ API: 2 instances (load balance)
├─ Worker: 2 instances (parallel tasks)
├─ Beat: 1 instance (single)
└─ Cron job: Backup automático

PostgreSQL:
├─ Upgrade para Postgres 16
├─ Replicação standby (failover)
├─ Backups diários + point-in-time
└─ Índices adicionais (performance)

Redis:
├─ Upgrade cluster mode
├─ Replicação
└─ Persistence (RDB + AOF)

Monitoring:
├─ Prometheus + Grafana
├─ Sentry para errors
├─ Uptime Kuma para health check
└─ PagerDuty para on-call
```

---

## 📈 Crescimento Esperado

```
JAN 2026 (v1.0):
├─ Usuários: 100-200
├─ Pageviews/mês: 5k-10k
├─ API calls/mês: 100k
└─ Status: MVP funcional

MAR 2026 (v2):
├─ Usuários: 500-1k
├─ Pageviews/mês: 50k-100k
├─ API calls/mês: 1M
└─ Status: Feature completo

MAY 2026 (v2+):
├─ Usuários: 2k-5k
├─ Pageviews/mês: 200k-500k
├─ API calls/mês: 5M
└─ Status: Production ready

JUL 2026 (v2.5):
├─ Usuários: 5k-10k
├─ Pageviews/mês: 500k-1M
├─ API calls/mês: 10M+
└─ Status: Platform consolidado
```

---

## 💡 Ideias Especulativas

Não priorizado, mas brainstorm:

- [ ] Integração Twitter: auto-posts sobre anomalias
- [ ] Integração Telegram bot: alerts
- [ ] WhatsApp alerts (via Twilio)
- [ ] Podcast: "Resumo político semanal" (TTS)
- [ ] Newsletter: insights semanais (email)
- [ ] Gamification: badges para usuários ativos
- [ ] Marketplace: plugins de terceiros
- [ ] GraphQL API (em vez de REST)
- [ ] Real-time WebSocket (proposições ao vivo)
- [ ] Integração com Waze: "Obras em vias"

---

## ⚠️ Riscos & Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|--------------|--------|-----------|
| Câmara API downtime | Média | Alto | Cache agressivo + fallback |
| DB fica muito grande | Alta | Médio | Limpeza automática (v2) |
| Gem ini rate limit atinge | Média | Médio | Fila priorizada, queue exponential |
| Segurança: SQL injection | Baixa | Alto | SQLAlchemy ORM + validação |
| Performance degrada | Média | Médio | Índices, cache, EXPLAIN |
| Scaling costs | Média | Médio | Otimizar, cache inteligente |

---

## 🎓 Aprendizados v1.0

### Wins

✨ **Arquitetura async desde o início**
- FastAPI + SQLAlchemy async economizou retrabalho
- Celery permitiu crescimento sem stress

✨ **IA integrada cedo**
- Gemini com structured output foi perfeito
- Score de anomalia muito útil

✨ **Deploy automatizado**
- Railway + Vercel foram plug-and-play
- Sem DevOps dedicado necessário

### Learnings

📚 **Rescanning é crítico**
- 30% dos dados chegam atrasados
- Sem rescanning, perda de informação
- Implementado cedo = economia de time

📚 **React Query > fetch tradicional**
- Cache automático economizou bandwidth
- UX muito melhor

📚 **DLQ é essencial**
- Sem DLQ, alguns dados seriam perdidos
- Com DLQ, 100% reliability

---

## ✅ Checklist antes de v2

- [x] v1.0 estável em produção
- [x] Rescanning funcionando
- [x] Dados sendo capturados corretamente
- [x] Zero downtime possible
- [ ] Monitoramento implementado
- [ ] Testes de carga feitos
- [ ] Backup strategy definida
- [ ] On-call procedure documentada

---

## 📞 Feedback Loop

Importante para v2 planning:

```bash
# Coletar dados de:
1. Google Analytics (pageviews, bounce rate)
2. API logs (endpoints populares, erros)
3. Sentry (bugs frequentes)
4. User feedback (GitHub issues, email)
5. Performance metrics (latency, errors)
```

---

## 🏁 Meta Final

Fazer de Lente Cidadã o **referência em transparência política brasileira**, com:
- ✅ 10k+ usuários mensais
- ✅ Dataset mais completo (gastos + votos + proposições)
- ✅ IA insights (não só flagging de anomalias)
- ✅ Community engajada (comentários, denúncias)
- ✅ APIs para terceiros (jornalistas, pesquisadores)

---

**Status**: ✅ Roadmap claro e priorizado  
**Próxima parada**: Fase 1 (Logging & Monitoring)  
**Quando**: Fevereiro 2026

