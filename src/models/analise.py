from sqlalchemy import String, JSON, Text, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from src.models.base import Base, TimestampMixin
from decimal import Decimal

class AnaliseIA(Base, TimestampMixin):
    __tablename__ = "analises_ia"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    entidade_tipo: Mapped[str] = mapped_column(String(50)) # 'POLITICO', 'GASTO', 'PROPOSICAO'
    entidade_id: Mapped[int] = mapped_column() # ID correspondente
    
    score_anomalia: Mapped[Decimal | None] = mapped_column(Numeric(3, 2))
    resumo_critico: Mapped[str | None] = mapped_column(Text)
    impacto_financeiro: Mapped[str | None] = mapped_column(String(50))
    grupos_beneficiados: Mapped[list[str] | None] = mapped_column(JSON)
    riscos_corrupcao: Mapped[str | None] = mapped_column(Text)
    raw_response: Mapped[dict | None] = mapped_column(JSON)
