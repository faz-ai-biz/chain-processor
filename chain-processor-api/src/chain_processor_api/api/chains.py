from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from chain_processor_db.session import get_db
from chain_processor_db.models.chain import ChainStrategy
from chain_processor_db.repositories.chain_repo import ChainRepository

from ..schemas import ChainCreate, ChainRead

router = APIRouter(prefix="/chains", tags=["chains"])


@router.post("/", response_model=ChainRead)
def create_chain(chain_in: ChainCreate, db: Session = Depends(get_db)) -> ChainRead:
    repo = ChainRepository(db)
    chain = ChainStrategy(
        name=chain_in.name,
        description=chain_in.description,
        is_active=True,
        tags=chain_in.tags,
    )
    repo.create(chain)
    return ChainRead(
        id=chain.id,
        name=chain.name,
        description=chain.description,
        tags=chain.tags,
        version=chain.version,
    )


@router.get("/", response_model=List[ChainRead])
def list_chains(db: Session = Depends(get_db)) -> List[ChainRead]:
    repo = ChainRepository(db)
    chains = repo.get_all()
    return [
        ChainRead(
            id=c.id,
            name=c.name,
            description=c.description,
            tags=c.tags,
            version=c.version,
        )
        for c in chains
    ]
