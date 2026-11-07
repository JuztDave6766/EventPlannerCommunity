# EventPlannerCommunity

Un'applicazione desktop innovativa (Python/Tkinter) che si trasforma in una piattaforma di scambio sociale.
Stanco delle solite idee per le feste? Qui puoi trovare modelli di eventi reali, creati e votati dalla community, pronti per essere copiati e personalizzati!

## Caratteristiche Principali

* **Modelli Condivisi:** Cerca eventi reali (Natale, Capodanno, Serate Casuali) creati e documentati da altri utenti.
* **Filtri Intelligenti:** Filtra i modelli per Tipo di Evento, Partecipanti e Range di Costo (Basso, Medio, Alto).
* **Sistema di Popolarità:** Vota i modelli migliori! I suggerimenti più votati appaiono sempre per primi.
* **Persistenza Dati:** I modelli sono salvati in un database SQLite (`event_organizer.db`).
* **Gestione Autori:** Ogni modello è associato a un utente; solo l'autore può modificarlo o cancellarlo.
* **Interfaccia Intuitiva:** App desktop Tkinter e app web Flask (condividono lo stesso database).

## Tecnologia

* **Linguaggio:** Python 3.x
* **Interfaccia Utente:** Tkinter (desktop) / Flask + Jinja (web)
* **Database:** SQLite

## Come Eseguire l'Applicazione

### Prerequisiti
Avrai bisogno di Python 3 installato sulla tua macchina.

```bash
python --version
```

### Installazione

```bash
git clone https://github.com/JuztDave6766/EventPlannerCommunity.git
cd EventPlannerCommunity
pip install -r requirements.txt
```

### App desktop (Tkinter)

```bash
python event_organizer.py
```

### App web (Flask)

```bash
python app.py
```

Poi apri http://127.0.0.1:5000 nel browser.

## Come Contribuire

Sei un appassionato di eventi o uno sviluppatore Python? Il tuo contributo è fondamentale!

1. Fai un Fork del progetto.
2. Crea un nuovo Branch per la tua funzionalità (`git checkout -b feature/AmazingFeature`).
3. Implementa e committa le tue modifiche (`git commit -m 'Add some AmazingFeature'`).
4. Esegui il Push del tuo Branch (`git push origin feature/AmazingFeature`).
5. Apri una Pull Request!

## Test

```bash
python -m pytest -q
```

## Prossimi Sviluppi (Roadmap)

* [x] Migrare la persistenza a SQLite.
* [x] Implementare modifica/cancellazione dei propri modelli.
* [x] Aggiungere versione web (Flask).
* [ ] Aggiungere un grafico di visualizzazione dei modelli più popolari.
* [ ] Migliorare l'autenticazione (password, sessioni sicure).
