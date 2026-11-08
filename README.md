# EventPlannerCommunity

Un'unica app per scoprire, condividere e votare idee per eventi. La stessa interfaccia funziona in due modalità:

- **Demo statica** su GitHub Pages: i dati restano nel browser (`localStorage`).
- **App completa** con backend Flask + SQLite: account, sessioni e dati persistenti sul server.

## Caratteristiche

- Ricerca per tipo evento, partecipanti e range di costo.
- Creazione, modifica e cancellazione delle proprie idee.
- Voti della community e classifica Top 5.
- Registrazione/login con password (hash) e sessioni HttpOnly.
- UI responsive, accessibile e con micro-animazioni (rispetta `prefers-reduced-motion`).

## Struttura

```
docs/            # La UI unica (SPA statica) servita da GitHub Pages e da Flask
  index.html
  style.css
  app.js
app.py           # Backend Flask: serve la SPA + API JSON
engine.py        # Motore SQLite (modelli, utenti, migrazione JSON)
tests/           # Test del motore e delle API
.github/workflows/pages.yml  # Deploy automatico della demo su GitHub Pages
```

## Eseguire l'app completa in locale

```bash
pip install -r requirements.txt
python app.py
```

Apri http://127.0.0.1:5000

Al primo avvio il database SQLite (`event_organizer.db`) viene creato e popolato con alcune idee dimostrative. La modalità backend viene rilevata automaticamente dalla UI.

## Eseguire la demo statica

La UI può essere aperta direttamente da `docs/index.html` oppure pubblicata su GitHub Pages. In assenza del backend, l'app passa automaticamente alla modalità demo e salva i dati nel browser.

### GitHub Pages

Il workflow `.github/workflows/pages.yml` pubblica la cartella `docs/` ad ogni push su `main`. Basta impostare **Settings → Pages → Source: GitHub Actions**.

URL: `https://JuztDave6766.github.io/EventPlannerCommunity/`

## Test

```bash
python -m pytest -q
```

## API principali

| Metodo | Endpoint | Descrizione |
|--------|----------|-------------|
| GET | `/api/health` | Rilevamento backend |
| GET | `/api/models` | Elenco idee |
| POST | `/api/models` | Crea idea (login) |
| PUT | `/api/models/<id>` | Modifica idea (autore) |
| DELETE | `/api/models/<id>` | Elimina idea (autore) |
| POST | `/api/models/<id>/vote` | Vota idea |
| POST | `/api/auth/register` | Registrazione |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/logout` | Logout |
| GET | `/api/auth/me` | Utente corrente |

## Deploy del backend

Il file `Procfile` è pronto per host che eseguono `gunicorn` (es. Railway, Render). Imposta la variabile d'ambiente `SECRET_KEY` con un valore sicuro.

> Nota: GitHub Pages ospita solo la demo statica. Per l'app completa con database serve un host Python.

## Roadmap

- [x] Migrazione a SQLite.
- [x] Modifica/cancellazione dei propri modelli.
- [x] Versione web unificata.
- [x] Grafico dei modelli più popolari.
- [x] Autenticazione con password.
- [ ] Deploy del backend su un host Python.
- [ ] Notifiche e attività della community.
