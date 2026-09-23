from datetime import datetime, timezone
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.config import settings
from app.database import get_db

router = APIRouter(prefix="/submissions", tags=["submissions"])


def require_admin(x_admin_key: str | None = Header(default=None)) -> None:
    if not x_admin_key or not secrets.compare_digest(x_admin_key, settings.admin_api_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Admin access required")


def get_submission_or_404(db: Session, submission_id: int) -> models.FighterSubmission:
    submission = db.get(models.FighterSubmission, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission


@router.post("", response_model=schemas.FighterSubmissionOut, status_code=201)
def create_submission(payload: schemas.FighterSubmissionCreate, db: Session = Depends(get_db)):
    submission = models.FighterSubmission(
        **payload.model_dump(exclude={"recent_fights"})
    )
    submission.recent_fights = [
        models.SubmissionFight(**fight.model_dump()) for fight in payload.recent_fights
    ]
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return submission


@router.get("", response_model=list[schemas.FighterSubmissionOut], dependencies=[Depends(require_admin)])
def list_submissions(db: Session = Depends(get_db)):
    return db.scalars(
        select(models.FighterSubmission).order_by(models.FighterSubmission.created_at.desc())
    ).all()


@router.patch("/{submission_id}", response_model=schemas.FighterSubmissionOut, dependencies=[Depends(require_admin)])
def update_submission(
    submission_id: int,
    payload: schemas.FighterSubmissionUpdate,
    db: Session = Depends(get_db),
):
    submission = get_submission_or_404(db, submission_id)
    values = payload.model_dump(exclude_unset=True)
    recent_fights = values.pop("recent_fights", None)
    for field, value in values.items():
        setattr(submission, field, value)
    if recent_fights is not None:
        submission.recent_fights = [models.SubmissionFight(**fight) for fight in recent_fights]
    db.commit()
    db.refresh(submission)
    return submission


@router.post("/{submission_id}/approve", response_model=schemas.FighterOut, dependencies=[Depends(require_admin)])
def approve_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = get_submission_or_404(db, submission_id)
    if submission.status == models.SubmissionStatus.rejected:
        raise HTTPException(status_code=409, detail="Rejected submissions must be edited before approval")

    fighter = db.scalar(
        select(models.Fighter).where(
            models.Fighter.name == submission.name,
            models.Fighter.gender == submission.gender,
        )
    )
    if fighter is None:
        fighter = models.Fighter(name=submission.name, gender=submission.gender)
        db.add(fighter)

    fighter.am_wins = submission.am_wins
    fighter.am_losses = submission.am_losses
    fighter.am_draws = submission.am_draws
    fighter.pro_wins = submission.pro_wins
    fighter.pro_losses = submission.pro_losses
    fighter.pro_draws = submission.pro_draws

    if submission.gym_name:
        gym = db.scalar(select(models.Gym).where(models.Gym.name == submission.gym_name))
        if gym is None:
            gym = models.Gym(name=submission.gym_name)
            db.add(gym)
        fighter.gym = gym

    submission.status = models.SubmissionStatus.approved
    submission.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(fighter)
    return schemas.FighterOut.from_orm_fighter(fighter)


@router.post("/{submission_id}/reject", response_model=schemas.FighterSubmissionOut, dependencies=[Depends(require_admin)])
def reject_submission(
    submission_id: int,
    payload: schemas.SubmissionDecision,
    db: Session = Depends(get_db),
):
    submission = get_submission_or_404(db, submission_id)
    submission.status = models.SubmissionStatus.rejected
    submission.admin_note = payload.admin_note
    submission.reviewed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(submission)
    return submission


@router.delete("/{submission_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_submission(submission_id: int, db: Session = Depends(get_db)):
    submission = get_submission_or_404(db, submission_id)
    db.delete(submission)
    db.commit()
