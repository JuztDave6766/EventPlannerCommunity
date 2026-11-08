import os

from flask import (
    Flask, jsonify, request, session, send_from_directory,
)

from engine import PublicEngine

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "docs")

MODEL_FIELDS = (
    "titolo", "tipo_evento", "partecipanti", "num_persone",
    "range_costo", "logistica_cibo", "desc_attivita",
)

SEED_MODELS = [
    {
        "titolo": "Pranzo di Natale",
        "votes": 12,
        "tipo_evento": "Christmas",
        "partecipanti": "Relatives",
        "num_persone": "10+",
        "range_costo": "Medio (€ 50-200)",
        "logistica_cibo": "Casa di famiglia, ognuno porta un piatto",
        "desc_attivita": "Pranzo lento, tombolata pomeridiana e scambio regali sotto l'albero.",
    },
    {
        "titolo": "Capodanno con amici",
        "votes": 24,
        "tipo_evento": "New Year's Eve",
        "partecipanti": "Friends",
        "num_persone": "10+",
        "range_costo": "Alto (€ >200)",
        "logistica_cibo": "Locale prenotato con buffet e open bar",
        "desc_attivita": "Cena, playlist condivisa, countdown e brindisi a mezzanotte.",
    },
    {
        "titolo": "Serata giochi da tavolo",
        "votes": 18,
        "tipo_evento": "Casual Evening",
        "partecipanti": "Friends",
        "num_persone": "5-10",
        "range_costo": "Basso (€ <50)",
        "logistica_cibo": "Pizza a domicilio e snack fatti in casa",
        "desc_attivita": "Torneo a squadre, giochi veloci e premio finale divertente.",
    },
    {
        "titolo": "Compleanno a sorpresa",
        "votes": 9,
        "tipo_evento": "Birthday",
        "partecipanti": "Friends",
        "num_persone": "5-10",
        "range_costo": "Medio (€ 50-200)",
        "logistica_cibo": "Torta personalizzata e aperitivo in terrazza",
        "desc_attivita": "Scavenger hunt in città e festa finale con foto polaroid.",
    },
    {
        "titolo": "Weekend fuori porta",
        "votes": 15,
        "tipo_evento": "Travel",
        "partecipanti": "Couple",
        "num_persone": "2-4",
        "range_costo": "Alto (€ >200)",
        "logistica_cibo": "B&B con colazione e cena tipica locale",
        "desc_attivita": "Due giorni tra borghi, passeggiate e mercatini.",
    },
]


def create_app(db_path=None, json_path=None):
    app = Flask(__name__, static_folder=None)
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,
    )
    eng = PublicEngine(
        db_path=db_path or os.environ.get("DB_PATH", "event_organizer.db"),
        json_path=json_path or os.environ.get("JSON_PATH", "public_events.json"),
    )
    app.config["ENGINE"] = eng
    if db_path is None and os.environ.get("SEED_DEMO", "1") != "0":
        if not eng.search_public_models():
            for model in SEED_MODELS:
                votes = model.get("votes", 0)
                data = {k: v for k, v in model.items() if k != "votes"}
                new_id = eng.add_public_model(autore="community", **data)
                for _ in range(votes):
                    eng.increase_popularity(new_id)

    def engine():
        return app.config["ENGINE"]

    def model_payload(data):
        return {k: (data.get(k) or "").strip() for k in MODEL_FIELDS}

    def validate_model(data):
        if not all(data.values()):
            return "Compila tutti i campi!"
        if "Any" in (data["tipo_evento"], data["partecipanti"], data["range_costo"]):
            return "Specifica Tipo Evento, Partecipanti e Range Costo."
        return None

    # ---------- SPA statica (stessa UI per GitHub Pages e Flask) ----------
    @app.route("/")
    def index():
        return send_from_directory(DOCS_DIR, "index.html")

    @app.route("/style.css")
    def style_css():
        return send_from_directory(DOCS_DIR, "style.css")

    @app.route("/app.js")
    def app_js():
        return send_from_directory(DOCS_DIR, "app.js")

    # ---------- API ----------
    @app.route("/api/health")
    def api_health():
        return jsonify(ok=True, mode="backend")

    @app.route("/api/auth/me")
    def api_me():
        return jsonify(user=session.get("user"))

    @app.route("/api/auth/register", methods=["POST"])
    def api_register():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if not username or not password:
            return jsonify(error="Compila tutti i campi"), 400
        if len(username) < 3:
            return jsonify(error="Il nome utente deve avere almeno 3 caratteri"), 400
        if len(password) < 4:
            return jsonify(error="La password deve avere almeno 4 caratteri"), 400
        if not engine().register_user(username, password):
            return jsonify(error="Utente già esistente"), 409
        session["user"] = username
        return jsonify(user=username), 201

    @app.route("/api/auth/login", methods=["POST"])
    def api_login():
        data = request.get_json(silent=True) or {}
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""
        if not engine().verify_user(username, password):
            return jsonify(error="Credenziali non valide"), 401
        session["user"] = username
        return jsonify(user=username)

    @app.route("/api/auth/logout", methods=["POST"])
    def api_logout():
        session.pop("user", None)
        return jsonify(ok=True)

    @app.route("/api/models")
    def api_models():
        tipo = request.args.get("tipo_evento", "Any")
        part = request.args.get("partecipanti", "Any")
        costo = request.args.get("range_costo", "Any")
        return jsonify(engine().search_public_models(tipo, part, costo))

    @app.route("/api/models", methods=["POST"])
    def api_create_model():
        user = session.get("user")
        if not user:
            return jsonify(error="Devi fare login"), 401
        data = model_payload(request.get_json(silent=True) or {})
        err = validate_model(data)
        if err:
            return jsonify(error=err), 400
        new_id = engine().add_public_model(autore=user, **data)
        if not new_id:
            return jsonify(error="Errore durante il salvataggio"), 500
        return jsonify(engine().get_model(new_id)), 201

    @app.route("/api/models/<int:model_id>", methods=["PUT"])
    def api_update_model(model_id):
        user = session.get("user")
        if not user:
            return jsonify(error="Devi fare login"), 401
        model = engine().get_model(model_id)
        if not model:
            return jsonify(error="Modello non trovato"), 404
        if model.get("autore") != user:
            return jsonify(error="Non sei autorizzato"), 403
        data = model_payload(request.get_json(silent=True) or {})
        err = validate_model(data)
        if err:
            return jsonify(error=err), 400
        if not engine().update_public_model(model_id, user, **data):
            return jsonify(error="Errore durante l'aggiornamento"), 500
        return jsonify(engine().get_model(model_id))

    @app.route("/api/models/<int:model_id>", methods=["DELETE"])
    def api_delete_model(model_id):
        user = session.get("user")
        if not user:
            return jsonify(error="Devi fare login"), 401
        if not engine().delete_public_model(model_id, user):
            return jsonify(error="Impossibile eliminare il modello"), 403
        return jsonify(ok=True)

    @app.route("/api/models/<int:model_id>/vote", methods=["POST"])
    def api_vote_model(model_id):
        if not engine().increase_popularity(model_id):
            return jsonify(error="Modello non trovato"), 404
        return jsonify(engine().get_model(model_id))

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
