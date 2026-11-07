from app import create_app


def _register(c, username="alice", password="secret"):
    return c.post("/register", data={
        "username": username, "password": password, "confirm": password,
    }, follow_redirects=True)


def test_index_ok(tmp_path):
    app = create_app(db_path=str(tmp_path / "w.db"), json_path=str(tmp_path / "w.json"))
    c = app.test_client()
    r = c.get("/")
    assert r.status_code == 200


def test_create_requires_login(tmp_path):
    app = create_app(db_path=str(tmp_path / "w.db"), json_path=str(tmp_path / "w.json"))
    c = app.test_client()
    r = c.post("/create", data={"titolo": "X"}, follow_redirects=True)
    assert r.status_code == 200
    assert b"Login" in r.data or b"login" in r.data.lower()


def test_register_and_login(tmp_path):
    app = create_app(db_path=str(tmp_path / "w.db"), json_path=str(tmp_path / "w.json"))
    c = app.test_client()
    r = _register(c)
    assert r.status_code == 200
    # duplicate registration fails
    r = _register(c)
    assert b"esistente" in r.data or b"errore" in r.data.lower()
    # login with wrong password fails
    c2 = app.test_client()
    r = c2.post("/login", data={"username": "alice", "password": "wrong"}, follow_redirects=True)
    assert b"Credenziali" in r.data
    # login ok
    r = c2.post("/login", data={"username": "alice", "password": "secret"}, follow_redirects=True)
    assert r.status_code == 200


def test_create_and_delete_flow(tmp_path):
    app = create_app(db_path=str(tmp_path / "w.db"), json_path=str(tmp_path / "w.json"))
    c = app.test_client()
    _register(c, "alice", "secret")
    r = c.post("/create", data={
        "titolo": "WebModel", "tipo_evento": "Birthday", "partecipanti": "Friends",
        "num_persone": "5-10", "range_costo": "Medio (€ 50-200)",
        "logistica_cibo": "casa", "desc_attivita": "giochi",
    }, follow_redirects=True)
    assert r.status_code == 200
    assert b"WebModel" in r.data
    eng = app.config["ENGINE"]
    m = eng.search_public_models()[0]
    # delete by non-author fails
    c2 = app.test_client()
    _register(c2, "bob", "secret2")
    r = c2.post(f"/delete/{m['id_modello']}", follow_redirects=True)
    assert b"Impossibile" in r.data or b"WebModel" in r.data
    # delete by author succeeds
    r = c.post(f"/delete/{m['id_modello']}", follow_redirects=True)
    assert b"WebModel" not in r.data
