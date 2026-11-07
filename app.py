import os

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, current_app,
)

from engine import PublicEngine

EVENT_OPTIONS = ["Any", "New Year's Eve", "Christmas", "Birthday", "Casual Evening", "Travel"]
ATTENDEES_OPTIONS = ["Any", "Relatives", "Friends", "Couple", "Colleagues"]
COST_OPTIONS = ["Any", "Basso (€ <50)", "Medio (€ 50-200)", "Alto (€ >200)"]
PEOPLE_OPTIONS = ["2-4", "5-10", "10+"]


def get_engine():
    return current_app.config["ENGINE"]


def create_app(db_path=None, json_path=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["ENGINE"] = PublicEngine(
        db_path=db_path or os.environ.get("DB_PATH", "event_organizer.db"),
        json_path=json_path or os.environ.get("JSON_PATH", "public_events.json"),
    )

    @app.context_processor
    def inject_opts():
        return dict(
            event_options=EVENT_OPTIONS,
            attendees_options=ATTENDEES_OPTIONS,
            cost_options=COST_OPTIONS,
            people_options=PEOPLE_OPTIONS,
        )

    def _extract_form(form):
        return {
            "titolo": form.get("titolo", "").strip(),
            "tipo_evento": form.get("tipo_evento"),
            "partecipanti": form.get("partecipanti"),
            "num_persone": form.get("num_persone"),
            "range_costo": form.get("range_costo"),
            "logistica_cibo": form.get("logistica_cibo", "").strip(),
            "desc_attivita": form.get("desc_attivita", "").strip(),
        }

    def _validate(data):
        if not all(data.values()):
            return "Compila tutti i campi!"
        if data["tipo_evento"] == "Any" or data["partecipanti"] == "Any" or data["range_costo"] == "Any":
            return "Specifica Tipo Evento, Partecipanti e Range Costo."
        return None

    @app.route("/")
    def index():
        engine = get_engine()
        tipo = request.args.get("tipo_evento", "Any")
        part = request.args.get("partecipanti", "Any")
        costo = request.args.get("range_costo", "Any")
        results = engine.search_public_models(tipo, part, costo)
        filters = {"tipo_evento": tipo, "partecipanti": part, "range_costo": costo}
        return render_template("index.html", results=results, filters=filters)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            name = request.form.get("username", "").strip()
            if not name:
                flash("Inserisci un nome utente")
                return redirect(url_for("login"))
            session["user"] = name
            flash(f"Benvenuto, {name}")
            return redirect(url_for("index"))
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("user", None)
        return redirect(url_for("index"))

    @app.route("/create", methods=["GET", "POST"])
    def create():
        if not session.get("user"):
            flash("Devi fare login per creare un modello")
            return redirect(url_for("login"))
        if request.method == "POST":
            data = _extract_form(request.form)
            err = _validate(data)
            if err:
                flash(err)
                return render_template("create.html", data=data)
            engine = get_engine()
            if engine.add_public_model(autore=session["user"], **data):
                flash("Modello pubblicato con successo!")
                return redirect(url_for("index"))
            flash("Problema nel salvataggio del Modello.")
        return render_template("create.html", data={})

    @app.route("/edit/<int:model_id>", methods=["GET", "POST"])
    def edit(model_id):
        engine = get_engine()
        model = engine.get_model(model_id)
        if not model:
            flash("Modello non trovato")
            return redirect(url_for("index"))
        if model.get("autore") != session.get("user"):
            flash("Non sei autorizzato a modificare questo modello")
            return redirect(url_for("index"))
        if request.method == "POST":
            data = _extract_form(request.form)
            err = _validate(data)
            if err:
                flash(err)
                return render_template("edit.html", model=model, data=data)
            if engine.update_public_model(model_id, session["user"], **data):
                flash("Modello aggiornato!")
                return redirect(url_for("index"))
            flash("Impossibile aggiornare il modello.")
        return render_template("edit.html", model=model, data=model)

    @app.route("/delete/<int:model_id>", methods=["POST"])
    def delete(model_id):
        engine = get_engine()
        if engine.delete_public_model(model_id, session.get("user", "")):
            flash("Modello eliminato.")
        else:
            flash("Impossibile eliminare il modello.")
        return redirect(url_for("index"))

    @app.route("/vote/<int:model_id>", methods=["POST"])
    def vote(model_id):
        engine = get_engine()
        engine.increase_popularity(model_id)
        return redirect(request.referrer or url_for("index"))

    @app.route("/chart")
    def chart():
        engine = get_engine()
        results = engine.search_public_models()[:5]
        max_pop = max((m.get("popolarita", 0) or 0) for m in results) if results else 1
        if max_pop == 0:
            max_pop = 1
        return render_template("chart.html", results=results, max_pop=max_pop)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
