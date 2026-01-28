from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.core.database import get_db
from src.models.proposicao import Proposicao
from src.models.politico import Politico
from src.models.analise import AnaliseIA
from src.schemas.public_api import ProposicaoPublic
from typing import List

router = APIRouter(prefix="/proposicoes", tags=["Proposições"])

@router.get("/", response_model=List[ProposicaoPublic])
async def list_proposicoes(
    politico_id: int = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy import func
    
    # Log request parameters
    print(f"[PROPOSICOES] Request - politico_id: {politico_id}, limit: {limit}")
    
    # Check total count in database
    count_query = select(func.count()).select_from(Proposicao)
    total_count = await db.scalar(count_query)
    print(f"[PROPOSICOES] Total proposições in DB: {total_count}")
    
    # Check autoria table
    from src.models.proposicao import autoria_proposicao
    autoria_count_query = select(func.count()).select_from(autoria_proposicao)
    autoria_count = await db.scalar(autoria_count_query)
    print(f"[PROPOSICOES] Total entries in autoria_proposicao: {autoria_count}")
    
    query = select(Proposicao).options(selectinload(Proposicao.autores))
    
    if politico_id:
        print(f"[PROPOSICOES] Filtering by politico_id: {politico_id}")
        # Filter by author using the many-to-many relationship
        query = query.join(Proposicao.autores).filter(Politico.id == politico_id)
        
        # Check count with filter
        count_filtered = select(func.count()).select_from(Proposicao).join(Proposicao.autores).filter(Politico.id == politico_id)
        filtered_count = await db.scalar(count_filtered)
        print(f"[PROPOSICOES] Proposições for politico_id {politico_id}: {filtered_count}")
    
    # Apply limit after filtering
    query = query.limit(limit)
    
    result = await db.execute(query)
    proposicoes = result.scalars().all()
    
    print(f"[PROPOSICOES] Returning {len(proposicoes)} proposições")
    
    # Adicionamos a análise manualmente se necessário ou via relationship se configurado
    # Por enquanto, retornamos o básico.
    return proposicoes

@router.get("/{id}", response_model=ProposicaoPublic)
async def get_proposicao(id: int, db: AsyncSession = Depends(get_db)):
    query = select(Proposicao).where(Proposicao.id == id)
    result = await db.execute(query)
    proposicao = result.scalar_one_or_none()
    
    if not proposicao:
        raise HTTPException(status_code=404, detail="Proposição não encontrada")
    
    return proposicao
