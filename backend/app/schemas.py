from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GymOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str | None = None


class Record(BaseModel):
    """Wins-losses-draws, kept separate for amateur and pro bouts."""
    am: tuple[int, int, int]
    pro: tuple[int, int, int]


class FighterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    gender: str
    gym: GymOut | None = None
    photo_url: str | None = None
    record: Record

    @classmethod
    def from_orm_fighter(cls, f) -> "FighterOut":
        return cls(
            id=f.id, name=f.name, gender=f.gender.value,
            gym=GymOut.model_validate(f.gym) if f.gym else None,
            photo_url=f.photo_url,
            record=Record(am=(f.am_wins, f.am_losses, f.am_draws), pro=(f.pro_wins, f.pro_losses, f.pro_draws)),
        )


class SubmissionFight(BaseModel):
    fight_number: int = Field(ge=1, le=5)
    opponent_name: str = Field(min_length=2, max_length=120)
    result: str = Field(
        pattern="^(Win|Loss|Draw|No contest|Decision win|Decision loss|TKO win|TKO loss)$"
    )


class FighterSubmissionCreate(BaseModel):
    submitted_name: str = Field(min_length=2, max_length=120)
    submitted_email: str = Field(min_length=5, max_length=254)
    name: str = Field(min_length=2, max_length=120)
    gender: str = Field(pattern="^[MF]$")
    gym_name: str | None = Field(default=None, max_length=120)
    am_wins: int = Field(default=0, ge=0)
    am_losses: int = Field(default=0, ge=0)
    am_draws: int = Field(default=0, ge=0)
    pro_wins: int = Field(default=0, ge=0)
    pro_losses: int = Field(default=0, ge=0)
    pro_draws: int = Field(default=0, ge=0)
    recent_fights: list[SubmissionFight] = Field(default_factory=list, max_length=5)

    @field_validator("recent_fights")
    @classmethod
    def validate_recent_fights(cls, value):
        numbers = [fight.fight_number for fight in value]
        if len(numbers) != len(set(numbers)):
            raise ValueError("Recent fight numbers must be unique")
        return value


class FighterSubmissionUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=120)
    gender: str | None = Field(default=None, pattern="^[MF]$")
    gym_name: str | None = Field(default=None, max_length=120)
    am_wins: int | None = Field(default=None, ge=0)
    am_losses: int | None = Field(default=None, ge=0)
    am_draws: int | None = Field(default=None, ge=0)
    pro_wins: int | None = Field(default=None, ge=0)
    pro_losses: int | None = Field(default=None, ge=0)
    pro_draws: int | None = Field(default=None, ge=0)
    admin_note: str | None = Field(default=None, max_length=2000)
    recent_fights: list[SubmissionFight] | None = Field(default=None, max_length=5)


class SubmissionDecision(BaseModel):
    admin_note: str | None = Field(default=None, max_length=2000)


class FighterSubmissionOut(FighterSubmissionCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    status: str
    admin_note: str | None
    reviewed_at: datetime | None
    created_at: datetime


class WeightClassOut(BaseModel):
    id: int
    gender: str
    code: str
    name: str
    kg_display: str


class ChampionOut(BaseModel):
    """A title's current holder, derived from the latest title_fights row."""
    title_id: int
    level: str
    scope: str
    weight_class: WeightClassOut
    fighter: FighterOut
    since: date
    won_against: str | None
    event: str | None
    defences: int


class RankingEntryOut(BaseModel):
    rank: int | None
    fighter: FighterOut
    requirement: str | None
    flag: str | None


class DivisionRankingsOut(BaseModel):
    weight_class: WeightClassOut
    level: str
    champion: ChampionOut | None
    contenders: list[RankingEntryOut]


class TitleFightOut(BaseModel):
    id: int
    fight_date: date
    weight_class: WeightClassOut
    level: str
    scope: str
    winner: FighterOut
    opponent: FighterOut | None
    event: str | None
    is_vacant_win: bool


class BoutOut(BaseModel):
    id: int
    scheduled_at: datetime
    weight_class: WeightClassOut
    is_title_fight: bool
    fighter_a: FighterOut
    fighter_b: FighterOut
    rounds: int
    city: str | None
    status: str


class NewsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    published_on: date
    title: str
    summary: str | None
    url: str | None
    source: str | None
