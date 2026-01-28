from google import genai
from src.core.config import settings
from pydantic import BaseModel, Field
from typing import List
import asyncio
import random

class AnalisePoliticaSchema(BaseModel):
    resumo_executivo: str = Field(description="Resumo de no máximo 3 frases em linguagem simples.")
    impacto_financeiro: str = Field(description="Classificação: ALTO, MEDIO, BAIXO ou INCERTO.")
    grupos_beneficiados: List[str] = Field(description="Lista de setores ou grupos afetados positivamente.")
    riscos_corrupcao: str = Field(description="Análise técnica de possíveis brechas para desvio de finalidade.")
    sentimento_politico: float = Field(description="Score de -1 (muito populista/agressivo) a 1 (muito técnico/institucional).")
    score_anomalia: float | None = Field(default=None, description="Probabilidade de anomalia entre 0.0 e 1.0")
    evidencias: List[str] = Field(default_factory=list, description="Pequena lista de evidências observadas no registro")
    recomendacoes: List[str] = Field(default_factory=list, description="Recomendações práticas e acionáveis para investigação ou mitigação")

class GeminiClient:
    def __init__(self):
        # allow either Gemini Developer API, Vertex AI, or a custom base URL
        if not settings.GEMINI_API_KEY and not settings.GOOGLE_GENAI_USE_VERTEXAI:
            raise ValueError("GEMINI_API_KEY not set (or enable Vertex mode via GOOGLE_GENAI_USE_VERTEXAI)")

        if settings.GOOGLE_GENAI_USE_VERTEXAI:
            # Vertex mode: the SDK will use the regional Vertex endpoint for the provided location
            self.client = genai.Client(
                vertexai=True,
                project=settings.GOOGLE_CLOUD_PROJECT,
                location=settings.GOOGLE_CLOUD_LOCATION,
            )
        elif settings.GEMINI_API_ENDPOINT:
            # Custom base_url (proxy / override)
            self.client = genai.Client(
                api_key=settings.GEMINI_API_KEY,
                http_options={"base_url": settings.GEMINI_API_ENDPOINT},
            )
        else:
            # Default Gemini Developer API using API key
            self.client = genai.Client(api_key=settings.GEMINI_API_KEY)

        self.model_name = "gemini-2.0-flash"
        # concurrency control for outbound LLM requests
        # keep default conservative (1) to avoid bursts; can be increased if desired
        self._semaphore = asyncio.Semaphore(1)

    def analisar_gasto(self, detalhes_gasto: str) -> dict:
        prompt_sistema = """
        Você é um Auditor Sênior focado em transparência pública.
        Sua tarefa é analisar registros públicos (gastos, votações e proposições) do Congresso.
        Leia com atenção os DETALHES DO REGISTRO e produza uma análise técnica.
        Responda estritamente em JSON seguindo o schema fornecido. Inclua os campos:
        - resumo_executivo: máximo 3 frases em linguagem simples
        - impacto_financeiro: ALTO | MEDIO | BAIXO | INCERTO
        - grupos_beneficiados: lista de setores ou grupos
        - riscos_corrupcao: avaliação técnica sobre riscos de desvio de finalidade
        - sentimento_politico: score entre -1.0 e 1.0
        - score_anomalia: probabilidade de anomalia entre 0.0 e 1.0
        - evidencias: lista curta (0..5) com itens que justifiquem suas conclusões
        - recomendacoes: lista curta (0..5) com ações recomendadas para investigação/mitigação
        Foco em objetividade, cite evidências, evite opiniões vagas e mantenha a linguagem concisa.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{prompt_sistema}\n\nDETALHES DO GASTO:\n{detalhes_gasto}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AnalisePoliticaSchema,
                    "temperature": 0.1,
                }
            )
            # The new SDK parses JSON automatically if response_schema is provided, 
            # but let's be safe and parse the text if needed or use response.parsed
            if hasattr(response, 'parsed'):
                 return response.parsed.model_dump()
            
            import json
            return json.loads(response.text)
            
        except Exception as e:
            print(f"[LLM Error] Falha na análise: {e}")
            raise

    def analisar_voto(self, detalhes_voto: str) -> dict:
        prompt_sistema = """
        Você é um Analista Legislativo especialista em comportamento de voto e integridade parlamentar.
        Sua tarefa é analisar um registro de voto, buscando padrões de coerência ideológica,
        sinais de coordenação indevida, troca de posições e possíveis riscos institucionais.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """
        return self._call_model(prompt_sistema, "DETALHES DO VOTO:", detalhes_voto)

    def analisar_proposicao(self, detalhes_proposicao: str) -> dict:
        prompt_sistema = """
        Você é um Analista Legislativo e Auditor de Política Pública.
        Sua tarefa é avaliar proposições (projetos, emendas, requerimentos) quanto a impacto,
        viabilidade política, favorecimento de grupos e riscos institucionais.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """
        return self._call_model(prompt_sistema, "DETALHES DA PROPOSIÇÃO:", detalhes_proposicao)

    def analisar_cross_data(self, detalhes_cross: str) -> dict:
        prompt_sistema = """
        Você é um Cientista de Dados e Auditor de Políticas Públicas.
        Sua tarefa é cruzar informações sobre um parlamentar (gastos, votos, proposições)
        e identificar padrões, conflitos de interesse e sinais de captura ou coordenação.
        Use as análises setoriais prévias quando relevante e construa um resumo consolidado.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """
        return self._call_model(prompt_sistema, "DETALHES CROSS-DATA:", detalhes_cross)

    def _call_model(self, prompt_sistema: str, header: str, detalhes: str) -> dict:
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=f"{prompt_sistema}\n\n{header}\n{detalhes}",
                config={
                    "response_mime_type": "application/json",
                    "response_schema": AnalisePoliticaSchema,
                    "temperature": 0.1,
                }
            )

            if hasattr(response, 'parsed'):
                return response.parsed.model_dump()

            import json
            return json.loads(response.text)

        except Exception as e:
            print(f"[LLM Error] Falha na análise: {e}")
            raise

    async def _call_model_async(self, prompt_sistema: str, header: str, detalhes: str, retries: int = 4) -> dict:
        """
        Async wrapper around the blocking `_call_model` with concurrency control
        and retry/backoff for transient errors (eg. 429 RESOURCE_EXHAUSTED).
        Adds a small delay after successful calls to avoid bursts.
        """
        backoff_base = 2.0

        for attempt in range(1, retries + 1):
            async with self._semaphore:
                try:
                    # run blocking client in a thread to avoid blocking the event loop
                    result = await asyncio.to_thread(self._call_model, prompt_sistema, header, detalhes)
                    # small fixed delay to space successful requests (throttle)
                    await asyncio.sleep(0.35)
                    return result

                except Exception as e:
                    # inspect message for rate limit / resource exhausted
                    msg = str(e)
                    if 'RESOURCE_EXHAUSTED' in msg or '429' in msg or 'rate limit' in msg.lower():
                        if attempt == retries:
                            raise
                        # exponential backoff with jitter
                        sleep_for = backoff_base * (2 ** (attempt - 1))
                        sleep_for = sleep_for + random.random() * 0.5
                        await asyncio.sleep(sleep_for)
                        continue
                    # non-retryable error -> raise immediately
                    raise

        # if we exit loop without returning, raise generic error
        raise RuntimeError('LLM call failed after retries')

    # Async convenience wrappers
    async def analisar_gasto_async(self, detalhes_gasto: str) -> dict:
        return await self._call_model_async("""
        Você é um Auditor Sênior focado em transparência pública.
        Sua tarefa é analisar registros públicos (gastos, votações e proposições) do Congresso.
        Leia com atenção os DETALHES DO REGISTRO e produza uma análise técnica.
        Responda estritamente em JSON seguindo o schema fornecido. Inclua evidências e recomendações.
        """, "DETALHES DO GASTO:", detalhes_gasto)

    async def analisar_voto_async(self, detalhes_voto: str) -> dict:
        return await self._call_model_async("""
        Você é um Analista Legislativo especialista em comportamento de voto e integridade parlamentar.
        Sua tarefa é analisar um registro de voto, buscando padrões de coerência ideológica,
        sinais de coordenação indevida, troca de posições e possíveis riscos institucionais.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """, "DETALHES DO VOTO:", detalhes_voto)

    async def analisar_proposicao_async(self, detalhes_proposicao: str) -> dict:
        return await self._call_model_async("""
        Você é um Analista Legislativo e Auditor de Política Pública.
        Sua tarefa é avaliar proposições (projetos, emendas, requerimentos) quanto a impacto,
        viabilidade política, favorecimento de grupos e riscos institucionais.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """, "DETALHES DA PROPOSIÇÃO:", detalhes_proposicao)

    async def analisar_cross_data_async(self, detalhes_cross: str) -> dict:
        return await self._call_model_async("""
        Você é um Cientista de Dados e Auditor de Políticas Públicas.
        Sua tarefa é cruzar informações sobre um parlamentar (gastos, votos, proposições)
        e identificar padrões, conflitos de interesse e sinais de captura ou coordenação.
        Use as análises setoriais prévias quando relevante e construa um resumo consolidado.
        Responda estritamente em JSON seguindo o schema fornecido e cite evidências objetivas.
        """, "DETALHES CROSS-DATA:", detalhes_cross)
