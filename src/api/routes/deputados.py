from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.core.database import get_db
from src.models.politico import Politico
from src.schemas.public_api import PoliticoPublic, PoliticoDetail
from typing import List

router = APIRouter(prefix="/deputados", tags=["Deputados"])

@router.get("/", response_model=List[PoliticoPublic])
async def list_deputados(
    partido: str = None, 
    uf: str = None,
    limit: int = 24,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = select(Politico).options(selectinload(Politico.partido))
    
    if partido:
        from src.models.politico import Partido
        query = query.join(Politico.partido).filter(Partido.sigla == partido.upper())
    if uf:
        query = query.filter(Politico.uf == uf.upper())
    
    # Add pagination
    query = query.offset(offset).limit(limit)
        
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{id}", response_model=PoliticoDetail)
async def get_deputado(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Politico).where(Politico.id == id).options(selectinload(Politico.partido))
    result = await db.execute(query)
    deputado = result.scalar_one_or_none()
    
    if not deputado:
        raise HTTPException(status_code=404, detail="Deputado não encontrado")
    
    return deputado

@router.get("/partidos/", response_model=List[dict])
async def list_partidos(db: AsyncSession = Depends(get_db)):
    """Fetch all political parties for filter dropdowns"""
    from src.models.politico import Partido
    
    query = select(Partido).order_by(Partido.sigla)
    result = await db.execute(query)
    partidos = result.scalars().all()
    
    return [{"id": p.id, "sigla": p.sigla, "nome": p.nome} for p in partidos]
