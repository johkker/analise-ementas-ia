# 📚 Documentação Lente Cidadã

**Status**: ✅ Consolidado em 3 arquivos principais | **Última atualização**: 28 Jan 2026

---

## 🗂️ Estrutura de Docs

```
/docs/
├── INDEX.md (este arquivo)
├── README.md ⭐ START HERE
├── TECHNICAL_SPEC.md (detalhes técnicos)
└── ROADMAP.md (v2+)
```

---

## 📖 Qual Arquivo Ler?

### 1️⃣ Para Começar: [README.md](README.md)

**Leia isso se você**: quer entender o projeto rapidamente

**Contém**:
- ✅ O que é Lente Cidadã
- ✅ Quick start (URLs, como rodar localmente)
- ✅ Status v1.0 (% completo de cada componente)
- ✅ Arquitetura em 30 segundos
- ✅ Dados em produção
- ✅ Rescanning automático (overview)
- ✅ 8 endpoints principais
- ✅ Segurança implementada
- ✅ Performance esperada
- ✅ Manutenção (diária/semanal/mensal)
- ✅ Problemas comuns

**Tempo**: 10 min  
**Para quem**: Product managers, stakeholders, usuários

---

### 2️⃣ Para Técnico: [TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)

**Leia isso se você**: precisa implementar, debugar, ou manter o código

**Contém**:
- ✅ Arquitetura completa (diagrama de fluxo)
- ✅ **Modelo de dados** (8 tabelas + schema SQL)
- ✅ **Relationships diagram** (como tudo conecta)
- ✅ 8 endpoints API (request/response completos)
- ✅ **Rescanning automático (detalhado)**
  - Por que é necessário
  - Implementação passo-a-passo
  - Schedule (Celery Beat)
  - Garantias
- ✅ **Como ativar Celery Beat**
  - Opção 1: Railway (recomendado)
  - Opção 2: Docker Compose
  - Opção 3: Manual
  - Validação
- ✅ Troubleshooting extenso
- ✅ Monitoramento (queries SQL)

**Tempo**: 30 min  
**Para quem**: Developers, DevOps, QA

---

### 3️⃣ Para Planejamento: [ROADMAP.md](ROADMAP.md)

**Leia isso se você**: quer saber o que vem depois

**Contém**:
- ✅ Visão geral v2 (quem está fazendo o quê)
- ✅ Timeline proposto (4 fases, 9 semanas)
- ✅ **Fase 1**: Logging & Monitoring (1w)
- ✅ **Fase 2**: Análise votações + TSE (3w)
- ✅ **Fase 3**: UI improvements (2w)
- ✅ **Fase 4**: IA avançada (3w)
- ✅ Quick wins (1-2 dias cada)
- ✅ Features futuras (community, analytics, mobile)
- ✅ Priorização (matrix)
- ✅ Infraestrutura melhorias
- ✅ Crescimento esperado (curva de usuários)
- ✅ Ideias especulativas
- ✅ Riscos & mitigações
- ✅ Aprendizados v1.0

**Tempo**: 15 min  
**Para quem**: Product managers, founders, stakeholders

---

## 🎯 Fluxo de Leitura por Perfil

### 👤 Product Manager / Founder

```
1. README.md (10 min)
   ↓
2. ROADMAP.md (15 min)
   ↓
3. TECHNICAL_SPEC.md (métricas e escalabilidade, 5 min)
```

**Tempo total**: 30 min

---

### 👨‍💻 Developer / Backend

```
1. README.md (10 min)
   ↓
2. TECHNICAL_SPEC.md (COMPLETO - 30 min)
   ├─ Modelo dados
   ├─ Endpoints
   ├─ Rescanning detalhado
   ├─ Como ativar Celery Beat
   └─ Troubleshooting
   ↓
3. ROADMAP.md (implementação próximas features, 10 min)
```

**Tempo total**: 50 min

---

### 🎨 Frontend Developer

```
1. README.md (10 min)
   ↓
2. TECHNICAL_SPEC.md (endpoints API, 10 min)
   ↓
3. ROADMAP.md (Fase 3: UI improvements, 5 min)
```

**Tempo total**: 25 min

---

### 🚀 DevOps / Infrastructure

```
1. README.md (10 min)
   ↓
2. TECHNICAL_SPEC.md (COMPLETO - 30 min)
   ├─ Como ativar Celery Beat
   ├─ Troubleshooting
   └─ Monitoramento
   ↓
3. ROADMAP.md (infraestrutura melhorias, 10 min)
```

**Tempo total**: 50 min

---

### ✅ QA / Tester

```
1. README.md (10 min)
   ↓
2. TECHNICAL_SPEC.md (endpoints, troubleshooting, 15 min)
   ↓
3. ROADMAP.md (phase testing, 5 min)
```

**Tempo total**: 30 min

---

## 🔍 Busca Rápida

Procurando algo específico? Use `Ctrl+F`:

| O que? | Arquivo | Seção |
|--------|---------|-------|
| Como rodar local | README.md | Quick Start |
| Endpoints API | TECHNICAL_SPEC.md | Endpoints API |
| Modelo dados | TECHNICAL_SPEC.md | Modelo de Dados |
| Rescanning | TECHNICAL_SPEC.md | Rescanning Automático |
| Ativar Celery Beat | TECHNICAL_SPEC.md | Como Ativar Celery Beat |
| Troubleshooting | TECHNICAL_SPEC.md | Troubleshooting |
| v2 features | ROADMAP.md | 4 Fases |
| Quick wins | ROADMAP.md | Quick Wins |
| Crescimento esperado | ROADMAP.md | Crescimento Esperado |
| Problemas comuns | README.md | Problemas Comuns |

---

## 🚨 CRITICAMENTE IMPORTANTE

⚠️ **Antes de deployed em produção, LEIE**:

1. [README.md - Rescanning](README.md#-ingestão-automática-rescanning-90-dias)
2. [TECHNICAL_SPEC.md - Como Ativar Celery Beat](TECHNICAL_SPEC.md#como-ativar-celery-beat)
3. [TECHNICAL_SPEC.md - Troubleshooting](TECHNICAL_SPEC.md#-troubleshooting)

**Sem Celery Beat em produção**: Gastos atrasados serão perdidos ❌

---

## 📊 Versões de Documentação

| Versão | Data | Status | Mudanças |
|--------|------|--------|----------|
| 1.0 | 28 Jan 2026 | ✅ ATUAL | Consolidado em 3 files |
| 0.9 | 28 Jan 2026 | 🗑️ Obsoleto | +10 docs redundantes |
| 0.1 | 27 Jan 2026 | 🗑️ Obsoleto | Docs iniciais |

---

## 📝 Notas Finais

- ✅ Documentação consolidada (3 files em vez de 13)
- ✅ Sem redundância entre arquivos
- ✅ Fácil navegar (este INDEX.md)
- ✅ Organizado por seção (use Ctrl+F)
- ✅ Pronto para manutenção long-term

**Se algo não está claro**: Abra uma issue no GitHub

---

**Última atualização**: 28 de Janeiro de 2026  
**Status**: ✅ Completo e consolidado

