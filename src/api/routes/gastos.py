from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from src.core.database import get_db
from src.models.gasto import Gasto
from src.models.politico import Politico, Partido
from src.models.analise import AnaliseIA
from typing import Optional
from datetime import date

router = APIRouter(prefix="/gastos", tags=["Gastos"])

@router.get("/exploration")
async def get_gastos_exploration(
    db: AsyncSession = Depends(get_db),
    politico_id: Optional[int] = Query(None),
    politico_nome: Optional[str] = Query(None),
    sigla_partido: Optional[str] = Query(None),
    ano: Optional[int] = Query(None),
    mes: Optional[int] = Query(None),
    data_inicio: Optional[date] = Query(None),
    data_fim: Optional[date] = Query(None),
    tipo_despesa: Optional[str] = Query(None),
    min_valor: Optional[float] = Query(None),
    max_valor: Optional[float] = Query(None),
    has_ai_analysis: Optional[bool] = Query(None),
    sort_by: str = Query("data", enum=["data", "valor"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    # Base query joining Gasto with Politico, Partido and optionally AnaliseIA
    stmt = (
        select(Gasto, Politico.nome_parlamentar, Partido.sigla, AnaliseIA.resumo_critico)
        .join(Politico, Gasto.politico_id == Politico.id)
        .join(Partido, Politico.partido_id == Partido.id)
        .outerjoin(AnaliseIA, and_(
            AnaliseIA.entidade_id == Gasto.ext_id,
            AnaliseIA.entidade_tipo == "GASTO"
        ))
    )

    # Apply filters
    filters = []
    if politico_id:
        filters.append(Gasto.politico_id == politico_id)
    if politico_nome:
        filters.append(Politico.nome_parlamentar.ilike(f"%{politico_nome}%"))
    if sigla_partido:
        filters.append(Partido.sigla.ilike(f"%{sigla_partido}%"))
    if data_inicio:
        filters.append(Gasto.data_emissao >= data_inicio)
    if data_fim:
        filters.append(Gasto.data_emissao <= data_fim)
    if ano:
        filters.append(func.extract('year', Gasto.data_emissao) == ano)
    if mes:
        filters.append(func.extract('month', Gasto.data_emissao) == mes)
    if tipo_despesa:
        filters.append(Gasto.tipo_despesa.ilike(f"%{tipo_despesa}%"))
    if min_valor:
        filters.append(Gasto.valor >= min_valor)
    if max_valor:
        filters.append(Gasto.valor <= max_valor)
    if has_ai_analysis is not None:
        if has_ai_analysis:
            filters.append(AnaliseIA.id != None)
        else:
            filters.append(AnaliseIA.id == None)

    if filters:
        stmt = stmt.where(and_(*filters))

    # Count total for pagination
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total_count = await db.scalar(count_stmt)

    # Paging and ordering
    order_col = Gasto.data_emissao if sort_by == "data" else Gasto.valor
    if sort_order == "desc":
        stmt = stmt.order_by(order_col.desc())
    else:
        stmt = stmt.order_by(order_col.asc())
        
    stmt = stmt.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(stmt)
    items = []
    for row in result.all():
        gasto, nome_politico, partido, ai_resumo = row
        items.append({
            "id": gasto.ext_id,
            "data": gasto.data_emissao,
            "valor": float(gasto.valor),
            "tipo": gasto.tipo_despesa,
            "fornecedor": gasto.empresa_cnpj, # Could join Empresa for name later
            "politico": nome_politico,
            "partido": partido,
            "ai_resumo": ai_resumo
        })

    return {
        "total": total_count,
        "page": page,
        "page_size": page_size,
        "items": items
    }
