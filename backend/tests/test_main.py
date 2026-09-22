from app.models import Fighter, Gender, WeightClass, Title, TitleLevel, Ranking


def test_rankings_amateur_with_seeded_data(client, db_session):
    # 1. Weight class
    wc = WeightClass(
        gender=Gender.M,
        code="LW",
        name="Lightweight",
        kg_display="61.2kg",
        sort_order=1,
    )
    db_session.add(wc)
    db_session.commit()
    db_session.refresh(wc)

    # 2. Amateur title for that weight class
    title = Title(weight_class_id=wc.id, level=TitleLevel.Amateur)
    db_session.add(title)
    db_session.commit()
    db_session.refresh(title)

    # 3. Fighter (record fields default to 0 per your model)
    fighter = Fighter(name="Test Fighter", gender=Gender.M)
    db_session.add(fighter)
    db_session.commit()
    db_session.refresh(fighter)

    # 4. Rank the fighter #1 contender (no title_fights row, so no champion yet)
    ranking = Ranking(title_id=title.id, fighter_id=fighter.id, rank=1)
    db_session.add(ranking)
    db_session.commit()

    # 5. Hit the real endpoint
    response = client.get("/rankings", params={"gender": "M", "level": "Amateur"})
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1  # one weight class in the test DB

    division = data[0]
    assert division["weight_class"]["id"] == wc.id
    assert division["level"] == "Amateur"
    assert division["champion"] is None  # no TitleFight row seeded, so no champion yet

    assert len(division["contenders"]) == 1
    contender = division["contenders"][0]
    assert contender["rank"] == 1
    assert contender["fighter"]["id"] == fighter.id
    assert contender["fighter"]["name"] == "Test Fighter"
    assert contender["fighter"]["record"]["am"] == [0, 0, 0]
    assert contender["fighter"]["record"]["pro"] == [0, 0, 0]



def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_champions(client):
    response = client.get("/champions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_rankings(client):
    response = client.get("/rankings", params={"gender": "M", "level": "Amateur"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_rankings_by_title_id_not_found(client):
    response = client.get("/rankings/999999", params={"gender": "F", "level": "Pro"})
    assert response.status_code == 404


def test_results(client):
    response = client.get("/results")
    assert response.status_code == 200


def test_bouts(client):
    response = client.get("/bouts")
    assert response.status_code == 200


def test_news(client):
    response = client.get("/news")
    assert response.status_code == 200