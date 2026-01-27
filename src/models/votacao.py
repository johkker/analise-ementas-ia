from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin
from datetime import datetime

class Votacao(Base, TimestampMixin):
    __tablename__ = "votacoes"

    id: Mapped[str] = mapped_column(String(50), primary_key=True) # API uses string IDs for votes
    uri: Mapped[str] = mapped_column(String(255))
    data: Mapped[datetime] = mapped_column(DateTime)
    sigla_orgao: Mapped[str] = mapped_column(String(20))
    aprovacao: Mapped[int | None] = mapped_column(Integer, nullable=True) # 0 or 1, or None
    descricao: Mapped[str] = mapped_column(Text)
    
    # Inferred from uriProposicaoObjeto or similar
    proposicao_id: Mapped[int | None] = mapped_column(ForeignKey("proposicoes.id"), nullable=True)
    
    votos: Mapped[list["Voto"]] = relationship(back_populates="votacao")
    proposicao: Mapped["Proposicao"] = relationship(back_populates="votacoes")
