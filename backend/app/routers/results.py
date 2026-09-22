from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, crud
from app.database import get_db

router = APIRouter(prefix="/results", tags=["results"])


@router.get("", response_model=list[schemas.TitleFightOut])
def list_results(
    limit: int = Query(20, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    fights = (
        db.execute(
            select(models.TitleFight)
            .options(
                joinedload(models.TitleFight.title).joinedload(models.Title.weight_class),
                joinedload(models.TitleFight.winner).joinedload(models.Fighter.gym),
                joinedload(models.TitleFight.opponent).joinedload(models.Fighter.gym),
            )
            .order_by(models.TitleFight.fight_date.desc(), models.TitleFight.id.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )
    return [
        schemas.TitleFightOut(
            id=f.id,
            fight_date=f.fight_date,
            weight_class=crud.weight_class_out(f.title.weight_class),
            level=f.title.level.value,
            scope=f.title.scope.value,
            winner=crud.fighter_out(f.winner),
            opponent=crud.fighter_out(f.opponent) if f.opponent else None,
            event=f.event,
            is_vacant_win=f.is_vacant_win,
        )
        for f in fights
    ]
