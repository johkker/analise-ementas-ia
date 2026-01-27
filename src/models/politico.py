from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin
from typing import List

class Partido(Base, TimestampMixin):
    __tablename__ = "partidos"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    sigla: Mapped[str] = mapped_column(String(20), unique=True)
    nome: Mapped[str] = mapped_column(String(255))
    logo_url: Mapped[str | None] = mapped_column(String(500))
    
    politicos: Mapped[List["Politico"]] = relationship(back_populates="partido")

class Politico(Base, TimestampMixin):
    __tablename__ = "politicos"
    
    id: Mapped[int] = mapped_column(primary_key=True) # ID da Câmara
    nome_civil: Mapped[str] = mapped_column(String(255))
    nome_parlamentar: Mapped[str] = mapped_column(String(255))
    partido_id: Mapped[int | None] = mapped_column(ForeignKey("partidos.id"))
    uf: Mapped[str] = mapped_column(String(2))
    email: Mapped[str | None] = mapped_column(String(255))
    foto_url: Mapped[str | None] = mapped_column(String(500))
    id_legislatura: Mapped[int | None] = mapped_column()
    
    partido: Mapped["Partido"] = relationship(back_populates="politicos")
    gastos: Mapped[List["Gasto"]] = relationship(back_populates="politico")
    votos: Mapped[List["Voto"]] = relationship(back_populates="politico")
    
    proposicoes: Mapped[List["Proposicao"]] = relationship(
        secondary="autoria_proposicao",
        back_populates="autores"
    )
