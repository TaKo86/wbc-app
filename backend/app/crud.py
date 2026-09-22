from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app import models, schemas


def fighter_out(f: models.Fighter) -> schemas.FighterOut:
    return schemas.FighterOut.from_orm_fighter(f)


def weight_class_out(wc: models.WeightClass) -> schemas.WeightClassOut:
    return schemas.WeightClassOut(id=wc.id, gender=wc.gender.value, code=wc.code, name=wc.name, kg_display=wc.kg_display)


def current_champion(db: Session, title: models.Title) -> schemas.ChampionOut | None:
    """
    The champion of a title is whoever won its most recent fight — there is
    no separate 'is_current' column to keep in sync. Defences are every
    fight since that fighter's current reign began (i.e. since the last
    fight they didn't win).
    """
    fights = (
        db.execute(
            select(models.TitleFight)
            .where(models.TitleFight.title_id == title.id)
            .options(joinedload(models.TitleFight.winner).joinedload(models.Fighter.gym))
            .order_by(models.TitleFight.fight_date, models.TitleFight.id)
        )
        .scalars()
        .all()
    )
    if not fights:
        return None

    latest = fights[-1]
    defences = 0
    for f in reversed(fights[:-1]):
        if f.winner_id == latest.winner_id:
            defences += 1
        else:
            break

    return schemas.ChampionOut(
        title_id=title.id,
        level=title.level.value,
        scope=title.scope.value,
        weight_class=weight_class_out(title.weight_class),
        fighter=fighter_out(latest.winner),
        since=latest.fight_date,
        won_against=latest.opponent.name if latest.opponent else None,
        event=latest.event,
        defences=defences,
    )


def division_rankings(db: Session, title: models.Title) -> schemas.DivisionRankingsOut:
    champ = current_champion(db, title)
    champ_fighter_id = champ.fighter.id if champ else None

    rankings = (
        db.execute(
            select(models.Ranking)
            .where(models.Ranking.title_id == title.id)
            .options(joinedload(models.Ranking.fighter).joinedload(models.Fighter.gym))
            .order_by(models.Ranking.rank.asc().nulls_last())
        )
        .scalars()
        .all()
    )
    contenders = [
        schemas.RankingEntryOut(rank=r.rank, fighter=fighter_out(r.fighter), requirement=r.requirement, flag=r.flag)
        for r in rankings
        if r.fighter_id != champ_fighter_id
    ]
    return schemas.DivisionRankingsOut(
        weight_class=weight_class_out(title.weight_class),
        level=title.level.value,
        champion=champ,
        contenders=contenders,
    )
