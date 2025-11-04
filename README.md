# EventPlannerCommunity

Un'applicazione desktop innovativa (Python/Tkinter) che si trasforma in una piattaforma di scambio sociale. 
Stanco delle solite idee per le feste? Qui puoi trovare modelli di eventi reali, creati e votati dalla community, pronti per essere copiati e personalizzati!

## Caratteristiche Principali

* **Modelli Condivisi:** Cerca eventi reali (Natale, Capodanno, Serate Casuali) creati e documentati da altri utenti.
* **Filtri Intelligenti:** Filtra i modelli per Tipo di Evento, Partecipanti e Range di Costo (Basso, Medio, Alto).
* **Sistema di Popolarità:** Vota i modelli migliori! I suggerimenti più votati appaiono sempre per primi.
* **Persistenza Dati:** I modelli sono salvati localmente in un file JSON (`public_events.json`), simulando un database.
* **Interfaccia Intuitiva:** Interfaccia utente pulita e moderna realizzata con Tkinter e lo stile `clam`.

## Tecnologia

* **Linguaggio:** Python 3.x
* **Interfaccia Utente:** Tkinter (con temi `ttk`)
* **Database (Mock):** File JSON per persistenza

## Come Eseguire l'Applicazione

Queste istruzioni ti permetteranno di avere una copia funzionante dell'app sul tuo computer locale per lo sviluppo e l'uso.

### Prerequisiti

Avrai bisogno solo di Python 3 installato sulla tua macchina.

```bash
python --version
```
### Installazione

    Clona la Repository:
    Bash

git clone [https://github.com/JuztDave6766/EventPlannerCommunity.git](https://github.com/JuztDave6766/EventPlannerCommunity.git)
cd EventPlannerCommunity

Esegui il File Principale:
Bash

    python event_organizer.py

## Come Contribuire

Sei un appassionato di eventi o uno sviluppatore Python? Il tuo contributo è fondamentale!

    Fai un Fork del progetto.

    Crea un nuovo Branch per la tua funzionalità (git checkout -b feature/AmazingFeature).

    Implementa e committa le tue modifiche (git commit -m 'Add some AmazingFeature').

    Esegui il Push del tuo Branch (git push origin feature/AmazingFeature).

    Apri una Pull Request!

## Prossimi Sviluppi (Roadmap)

    [ ] Implementare la possibilità di modificare/cancellare i propri modelli pubblicati.

    [ ] Aggiungere un grafico di visualizzazione dei modelli più popolari.

    [ ] Integrazione con un database relazionale (es. SQLite) per una migliore scalabilità.
