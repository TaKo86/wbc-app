from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/news", tags=["news"])


@router.get("", response_model=list[schemas.NewsOut])
def list_news(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    rows = (
        db.execute(select(models.News).order_by(models.News.published_on.desc()).limit(limit))
        .scalars()
        .all()
    )
    return [schemas.NewsOut.model_validate(r) for r in rows]
