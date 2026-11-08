const EVENT_OPTIONS = ["Any", "New Year's Eve", "Christmas", "Birthday", "Casual Evening", "Travel"];
const ATTENDEES_OPTIONS = ["Any", "Relatives", "Friends", "Couple", "Colleagues"];
const COST_OPTIONS = ["Any", "Basso (€ <50)", "Medio (€ 50-200)", "Alto (€ >200)"];
const PEOPLE_OPTIONS = ["2-4", "5-10", "10+"];

const STORAGE = {
  models: "epc_models_v3",
  users: "epc_users_v3",
  session: "epc_session_v3",
};

const SEED_MODELS = [
  {
    id: 1, titolo: "Pranzo di Natale", tipo_evento: "Christmas", partecipanti: "Relatives",
    num_persone: "10+", range_costo: "Medio (€ 50-200)",
    logistica_cibo: "Casa di famiglia, ognuno porta un piatto",
    desc_attivita: "Pranzo lento, tombolata pomeridiana e scambio regali sotto l'albero.",
    popolarita: 12, autore: "community",
  },
  {
    id: 2, titolo: "Capodanno con amici", tipo_evento: "New Year's Eve", partecipanti: "Friends",
    num_persone: "10+", range_costo: "Alto (€ >200)",
    logistica_cibo: "Locale prenotato con buffet e open bar",
    desc_attivita: "Cena, playlist condivisa, countdown e brindisi a mezzanotte.",
    popolarita: 24, autore: "community",
  },
  {
    id: 3, titolo: "Serata giochi da tavolo", tipo_evento: "Casual Evening", partecipanti: "Friends",
    num_persone: "5-10", range_costo: "Basso (€ <50)",
    logistica_cibo: "Pizza a domicilio e snack fatti in casa",
    desc_attivita: "Torneo a squadre, giochi veloci e premio finale divertente.",
    popolarita: 18, autore: "community",
  },
  {
    id: 4, titolo: "Compleanno a sorpresa", tipo_evento: "Birthday", partecipanti: "Friends",
    num_persone: "5-10", range_costo: "Medio (€ 50-200)",
    logistica_cibo: "Torta personalizzata e aperitivo in terrazza",
    desc_attivita: "Scavenger hunt in città e festa finale con foto polaroid.",
    popolarita: 9, autore: "community",
  },
  {
    id: 5, titolo: "Weekend fuori porta", tipo_evento: "Travel", partecipanti: "Couple",
    num_persone: "2-4", range_costo: "Alto (€ >200)",
    logistica_cibo: "B&B con colazione e cena tipica locale",
    desc_attivita: "Due giorni tra borghi, passeggiate e mercatini.",
    popolarita: 15, autore: "community",
  },
  {
    id: 6, titolo: "Aperitivo con colleghi", tipo_evento: "Casual Evening", partecipanti: "Colleagues",
    num_persone: "5-10", range_costo: "Basso (€ <50)",
    logistica_cibo: "Aperitivo in rooftop con finger food",
    desc_attivita: "Speed networking informale e playlist rilassata.",
    popolarita: 7, autore: "community",
  },
];

const state = {
  mode: "demo",
  user: null,
  models: [],
  view: "explore",
  filters: { tipo_evento: "Any", partecipanti: "Any", range_costo: "Any" },
};

let toastTimer = null;

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

function readJSON(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    return raw === null ? fallback : JSON.parse(raw);
  } catch {
    return fallback;
  }
}

function writeJSON(key, value) {
  try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* ignore */ }
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function initialOf(name) {
  return escapeHtml((name || "?").trim().charAt(0).toUpperCase() || "?");
}

function optionHtml(value) {
  return `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`;
}

function fillSelect(id, options) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = options.map(optionHtml).join("");
}

function populateSelects() {
  ["filterTipo", "cTipo", "eTipo"].forEach(id => fillSelect(id, EVENT_OPTIONS));
  ["filterPart", "cPart", "ePart"].forEach(id => fillSelect(id, ATTENDEES_OPTIONS));
  ["filterCosto", "cCosto", "eCosto"].forEach(id => fillSelect(id, COST_OPTIONS));
  ["cPers", "ePers"].forEach(id => fillSelect(id, PEOPLE_OPTIONS));
}

const demoStore = {
  models: [],
  users: [],
  session: null,
  load() {
    const storedModels = readJSON(STORAGE.models, null);
    if (Array.isArray(storedModels)) {
      this.models = storedModels;
    } else {
      this.models = SEED_MODELS.map(m => ({ ...m }));
      this.saveModels();
    }
    this.users = readJSON(STORAGE.users, []);
    if (!Array.isArray(this.users)) this.users = [];
    this.session = readJSON(STORAGE.session, null);
    if (this.session && !this.users.some(u => u.username === this.session)) {
      this.session = null;
      this.saveSession();
    }
  },
  saveModels() { writeJSON(STORAGE.models, this.models); },
  saveUsers() { writeJSON(STORAGE.users, this.users); },
  saveSession() { writeJSON(STORAGE.session, this.session); },
};

async function hashPassword(password) {
  try {
    if (window.crypto && crypto.subtle && window.TextEncoder) {
      const data = new TextEncoder().encode(password);
      const buf = await crypto.subtle.digest("SHA-256", data);
      return Array.from(new Uint8Array(buf))
        .map(b => b.toString(16).padStart(2, "0"))
        .join("");
    }
  } catch { /* fall through */ }
  return `plain:${password}`;
}

async function jsonFetch(url, options = {}) {
  const headers = { Accept: "application/json", ...(options.headers || {}) };
  if (options.body) headers["Content-Type"] = "application/json";
  const res = await fetch(url, { ...options, headers });
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (!res.ok) throw new Error((data && data.error) || "Errore di rete");
  return data;
}

async function detectMode() {
  try {
    const res = await fetch("api/health", {
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    if (res.ok) {
      const data = await res.json();
      if (data && data.ok) return "backend";
    }
  } catch { /* demo */ }
  return "demo";
}

function normalizeModel(model) {
  return { ...model, id: model.id ?? model.id_modello };
}

async function refreshModels() {
  if (state.mode === "backend") {
    const models = await jsonFetch("api/models");
    state.models = models.map(normalizeModel);
  } else {
    state.models = demoStore.models;
  }
}

const api = {
  async login(username, password) {
    if (state.mode === "backend") {
      const data = await jsonFetch("api/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      state.user = data.user;
    } else {
      const hash = await hashPassword(password);
      const found = demoStore.users.find(u => u.username === username && u.passwordHash === hash);
      if (!found) throw new Error("Credenziali non valide");
      state.user = username;
      demoStore.session = username;
      demoStore.saveSession();
    }
    await refreshModels();
  },

  async register(username, password) {
    if (state.mode === "backend") {
      const data = await jsonFetch("api/auth/register", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
      state.user = data.user;
    } else {
      if (demoStore.users.some(u => u.username === username)) {
        throw new Error("Utente già esistente");
      }
      const passwordHash = await hashPassword(password);
      demoStore.users.push({ username, passwordHash });
      demoStore.saveUsers();
      demoStore.session = username;
      demoStore.saveSession();
      state.user = username;
    }
    await refreshModels();
  },

  async logout() {
    if (state.mode === "backend") {
      try { await jsonFetch("api/auth/logout", { method: "POST" }); } catch { /* ignore */ }
    } else {
      demoStore.session = null;
      demoStore.saveSession();
    }
    state.user = null;
  },

  async createModel(data) {
    if (state.mode === "backend") {
      await jsonFetch("api/models", { method: "POST", body: JSON.stringify(data) });
    } else {
      demoStore.models.push({
        id: Date.now(),
        ...data,
        popolarita: 0,
        autore: state.user,
      });
      demoStore.saveModels();
    }
    await refreshModels();
  },

  async updateModel(id, data) {
    if (state.mode === "backend") {
      await jsonFetch(`api/models/${id}`, { method: "PUT", body: JSON.stringify(data) });
    } else {
      const model = demoStore.models.find(m => m.id === id);
      if (!model) throw new Error("Modello non trovato");
      Object.assign(model, data);
      demoStore.saveModels();
    }
    await refreshModels();
  },

  async deleteModel(id) {
    if (state.mode === "backend") {
      await jsonFetch(`api/models/${id}`, { method: "DELETE" });
    } else {
      demoStore.models = demoStore.models.filter(m => m.id !== id);
      demoStore.saveModels();
    }
    await refreshModels();
  },

  async vote(id) {
    if (state.mode === "backend") {
      await jsonFetch(`api/models/${id}/vote`, { method: "POST" });
    } else {
      const model = demoStore.models.find(m => m.id === id);
      if (model) {
        model.popolarita = (model.popolarita || 0) + 1;
        demoStore.saveModels();
      }
    }
    await refreshModels();
  },
};

function toast(message, type = "success") {
  const el = document.getElementById("toast");
  el.textContent = message;
  el.className = `toast is-visible ${type}`;
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => { el.className = "toast"; }, 3200);
}

function setAuthTab(tab) {
  $$(".auth-tab").forEach(btn => {
    const active = btn.dataset.auth === tab;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-selected", active ? "true" : "false");
  });
  document.getElementById("loginForm").classList.toggle("hidden", tab !== "login");
  document.getElementById("registerForm").classList.toggle("hidden", tab !== "register");
}

function showAuth(tab = "login") {
  if (state.user) return;
  document.getElementById("authCard").scrollIntoView({ behavior: "smooth", block: "center" });
  setAuthTab(tab);
  const input = tab === "login" ? "loginUser" : "regUser";
  setTimeout(() => document.getElementById(input)?.focus(), 300);
}

function goHome() {
  if (state.user) setView("explore");
  else window.scrollTo({ top: 0, behavior: "smooth" });
}

function setView(view, scroll = true) {
  if (!state.user) {
    showAuth("login");
    return;
  }
  state.view = view;
  $$("#topnav .nav-link").forEach(btn => {
    const active = btn.dataset.view === view;
    btn.classList.toggle("is-active", active);
    if (active) btn.setAttribute("aria-current", "page");
    else btn.removeAttribute("aria-current");
  });
  ["explore", "create", "chart"].forEach(name => {
    document.getElementById(`view-${name}`).classList.toggle("hidden", name !== view);
  });
  if (view === "chart") renderChart();
  if (scroll) window.scrollTo({ top: 0, behavior: "smooth" });
}

function renderModeBadge() {
  const badge = document.getElementById("modeBadge");
  badge.hidden = false;
  badge.className = `mode-badge ${state.mode}`;
  badge.textContent = state.mode === "backend" ? "Backend connesso" : "Demo locale";
  document.getElementById("authNote").textContent = state.mode === "backend"
    ? "Account e dati salvati nel database del server."
    : "Modalità demo: account e dati restano nel tuo browser.";
}

function renderUserArea() {
  const area = document.getElementById("userArea");
  if (!state.user) {
    area.innerHTML = "";
    return;
  }
  area.innerHTML = `
    <span class="user-chip">
      <span class="avatar">${initialOf(state.user)}</span>
      <span>${escapeHtml(state.user)}</span>
    </span>
    <button class="icon-btn small" type="button" data-action="logout" aria-label="Esci">
      <svg class="icon"><use href="#i-logout"/></svg>
    </button>`;
}

function renderStats() {
  const models = state.models || [];
  const votes = models.reduce((sum, m) => sum + (Number(m.popolarita) || 0), 0);
  const authors = new Set(models.map(m => m.autore).filter(Boolean));
  document.getElementById("statModels").textContent = models.length;
  document.getElementById("statVotes").textContent = votes;
  document.getElementById("statAuthors").textContent = authors.size;
}

function cardHtml(model, index) {
  const own = state.user && model.autore === state.user;
  const initial = initialOf(model.autore || "anonimo");
  return `
    <article class="card" style="--i:${index}">
      <div class="card-top">
        <h3 class="card-title">${escapeHtml(model.titolo)}</h3>
      </div>
      <div class="card-author">
        <span class="avatar">${initial}</span>
        <span>${escapeHtml(model.autore || "anonimo")}</span>
      </div>
      <p class="card-desc">${escapeHtml(model.desc_attivita)}</p>
      <div class="tags">
        <span class="tag tipo"><svg class="icon"><use href="#i-calendar"/></svg>${escapeHtml(model.tipo_evento)}</span>
        <span class="tag"><svg class="icon"><use href="#i-users"/></svg>${escapeHtml(model.partecipanti)}</span>
        <span class="tag persone"><svg class="icon"><use href="#i-users"/></svg>${escapeHtml(model.num_persone)}</span>
        <span class="tag costo"><svg class="icon"><use href="#i-wallet"/></svg>${escapeHtml(model.range_costo)}</span>
      </div>
      <p class="card-desc"><strong>Logistica:</strong> ${escapeHtml(model.logistica_cibo)}</p>
      <div class="card-actions">
        <button class="vote-btn" type="button" data-action="vote" data-id="${model.id}" aria-label="Vota questa idea">
          <svg class="icon"><use href="#i-heart"/></svg>
          <span>${Number(model.popolarita) || 0}</span>
        </button>
        <span class="spacer"></span>
        ${own ? `
          <button class="icon-btn small" type="button" data-action="edit" data-id="${model.id}" aria-label="Modifica idea">
            <svg class="icon"><use href="#i-edit"/></svg>
          </button>
          <button class="icon-btn small" type="button" data-action="delete" data-id="${model.id}" aria-label="Elimina idea">
            <svg class="icon"><use href="#i-trash"/></svg>
          </button>` : ""}
      </div>
    </article>`;
}

function renderResults() {
  const { tipo_evento, partecipanti, range_costo } = state.filters;
  const filtered = (state.models || [])
    .filter(m => tipo_evento === "Any" || m.tipo_evento === tipo_evento)
    .filter(m => partecipanti === "Any" || m.partecipanti === partecipanti)
    .filter(m => range_costo === "Any" || m.range_costo === range_costo)
    .sort((a, b) => (Number(b.popolarita) || 0) - (Number(a.popolarita) || 0) || b.id - a.id);

  const count = document.getElementById("resultsCount");
  count.textContent = `${filtered.length} ${filtered.length === 1 ? "idea" : "idee"}`;

  const results = document.getElementById("results");
  if (!filtered.length) {
    results.innerHTML = `
      <div class="empty-state">
        <h3>Nessuna idea con questi filtri</h3>
        <p>Prova a cambiare i filtri oppure pubblica tu la prima idea.</p>
        <button class="btn btn-primary" type="button" data-view="create" style="margin-top:16px">
          <svg class="icon"><use href="#i-plus"/></svg> Crea un'idea
        </button>
      </div>`;
    return;
  }
  results.innerHTML = filtered.map(cardHtml).join("");
}

function renderChart() {
  const top = (state.models || [])
    .slice()
    .sort((a, b) => (Number(b.popolarita) || 0) - (Number(a.popolarita) || 0))
    .slice(0, 5);
  const chart = document.getElementById("chart");
  if (!top.length) {
    chart.innerHTML = `<div class="empty-state"><h3>Ancora nessun voto</h3><p>Pubblica un'idea e invita la community a votarla.</p></div>`;
    return;
  }
  const max = Math.max(...top.map(m => Number(m.popolarita) || 0), 1);
  chart.innerHTML = top.map((model, index) => {
    const pct = (((Number(model.popolarita) || 0) / max) * 100).toFixed(1);
    return `
      <div class="chart-row" style="--i:${index}">
        <span class="chart-label">${escapeHtml(model.titolo)}</span>
        <div class="chart-track"><div class="chart-bar" style="--pct:${pct}%"></div></div>
        <span class="chart-value">${Number(model.popolarita) || 0}</span>
      </div>`;
  }).join("");
}

function renderAll() {
  document.body.dataset.auth = state.user ? "in" : "out";
  renderModeBadge();
  document.getElementById("topnav").classList.toggle("hidden", !state.user);
  document.getElementById("loginCta").classList.toggle("hidden", !!state.user);
  renderUserArea();
  document.getElementById("landingView").classList.toggle("hidden", !!state.user);
  document.getElementById("appView").classList.toggle("hidden", !state.user);
  renderStats();
  if (state.user) {
    document.getElementById("greetingName").textContent = state.user;
    setView(state.view, false);
    renderResults();
    renderChart();
  }
}

function validateModel(data) {
  if (!data.titolo || !data.logistica_cibo || !data.desc_attivita) {
    toast("Compila tutti i campi!", "error");
    return false;
  }
  if (data.tipo_evento === "Any" || data.partecipanti === "Any" || data.range_costo === "Any") {
    toast("Specifica tipo evento, partecipanti e range costo.", "error");
    return false;
  }
  return true;
}

function formData(prefix) {
  return {
    titolo: document.getElementById(`${prefix}Titolo`)?.value.trim() || "",
    tipo_evento: document.getElementById(`${prefix}Tipo`)?.value || "Any",
    partecipanti: document.getElementById(`${prefix}Part`)?.value || "Any",
    num_persone: document.getElementById(`${prefix}Pers`)?.value || PEOPLE_OPTIONS[0],
    range_costo: document.getElementById(`${prefix}Costo`)?.value || "Any",
    logistica_cibo: document.getElementById(`${prefix}Log`)?.value.trim() || "",
    desc_attivita: document.getElementById(`${prefix}Att`)?.value.trim() || "",
  };
}

function openEdit(id) {
  const model = (state.models || []).find(m => m.id === id);
  if (!model) return;
  if (model.autore !== state.user) {
    toast("Puoi modificare solo le tue idee.", "error");
    return;
  }
  document.getElementById("eId").value = model.id;
  document.getElementById("eTitolo").value = model.titolo;
  document.getElementById("eTipo").value = model.tipo_evento;
  document.getElementById("ePart").value = model.partecipanti;
  document.getElementById("ePers").value = model.num_persone;
  document.getElementById("eCosto").value = model.range_costo;
  document.getElementById("eLog").value = model.logistica_cibo;
  document.getElementById("eAtt").value = model.desc_attivita;
  document.getElementById("editModal").hidden = false;
  document.body.classList.add("modal-open");
  setTimeout(() => document.getElementById("eTitolo").focus(), 50);
}

function closeEdit() {
  document.getElementById("editModal").hidden = true;
  document.body.classList.remove("modal-open");
}

async function handleLogin(event) {
  event.preventDefault();
  const username = document.getElementById("loginUser").value.trim();
  const password = document.getElementById("loginPass").value;
  try {
    await api.login(username, password);
    document.getElementById("loginForm").reset();
    renderAll();
    toast(`Bentornato, ${username}!`);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleRegister(event) {
  event.preventDefault();
  const username = document.getElementById("regUser").value.trim();
  const password = document.getElementById("regPass").value;
  const confirm = document.getElementById("regConfirm").value;
  if (!username || !password) {
    toast("Compila tutti i campi!", "error");
    return;
  }
  if (password !== confirm) {
    toast("Le password non coincidono.", "error");
    return;
  }
  try {
    await api.register(username, password);
    document.getElementById("registerForm").reset();
    renderAll();
    toast(`Benvenuto nella community, ${username}!`);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleCreate(event) {
  event.preventDefault();
  const data = formData("c");
  if (!validateModel(data)) return;
  try {
    await api.createModel(data);
    document.getElementById("createForm").reset();
    setView("explore");
    renderResults();
    renderStats();
    toast("Idea pubblicata! Ora aspetta i voti della community.", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleEdit(event) {
  event.preventDefault();
  const id = Number(document.getElementById("eId").value);
  const data = formData("e");
  if (!validateModel(data)) return;
  try {
    await api.updateModel(id, data);
    closeEdit();
    renderResults();
    renderChart();
    toast("Idea aggiornata!", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleVote(id) {
  try {
    await api.vote(id);
    renderResults();
    renderChart();
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleDelete(id) {
  if (!window.confirm("Vuoi davvero eliminare questa idea?")) return;
  try {
    await api.deleteModel(id);
    renderResults();
    renderChart();
    renderStats();
    toast("Idea eliminata.", "success");
  } catch (err) {
    toast(err.message, "error");
  }
}

async function handleLogout() {
  try {
    await api.logout();
    renderAll();
    toast("Sei uscito. A presto!");
  } catch (err) {
    toast(err.message, "error");
  }
}

function bindEvents() {
  document.getElementById("loginForm").addEventListener("submit", handleLogin);
  document.getElementById("registerForm").addEventListener("submit", handleRegister);
  document.getElementById("createForm").addEventListener("submit", handleCreate);
  document.getElementById("editForm").addEventListener("submit", handleEdit);
  document.getElementById("closeEdit").addEventListener("click", closeEdit);
  document.getElementById("cancelEdit").addEventListener("click", closeEdit);
  document.getElementById("editModal").addEventListener("click", event => {
    if (event.target.id === "editModal") closeEdit();
  });
  document.addEventListener("keydown", event => {
    if (event.key === "Escape" && !document.getElementById("editModal").hidden) closeEdit();
  });

  document.getElementById("loginCta").addEventListener("click", () => showAuth("login"));
  document.getElementById("heroLogin").addEventListener("click", () => showAuth("login"));
  document.getElementById("heroRegister").addEventListener("click", () => showAuth("register"));
  document.getElementById("newIdeaBtn").addEventListener("click", () => setView("create"));
  document.getElementById("searchBtn").addEventListener("click", renderResults);

  $$(".auth-tab").forEach(btn => {
    btn.addEventListener("click", () => setAuthTab(btn.dataset.auth));
  });

  document.getElementById("filterTipo").addEventListener("change", event => {
    state.filters.tipo_evento = event.target.value;
    renderResults();
  });
  document.getElementById("filterPart").addEventListener("change", event => {
    state.filters.partecipanti = event.target.value;
    renderResults();
  });
  document.getElementById("filterCosto").addEventListener("change", event => {
    state.filters.range_costo = event.target.value;
    renderResults();
  });

  document.addEventListener("click", event => {
    const viewBtn = event.target.closest("[data-view]");
    if (viewBtn && !viewBtn.closest("#editModal")) {
      event.preventDefault();
      setView(viewBtn.dataset.view);
      return;
    }
    const logoutBtn = event.target.closest('[data-action="logout"]');
    if (logoutBtn) {
      event.preventDefault();
      handleLogout();
    }
  });

  document.getElementById("results").addEventListener("click", event => {
    const actionBtn = event.target.closest("[data-action]");
    if (!actionBtn) return;
    const id = Number(actionBtn.dataset.id);
    const action = actionBtn.dataset.action;
    if (action === "vote") handleVote(id);
    if (action === "edit") openEdit(id);
    if (action === "delete") handleDelete(id);
  });
}

async function loadInitialData() {
  if (state.mode === "backend") {
    try {
      const [me, models] = await Promise.all([
        jsonFetch("api/auth/me"),
        jsonFetch("api/models"),
      ]);
      state.user = me.user;
      state.models = models.map(normalizeModel);
      return;
    } catch {
      state.mode = "demo";
      toast("Backend non raggiungibile: passo alla modalità demo.", "error");
    }
  }
  demoStore.load();
  state.models = demoStore.models;
  state.user = demoStore.session;
}

async function init() {
  populateSelects();
  bindEvents();
  state.mode = await detectMode();
  await loadInitialData();
  renderAll();
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", init);
} else {
  init();
}
