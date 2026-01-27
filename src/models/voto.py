from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

class Voto(Base, TimestampMixin):
    __tablename__ = "votos"
    
    # Composite PK via relationship or just an autoincrement ID? 
    # Since a deputy votes only once per votacao, (votacao_id, politico_id) should be unique.
    # But let's use a simple ID for simplicity and unique constraint.
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    votacao_id: Mapped[str] = mapped_column(ForeignKey("votacoes.id"))
    politico_id: Mapped[int] = mapped_column(ForeignKey("politicos.id"))
    tipo_voto: Mapped[str] = mapped_column(String(50)) # Sim, Não, Obstrução, etc.
    
    votacao: Mapped["Votacao"] = relationship(back_populates="votos")
    politico: Mapped["Politico"] = relationship(back_populates="votos")
