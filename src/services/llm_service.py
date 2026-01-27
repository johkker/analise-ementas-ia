import google.generativeai as genai
import json
from src.core.config import settings
from pydantic import BaseModel, Field
from typing import List

class AnalisePoliticaSchema(BaseModel):
    resumo_executivo: str = Field(description="Resumo de no máximo 3 frases em linguagem simples.")
    impacto_financeiro: str = Field(description="Classificação: ALTO, MEDIO, BAIXO ou INCERTO.")
    grupos_beneficiados: List[str] = Field(description="Lista de setores ou grupos afetados positivamente.")
    riscos_corrupcao: str = Field(description="Análise técnica de possíveis brechas para desvio de finalidade.")
    sentimento_politico: float = Field(description="Score de -1 (muito populista/agressivo) a 1 (muito técnico/institucional).")

def _limpar_schema(schema: dict):
    """Remove campos não suportados pelo Gemini (como 'title')."""
    if not isinstance(schema, dict):
        return
    schema.pop("title", None)
    for key, value in schema.items():
        if isinstance(value, dict):
            _limpar_schema(value)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    _limpar_schema(item)

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY not set")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        schema = AnalisePoliticaSchema.model_json_schema()
        _limpar_schema(schema)
        
        self.model = genai.GenerativeModel(
            model_name="gemini-3-flash-preview",
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.1,
            }
        )

    def analisar_gasto(self, detalhes_gasto: str) -> dict:
        prompt_sistema = """
        Você é um Auditor Sênior focado em transparência pública.
        Sua tarefa é analisar gastos de parlamentares brasileiros.
        Extraia dados técnicos objetivos e identifique possíveis anomalias.
        """
        try:
            response = self.model.generate_content(
                f"{prompt_sistema}\n\nDETALHES DO GASTO:\n{detalhes_gasto}"
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[LLM Error] Falha na análise: {e}")
            raise
