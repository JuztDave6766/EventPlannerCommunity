import json
import os

from engine import PublicEngine


def test_add_and_search(tmp_path):
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(tmp_path / "no.json"))
    assert engine.add_public_model(
        titolo="Festa", tipo_evento="Birthday", partecipanti="Friends",
        num_persone="5-10", range_costo="Medio (€ 50-200)",
        logistica_cibo="a casa", desc_attivita="giochi", autore="alice")
    res = engine.search_public_models()
    assert len(res) == 1
    assert res[0]["titolo"] == "Festa"
    assert res[0]["autore"] == "alice"
    assert res[0]["popolarita"] == 0


def test_filters(tmp_path):
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(tmp_path / "no.json"))
    engine.add_public_model(titolo="A", tipo_evento="Christmas", partecipanti="Relatives",
                           num_persone="2-4", range_costo="Basso (€ <50)",
                           logistica_cibo="x", desc_attivita="y", autore="a")
    engine.add_public_model(titolo="B", tipo_evento="Birthday", partecipanti="Friends",
                           num_persone="5-10", range_costo="Alto (€ >200)",
                           logistica_cibo="x", desc_attivita="y", autore="b")
    assert len(engine.search_public_models(tipo_evento="Christmas")) == 1
    assert len(engine.search_public_models(partecipanti="Friends")) == 1
    assert len(engine.search_public_models(range_costo="Any")) == 2


def test_popularity_sort(tmp_path):
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(tmp_path / "no.json"))
    engine.add_public_model(titolo="A", tipo_evento="Birthday", partecipanti="Friends",
                           num_persone="2-4", range_costo="Basso (€ <50)",
                           logistica_cibo="x", desc_attivita="y", autore="a")
    engine.add_public_model(titolo="B", tipo_evento="Birthday", partecipanti="Friends",
                           num_persone="2-4", range_costo="Basso (€ <50)",
                           logistica_cibo="x", desc_attivita="y", autore="b")
    models = engine.search_public_models()
    first_id = models[1]["id_modello"]
    engine.increase_popularity(first_id)
    engine.increase_popularity(first_id)
    ordered = engine.search_public_models()
    assert ordered[0]["id_modello"] == first_id


def test_update_requires_author(tmp_path):
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(tmp_path / "no.json"))
    engine.add_public_model(titolo="A", tipo_evento="Birthday", partecipanti="Friends",
                           num_persone="2-4", range_costo="Basso (€ <50)",
                           logistica_cibo="x", desc_attivita="y", autore="alice")
    m = engine.search_public_models()[0]
    assert not engine.update_public_model(m["id_modello"], "bob", titolo="Hacked")
    assert engine.update_public_model(m["id_modello"], "alice", titolo="Aggiornato")
    assert engine.get_model(m["id_modello"])["titolo"] == "Aggiornato"


def test_delete_requires_author(tmp_path):
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(tmp_path / "no.json"))
    engine.add_public_model(titolo="A", tipo_evento="Birthday", partecipanti="Friends",
                           num_persone="2-4", range_costo="Basso (€ <50)",
                           logistica_cibo="x", desc_attivita="y", autore="alice")
    m = engine.search_public_models()[0]
    assert not engine.delete_public_model(m["id_modello"], "bob")
    assert len(engine.search_public_models()) == 1
    assert engine.delete_public_model(m["id_modello"], "alice")
    assert len(engine.search_public_models()) == 0


def test_migration_from_json(tmp_path):
    json_path = tmp_path / "public_events.json"
    data = [
        {"id_modello": 1, "titolo": "Legacy", "tipo_evento": "Christmas",
         "partecipanti": "Relatives", "num_persone": "2-4",
         "range_costo": "Basso (€ <50)", "logistica_cibo": "casa",
         "desc_attivita": "pranzo", "popolarita": 3}
    ]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    db = tmp_path / "test.db"
    engine = PublicEngine(db_path=str(db), json_path=str(json_path))
    res = engine.search_public_models()
    assert len(res) == 1
    assert res[0]["titolo"] == "Legacy"
    assert res[0]["popolarita"] == 3
    assert not os.path.exists(json_path)


def test_migration_idempotent(tmp_path):
    json_path = tmp_path / "public_events.json"
    data = [{"id_modello": 1, "titolo": "Legacy", "tipo_evento": "Christmas",
             "partecipanti": "Relatives", "num_persone": "2-4",
             "range_costo": "Basso (€ <50)", "logistica_cibo": "casa",
             "desc_attivita": "pranzo", "popolarita": 3}]
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f)
    db = tmp_path / "test.db"
    PublicEngine(db_path=str(db), json_path=str(json_path))
    # second run: json gone, db has data
    engine2 = PublicEngine(db_path=str(db), json_path=str(json_path))
    assert len(engine2.search_public_models()) == 1
