from google import genai
from src.core.config import settings
from pydantic import BaseModel, Field
from typing import List

class AnalisePoliticaSchema(BaseModel):
    resumo_executivo: str = Field(description="Resumo de no máximo 3 frases em linguagem simples.")
    impacto_financeiro: str = Field(description="Classificação: ALTO, MEDIO, BAIXO ou INCERTO.")
    grupos_beneficiados: List[str] = Field(description="Lista de setores ou grupos afetados positivamente.")
    riscos_corrupcao: str = Field(description="Análise técnica de possíveis brechas para desvio de finalidade.")
    sentimento_politico: float = Field(description="Score de -1 (muito populista/agressivo) a 1 (muito técnico/institucional).")

class GeminiClient:
    def __init__(self):
        if not settings.GEMINI_API_KEY:
             raise ValueError("GEMINI_API_KEY not set")
        
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY)
        self.model_name = "gemini-2.0-flash"

    def analisar_gasto(self, detalhes_gasto: str) -> dict:
        prompt_sistema = """
        Você é um Auditor Sênior focado em transparência pública.
        Sua tarefa é analisar gastos de parlamentares brasileiros.
        Extraia dados técnicos objetivos e identifique possíveis anomalias.
        Retorne a análise seguindo estritamente o schema JSON solicitado.
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
