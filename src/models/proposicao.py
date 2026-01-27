from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin
from datetime import datetime

class Proposicao(Base, TimestampMixin):
    __tablename__ = "proposicoes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uri: Mapped[str] = mapped_column(String(255))
    sigla_tipo: Mapped[str] = mapped_column(String(10))
    cod_tipo: Mapped[int] = mapped_column(Integer)
    numero: Mapped[int] = mapped_column(Integer)
    ano: Mapped[int] = mapped_column(Integer)
    ementa: Mapped[str] = mapped_column(Text)
    data_apresentacao: Mapped[datetime] = mapped_column(DateTime)

    votacoes: Mapped[list["Votacao"]] = relationship(back_populates="proposicao")
    
    # Many-to-Many via association object or table? 
    # Let's use a simple association table for now.
    autores: Mapped[list["Politico"]] = relationship(
        secondary="autoria_proposicao",
        back_populates="proposicoes"
    )

# Association table must be defined to be picked up by Alembic
from sqlalchemy import Table, Column, Integer, ForeignKey
autoria_proposicao = Table(
    "autoria_proposicao",
    Base.metadata,
    Column("proposicao_id", ForeignKey("proposicoes.id"), primary_key=True),
    Column("politico_id", ForeignKey("politicos.id"), primary_key=True),
)
