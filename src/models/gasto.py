from sqlalchemy import String, ForeignKey, Numeric, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin
from datetime import date
from decimal import Decimal

class Empresa(Base, TimestampMixin):
    __tablename__ = "empresas"
    
    cnpj: Mapped[str] = mapped_column(String(20), primary_key=True)
    nome_fantasia: Mapped[str | None] = mapped_column(String(255))
    razao_social: Mapped[str | None] = mapped_column(String(255))
    
    gastos: Mapped[list["Gasto"]] = relationship(back_populates="empresa")

class Gasto(Base, TimestampMixin):
    __tablename__ = "gastos_gabinete"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ext_id: Mapped[int] = mapped_column(unique=True) # idDocumento da API
    politico_id: Mapped[int] = mapped_column(ForeignKey("politicos.id"))
    empresa_cnpj: Mapped[str | None] = mapped_column(ForeignKey("empresas.cnpj"))
    valor: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    data_emissao: Mapped[date | None] = mapped_column(Date)
    tipo_despesa: Mapped[str | None] = mapped_column(String(255))
    url_documento: Mapped[str | None] = mapped_column(String(500))
    
    politico: Mapped["Politico"] = relationship(back_populates="gastos")
    empresa: Mapped["Empresa"] = relationship(back_populates="gastos")
