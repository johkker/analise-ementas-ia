from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from src.core.database import get_db
from src.models.politico import Politico
from src.models.gasto import Gasto
from src.models.proposicao import Proposicao

router = APIRouter(prefix="/stats", tags=["Stats"])

from datetime import datetime

@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    # Current year for default filtering
    target_year = datetime.now().year
    
    # 1. Broad Counts
    total_deputados = await db.scalar(select(func.count(Politico.id)))
    total_proposicoes = await db.scalar(select(func.count(Proposicao.id)))
    
    # 2. Financial Metrics for the current year
    total_gastos_2026 = await db.scalar(
        select(func.sum(Gasto.valor))
        .where(func.extract('year', Gasto.data_emissao) == target_year)
    )
    
    # 3. Top 5 Spenders in 2026
    top_spenders_query = (
        select(
            Politico.nome_parlamentar,
            Politico.foto_url,
            func.sum(Gasto.valor).label("total_gasto")
        )
        .join(Gasto)
        .where(func.extract('year', Gasto.data_emissao) == target_year)
        .group_by(Politico.id)
        .order_by(func.sum(Gasto.valor).desc())
        .limit(5)
    )
    top_spenders_result = await db.execute(top_spenders_query)
    top_spenders = [
        {"nome": r[0], "foto_url": r[1], "valor": float(r[2])} 
        for r in top_spenders_result.all()
    ]
    
    # 4. Expenditure by Category
    category_query = (
        select(Gasto.tipo_despesa, func.sum(Gasto.valor))
        .where(func.extract('year', Gasto.data_emissao) == target_year)
        .group_by(Gasto.tipo_despesa)
        .order_by(func.sum(Gasto.valor).desc())
        .limit(5)
    )
    category_result = await db.execute(category_query)
    categories = [
        {"categoria": r[0], "valor": float(r[1])}
        for r in category_result.all()
    ]
    
    return {
        "year": target_year,
        "total_deputados": total_deputados or 0,
        "total_proposicoes": total_proposicoes or 0,
        "total_gastos": float(total_gastos_2026 or 0),
        "top_spenders": top_spenders,
        "categories": categories,
        "savings_opportunity_estimate": float(total_gastos_2026 or 0) * 0.05
    }
