from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas, crud
from app.database import get_db

router = APIRouter(prefix="/bouts", tags=["bouts"])


@router.get("", response_model=list[schemas.BoutOut])
def list_upcoming_bouts(
    include_past: bool = Query(False),
    db: Session = Depends(get_db),
):
    stmt = (
        select(models.Bout)
        .options(
            joinedload(models.Bout.weight_class),
            joinedload(models.Bout.fighter_a).joinedload(models.Fighter.gym),
            joinedload(models.Bout.fighter_b).joinedload(models.Fighter.gym),
        )
        .order_by(models.Bout.scheduled_at)
    )
    if not include_past:
        stmt = stmt.where(models.Bout.scheduled_at >= datetime.now(timezone.utc))
    bouts = db.execute(stmt).scalars().all()
    return [
        schemas.BoutOut(
            id=b.id,
            scheduled_at=b.scheduled_at,
            weight_class=crud.weight_class_out(b.weight_class),
            is_title_fight=b.title_id is not None,
            fighter_a=crud.fighter_out(b.fighter_a),
            fighter_b=crud.fighter_out(b.fighter_b),
            rounds=b.rounds,
            city=b.city,
            status=b.status.value,
        )
        for b in bouts
    ]
