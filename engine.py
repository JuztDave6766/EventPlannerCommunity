import json
import os
import sqlite3
import time
try:
    from werkzeug.security import generate_password_hash, check_password_hash
except Exception:  # pragma: no cover
    import hashlib
    def generate_password_hash(pw):
        return hashlib.sha256(pw.encode()).hexdigest()
    def check_password_hash(h, pw):
        return h == hashlib.sha256(pw.encode()).hexdigest()
from typing import Any, Dict, List, Optional


class PublicEngine:
    """Gestisce il database SQLite dei Modelli Evento Pubblici."""

    def __init__(self, db_path: str = "event_organizer.db",
                 json_path: str = "public_events.json"):
        self.db_path = db_path
        self.json_path = json_path
        self._init_db()
        self._migrate_from_json()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS models (
                    id_modello   INTEGER PRIMARY KEY,
                    titolo       TEXT NOT NULL,
                    tipo_evento  TEXT NOT NULL,
                    partecipanti TEXT NOT NULL,
                    num_persone  TEXT NOT NULL,
                    range_costo  TEXT NOT NULL,
                    logistica_cibo TEXT NOT NULL,
                    desc_attivita TEXT NOT NULL,
                    popolarita   INTEGER NOT NULL DEFAULT 0,
                    autore       TEXT NOT NULL DEFAULT ''
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    password_hash TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _migrate_from_json(self) -> None:
        if not os.path.exists(self.json_path):
            return
        try:
            with self._connect() as conn:
                count = conn.execute("SELECT COUNT(*) FROM models").fetchone()[0]
        except sqlite3.Error:
            return
        if count > 0:
            self._remove_json()
            return
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError, ValueError):
            return
        if not isinstance(data, list):
            return
        with self._connect() as conn:
            for m in data:
                if not isinstance(m, dict):
                    continue
                model_id = m.get("id_modello")
                if model_id is None:
                    model_id = int(time.time() * 1000)
                conn.execute(
                    """
                    INSERT OR IGNORE INTO models
                    (id_modello, titolo, tipo_evento, partecipanti, num_persone,
                     range_costo, logistica_cibo, desc_attivita, popolarita, autore)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        model_id,
                        m.get("titolo", ""),
                        m.get("tipo_evento", ""),
                        m.get("partecipanti", ""),
                        m.get("num_persone", ""),
                        m.get("range_costo", ""),
                        m.get("logistica_cibo", ""),
                        m.get("desc_attivita", ""),
                        int(m.get("popolarita", 0) or 0),
                        m.get("autore", "") or "",
                    ),
                )
            conn.commit()
        self._remove_json()

    def _remove_json(self) -> None:
        try:
            os.remove(self.json_path)
        except OSError:
            pass

    def _row_to_dict(self, row: sqlite3.Row) -> dict:
        return {k: row[k] for k in row.keys()}

    def add_public_model(self, titolo: str, tipo_evento: str, partecipanti: str,
                        num_persone: str, range_costo: str, logistica_cibo: str,
                        desc_attivita: str, autore: str = "") -> bool:
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO models
                    (titolo, tipo_evento, partecipanti, num_persone,
                     range_costo, logistica_cibo, desc_attivita, popolarita, autore)
                    VALUES (?,?,?,?,?,?,?,?,?)
                    """,
                    (titolo, tipo_evento, partecipanti, num_persone,
                     range_costo, logistica_cibo, desc_attivita, 0, autore or ""),
                )
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def search_public_models(self, tipo_evento=None, partecipanti=None,
                            range_costo=None):
        query = "SELECT * FROM models"
        conditions = []
        params = []
        if tipo_evento and tipo_evento != "Any":
            conditions.append("tipo_evento = ?")
            params.append(tipo_evento)
        if partecipanti and partecipanti != "Any":
            conditions.append("partecipanti = ?")
            params.append(partecipanti)
        if range_costo and range_costo != "Any":
            conditions.append("range_costo = ?")
            params.append(range_costo)
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY popolarita DESC, id_modello DESC"
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_dict(r) for r in rows]

    def get_model(self, model_id):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM models WHERE id_modello = ?", (model_id,)
            ).fetchone()
        return self._row_to_dict(row) if row else None

    def increase_popularity(self, model_id) -> bool:
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "UPDATE models SET popolarita = popolarita + 1 WHERE id_modello = ?",
                    (model_id,),
                )
                conn.commit()
            return cur.rowcount > 0
        except sqlite3.Error:
            return False

    def register_user(self, username: str, password: str) -> bool:
        username = (username or "").strip()
        if not username or not password:
            return False
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        except sqlite3.Error:
            return False

    def verify_user(self, username: str, password: str) -> bool:
        username = (username or "").strip()
        if not username or not password:
            return False
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT password_hash FROM users WHERE username = ?", (username,)
                ).fetchone()
        except sqlite3.Error:
            return False
        if not row:
            return False
        try:
            return check_password_hash(row["password_hash"], password)
        except Exception:
            return False

    def user_exists(self, username: str) -> bool:
        username = (username or "").strip()
        if not username:
            return False
        try:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT 1 FROM users WHERE username = ?", (username,)
                ).fetchone()
            return row is not None
        except sqlite3.Error:
            return False

    def update_public_model(self, model_id, autore, **fields) -> bool:
        allowed = {
            "titolo", "tipo_evento", "partecipanti", "num_persone",
            "range_costo", "logistica_cibo", "desc_attivita",
        }
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return False
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        params = list(updates.values()) + [model_id, autore or ""]
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    f"UPDATE models SET {set_clause} WHERE id_modello = ? AND autore = ?",
                    params,
                )
                conn.commit()
            return cur.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_public_model(self, model_id, autore) -> bool:
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "DELETE FROM models WHERE id_modello = ? AND autore = ?",
                    (model_id, autore or ""),
                )
                conn.commit()
            return cur.rowcount > 0
        except sqlite3.Error:
            return False
