from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, crud
from app.database import get_db

router = APIRouter(prefix="/rankings", tags=["rankings"])


@router.get("", response_model=list[schemas.DivisionRankingsOut])
def list_rankings(
    gender: str = Query(..., pattern="^[MF]$"),
    level: str = Query(..., pattern="^(Pro|Amateur)$"),
    db: Session = Depends(get_db),
):
    titles = (
        db.execute(
            select(models.Title)
            .join(models.WeightClass)
            .where(models.WeightClass.gender == gender, models.Title.level == level)
            .options(joinedload(models.Title.weight_class))
            .order_by(models.WeightClass.sort_order)
        )
        .scalars()
        .all()
    )
    return [crud.division_rankings(db, t) for t in titles]


@router.get("/{title_id}", response_model=schemas.DivisionRankingsOut)
def get_division(title_id: int, db: Session = Depends(get_db)):
    title = db.get(models.Title, title_id)
    if not title:
        raise HTTPException(404, "Title not found")
    return crud.division_rankings(db, title)
