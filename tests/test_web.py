import pytest

from app import create_app


@pytest.fixture()
def app(tmp_path):
    return create_app(db_path=str(tmp_path / "w.db"), json_path=str(tmp_path / "w.json"))


@pytest.fixture()
def client(app):
    return app.test_client()


def register(client, username="alice", password="secret"):
    return client.post("/api/auth/register", json={
        "username": username, "password": password,
    })


def login(client, username="alice", password="secret"):
    return client.post("/api/auth/login", json={
        "username": username, "password": password,
    })


def model_data(titolo="WebModel"):
    return {
        "titolo": titolo,
        "tipo_evento": "Birthday",
        "partecipanti": "Friends",
        "num_persone": "5-10",
        "range_costo": "Medio (€ 50-200)",
        "logistica_cibo": "casa",
        "desc_attivita": "giochi",
    }


def test_index_serves_spa(client):
    r = client.get("/")
    assert r.status_code == 200
    assert b"EventPlanner" in r.data


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.get_json()["ok"] is True


def test_register_login_me_logout(client):
    r = register(client)
    assert r.status_code == 201
    assert r.get_json()["user"] == "alice"

    r = client.get("/api/auth/me")
    assert r.get_json()["user"] == "alice"

    r = client.post("/api/auth/logout")
    assert r.status_code == 200
    assert client.get("/api/auth/me").get_json()["user"] is None

    r = login(client, password="wrong")
    assert r.status_code == 401

    r = login(client)
    assert r.status_code == 200


def test_duplicate_register(client):
    assert register(client).status_code == 201
    assert register(client).status_code == 409


def test_create_requires_login(client):
    r = client.post("/api/models", json=model_data())
    assert r.status_code == 401


def test_crud_and_vote(client):
    register(client)
    r = client.post("/api/models", json=model_data())
    assert r.status_code == 201
    model = r.get_json()
    model_id = model["id_modello"]
    assert model["autore"] == "alice"

    r = client.get("/api/models")
    assert len(r.get_json()) == 1

    r = client.put(f"/api/models/{model_id}", json={**model_data("Aggiornato")})
    assert r.status_code == 200
    assert r.get_json()["titolo"] == "Aggiornato"

    r = client.post(f"/api/models/{model_id}/vote")
    assert r.status_code == 200
    assert r.get_json()["popolarita"] == 1

    # another user cannot update/delete
    other = client.application.test_client()
    register(other, "bob", "secret2")
    r = other.put(f"/api/models/{model_id}", json=model_data("Hacked"))
    assert r.status_code == 403
    r = other.delete(f"/api/models/{model_id}")
    assert r.status_code == 403

    r = client.delete(f"/api/models/{model_id}")
    assert r.status_code == 200
    assert client.get("/api/models").get_json() == []
