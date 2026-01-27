from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

class PartidoPublic(BaseModel):
    id: int
    sigla: str
    nome: str
    logo_url: Optional[str]

class PoliticoPublic(BaseModel):
    id: int
    nome_parlamentar: str
    uf: str
    partido: Optional[PartidoPublic]
    foto_url: Optional[str]

class GastoPublic(BaseModel):
    id: int
    data_emissao: Optional[date]
    valor: Decimal
    empresa_nome: Optional[str]
    tipo_despesa: Optional[str]
    url_documento: Optional[str]

class PoliticoDetail(PoliticoPublic):
    nome_civil: str
    email: Optional[str]
    id_legislatura: Optional[int]

class AnaliseIAPublic(BaseModel):
    id: int
    entidade_tipo: str
    entidade_id: str
    resultado_json: dict
    created_at: datetime

class ProposicaoPublic(BaseModel):
    id: int
    sigla_tipo: str
    numero: int
    ano: int
    ementa: str
    data_apresentacao: Optional[datetime]
    analise: Optional[AnaliseIAPublic] = None
