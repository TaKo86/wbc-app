from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, crud
from app.database import get_db

router = APIRouter(prefix="/champions", tags=["champions"])


@router.get("", response_model=list[schemas.ChampionOut])
def list_champions(db: Session = Depends(get_db)):
    titles = (
        db.execute(select(models.Title).options(joinedload(models.Title.weight_class)))
        .scalars()
        .all()
    )
    out = [crud.current_champion(db, t) for t in titles]
    return [c for c in out if c is not None]
