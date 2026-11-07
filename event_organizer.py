import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from engine import PublicEngine

CONFIG_FILE = "user_config.json"


def load_username() -> str:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                return str(data.get("username", "") or "").strip()
        except (OSError, json.JSONDecodeError, ValueError):
            return ""
    return ""


def save_username(name: str) -> None:
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"username": name}, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


# --- 2. INTERFACCIA UTENTE (PublicModelUI) ---

class PublicModelUI:
    def __init__(self, root):
        self.root = root
        self.engine = PublicEngine()
        self.style = ttk.Style()
        try:
            self.style.theme_use('clam')
        except tk.TclError:
            pass
        self.style.configure("TLabel", font=("Helvetica", 11), padding=5)
        self.style.configure("TButton", font=("Helvetica", 11, "bold"), padding=8)
        self.style.configure("TNotebook.Tab", font=("Helvetica", 11, "bold"))
        self.style.configure("Card.TFrame", background="#f0f0f0", borderwidth=1, relief="solid")

        # Variabili di scelta
        self.event_options = ["Any", "New Year's Eve", "Christmas", "Birthday", "Casual Evening", "Travel"]
        self.attendees_options = ["Any", "Relatives", "Friends", "Couple", "Colleagues"]
        self.cost_options = ["Any", "Basso (€ <50)", "Medio (€ 50-200)", "Alto (€ >200)"]
        self.people_options = ["2-4", "5-10", "10+"]

        self.current_user = load_username()
        if not self.current_user:
            self.current_user = self._prompt_username(initial=True)
            if self.current_user:
                save_username(self.current_user)

        self.root.title(f"Piattaforma Modelli Evento Condivisi - Utente: {self.current_user or '(anonimo)'}")
        self.root.geometry("640x720")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        self._build_menu()

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(pady=10, padx=10, expand=True, fill="both")

        self.search_frame = ttk.Frame(self.notebook, padding="10 10 10 10")
        self.create_frame = ttk.Frame(self.notebook, padding="10 10 10 10")

        self.notebook.add(self.search_frame, text="🔍 Cerca Modelli")
        self.notebook.add(self.create_frame, text="✍️ Crea Nuovo Modello")

        self._setup_create_tab()
        self._setup_search_tab()

    # ---------- menu ----------
    def _build_menu(self):
        menubar = tk.Menu(self.root)
        user_menu = tk.Menu(menubar, tearoff=0)
        user_menu.add_command(label="Cambia utente...", command=self._change_user)
        menubar.add_cascade(label="Utente", menu=user_menu)
        self.root.config(menu=menubar)

    def _prompt_username(self, initial=False):
        prompt = "Inserisci il tuo nome utente:" if not initial else "Benvenuto! Inserisci un nome utente per pubblicare/modificare i tuoi modelli:"
        name = simpledialog.askstring("Utente", prompt, parent=self.root)
        if name is None:
            return ""
        return name.strip()

    def _change_user(self):
        name = self._prompt_username()
        if name == "":
            # consente di annullare senza cambiare
            return
        self.current_user = name
        save_username(name)
        self.root.title(f"Piattaforma Modelli Evento Condivisi - Utente: {self.current_user}")
        self._perform_search()

    # ---------- tab crea ----------
    def _setup_create_tab(self):
        ttk.Label(self.create_frame, text="Crea il tuo Modello di Evento Pubblico", font=("Helvetica", 14, "bold")).pack(pady=10)

        input_frame = ttk.Frame(self.create_frame)
        input_frame.pack(fill='x', padx=20)

        self.create_fields = {}
        row = 0

        ttk.Label(input_frame, text="📝 Titolo Breve:").grid(row=row, column=0, sticky='w')
        self.create_fields['titolo'] = ttk.Entry(input_frame, width=40)
        self.create_fields['titolo'].grid(row=row, column=1, pady=5); row += 1

        ttk.Label(input_frame, text="📅 Tipo Evento:").grid(row=row, column=0, sticky='w')
        self.create_fields['tipo_evento'] = tk.StringVar(value=self.event_options[0])
        ttk.OptionMenu(input_frame, self.create_fields['tipo_evento'], self.event_options[0], *self.event_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="👤 Partecipanti:").grid(row=row, column=0, sticky='w')
        self.create_fields['partecipanti'] = tk.StringVar(value=self.attendees_options[0])
        ttk.OptionMenu(input_frame, self.create_fields['partecipanti'], self.attendees_options[0], *self.attendees_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="👥 N° Persone:").grid(row=row, column=0, sticky='w')
        self.create_fields['num_persone'] = tk.StringVar(value=self.people_options[0])
        ttk.OptionMenu(input_frame, self.create_fields['num_persone'], self.people_options[0], *self.people_options).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(input_frame, text="💰 Range Costo:").grid(row=row, column=0, sticky='w')
        self.create_fields['range_costo'] = tk.StringVar(value=self.cost_options[0])
        ttk.OptionMenu(input_frame, self.create_fields['range_costo'], self.cost_options[0], *self.cost_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(self.create_frame, text="🏡 Logistica Cibo/Location:").pack(fill='x', padx=20, pady=(10, 0))
        self.create_fields['logistica_cibo'] = tk.Text(self.create_frame, height=4, width=50)
        self.create_fields['logistica_cibo'].pack(fill='x', padx=20)

        ttk.Label(self.create_frame, text="🕹️ Descrizione Attività:").pack(fill='x', padx=20, pady=(10, 0))
        self.create_fields['desc_attivita'] = tk.Text(self.create_frame, height=6, width=50)
        self.create_fields['desc_attivita'].pack(fill='x', padx=20)

        ttk.Button(self.create_frame, text="➕ Pubblica il mio Modello", command=self._save_public_model, style="TButton").pack(pady=20)

    def _extract_fields(self, fields):
        data = {}
        for k, v in fields.items():
            if isinstance(v, (tk.StringVar, tk.IntVar)):
                data[k] = v.get()
            elif isinstance(v, tk.Text):
                data[k] = v.get("1.0", tk.END).strip()
            elif hasattr(v, 'get'):
                data[k] = v.get().strip()
        return data

    def _save_public_model(self):
        data = self._extract_fields(self.create_fields)

        if not all(data.values()):
            messagebox.showerror("Errore", "Per favore, compila tutti i campi!")
            return
        if data['tipo_evento'] == 'Any' or data['partecipanti'] == 'Any' or data['range_costo'] == 'Any':
            messagebox.showerror("Errore", "Per pubblicare, devi specificare Tipo Evento, Partecipanti e Range Costo.")
            return
        if not self.current_user:
            self.current_user = self._prompt_username()
            if not self.current_user:
                messagebox.showerror("Errore", "Serve un nome utente per pubblicare.")
                return
            save_username(self.current_user)
            self.root.title(f"Piattaforma Modelli Evento Condivisi - Utente: {self.current_user}")

        if self.engine.add_public_model(autore=self.current_user, **data):
            messagebox.showinfo("Successo", "🎉 Modello pubblicato con successo! Grazie per il tuo contributo!")
            for key in self.create_fields:
                if isinstance(self.create_fields[key], tk.StringVar):
                    self.create_fields[key].set(self.event_options[0] if key == 'tipo_evento' else self.attendees_options[0] if key == 'partecipanti' else self.cost_options[0])
                elif isinstance(self.create_fields[key], tk.Text):
                    self.create_fields[key].delete("1.0", tk.END)
                elif isinstance(self.create_fields[key], ttk.Entry):
                    self.create_fields[key].delete(0, tk.END)
            self._perform_search()
        else:
            messagebox.showerror("Errore", "Problema nel salvataggio del Modello.")

    # ---------- tab ricerca ----------
    def _setup_search_tab(self):
        ttk.Label(self.search_frame, text="Trova il Modello Perfetto", font=("Helvetica", 14, "bold")).pack(pady=10)

        filter_frame = ttk.Frame(self.search_frame)
        filter_frame.pack(pady=10, fill='x', padx=10)
        filter_frame.columnconfigure((0, 2, 4), weight=0)
        filter_frame.columnconfigure((1, 3, 5), weight=1)
        filter_frame.columnconfigure(6, weight=0)

        self.search_filters = {
            'tipo_evento': tk.StringVar(value='Any'),
            'partecipanti': tk.StringVar(value='Any'),
            'range_costo': tk.StringVar(value='Any')
        }

        ttk.Label(filter_frame, text="📅 Evento:").grid(row=0, column=0, padx=5, sticky='w')
        ttk.OptionMenu(filter_frame, self.search_filters['tipo_evento'], 'Any', *self.event_options).grid(row=0, column=1, padx=5, sticky='ew')

        ttk.Label(filter_frame, text="👤 Persone:").grid(row=0, column=2, padx=5, sticky='w')
        ttk.OptionMenu(filter_frame, self.search_filters['partecipanti'], 'Any', *self.attendees_options).grid(row=0, column=3, padx=5, sticky='ew')

        ttk.Label(filter_frame, text="💰 Costo:").grid(row=0, column=4, padx=5, sticky='w')
        ttk.OptionMenu(filter_frame, self.search_filters['range_costo'], 'Any', *self.cost_options).grid(row=0, column=5, padx=5, sticky='ew')

        ttk.Button(filter_frame, text="🔍 Cerca", command=self._perform_search).grid(row=0, column=6, padx=15, sticky='e')

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

        self._perform_search()

    def _perform_search(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

        tipo_evento = self.search_filters['tipo_evento'].get()
        partecipanti = self.search_filters['partecipanti'].get()
        range_costo = self.search_filters['range_costo'].get()

        results = self.engine.search_public_models(tipo_evento, partecipanti, range_costo)

        if not results:
            ttk.Label(self.results_frame, text="😔 Nessun modello di evento trovato con questi filtri. Prova a crearne uno tu!").pack(pady=20, padx=10)
            return

        ttk.Label(self.results_frame, text=f"🎉 Trovati {len(results)} Modelli (Ordinati per Popolarità):\n", font=("Helvetica", 11, "bold")).pack(pady=(10, 5), padx=10, anchor='w')

        for model in results:
            card = ttk.Frame(self.results_frame, padding="10", style="Card.TFrame")
            card.pack(fill='x', padx=10, pady=5)
            card.columnconfigure(0, weight=1)

            title_label = ttk.Label(card, text=f"**{model['titolo']}**", font=("Helvetica", 13, "bold"))
            title_label.grid(row=0, column=0, sticky='w', pady=(0, 5))

            stats_frame = ttk.Frame(card)
            stats_frame.grid(row=1, column=0, sticky='w', pady=(0, 5))

            ttk.Label(stats_frame, text=f"❤️ {model['popolarita']} Voti", foreground="red", font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 15))
            ttk.Label(stats_frame, text=f"📅 {model['tipo_evento']}", foreground="#007bff").pack(side="left", padx=10)
            ttk.Label(stats_frame, text=f"👤 {model['partecipanti']}", foreground="#28a745").pack(side="left", padx=10)
            ttk.Label(stats_frame, text=f"💰 {model['range_costo']}", foreground="#ffc107").pack(side="left", padx=10)

            autore = model.get('autore') or '(anonimo)'
            ttk.Label(card, text=f"✍️ Autore: {autore}", foreground="#555", font=("Helvetica", 9, "italic")).grid(row=2, column=0, sticky='w')

            ttk.Label(card, text=f"🏡 Logistica: {model['logistica_cibo']}", wraplength=550, justify=tk.LEFT).grid(row=3, column=0, sticky='w')
            ttk.Label(card, text=f"🕹️ Attività: {model['desc_attivita']}", wraplength=550, justify=tk.LEFT).grid(row=4, column=0, sticky='w', pady=(2, 10))

            btn_frame = ttk.Frame(card)
            btn_frame.grid(row=5, column=0, sticky='e')

            ttk.Button(btn_frame, text="⭐ VOTA / USA QUESTA IDEA",
                       command=lambda mid=model['id_modello']: self._vote_and_copy(mid)).pack(side="left", padx=5)

            if self.current_user and model.get('autore') == self.current_user:
                ttk.Button(btn_frame, text="✏️ Modifica",
                           command=lambda m=model: self._open_edit_dialog(m)).pack(side="left", padx=5)
                ttk.Button(btn_frame, text="🗑️ Elimina",
                           command=lambda mid=model['id_modello']: self._delete_model(mid)).pack(side="left", padx=5)

        self.results_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _vote_and_copy(self, model_id):
        if self.engine.increase_popularity(model_id):
            messagebox.showinfo("Grazie!", "Voto registrato! La popolarità del modello è aumentata. Sentiti libero di copiare questa idea per il tuo prossimo evento!")
            self._perform_search()
        else:
            messagebox.showerror("Errore", "Impossibile registrare il voto.")

    def _delete_model(self, model_id):
        if not messagebox.askyesno("Conferma", "Vuoi davvero eliminare questo modello?"):
            return
        if self.engine.delete_public_model(model_id, self.current_user):
            messagebox.showinfo("Eliminato", "Modello eliminato.")
            self._perform_search()
        else:
            messagebox.showerror("Errore", "Impossibile eliminare il modello (non sei l'autore o errore).")

    def _open_edit_dialog(self, model):
        dialog = tk.Toplevel(self.root)
        dialog.title("Modifica Modello")
        dialog.geometry("520x620")
        dialog.transient(self.root)
        dialog.grab_set()

        fields = {}
        row = 0
        frm = ttk.Frame(dialog, padding=10)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, text="📝 Titolo Breve:").grid(row=row, column=0, sticky='w')
        fields['titolo'] = ttk.Entry(frm, width=40)
        fields['titolo'].insert(0, model.get('titolo', ''))
        fields['titolo'].grid(row=row, column=1, pady=5); row += 1

        ttk.Label(frm, text="📅 Tipo Evento:").grid(row=row, column=0, sticky='w')
        fields['tipo_evento'] = tk.StringVar(value=model.get('tipo_evento', self.event_options[0]))
        ttk.OptionMenu(frm, fields['tipo_evento'], fields['tipo_evento'].get(), *self.event_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(frm, text="👤 Partecipanti:").grid(row=row, column=0, sticky='w')
        fields['partecipanti'] = tk.StringVar(value=model.get('partecipanti', self.attendees_options[0]))
        ttk.OptionMenu(frm, fields['partecipanti'], fields['partecipanti'].get(), *self.attendees_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(frm, text="👥 N° Persone:").grid(row=row, column=0, sticky='w')
        fields['num_persone'] = tk.StringVar(value=model.get('num_persone', self.people_options[0]))
        ttk.OptionMenu(frm, fields['num_persone'], fields['num_persone'].get(), *self.people_options).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(frm, text="💰 Range Costo:").grid(row=row, column=0, sticky='w')
        fields['range_costo'] = tk.StringVar(value=model.get('range_costo', self.cost_options[0]))
        ttk.OptionMenu(frm, fields['range_costo'], fields['range_costo'].get(), *self.cost_options[1:]).grid(row=row, column=1, pady=5, sticky='w'); row += 1

        ttk.Label(frm, text="🏡 Logistica Cibo/Location:").grid(row=row, column=0, sticky='w')
        fields['logistica_cibo'] = tk.Text(frm, height=4, width=40)
        fields['logistica_cibo'].insert("1.0", model.get('logistica_cibo', ''))
        fields['logistica_cibo'].grid(row=row, column=1, pady=5); row += 1

        ttk.Label(frm, text="🕹️ Descrizione Attività:").grid(row=row, column=0, sticky='w')
        fields['desc_attivita'] = tk.Text(frm, height=6, width=40)
        fields['desc_attivita'].insert("1.0", model.get('desc_attivita', ''))
        fields['desc_attivita'].grid(row=row, column=1, pady=5); row += 1

        def save():
            data = self._extract_fields(fields)
            if not all(data.values()):
                messagebox.showerror("Errore", "Compila tutti i campi!", parent=dialog)
                return
            if data['tipo_evento'] == 'Any' or data['partecipanti'] == 'Any' or data['range_costo'] == 'Any':
                messagebox.showerror("Errore", "Specifica Tipo Evento, Partecipanti e Range Costo.", parent=dialog)
                return
            if self.engine.update_public_model(model['id_modello'], self.current_user, **data):
                messagebox.showinfo("Successo", "Modello aggiornato!", parent=dialog)
                dialog.destroy()
                self._perform_search()
            else:
                messagebox.showerror("Errore", "Impossibile aggiornare (non sei l'autore o errore).", parent=dialog)

        ttk.Button(frm, text="💾 Salva modifiche", command=save).grid(row=row, column=0, columnspan=2, pady=15)


def main():
    root = tk.Tk()
    app = PublicModelUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
