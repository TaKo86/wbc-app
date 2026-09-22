"""
One-off loader: reads the site's old data.json (champions/divisions/results/
news) and inserts it through the ORM. Run after db/schema.sql:

    python seed.py path/to/data.json
"""
import json
import re
import sys
from datetime import datetime, date, timezone


def norm(s: str) -> str:
    return re.sub(r"[^a-z]", "", s.lower())

from app import models
from app.database import SessionLocal, engine, Base

KG_ORDER = ["53.5", "55.3", "57.1", "58.9", "61.25", "63.5", "66.6", "69.8", "72.6", "76.2", "79.3", "90.7", "+90.7"]
NAME_BY_KG = {
    "53.5": "Bantamweight", "55.3": "Super-bantamweight", "57.1": "Featherweight",
    "58.9": "Super-featherweight", "61.25": "Lightweight", "63.5": "Super-lightweight",
    "66.6": "Welterweight", "69.8": "Super-welterweight", "72.6": "Middleweight",
    "76.2": "Super-middleweight", "79.3": "Light-heavyweight", "90.7": "Cruiserweight",
    "+90.7": "Heavyweight",
}
CODE_BY_KG = {
    "53.5": "BW", "55.3": "SBW", "57.1": "FW", "58.9": "SFW", "61.25": "LW", "63.5": "SLW",
    "66.6": "WW", "69.8": "SWW", "72.6": "MW", "76.2": "SMW", "79.3": "LHW", "90.7": "CW", "+90.7": "HW",
}


def get_or_create_gym(db, cache, name):
    if not name:
        return None
    if name not in cache:
        gym = models.Gym(name=name)
        db.add(gym)
        db.flush()
        cache[name] = gym
    return cache[name]


def get_or_create_fighter(db, cache, gyms, name, gender, gym_name="", am=None, pro=None):
    key = (name, gender)
    if key in cache:
        f = cache[key]
    else:
        f = models.Fighter(name=name, gender=models.Gender(gender))
        db.add(f)
        db.flush()
        cache[key] = f
    if gym_name and not f.gym_id:
        f.gym = get_or_create_gym(db, gyms, gym_name)
    if am:
        f.am_wins, f.am_losses, f.am_draws = am
    if pro:
        f.pro_wins, f.pro_losses, f.pro_draws = pro
    return f


def get_or_create_weight_class(db, cache, gender, kg):
    key = (gender, kg)
    if key not in cache:
        wc = models.WeightClass(
            gender=models.Gender(gender), code=CODE_BY_KG[kg], name=NAME_BY_KG[kg],
            kg_display=kg, sort_order=KG_ORDER.index(kg),
        )
        db.add(wc)
        db.flush()
        cache[key] = wc
    return cache[key]


def get_or_create_title(db, cache, wc, level, scope="New Zealand"):
    key = (wc.id, level, scope)
    if key not in cache:
        t = models.Title(weight_class_id=wc.id, level=models.TitleLevel(level), scope=models.TitleScope(scope))
        db.add(t)
        db.flush()
        cache[key] = t
    return cache[key]


def main(path):
    data = json.load(open(path))
    Base.metadata.create_all(bind=engine)  # no-op if db/schema.sql already ran

    db = SessionLocal()
    gyms, fighters, wclasses, titles = {}, {}, {}, {}

    try:
        # Divisions -> weight classes, titles, fighters, rankings
        for gender, divisions in data["divisions"].items():
            for div in divisions:
                wc = get_or_create_weight_class(db, wclasses, gender, div["kg"])
                for level_key, level_name in (("proChamp", "Pro"), ("amChamp", "Amateur")):
                    get_or_create_title(db, titles, wc, level_name)  # ensure title exists even if vacant

                for r in div["ranks"]:
                    f = get_or_create_fighter(db, fighters, gyms, r["name"], gender, r.get("gym", ""), r.get("am"), r.get("pro"))
                    tier = r.get("tier", "")
                    level = "Pro" if "pro" in tier else ("Amateur" if "am" in tier else None)
                    if level:
                        title = get_or_create_title(db, titles, wc, level)
                        db.add(models.Ranking(title_id=title.id, fighter_id=f.id, requirement=r.get("req") or None, flag=r.get("flag") or None))

        # Champions -> title_fights (first/only row per title here; results below adds full history)
        for c in data["champions"]:
            gender = c["gender"]
            wc = get_or_create_weight_class(db, wclasses, gender, c["kg"])
            scope = "World" if c["level"] == "World" else "New Zealand"
            title = get_or_create_title(db, titles, wc, c["level"], scope)
            winner = get_or_create_fighter(db, fighters, gyms, c["name"], gender, c.get("gym", ""), c.get("am"), c.get("pro"))
            opponent = get_or_create_fighter(db, fighters, gyms, c["opponent"], gender) if c.get("opponent") else None
            db.add(models.TitleFight(
                title_id=title.id, fight_date=date.fromisoformat(c["since"]), winner_id=winner.id,
                opponent_id=opponent.id if opponent else None, event=c.get("promotion"),
            ))

        # Results -> additional title_fights history (skip ones already added as the champion row)
        db.flush()
        seen = {(tf.title_id, tf.winner_id, tf.fight_date) for tf in db.query(models.TitleFight)}
        by_norm_name = {}
        for (name, gender) in fighters:
            by_norm_name.setdefault(norm(name), []).append(gender)

        skipped = []
        for r in data["results"]:
            # Results don't carry gender directly, so resolve it from a fighter we
            # already created (champions/rankings loops). If the name doesn't match
            # anyone — often a spelling variant between sheets — skip and report it
            # rather than silently guessing a gender and creating a duplicate fighter.
            genders = by_norm_name.get(norm(r["winner"]))
            if not genders or len(set(genders)) > 1:
                skipped.append(r["winner"])
                continue
            gender = genders[0]
            kg = None
            for k, name in NAME_BY_KG.items():
                if r["division"].startswith(name):
                    kg = k
                    break
            if not kg:
                continue
            wc = get_or_create_weight_class(db, wclasses, gender, kg)
            scope = r.get("scope", "New Zealand")
            # In this schema a title's scope and level are tied together: a
            # scope of "World" is always the World title, regardless of what
            # the source row's level column says (the source data has at
            # least one "World" scope row labelled level "Pro" — see the
            # handoff notes for the specific case this affects).
            level = "World" if scope == "World" else (r.get("level") or "Pro")
            title = get_or_create_title(db, titles, wc, level, scope)
            winner = get_or_create_fighter(db, fighters, gyms, r["winner"], gender)
            opponent = get_or_create_fighter(db, fighters, gyms, r["opponent"], gender) if r.get("opponent") else None
            fight_date = date.fromisoformat(r["date"])
            key = (title.id, winner.id, fight_date)
            if key in seen:
                continue
            db.add(models.TitleFight(
                title_id=title.id, fight_date=fight_date, winner_id=winner.id,
                opponent_id=opponent.id if opponent else None, event=r.get("event"),
            ))
            seen.add(key)

        # News
        for n in data["news"]:
            db.add(models.News(
                published_on=date.fromisoformat(n["date"][:10]),
                title=n["title"], summary=n.get("summary"), url=n.get("url"), source=n.get("source"),
            ))

        # Bouts (empty in the source file today, kept for when they're added)
        for b in data.get("bouts", []):
            wc = get_or_create_weight_class(db, wclasses, b.get("gender", "M"), b["kg"])
            fa = get_or_create_fighter(db, fighters, gyms, b["a"], b.get("gender", "M"))
            fb = get_or_create_fighter(db, fighters, gyms, b["b"], b.get("gender", "M"))
            db.add(models.Bout(
                scheduled_at=datetime.fromisoformat(b["date"]), weight_class_id=wc.id,
                fighter_a_id=fa.id, fighter_b_id=fb.id, rounds=b.get("rounds", 5), city=b.get("city"),
            ))

        db.commit()
        print(f"Seeded {len(fighters)} fighters, {len(gyms)} gyms, {len(wclasses)} weight classes, {len(titles)} titles.")
        if skipped:
            print(f"Skipped {len(skipped)} result(s) — winner name didn't match a known fighter (check spelling):")
            for name in sorted(set(skipped)):
                print(f"  - {name}")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data.json")
