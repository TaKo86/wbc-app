import enum
from datetime import date, datetime

from sqlalchemy import (
    String, Text, Integer, SmallInteger, Boolean, Date, DateTime,
    ForeignKey, UniqueConstraint, Enum, func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Gender(str, enum.Enum):
    M = "M"
    F = "F"


class TitleLevel(str, enum.Enum):
    World = "World"
    Pro = "Pro"
    Amateur = "Amateur"


class TitleScope(str, enum.Enum):
    NZ = "New Zealand"
    Oceania = "Oceania"
    International = "International"
    World = "World"


class BoutStatus(str, enum.Enum):
    scheduled = "scheduled"
    completed = "completed"
    cancelled = "cancelled"


class Gym(Base):
    __tablename__ = "gyms"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    city: Mapped[str | None] = mapped_column(String, nullable=True)

    fighters: Mapped[list["Fighter"]] = relationship(back_populates="gym")


class Fighter(Base):
    __tablename__ = "fighters"
    __table_args__ = (UniqueConstraint("name", "gender"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender_t"))
    gym_id: Mapped[int | None] = mapped_column(ForeignKey("gyms.id", ondelete="SET NULL"))
    photo_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    am_wins: Mapped[int] = mapped_column(Integer, default=0)
    am_losses: Mapped[int] = mapped_column(Integer, default=0)
    am_draws: Mapped[int] = mapped_column(Integer, default=0)
    pro_wins: Mapped[int] = mapped_column(Integer, default=0)
    pro_losses: Mapped[int] = mapped_column(Integer, default=0)
    pro_draws: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    gym: Mapped[Gym | None] = relationship(back_populates="fighters")


class WeightClass(Base):
    __tablename__ = "weight_classes"
    __table_args__ = (UniqueConstraint("gender", "code"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name="gender_t"))
    code: Mapped[str] = mapped_column(String(6))
    name: Mapped[str] = mapped_column(String)
    kg_display: Mapped[str] = mapped_column(String(8))
    sort_order: Mapped[int] = mapped_column(SmallInteger)

    titles: Mapped[list["Title"]] = relationship(back_populates="weight_class")


class Title(Base):
    __tablename__ = "titles"
    __table_args__ = (UniqueConstraint("weight_class_id", "level", "scope"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    weight_class_id: Mapped[int] = mapped_column(ForeignKey("weight_classes.id", ondelete="CASCADE"))
    level: Mapped[TitleLevel] = mapped_column(Enum(TitleLevel, name="title_level_t"))
    scope: Mapped[TitleScope] = mapped_column(Enum(TitleScope, name="title_scope_t"), default=TitleScope.NZ)

    weight_class: Mapped[WeightClass] = relationship(back_populates="titles")
    fights: Mapped[list["TitleFight"]] = relationship(back_populates="title", order_by="TitleFight.fight_date")
    rankings: Mapped[list["Ranking"]] = relationship(back_populates="title")


class TitleFight(Base):
    __tablename__ = "title_fights"

    id: Mapped[int] = mapped_column(primary_key=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    fight_date: Mapped[date] = mapped_column(Date)
    winner_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    opponent_id: Mapped[int | None] = mapped_column(ForeignKey("fighters.id"), nullable=True)
    event: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_vacant_win: Mapped[bool] = mapped_column(Boolean, default=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    title: Mapped[Title] = relationship(back_populates="fights")
    winner: Mapped[Fighter] = relationship(foreign_keys=[winner_id])
    opponent: Mapped[Fighter | None] = relationship(foreign_keys=[opponent_id])


class Ranking(Base):
    __tablename__ = "rankings"
    __table_args__ = (UniqueConstraint("title_id", "fighter_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    title_id: Mapped[int] = mapped_column(ForeignKey("titles.id", ondelete="CASCADE"))
    fighter_id: Mapped[int] = mapped_column(ForeignKey("fighters.id", ondelete="CASCADE"))
    rank: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    requirement: Mapped[str | None] = mapped_column(Text, nullable=True)
    flag: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    title: Mapped[Title] = relationship(back_populates="rankings")
    fighter: Mapped[Fighter] = relationship()


class Bout(Base):
    __tablename__ = "bouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    weight_class_id: Mapped[int] = mapped_column(ForeignKey("weight_classes.id"))
    title_id: Mapped[int | None] = mapped_column(ForeignKey("titles.id"), nullable=True)
    fighter_a_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    fighter_b_id: Mapped[int] = mapped_column(ForeignKey("fighters.id"))
    rounds: Mapped[int] = mapped_column(SmallInteger, default=5)
    city: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[BoutStatus] = mapped_column(Enum(BoutStatus, name="bout_status_t"), default=BoutStatus.scheduled)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    weight_class: Mapped[WeightClass] = relationship()
    title: Mapped[Title | None] = relationship()
    fighter_a: Mapped[Fighter] = relationship(foreign_keys=[fighter_a_id])
    fighter_b: Mapped[Fighter] = relationship(foreign_keys=[fighter_b_id])


class News(Base):
    __tablename__ = "news"

    id: Mapped[int] = mapped_column(primary_key=True)
    published_on: Mapped[date] = mapped_column(Date)
    title: Mapped[str] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
