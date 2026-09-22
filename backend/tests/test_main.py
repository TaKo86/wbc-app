def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_item(client):
    payload = {"name": "Test Item"}  # adjust to your actual schema
    response = client.post("/items/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Item"
    assert "id" in data


def test_get_item_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 404