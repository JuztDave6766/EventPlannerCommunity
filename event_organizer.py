import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
import time

# --- 1. MOTORE DI GESTIONE DEI MODELLI PUBBLICI (PublicEngine) ---
# (Questa classe rimane invariata)
class PublicEngine:
    """Gestisce il database dei Modelli Evento Pubblici."""
    
    def __init__(self, filename="public_events.json"):
        self.filename = filename
        self.public_models = self._load_public_models()

    def _load_public_models(self):
        # ... (Logica di caricamento JSON) ...
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("File Error", "Impossibile leggere il file dei modelli pubblici. Verrà creato un nuovo file.")
                return []
        return []

    def _save_public_models(self):
        # ... (Logica di salvataggio JSON) ...
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.public_models, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Errore durante il salvataggio del file: {e}")
            return False

    def add_public_model(self, titolo, tipo_evento, partecipanti, num_persone, range_costo, logistica_cibo, desc_attivita):
        # ... (Logica di aggiunta modello) ...
        new_id = int(time.time() * 1000)
        new_model = {
            "id_modello": new_id, "titolo": titolo, "tipo_evento": tipo_evento, "partecipanti": partecipanti, 
            "num_persone": num_persone, "range_costo": range_costo, "logistica_cibo": logistica_cibo, 
            "desc_attivita": desc_attivita, "popolarita": 0
        }
        self.public_models.append(new_model)
        if self._save_public_models():
            return True
        else:
            self.public_models.pop()
            return False

    def search_public_models(self, tipo_evento=None, partecipanti=None, range_costo=None):
        # ... (Logica di ricerca e ordinamento) ...
        results = []
        for model in self.public_models:
            match = True
            if tipo_evento and tipo_evento != 'Any' and model.get('tipo_evento') != tipo_evento: match = False
            if partecipanti and partecipanti != 'Any' and model.get('partecipanti') != partecipanti: match = False
            if range_costo and range_costo != 'Any' and model.get('range_costo') != range_costo: match = False
                
            if match: results.append(model)
        results.sort(key=lambda x: x['popolarita'], reverse=True)
        return results

    def increase_popularity(self, model_id):
        # ... (Logica di aumento popolarità) ...
        for model in self.public_models:
            if model['id_modello'] == model_id:
                model['popolarita'] += 1
                self._save_public_models()
                return True
        return False
        
# --- 2. INTERFACCIA UTENTE (PublicModelUI) ---

class PublicModelUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Piattaforma Modelli Evento Condivisi")
        self.root.geometry("600x650") # Finestra predefinita
        self.root.columnconfigure(0, weight=1) # Permette il resize orizzontale
        self.root.rowconfigure(0, weight=1) # Permette il resize verticale

        self.engine = PublicEngine() 
        self.style = ttk.Style()
        self.style.theme_use('clam') # Tema moderno
        self.style.configure("TLabel", font=("Helvetica", 11), padding=5)
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), padding=8)
        self.style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"))
        self.style.configure("Card.TFrame", background="#f0f0f0", borderwidth=1, relief="solid") # Nuovo stile per le schede

        # Variabili di scelta
        self.event_options = ["Any", "New Year's Eve", "Christmas", "Birthday", "Casual Evening", "Travel"]
        self.attendees_options = ["Any", "Relatives", "Friends", "Couple", "Colleagues"]
        self.cost_options = ["Any", "Basso (€ <50)", "Medio (€ 50-200)", "Alto (€ >200)"]
        self.people_options = ["2-4", "5-10", "10+"]
        
        # Crea il widget Notebook (Le schede)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
        
        # Crea le schede (Frame)
        self.search_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.create_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        
        self.notebook.add(self.search_frame, text="🔍 Cerca Modelli")
        self.notebook.add(self.create_frame, text="✍️ Crea Nuovo Modello")
        
        # Inizializza le interfacce per le due schede
        self._setup_search_tab()
        self._setup_create_tab()
        

    # --- Setup Scheda 1: CREA NUOVO MODELLO ---
    def _setup_create_tab(self):
        # ... (Logica di creazione input invariata, ma con simboli nei label) ...
        ttk.Label(self.create_frame, text="Crea il tuo Modello di Evento Pubblico", font=("Helvetica", 14, "bold")).pack(pady=10)
        
        input_frame = ttk.Frame(self.create_frame)
        input_frame.pack(fill='x', padx=20)
        
        self.create_fields = {}
        row = 0
        
        ttk.Label(input_frame, text="📝 Titolo Breve:").grid(row=row, column=0, sticky='w'); 
        self.create_fields['titolo'] = ttk.Entry(input_frame, width=40); 
        self.create_fields['titolo'].grid(row=row, column=1, pady=5); row += 1
        
        ttk.Label(input_frame, text="📅 Tipo Evento:").grid(row=row, column=0, sticky='w'); 
        self.create_fields['tipo_evento'] = tk.StringVar(value=self.event_options[0]);
        ttk.OptionMenu(input_frame, self.create_fields['tipo_evento'], self.event_options[0], *self.event_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="👤 Partecipanti:").grid(row=row, column=0, sticky='w'); 
        self.create_fields['partecipanti'] = tk.StringVar(value=self.attendees_options[0]);
        ttk.OptionMenu(input_frame, self.create_fields['partecipanti'], self.attendees_options[0], *self.attendees_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="👥 N° Persone:").grid(row=row, column=0, sticky='w'); 
        self.create_fields['num_persone'] = tk.StringVar(value=self.people_options[0]);
        ttk.OptionMenu(input_frame, self.create_fields['num_persone'], self.people_options[0], *self.people_options).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="💰 Range Costo:").grid(row=row, column=0, sticky='w'); 
        self.create_fields['range_costo'] = tk.StringVar(value=self.cost_options[0]);
        ttk.OptionMenu(input_frame, self.create_fields['range_costo'], self.cost_options[0], *self.cost_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1
        
        ttk.Label(self.create_frame, text="🏡 Logistica Cibo/Location:").pack(fill='x', padx=20, pady=(10,0))
        self.create_fields['logistica_cibo'] = tk.Text(self.create_frame, height=4, width=50); 
        self.create_fields['logistica_cibo'].pack(fill='x', padx=20)
        
        ttk.Label(self.create_frame, text="🕹️ Descrizione Attività:").pack(fill='x', padx=20, pady=(10,0))
        self.create_fields['desc_attivita'] = tk.Text(self.create_frame, height=6, width=50); 
        self.create_fields['desc_attivita'].pack(fill='x', padx=20)
        
        ttk.Button(self.create_frame, text="➕ Pubblica il mio Modello", command=self._save_public_model, style="TButton").pack(pady=20)

    def _save_public_model(self):
        """Prende i dati di input e li salva usando PublicEngine."""
        data = {}
        
        # Logica di estrazione dati robusta (corretta nell'errore precedente)
        for k, v in self.create_fields.items():
            if isinstance(v, (tk.StringVar, tk.IntVar)):
                data[k] = v.get()
            elif isinstance(v, tk.Text):
                data[k] = v.get("1.0", tk.END).strip()
            elif hasattr(v, 'get'):
                data[k] = v.get().strip()

        # Semplice validazione
        if not all(data.values()):
            messagebox.showerror("Errore", "Per favore, compila tutti i campi!")
            return

        # Verifica che i dropdown non siano su 'Any'
        if data['tipo_evento'] == 'Any' or data['partecipanti'] == 'Any' or data['range_costo'] == 'Any':
             messagebox.showerror("Errore", "Per pubblicare, devi specificare Tipo Evento, Partecipanti e Range Costo.")
             return
             
        # Chiama il motore per salvare
        if self.engine.add_public_model(**data):
            messagebox.showinfo("Successo", "🎉 Modello pubblicato con successo! Grazie per il tuo contributo!")
            # Pulisce i campi
            for key in self.create_fields:
                if isinstance(self.create_fields[key], tk.StringVar):
                    self.create_fields[key].set(self.event_options[0] if key == 'tipo_evento' else self.attendees_options[0] if key == 'partecipanti' else self.cost_options[0])
                elif isinstance(self.create_fields[key], tk.Text):
                    self.create_fields[key].delete("1.0", tk.END)
                elif isinstance(self.create_fields[key], ttk.Entry):
                    self.create_fields[key].delete(0, tk.END)
        else:
            messagebox.showerror("Errore", "Problema nel salvataggio del Modello.")

    # --- Setup Scheda 2: RICERCA MODELLI (Logica migliorata) ---
    def _setup_search_tab(self):
        ttk.Label(self.search_frame, text="Trova il Modello Perfetto", font=("Helvetica", 14, "bold")).pack(pady=10)

        # Frame dei Filtri (Assicura che sia ri-dimensionabile)
        filter_frame = ttk.Frame(self.search_frame)
        filter_frame.pack(pady=10, fill='x', padx=10)
        filter_frame.columnconfigure((0, 2, 4), weight=0)
        filter_frame.columnconfigure((1, 3, 5), weight=1) # Dropdown si espandono
        filter_frame.columnconfigure(6, weight=0)

        # Inizializza le variabili dei filtri
        self.search_filters = {
            'tipo_evento': tk.StringVar(value='Any'),
            'partecipanti': tk.StringVar(value='Any'),
            'range_costo': tk.StringVar(value='Any')
        }

        # Dropdown Tipo Evento
        ttk.Label(filter_frame, text="📅 Evento:").grid(row=0, column=0, padx=5, sticky='w');
        ttk.OptionMenu(filter_frame, self.search_filters['tipo_evento'], 'Any', *self.event_options).grid(row=0, column=1, padx=5, sticky='ew')

        # Dropdown Partecipanti
        ttk.Label(filter_frame, text="👤 Persone:").grid(row=0, column=2, padx=5, sticky='w');
        ttk.OptionMenu(filter_frame, self.search_filters['partecipanti'], 'Any', *self.attendees_options).grid(row=0, column=3, padx=5, sticky='ew')

        # Dropdown Costo
        ttk.Label(filter_frame, text="💰 Costo:").grid(row=0, column=4, padx=5, sticky='w');
        ttk.OptionMenu(filter_frame, self.search_filters['range_costo'], 'Any', *self.cost_options).grid(row=0, column=5, padx=5, sticky='ew')

        # Pulsante Cerca
        ttk.Button(filter_frame, text="🔍 Cerca", command=self._perform_search).grid(row=0, column=6, padx=15, sticky='e')
        
        # --- Area Risultati con Canvas e Scrollbar (Migliore Leggibilità) ---
        self.results_canvas_frame = ttk.Frame(self.search_frame)
        self.results_canvas_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.canvas = tk.Canvas(self.results_canvas_frame, highlightthickness=0)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = ttk.Scrollbar(self.results_canvas_frame, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_frame_id, width=self.canvas.winfo_width()))
        
        self.results_frame = ttk.Frame(self.canvas)
        self.canvas_frame_id = self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        
        self.results_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        # Esegui la prima ricerca all'avvio
        self._perform_search()

    def _perform_search(self):
        """Esegue la ricerca e crea le schede (Frames) per i risultati."""
        
        # Pulisce i risultati precedenti
        for widget in self.results_frame.winfo_children():
            widget.destroy()
        
        # Prende i filtri
        tipo_evento = self.search_filters['tipo_evento'].get()
        partecipanti = self.search_filters['partecipanti'].get()
        range_costo = self.search_filters['range_costo'].get()
        
        results = self.engine.search_public_models(tipo_evento, partecipanti, range_costo)
        
        if not results:
            ttk.Label(self.results_frame, text="😔 Nessun modello di evento trovato con questi filtri. Prova a crearne uno tu!").pack(pady=20, padx=10)
            return
            
        ttk.Label(self.results_frame, text=f"🎉 Trovati {len(results)} Modelli (Ordinati per Popolarità):\n", font=("Helvetica", 11, "bold")).pack(pady=(10, 5), padx=10, anchor='w')

        for model in results:
            # Crea una "scheda" (Frame) per ogni risultato
            card = ttk.Frame(self.results_frame, padding="10", style="Card.TFrame")
            card.pack(fill='x', padx=10, pady=5)
            card.columnconfigure(0, weight=1)

            # Titolo (Grande e Grosso)
            title_label = ttk.Label(card, text=f"**{model['titolo']}**", font=("Helvetica", 13, "bold"))
            title_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

            # Popolarità e Filtri Chiave (Icone e colori)
            stats_frame = ttk.Frame(card)
            stats_frame.grid(row=1, column=0, sticky='w', pady=(0, 5))
            
            ttk.Label(stats_frame, text=f"❤️ {model['popolarita']} Voti", foreground="red", font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 15))
            ttk.Label(stats_frame, text=f"📅 {model['tipo_evento']}", foreground="#007bff").pack(side="left", padx=10)
            ttk.Label(stats_frame, text=f"👤 {model['partecipanti']}", foreground="#28a745").pack(side="left", padx=10)
            ttk.Label(stats_frame, text=f"💰 {model['range_costo']}", foreground="#ffc107").pack(side="left", padx=10)

            # Logistica e Attività
            ttk.Label(card, text=f"🏡 Logistica: {model['logistica_cibo']}", wraplength=550, justify=tk.LEFT).grid(row=2, column=0, sticky='w')
            ttk.Label(card, text=f"🕹️ Attività: {model['desc_attivita']}", wraplength=550, justify=tk.LEFT).grid(row=3, column=0, sticky='w', pady=(2, 10))

            # Pulsante Vota/Copia
            ttk.Button(card, text="⭐ VOTA / USA QUESTA IDEA", 
                       command=lambda id=model['id_modello']: self._vote_and_copy(id)).grid(row=4, column=0, sticky='e')
        
        # Aggiorna l'area di scorrimento dopo aver aggiunto tutti i widget
        self.results_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _vote_and_copy(self, model_id):
        """Aumenta la popolarità del modello e informa l'utente."""
        if self.engine.increase_popularity(model_id):
            messagebox.showinfo("Grazie!", "Voto registrato! La popolarità del modello è aumentata. Sentiti libero di copiare questa idea per il tuo prossimo evento!")
            self._perform_search() # Ricarica i risultati per vedere l'aggiornamento
        else:
            messagebox.showerror("Errore", "Impossibile registrare il voto.")


def main():
    root = tk.Tk()
    app = PublicModelUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()