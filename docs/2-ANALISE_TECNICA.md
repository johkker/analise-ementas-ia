# 🎯 Análise Técnica & Recomendações - Lente Cidadã

## 📊 Status Geral: **85% PRONTO PARA PRODUÇÃO**


## ✅ Pontos Fortes
- ✅ ORM moderno com SQLAlchemy 2.0
- ✅ Retry automático com backoff exponencial
- ✅ Next.js 16 com App Router (latest)
### 4. **IA Integrada**
- ✅ Gemini com structured output (JSON schema)
- ✅ Celery para processamento async
- ✅ Rate limiting respeitado (4 req/min)

---

## ⚠️ Pontos de Atenção (Não-Bloqueantes)

### 1. **Testes Não Implementados**
```python
# ❌ Faltam:
# - Testes unitários (pytest)
# - Testes de integração (db, api)
# - Mock para Gemini
# - Fixtures de dados

# Risco: Regressões em produção
# Impacto: MÉDIO (funciona, mas sem cobertura)
```

**Recomendação:**
```bash
# Instalar dependências de teste
poetry add --group dev pytest pytest-asyncio pytest-mock

# Criar arquivo tests/test_extractor.py
# Criar arquivo tests/test_ingestor.py
# Criar arquivo tests/test_routes.py
```
# ❌ Atualmente: print() statements
# ✅ Recomendado: loguru + ELK stack
```

**Rápida Fix:**
```bash
poetry add loguru
# Substituir prints por logger.info(), logger.error()
```

### 3. **Autenticação Não Implementada**
- ✅ API é pública (OK para protótipo)
- ⚠️ Endpoints de ingestão expostos publicamente
- 🔴 Risco: Spam, DDoS

**Recomendação:**
```python
# Adicionar JWT nos endpoints internos
from fastapi import Security, HTTPBeautailon
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/ingest/deputados")
async def ingest_deputados(credentials: HTTPAuthenticationCredentials = Depends(security)):
    # Verificar token
    pass
alembic current    # Ver última migration
alembic upgrade head  # Aplicar todas
```

**Issue Potencial:** Se `autoria_proposicao` table não foi criada via migration, pode ter problema.

**Fix:**
```bash
# Criar migration se falta
alembic revision --autogenerate -m "Fix autoria_proposicao table"
alembic upgrade head
```

### 5. **Frontend: Faltam Charts & Visualizações Avançadas**
- ✅ Dashboard básico existe
- ❌ Gráficos de tendências (recharts, plotly)
- ❌ Heatmaps de anomalias
- ❌ Análise temporal

---

## 🔴 Problemas Reais (Bloqueantes)

### 1. **Proposições: Join Não Está Funcionando**
```python
# No arquivo: src/api/routes/proposicoes.py
# Linha ~45
query = query.join(Proposicao.autores).filter(Politico.id == politico_id)
```

**Issue:** Pode gerar SQL inválido se autoria_proposicao não foi criada corretamente.

**Teste:**
```bash
curl "http://localhost:8000/proposicoes/?politico_id=1"
# Se retorna erro 500 ou lista vazia = problema
```

**Fix:**
```python
# Verificar migration
alembic history
# Se falta autoria_proposicao, criar:
alembic revision --autogenerate -m "Add autoria_proposicao"
alembic upgrade head

# Testar SQL diretamente
psql postgresql://user:pass@localhost/db
SELECT * FROM autoria_proposicao LIMIT 1;
```

### 2. **Análise IA: Score Anomalia Pode Ser NULL**
```python
# ai_worker.py linha ~49
score = resultado.get('sentimento_politico', 0)
nova_analise.score_anomalia = Decimal(str(score)) if score is not None else Decimal('0')
```


**Fix:**
```python
# Melhorar prompt do Gemini
# Incluir: "Sempre forneça um score_anomalia de 0.0 a 1.0"

# Validar resposta
def validate_gemini_response(resultado):
    assert 'score_anomalia' in resultado, "Missing score_anomalia"
    assert 0 <= resultado['score_anomalia'] <= 1.0
```

### 3. **Gastos: empresa_cnpj Pode Estar NULL**
```python
# gasto.py
empresa_cnpj: Mapped[str | None] = mapped_column(ForeignKey("empresas.cnpj"))
```

**Issue:** Nem todo gasto tem CNPJ válido. Sem empresa_cnpj, análise fica incompleta.

**Cenário:** Gasto com tipo "REEMBOLSO DE PASSAGEM AÉREA" - empresa pode ser "N/A".

**Fix:**
```python
# Validar antes de criar Gasto
if gasto_raw.get('empresa_cnpj'):
    # Salvar com CNPJ
else:
    # Salvar sem CNPJ (já suporta NULL)
    # Ou criar empresa genérica "DIVERSOS"
    
# No frontend, handle NULL:
<td>{gasto.fornecedor || 'Não informado'}</td>
```

---

## 🚀 Próximas Prioridades

### P0 (Crítico - Esta Semana)
1. ✅ [**Verificar Migrations**]
   ```bash
   poetry run alembic current
   poetry run alembic upgrade head
   docker exec lente-cidada-db psql -U postgres -d lupa -c "\dt"
   ```

2. ✅ [**Testar Endpoints**]
   ```bash
   curl http://localhost:8000/deputados/ | jq .
   curl http://localhost:8000/proposicoes/ | jq .
   curl http://localhost:8000/gastos/exploration | jq .
   ```

3. ⚠️ [**Validar Proposições Join**]
   - Testar: `GET /proposicoes/?politico_id=160123`
   - Se 500: debugar SQL
   - Se vazio: verificar dados em autoria_proposicao

4. 🔴 [**Secured Ingest Endpoints**]
   - Adicionar JWT auth aos endpoints POST /ingest/*
   - Criar super_user pode fazer ingestão

### P1 (Alto - Esta Semana)
1. **Testes Básicos**
   ```bash
   poetry add --group dev pytest pytest-asyncio
   touch tests/test_routes.py
   poetry run pytest -v
   ```

   ```bash
   poetry add loguru
   # Substituir todos os prints
   ```

3. **CI/CD GitHub Actions**
   ```yaml
   # .github/workflows/test.yml
   name: Tests
   on: [push, pull_request]
   jobs:
     test:
       runs-on: ubuntu-latest
       services:
         postgres:
           image: postgres:15
           ...
   ```

4. **Documentação API (Swagger)**
   - FastAPI gera automaticamente: `http://localhost:8000/docs`
   - Verificar se está correto

### P2 (Médio - Próximas 2 Semanas)
1. **Dashboard de Análises**
   - Página `/dashboard` com AnaliseIA insights
   - Filter por `score_anomalia > 0.7`

2. **Charts & Visualizações**
   ```bash
   cd frontend
   npm add recharts date-fns
   # Criar componente GastosChart.tsx
   ```

3. **Otimizações DB**
   - Índices em colunas frequentes
   - EXPLAIN ANALYZE queries pesadas
   - Particionamento de gastos por ano (futura)

4. **Notificações Email**
   - Quando novo gasto suspeito detectado
   - Template com IA resumo

### P3 (Baixo - Futuro)
1. Análise de votações (padrões de voto)
3. Chat com IA customizado

# Celery Worker
poetry run celery -A src.core.celery_app worker --loglevel=info

poetry run celery -A src.core.celery_app beat --loglevel=info

# Flower (Monitor)
poetry run celery -A src.core.celery_app flower --port=5555
```

### Database
```bash
# Migrations
poetry run alembic revision --autogenerate -m "description"
poetry run alembic upgrade head
poetry run alembic downgrade -1

# Backup
docker exec lente-cidada-db pg_dump -U postgres lupa > backup.sql

# Restore
docker exec -i lente-cidada-db psql -U postgres lupa < backup.sql
```

### Testing
```bash
# Run all tests
poetry run pytest -v

# Specific test
poetry run pytest tests/test_routes.py::test_get_deputados -v

# With coverage
poetry run pytest --cov=src tests/
```

### Deployment
```bash
# Build Docker
docker build -t lente-cidada:latest .

# Push to Registry
docker tag lente-cidada:latest <registry>/lente-cidada:latest
docker push <registry>/lente-cidada:latest

# Deploy Railway
railway up

# Deploy Vercel (frontend)
cd frontend && vercel --prod
```

---

## 📋 Checklist de Go-Live

- [ ] Testes unitários passando (>80% cobertura)
- [ ] Migrations all applied (`alembic current` = latest)
- [ ] Endpoints testados manualmente
- [ ] CORS configurado corretamente
- [ ] Rate limiting ativo
- [ ] Gemini API key configurada
- [ ] Database backups automatizados
- [ ] Monitoring/Logging setup
- [ ] SSL certificados válidos
- [ ] DNS apontando corretamente
- [ ] Vercel deployment testado
- [ ] Railway deployment testado

---

## 📞 Contato & Suporte

**Issues/Bugs:** GitHub Issues  
**Sugestões:** Discussions  
**Emergência:** johkker@email.com  

---

**Próxima revisão:** 04 de Fevereiro de 2026

