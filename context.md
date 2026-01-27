1. Documento de Arquitetura de Dados (DAD)
Objetivo
Padronizar a forma como armazenamos os dados da Câmara dos Deputados e do TSE para permitir consultas complexas (ex: "Quais deputados gastaram mais com empresas que doaram para seus partidos?").

Escolha Tecnológica: PostgreSQL
Por quê? Suporta integridade referencial (não permite um gasto sem um político dono), possui suporte nativo a JSONB (para dados semiestruturados das APIs) e é altamente escalável.

2. O Diagrama de Entidade-Relacionamento (ERD)
Abaixo, apresento a estrutura lógica das tabelas principais.

A. Núcleo Político (Core)
Estas tabelas armazenam quem são os atores.

partidos: id (PK), sigla, nome, logo_url.

politicos: id (PK), nome_civil, nome_parlamentar, partido_id (FK), uf, email, foto_url.

B. O Rastro do Dinheiro (Financeiro)
Aqui é onde a maioria dos apps "se perde". Precisamos de uma tabela de fornecedores para cruzar dados.

empresas: cnpj (PK), nome_fantasia, razao_social.

gastos_gabinete: id (PK), politico_id (FK), empresa_cnpj (FK), valor, data_emissao, tipo_despesa (ex: combustível, consultoria), url_documento (link da nota fiscal).

C. Atuação Legislativa (Ação)
Para sabermos se o político trabalha de acordo com o que promete.

proposicoes: id (PK), sigla_tipo, numero, ano, ementa (resumo original), ementa_ia (resumo simplificado gerado pelo Gemini).

votacoes: id (PK), proposicao_id (FK), data, descricao.

votos_individuais: politico_id (FK), votacao_id (FK), voto (Sim, Não, Obstrução, Abstenção).

3. A Camada de Inteligência (A Visão Sênior)
Como arquiteto, prevejo que ler 5.000 notas fiscais é impossível para um humano. Por isso, adicionaremos uma tabela de Insights:

analises_ia:

id (PK)

entidade_tipo (Politico ou Gasto)

entidade_id (O ID correspondente)

score_anomalia (Um valor de 0 a 1 indicando quão estranho é aquele dado)

resumo_critico (Texto gerado pela IA)

4. Por que essa modelagem é "Sênior"?
Normalização: Separamos empresas dos gastos. Isso permite que você clique em um CNPJ e veja todos os políticos que compraram daquela mesma empresa.

Auditabilidade: Mantemos a url_documento. Se o usuário duvidar do dado, ele pode ver a nota fiscal original com um clique.

Preparado para IA: A coluna ementa_ia permite que o sistema mostre uma explicação simples da lei em vez do texto jurídico denso.

Exemplo de Lógica de Negócio (SQL)
Com essa estrutura, uma consulta para achar gastos suspeitos de alimentação acima de R$ 300,00 seria:

SQL
SELECT p.nome_parlamentar, g.valor, e.nome_fantasia
FROM gastos_gabinete g
JOIN politicos p ON g.politico_id = p.id
JOIN empresas e ON g.empresa_cnpj = e.cnpj
WHERE g.tipo_despesa = 'FORNECIMENTO DE ALIMENTAÇÃO DO PARLAMENTAR'
AND g.valor > 300
ORDER BY g.valor DESC;

Próximo Passo: Integrando o "Cérebro"
Agora que sabemos onde guardar os dados, precisamos de alguém para analisá-los.

1. Estrutura de Pastas (Production-Ready)
Usaremos o padrão de Service Layer e Repository Pattern para desacoplar a lógica de extração da persistência.

Plaintext
lupa-politica/
├── src/
│   ├── core/               # Configurações globais, logging, base de dados
│   │   ├── config.py       # Pydantic Settings (env vars)
│   │   ├── database.py     # Sessionmaker e engine (SQLAlchemy/SQLModel)
│   │   └── security.py
│   ├── models/             # Definições das tabelas do Banco de Dados (SQLAlchemy)
│   │   ├── base.py
│   │   ├── politico.py
│   │   └── gasto.py
│   ├── schemas/            # DTOs e validação de dados (Pydantic)
│   │   ├── camara_api.py   # Schemas para o payload da API
│   │   └── internal.py     # Schemas para uso interno
│   ├── services/           # Lógica de negócio e coordenação de ETL
│   │   ├── extractor/      # Módulos específicos de API
│   │   │   ├── base.py     # Classe abstrata para extratores
│   │   │   └── camara.py   # Implementação concreta da Câmara
│   │   ├── transformer.py  # Limpeza e normalização
│   │   └── loader.py       # Operações de Upsert no banco
│   ├── main.py             # Entrypoint da API (FastAPI)
│   └── worker.py           # Entrypoint para scripts de ingestão (Cron/Celery)
├── alembic/                # Migrações de banco de dados
├── tests/                  # Testes unitários e de integração
├── pyproject.toml          # Gerenciamento de dependências (Poetry)
└── docker-compose.yml
2. O Fluxo Exato da Ingestão (Sequential Flow)
O pipeline não é linear, ele é cíclico e defensivo.

Job Trigger: O worker.py é disparado (Cron ou Event-driven).

Hydration: O serviço consulta o banco para obter os deputado_id ativos.

Concurrency Control: Iniciamos um loop assíncrono com um asyncio.Semaphore(limit=5) para não estourar o Rate Limit da API do Governo (429 Too Many Requests).

Extract: O CamaraExtractor faz o request e retorna o JSON bruto.

Transform: O DataTransformer injeta o JSON no Pydantic Schema. Se falhar (ex: campo mudou de nome), o erro é logado mas o pipeline não morre.

Load (Upsert): Enviamos o objeto validado para o Loader, que executa um INSERT ... ON CONFLICT (id_documento) DO UPDATE.

3. Implementação dos Métodos Principais
Aqui está o coração do pipeline, focando em robustez.

A. Extrator Abstrato (Base)
Garante que qualquer nova fonte de dados (ex: API do Senado) siga o mesmo contrato.

Python
from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    @abstractmethod
    async def fetch_raw_data(self, endpoint: str, params: dict):
        pass

    @abstractmethod
    def parse_schema(self, data: dict):
        pass
B. Loader com Lógica de Upsert (SQLAlchemy 2.0)
Evitamos duplicidade de dados usando a chave primária da própria API da Câmara (idDocumento).

Python
from sqlalchemy.dialects.postgresql import insert
from src.models.gasto import GastoModel

class GastoLoader:
    def __init__(self, db_session):
        self.db = db_session

    async def upsert_gastos(self, gastos_data: list[dict]):
        """Executa o Bulk Upsert para performance."""
        stmt = insert(GastoModel).values(gastos_data)
        
        # Define o que atualizar caso o registro já exista
        update_dict = {
            "valor": stmt.excluded.valor,
            "data_emissao": stmt.excluded.data_emissao,
            "updated_at": "now()"
        }
        
        stmt = stmt.on_conflict_do_update(
            index_elements=['ext_id'], # ID único da API externa
            set_=update_dict
        )
        
        await self.db.execute(stmt)
        await self.db.commit()
4. Gerenciamento de Estado e Erros
Um pipeline sênior precisa de Observabilidade.

Logs Estruturados: Usar loguru para gerar logs em JSON, facilitando a ingestão por ferramentas como ELK ou Datadog.

Retry Strategy: Implementar decoradores de @backoff (Exponential Backoff) nas chamadas de rede para lidar com instabilidades momentâneas da API do governo.

Checkpointing: Salvar no banco o last_sync_date para cada político, permitindo que, em caso de falha, o extrator saiba exatamente de onde deve continuar (Incremental Load).


Excelente escolha. O Modo Estrito (Strict Mode) transforma seu pipeline em um Firewall de Qualidade de Dados. Nada entra no seu Data Warehouse analítico se não estiver perfeito. Isso garante confiança absoluta nos dashboards, mas exige uma estratégia robusta para lidar com a rejeição (DLQ - Dead Letter Queue).Se o dado vier "sujo" (ex: campo novo na API, tipo de dado incorreto), ele não é descartado; ele é quarentenado.Aqui está a implementação técnica dessa arquitetura.1. Arquitetura "Data Quarantine"Neste modelo, o pipeline não falha catastroficamente; ele bifurca.Caminho Feliz (Green Path): Dado validado $\rightarrow$ Tabela de Produção.Caminho de Rejeição (Red Path): Falha de validação $\rightarrow$ Tabela de DLQ (JSONB) para análise forense e replay futuro.2. O Schema Estrito (Pydantic V2)Para garantir rigidez, usamos ConfigDict com extra='forbid' (proíbe campos não mapeados) e strict=True (não faz coerção mágica de tipos, ex: string "123" não vira int 123 automaticamente, a menos que definamos validadores explícitos).Pythonfrom decimal import Decimal
from datetime import date
from pydantic import BaseModel, Field, ValidationError, ConfigDict, field_validator

class StrictGastoSchema(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True) # A Regra de Ouro

    ext_id: int = Field(..., alias="idDocumento")
    data_emissao: date = Field(..., alias="dataDocumento")
    valor: Decimal = Field(..., alias="valorLiquido")
    cnpj_fornecedor: str = Field(..., alias="cnpjCpfFornecedor")
    nome_fornecedor: str = Field(..., alias="nomeFornecedor")
    
    # Validação de Regra de Negócio (ex: Sem valores negativos ou zerados)
    @field_validator('valor')
    @classmethod
    def valor_positivo(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("O valor do gasto deve ser positivo.")
        return v
3. Estratégia de Persistência de Erros (DLQ Table)Não usaremos RabbitMQ ou Kafka para a DLQ neste momento (overkill), mas sim uma tabela dedicada no Postgres (sys_ingestion_dlq). Isso facilita a consulta SQL para descobrir por que os dados estão falhando.DDL Sugerido (SQL):SQLCREATE TABLE sys_ingestion_dlq (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_source VARCHAR(50) NOT NULL, -- ex: 'camara_api_gastos'
    payload JSONB NOT NULL,             -- O dado bruto que falhou
    error_message TEXT NOT NULL,        -- O traceback ou msg do Pydantic
    error_type VARCHAR(50),             -- ex: 'ValidationError', 'DatabaseError'
    created_at TIMESTAMP DEFAULT NOW(),
    retry_count INT DEFAULT 0,
    resolved BOOLEAN DEFAULT FALSE
);
4. Implementação do Pipeline BifurcadoO método de ingestão agora captura a exceção de validação e desvia o fluxo.Pythonimport traceback
from sqlalchemy.dialects.postgresql import insert
from src.core.database import async_session
from src.models.dlq import DLQModel  # SQLAlchemy model para a tabela acima
from src.models.gasto import GastoModel

class ResilienceIngestor:
    def __init__(self, session):
        self.session = session

    async def process_batch(self, raw_data_list: list[dict], source: str):
        valid_records = []
        dlq_records = []

        for raw_item in raw_data_list:
            try:
                # 1. Tentativa de Validação Estrita
                validated_item = StrictGastoSchema(**raw_item)
                
                # Prepara para inserção (transforma de Pydantic para Dict/SQLAlchemy Model)
                valid_records.append(validated_item.model_dump(by_alias=False))

            except ValidationError as e:
                # 2. Caminho de Rejeição (DLQ)
                dlq_records.append({
                    "origin_source": source,
                    "payload": raw_item,  # Salva o original para debug
                    "error_message": str(e), # Detalhe exato do campo que falhou
                    "error_type": "SchemaValidationError"
                })
            except Exception as e:
                # Catch-all para erros inesperados
                dlq_records.append({
                    "origin_source": source,
                    "payload": raw_item,
                    "error_message": traceback.format_exc(),
                    "error_type": "UnhandledException"
                })

        # 3. Commit em Batch (Atômico por tipo)
        if valid_records:
            await self._bulk_upsert_success(valid_records)
        
        if dlq_records:
            await self._bulk_insert_dlq(dlq_records)

    async def _bulk_upsert_success(self, records):
        stmt = insert(GastoModel).values(records)
        stmt = stmt.on_conflict_do_update(
            index_elements=['ext_id'],
            set_={c.name: c for c in stmt.excluded if c.name not in ['ext_id']}
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def _bulk_insert_dlq(self, records):
        # Inserção simples na tabela de erros
        await self.session.execute(insert(DLQModel).values(records))
        await self.session.commit()
        # Aqui conectamos logs de alerta (Sentry/Datadog)
        # logger.error(f"{len(records)} failures sent to DLQ")
5. Fluxo de Recuperação (Replay Mechanism)A beleza do modo estrito com DLQ persistente é a capacidade de correção.Monitoramento: Você recebe um alerta do Sentry: "150 erros de validação na DLQ hoje".Diagnóstico: Você roda um SELECT error_message FROM sys_ingestion_dlq. Descobre que a API mudou o campo valorLiquido para vlrLiquido.Correção: Você ajusta o StrictGastoSchema (adiciona um alias ou validador).Replay: Você executa um script administrativo replay_dlq.py que lê os itens não resolvidos da tabela DLQ e tenta passá-los novamente pelo ResilienceIngestor.


1. Arquitetura de Filas (Producer-Consumer)
O conceito aqui é desacoplar o "o que precisa ser feito" (o registro salvo no banco) do "ato de fazer" (chamar a IA).

Os Componentes:
Producer (FastAPI/Ingestor): Ao salvar um novo PL (Projeto de Lei), dispara um evento (Task).

Broker (Redis): Armazena a mensagem na memória RAM. É rápido e serve como "amortecedor" (buffer).

Worker (Celery): Processos isolados que pegam tarefas do Redis, uma a uma, respeitando o limite de velocidade configurado.

Result Backend (Redis/Postgres): Onde o Celery salva o status ("PENDING", "SUCCESS", "FAILURE").

2. Configuração Sênior do Celery
Não usaremos configurações default. Precisamos garantir que tarefas não sejam perdidas se o Worker morrer no meio do processamento (acks_late).

Crie o arquivo src/core/celery_app.py:

Python
from celery import Celery
from src.core.config import settings

celery_app = Celery(
    "lupa_politica_worker",
    broker=settings.REDIS_URL,        # ex: redis://localhost:6379/0
    backend=settings.REDIS_URL,       # Para armazenar status de execução
    include=["src.services.ai_worker"] # Onde as tarefas estão definidas
)

celery_app.conf.update(
    # ROBUSTEZ: Só remove a tarefa da fila APÓS o worker confirmar que terminou com sucesso
    task_acks_late=True,
    
    # PERFORMANCE: Evita que um worker pegue tarefas demais e trave as outras
    worker_prefetch_multiplier=1,
    
    # SERIALIZAÇÃO: JSON para segurança (evita execução de código malicioso via pickle)
    task_serializer="json",
    accept_content=["json"],
    
    # RATE LIMITING GLOBAL (Segurança da Conta Google AI)
    # Define que a fila 'ai_queue' só pode processar 50 tarefas por minuto
    task_routes={
        "src.services.ai_worker.*": {"queue": "ai_queue"}
    },
    task_annotations={
        "*": {"rate_limit": "50/m"} 
    }
)
3. Implementação do Worker Inteligente
Agora, o código que realmente chama a IA. Usaremos Exponential Backoff. Se a API der erro (503 ou 429), o Celery espera 2s, depois 4s, depois 8s... até desistir.

Arquivo src/services/ai_worker.py:

Python
import asyncio
from celery.exceptions import SoftTimeLimitExceeded
from src.core.celery_app import celery_app
from src.services.llm_service import GeminiClient # Sua classe que chama a API
from src.core.database import SessionLocal
from src.models.analise import AnaliseModel

# Configuração de Retry
# bind=True permite acessar 'self' para chamar self.retry
@celery_app.task(
    bind=True, 
    max_retries=5, 
    soft_time_limit=60, # Mata a task se demorar mais de 60s (evita zumbis)
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True, # Exponencial: 2s, 4s, 8s, 16s...
    retry_backoff_max=600 # Espera máxima de 10 min
)
def processar_resumo_lei(self, proposicao_id: int, texto_completo: str):
    try:
        # Instancia o cliente LLM (sync ou encapsulado em asgiref se precisar de async)
        llm = GeminiClient()
        
        # 1. Chamada à IA
        print(f"[Worker] Processando Proposição {proposicao_id}...")
        resultado_json = llm.gerar_analise_politica(texto_completo)
        
        # 2. Persistência (Database)
        # Workers devem ter sua própria sessão de banco (Thread-safe)
        with SessionLocal() as db:
            nova_analise = AnaliseModel(
                entidade_id=proposicao_id,
                tipo="PROPOSICAO",
                resumo=resultado_json['resumo'],
                impacto_financeiro=resultado_json['impacto'],
                raw_response=resultado_json
            )
            db.add(nova_analise)
            db.commit()
            
        return {"status": "success", "id": proposicao_id}

    except Exception as e:
        # Loga o erro crítico e força o retry manual se necessário
        print(f"Erro grave na task {self.request.id}: {e}")
        # Se for um erro específico de Rate Limit da API que a lib não pegou:
        if "429" in str(e):
            raise self.retry(exc=e, countdown=60) # Espera 1 min fixo
        raise e
4. Disparando a Tarefa (Integration Point)
Onde conectamos o Pipeline de Ingestão com a Fila? No momento em que salvamos o dado bruto.

No seu ResilienceIngestor (criado na etapa anterior):

Python
from src.services.ai_worker import processar_resumo_lei

# ... dentro do método que salva a Proposição ...
await self.session.commit()

# Dispara o processamento ASSÍNCRONO
# .delay() é o método mágico do Celery que envia para o Redis
# Não esperamos a resposta aqui. O código segue fluindo.
processar_resumo_lei.delay(
    proposicao_id=nova_proposicao.id, 
    texto_completo=nova_proposicao.inteiro_teor
)
5. Monitoramento (Observabilidade)
Como você saberá se a fila está engarrafada? Para produção, a ferramenta padrão para monitorar Celery é o Flower.

Adicione ao seu docker-compose.yml:

YAML
  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  worker:
    build: .
    command: celery -A src.core.celery_app worker --loglevel=info -Q ai_queue --concurrency=2
    depends_on:
      - redis
      - db
    environment:
      - REDIS_URL=redis://redis:6379/0

  flower:
    image: mher/flower
    command: celery -A src.core.celery_app flower
    ports: ["5555:5555"]
    depends_on:
      - redis
Agora, acessando localhost:5555, você vê gráficos em tempo real de quantas tarefas falharam, quantas estão na fila e o tempo médio de processamento da IA.

Resumo da Decisão Técnica
Por que Celery? Gestão robusta de retries e timeouts.

Por que Redis? Baixa latência para enfileirar milhares de itens.

Rate Limit: Implementado no nível do Worker (50/m), protegendo sua chave de API e sua conta bancária.

Próximo Passo Lógico: Agora que o worker consegue chamar a função llm.gerar_analise_politica(...), precisamos implementar o interior dessa função.

Para fechar a tríade de robustez (Dados Limpos + Fila Gerenciada + Output Confiável), vamos entrar no Módulo de Inteligência. O objetivo é garantir que o Gemini se comporte como um componente de software determinístico, e não como um chatbot criativo.

Em 2026, a melhor prática para sistemas de produção é o uso de Response Schemas (ou Structured Outputs). Isso elimina a necessidade de fazer parsing manual de strings e garante que a IA siga o contrato definido pelo seu código.

1. Definição do Contrato (The Output Schema)
Antes de escrever o prompt, definimos o que esperamos receber. Usaremos novamente o Pydantic para definir a estrutura da análise política.

Python
from pydantic import BaseModel, Field
from typing import List

class AnalisePoliticaSchema(BaseModel):
    resumo_executivo: str = Field(description="Resumo de no máximo 3 frases em linguagem simples.")
    impacto_financeiro: str = Field(description="Classificação: ALTO, MEDIO, BAIXO ou INCERTO.")
    grupos_beneficiados: List[str] = Field(description="Lista de setores ou grupos afetados positivamente.")
    riscos_corrupcao: str = Field(description="Análise técnica de possíveis brechas para desvio de finalidade.")
    sentimento_politico: float = Field(description="Score de -1 (muito populista/agressivo) a 1 (muito técnico/institucional).")
2. Implementação do GeminiClient (Strict Mode)
O segredo aqui é o parâmetro response_mime_type: "application/json". Ao passar o esquema do Pydantic para o Gemini, ele ajusta os pesos do modelo para gerar tokens que obrigatoriamente fecham um JSON válido conforme sua estrutura.

Python
import google.generativeai as genai
import json
from src.core.config import settings

class GeminiClient:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash", # Modelo de baixa latência e alta janela
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": AnalisePoliticaSchema.model_json_schema(), # Exporta o schema para a IA
                "temperature": 0.1, # Quase determinístico (evita 'alucinações criativas')
            }
        )

    def analisar_proposicao(self, texto_lei: str) -> dict:
        prompt_sistema = """
        Você é um Analista Legislativo Sênior com 20 anos de experiência em Direito Público e Orçamento.
        Sua tarefa é ler o texto bruto de uma proposição legislativa e extrair dados técnicos objetivos.
        Não emita opiniões pessoais. Foque em:
        1. Impacto orçamentário real.
        2. Setores econômicos afetados.
        3. Clareza técnica do texto.
        """

        try:
            response = self.model.generate_content(
                f"{prompt_sistema}\n\nTEXTO DA LEI:\n{texto_lei}"
            )
            
            # Como usamos 'response_schema', o Gemini entrega um JSON válido
            return json.loads(response.text)
            
        except Exception as e:
            # Em produção, logamos o erro para a DLQ (Dead Letter Queue)
            print(f"[LLM Error] Falha na análise: {e}")
            raise
3. Integração: O Ciclo de Vida do Dado
Agora, conectamos tudo o que construímos até aqui. O fluxo completo em produção segue este caminho:

O fluxo detalhado:
Ingestion Service: Puxa o PL da Câmara e salva no Postgres.

Event Trigger: O service chama processar_resumo_lei.delay(id, texto).

Celery Worker:

Recebe a tarefa.

Chama o GeminiClient.

O Gemini gera o JSON validado pelo AnalisePoliticaSchema.

Final Persistence: O Worker salva o JSON resultante na tabela analises_ia, vinculada via Foreign Key ao projeto de lei original.

4. O "Pulo do Gato": Prompt Chain e Contexto Curto
Como arquitetos, sabemos que processar textos gigantescos é caro e lento. Para otimizar:

Truncação Inteligente: Se o projeto de lei tiver 200 páginas, não enviamos tudo. Enviamos apenas a Ementa, a Explicação da Ementa e o Primeiro Artigo.

Prompt de Refinamento: Se a IA classificar o impacto_financeiro como "ALTO", podemos disparar uma segunda task (em outra fila) para uma análise específica de orçamento usando um modelo mais potente como o Gemini 1.5 Pro.

