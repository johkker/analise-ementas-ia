from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from src.core.database import get_db
from src.models.politico import Politico
from src.models.gasto import Gasto
from src.models.proposicao import Proposicao

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Exemplo de stats agregadas
    total_deputados = await db.scalar(select(func.count(Politico.id)))
    total_gastos = await db.scalar(select(func.sum(Gasto.valor)))
    total_proposicoes = await db.scalar(select(func.count(Proposicao.id)))
    
    return {
        "total_deputados": total_deputados or 0,
        "total_gastos": float(total_gastos or 0),
        "total_proposicoes": total_proposicoes or 0,
        "savings_opportunity_estimate": float(total_gastos or 0) * 0.05 # Exemplo de métrica "AI"
    }
