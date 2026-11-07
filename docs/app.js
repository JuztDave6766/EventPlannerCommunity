const EVENT_OPTIONS = ["Any", "New Year's Eve", "Christmas", "Birthday", "Casual Evening", "Travel"];
const ATTENDEES_OPTIONS = ["Any", "Relatives", "Friends", "Couple", "Colleagues"];
const COST_OPTIONS = ["Any", "Basso (€ <50)", "Medio (€ 50-200)", "Alto (€ >200)"];
const PEOPLE_OPTIONS = ["2-4", "5-10", "10+"];

function load(key, fallback) {
  try { return JSON.parse(localStorage.getItem(key)) ?? fallback; } catch { return fallback; }
}
function save(key, val) { localStorage.setItem(key, JSON.stringify(val)); }

let users = load("epc_users", []);
let models = load("epc_models", null);
if (models === null) {
  models = [
    {id: 1, titolo: "Pranzo di Natale", tipo_evento: "Christmas", partecipanti: "Relatives", num_persone: "10+", range_costo: "Medio (€ 50-200)", logistica_cibo: "a casa", desc_attivita: "pranzo e regali", popolarita: 5, autore: "demo"},
    {id: 2, titolo: "Capodanno con amici", tipo_evento: "New Year's Eve", partecipanti: "Friends", num_persone: "10+", range_costo: "Alto (€ >200)", logistica_cibo: "locale", desc_attivita: "musica e brindisi", popolarita: 8, autore: "demo"},
    {id: 3, titolo: "Serata giochi", tipo_evento: "Casual Evening", partecipanti: "Friends", num_persone: "5-10", range_costo: "Basso (€ <50)", logistica_cibo: "a casa", desc_attivita: "giochi da tavolo", popolarita: 3, autore: "demo"},
  ];
  save("epc_models", models);
}
let sessionUser = load("epc_session", null);

function flash(msg) {
  const el = document.getElementById("flash");
  el.textContent = msg;
  el.className = "flash";
  setTimeout(() => { el.textContent = ""; el.className = ""; }, 3000);
}

function fillSelect(id, options, selected) {
  const sel = document.getElementById(id);
  sel.innerHTML = "";
  for (const o of options) {
    const opt = document.createElement("option");
    opt.value = o; opt.textContent = o;
    if (o === selected) opt.selected = true;
    sel.appendChild(opt);
  }
}

function initOptions() {
  for (const [f, opts] of [["fTipo", EVENT_OPTIONS],["fPart", ATTENDEES_OPTIONS],["fCosto", COST_OPTIONS],
    ["cTipo", EVENT_OPTIONS],["cPart", ATTENDEES_OPTIONS],["cPers", PEOPLE_OPTIONS],["cCosto", COST_OPTIONS],
    ["eTipo", EVENT_OPTIONS],["ePart", ATTENDEES_OPTIONS],["ePers", PEOPLE_OPTIONS],["eCosto", COST_OPTIONS]]) {
    fillSelect(f, opts, opts[0]);
  }
}

function showLogin() {
  document.getElementById("loginBox").classList.remove("hidden");
  document.getElementById("registerBox").classList.add("hidden");
}
function showRegister() {
  document.getElementById("loginBox").classList.add("hidden");
  document.getElementById("registerBox").classList.remove("hidden");
}

function doRegister() {
  const u = document.getElementById("regUser").value.trim();
  const p = document.getElementById("regPass").value;
  const c = document.getElementById("regConfirm").value;
  if (!u || !p) { flash("Compila tutti i campi"); return; }
  if (p !== c) { flash("Le password non coincidono"); return; }
  if (users.some(x => x.username === u)) { flash("Utente già esistente"); return; }
  users.push({username: u, password: p});
  save("epc_users", users);
  sessionUser = u;
  save("epc_session", sessionUser);
  enterApp();
}

function doLogin() {
  const u = document.getElementById("loginUser").value.trim();
  const p = document.getElementById("loginPass").value;
  const user = users.find(x => x.username === u && x.password === p);
  if (!user) { flash("Credenziali non valide"); return; }
  sessionUser = u;
  save("epc_session", sessionUser);
  enterApp();
}

function logout() {
  sessionUser = null;
  save("epc_session", null);
  document.getElementById("appView").classList.add("hidden");
  document.getElementById("authView").classList.remove("hidden");
  showLogin();
}

function enterApp() {
  document.getElementById("authView").classList.add("hidden");
  document.getElementById("appView").classList.remove("hidden");
  document.getElementById("currentUser").textContent = sessionUser;
  showTab("search");
  renderSearch();
}

function showTab(tab) {
  for (const t of ["search","create","chart"]) {
    document.getElementById("tab-" + t).classList.toggle("hidden", t !== tab);
  }
  if (tab === "chart") renderChart();
}

function renderSearch() {
  const tipo = document.getElementById("fTipo").value;
  const part = document.getElementById("fPart").value;
  const costo = document.getElementById("fCosto").value;
  let res = models.slice();
  if (tipo !== "Any") res = res.filter(m => m.tipo_evento === tipo);
  if (part !== "Any") res = res.filter(m => m.partecipanti === part);
  if (costo !== "Any") res = res.filter(m => m.range_costo === costo);
  res.sort((a,b) => (b.popolarita||0) - (a.popolarita||0));
  const container = document.getElementById("results");
  container.innerHTML = "";
  if (res.length === 0) { container.innerHTML = "<p>Nessun modello trovato.</p>"; return; }
  const title = document.createElement("p");
  title.innerHTML = "<strong>Trovati " + res.length + " Modelli</strong>";
  container.appendChild(title);
  for (const m of res) {
    const card = document.createElement("div");
    card.className = "card";
    card.innerHTML = `
      <h3>${escapeHtml(m.titolo)}</h3>
      <p>❤️ ${m.popolarita||0} Voti | 📅 ${escapeHtml(m.tipo_evento)} | 👤 ${escapeHtml(m.partecipanti)} | 💰 ${escapeHtml(m.range_costo)}</p>
      <p><em>Autore: ${escapeHtml(m.autore||"(anonimo)")}</em></p>
      <p>🏡 Logistica: ${escapeHtml(m.logistica_cibo)}</p>
      <p>🕹️ Attività: ${escapeHtml(m.desc_attivita)}</p>
    `;
    const voteBtn = document.createElement("button");
    voteBtn.className = "btn"; voteBtn.textContent = "⭐ Vota";
    voteBtn.onclick = () => { m.popolarita = (m.popolarita||0)+1; save("epc_models", models); renderSearch(); };
    card.appendChild(voteBtn);
    if (m.autore === sessionUser) {
      const editBtn = document.createElement("button");
      editBtn.className = "btn"; editBtn.textContent = "✏️ Modifica";
      editBtn.onclick = () => openEdit(m.id);
      card.appendChild(editBtn);
      const delBtn = document.createElement("button");
      delBtn.className = "btn btn-danger"; delBtn.textContent = "🗑️ Elimina";
      delBtn.onclick = () => {
        if (!confirm("Eliminare questo modello?")) return;
        models = models.filter(x => x.id !== m.id);
        save("epc_models", models);
        renderSearch();
      };
      card.appendChild(delBtn);
    }
    container.appendChild(card);
  }
}

function escapeHtml(s) {
  return String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function createModel(e) {
  e.preventDefault();
  const data = {
    titolo: document.getElementById("cTitolo").value.trim(),
    tipo_evento: document.getElementById("cTipo").value,
    partecipanti: document.getElementById("cPart").value,
    num_persone: document.getElementById("cPers").value,
    range_costo: document.getElementById("cCosto").value,
    logistica_cibo: document.getElementById("cLog").value.trim(),
    desc_attivita: document.getElementById("cAtt").value.trim(),
  };
  if (!data.titolo || !data.logistica_cibo || !data.desc_attivita) { flash("Compila tutti i campi"); return false; }
  if (data.tipo_evento === "Any" || data.partecipanti === "Any" || data.range_costo === "Any") {
    flash("Specifica Tipo Evento, Partecipanti e Range Costo"); return false;
  }
  const newId = Date.now();
  models.push({id: newId, ...data, popolarita: 0, autore: sessionUser});
  save("epc_models", models);
  flash("Modello pubblicato!");
  document.getElementById("cTitolo").value = "";
  document.getElementById("cLog").value = "";
  document.getElementById("cAtt").value = "";
  showTab("search");
  renderSearch();
  return false;
}

function openEdit(id) {
  const m = models.find(x => x.id === id);
  if (!m) return;
  document.getElementById("eId").value = m.id;
  document.getElementById("eTitolo").value = m.titolo;
  document.getElementById("eTipo").value = m.tipo_evento;
  document.getElementById("ePart").value = m.partecipanti;
  document.getElementById("ePers").value = m.num_persone;
  document.getElementById("eCosto").value = m.range_costo;
  document.getElementById("eLog").value = m.logistica_cibo;
  document.getElementById("eAtt").value = m.desc_attivita;
  document.getElementById("editModal").style.display = "flex";
}

function closeEdit() {
  document.getElementById("editModal").style.display = "none";
}

function saveEdit(e) {
  e.preventDefault();
  const id = Number(document.getElementById("eId").value);
  const m = models.find(x => x.id === id);
  if (!m) return false;
  const data = {
    titolo: document.getElementById("eTitolo").value.trim(),
    tipo_evento: document.getElementById("eTipo").value,
    partecipanti: document.getElementById("ePart").value,
    num_persone: document.getElementById("ePers").value,
    range_costo: document.getElementById("eCosto").value,
    logistica_cibo: document.getElementById("eLog").value.trim(),
    desc_attivita: document.getElementById("eAtt").value.trim(),
  };
  if (!data.titolo || !data.logistica_cibo || !data.desc_attivita) { flash("Compila tutti i campi"); return false; }
  if (data.tipo_evento === "Any" || data.partecipanti === "Any" || data.range_costo === "Any") {
    flash("Specifica Tipo Evento, Partecipanti e Range Costo"); return false;
  }
  Object.assign(m, data);
  save("epc_models", models);
  flash("Modello aggiornato!");
  closeEdit();
  renderSearch();
  return false;
}

function renderChart() {
  const top = models.slice().sort((a,b) => (b.popolarita||0)-(a.popolarita||0)).slice(0,5);
  const container = document.getElementById("chart");
  container.innerHTML = "";
  if (top.length === 0) { container.textContent = "Nessun modello."; return; }
  const maxPop = Math.max(...top.map(m => m.popolarita||0)) || 1;
  for (const m of top) {
    const pct = ((m.popolarita||0)/maxPop*100).toFixed(1);
    const div = document.createElement("div");
    div.style.margin = "10px 0";
    div.innerHTML = `<div style="font-weight:bold;margin-bottom:4px;">${escapeHtml(m.titolo)} (${m.popolarita||0} voti)</div>
      <div style="background:#eee;border-radius:4px;overflow:hidden;">
        <div class="bar" style="width:${pct}%">${m.popolarita||0}</div>
      </div>`;
    container.appendChild(div);
  }
}

initOptions();
if (sessionUser) enterApp();
else showLogin();