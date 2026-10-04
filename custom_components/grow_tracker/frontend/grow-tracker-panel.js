/**
 * Grow Tracker – Seitenleisten-Panel für Home Assistant.
 * Eigenständige Web-Komponente ohne Build-Schritt.
 */

const PHASES = [
  "germination",
  "rooting",
  "vegetative",
  "mother",
  "flowering",
  "drying",
  "curing",
  "finished",
];

const PHASE_COLORS = {
  germination: "#9ccc65",
  rooting: "#a1887f",
  vegetative: "#43a047",
  mother: "#00897b",
  flowering: "#ab47bc",
  drying: "#fb8c00",
  curing: "#8d6e63",
  finished: "#9e9e9e",
};

const I18N = {
  en: {
    title: "Grow Tracker",
    manage: "Manage",
    not_loaded: "Grow Tracker is not set up or not loaded.",
    no_locations: "No locations yet. Add locations and plants on the integration page.",
    no_plants: "No plants",
    without_location: "Without location",
    plant_one: "plant",
    plants: "plants",
    day: "Day",
    week: "Week",
    days: "days",
    harvest_in: "Harvest in {n} days",
    harvest_today: "Harvest due",
    harvest_over: "Harvest {n} days overdue",
    cuttings: "{n} cuttings",
    cutting_of: "Cutting of {name}",
    seed: "From seed",
    total: "Total",
    in_phase: "In phase",
    at_location: "At location",
    expected_harvest: "Expected harvest",
    since: "since",
    change_phase: "Change phase",
    change_location: "Change location",
    add_note: "Add note",
    note_placeholder: "e.g. feeding, training, observation …",
    take_cuttings: "Take cuttings",
    count: "Count",
    create_plants: "Create as plants",
    target_location: "Location",
    automatic: "Automatic",
    date: "Date",
    save: "Save",
    phase_history: "Phase history",
    location_history: "Location history",
    notes: "Notes",
    cuttings_log: "Cuttings",
    tracked_cuttings: "Tracked cuttings",
    no_notes: "No notes yet",
    edit: "Edit plant",
    close: "Close",
    saved: "Saved",
    delete_plant: "Delete plant",
    delete_confirm: "Really delete “{name}”?",
    delete_warning: "Phase and location history, notes and the cuttings log will be lost. This cannot be undone.",
    delete_children_note: "Its {n} tracked cuttings are kept.",
    cancel: "Cancel",
    delete_final: "Delete permanently",
    phases: {
      germination: "Germination",
      rooting: "Rooting",
      vegetative: "Vegetative",
      mother: "Mother plant",
      flowering: "Flowering",
      drying: "Drying",
      curing: "Curing",
      finished: "Finished",
    },
    location_types: {
      propagation: "Propagation",
      mother: "Mother plants",
      vegetative: "Vegetative",
      flowering: "Flowering",
      drying: "Drying",
      other: "Other",
    },
  },
  de: {
    title: "Grow Tracker",
    manage: "Verwalten",
    not_loaded: "Grow Tracker ist nicht eingerichtet oder nicht geladen.",
    no_locations: "Noch keine Standorte. Standorte und Pflanzen legst du auf der Integrationsseite an.",
    no_plants: "Keine Pflanzen",
    without_location: "Ohne Standort",
    plant_one: "Pflanze",
    plants: "Pflanzen",
    day: "Tag",
    week: "Woche",
    days: "Tage",
    harvest_in: "Ernte in {n} Tagen",
    harvest_today: "Ernte fällig",
    harvest_over: "Ernte seit {n} Tagen fällig",
    cuttings: "{n} Stecklinge",
    cutting_of: "Steckling von {name}",
    seed: "Aus Samen",
    total: "Gesamt",
    in_phase: "In Phase",
    at_location: "Am Standort",
    expected_harvest: "Voraussichtliche Ernte",
    since: "seit",
    change_phase: "Phase ändern",
    change_location: "Standort ändern",
    add_note: "Notiz hinzufügen",
    note_placeholder: "z. B. Düngung, Training, Beobachtung …",
    take_cuttings: "Stecklinge schneiden",
    count: "Anzahl",
    create_plants: "Als Pflanzen anlegen",
    target_location: "Standort",
    automatic: "Automatisch",
    date: "Datum",
    save: "Speichern",
    phase_history: "Phasen-Historie",
    location_history: "Standort-Historie",
    notes: "Notizen",
    cuttings_log: "Stecklinge",
    tracked_cuttings: "Erfasste Stecklinge",
    no_notes: "Noch keine Notizen",
    edit: "Pflanze bearbeiten",
    close: "Schließen",
    saved: "Gespeichert",
    delete_plant: "Pflanze löschen",
    delete_confirm: "„{name}“ wirklich löschen?",
    delete_warning: "Phasen- und Standort-Historie, Notizen und das Stecklings-Protokoll gehen verloren. Das lässt sich nicht rückgängig machen.",
    delete_children_note: "Die {n} erfassten Stecklinge bleiben erhalten.",
    cancel: "Abbrechen",
    delete_final: "Endgültig löschen",
    phases: {
      germination: "Keimung",
      rooting: "Bewurzelung",
      vegetative: "Wachstum",
      mother: "Mutterpflanze",
      flowering: "Blüte",
      drying: "Trocknung",
      curing: "Curing",
      finished: "Abgeschlossen",
    },
    location_types: {
      propagation: "Anzucht",
      mother: "Mutterpflanzen",
      vegetative: "Wachstum",
      flowering: "Blüte",
      drying: "Trocknung",
      other: "Sonstiges",
    },
  },
};

const INTEGRATION_URL = "/config/integrations/integration/grow_tracker";

function esc(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

class GrowTrackerPanel extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
    this._data = null;
    this._error = null;
    this._selectedId = null;
    this._unsub = null;
    this._built = false;
  }

  // --- Eigenschaften, die Home Assistant setzt ------------------------------

  set hass(hass) {
    const languageChanged = this._hass && this._hass.language !== hass.language;
    this._hass = hass;
    if (!this._built) this._build();
    this._menuButton.hass = hass;
    if (!this._unsub) this._subscribe();
    if (languageChanged) this._renderAll();
  }

  set narrow(narrow) {
    this._narrow = narrow;
    if (this._menuButton) this._menuButton.narrow = narrow;
  }

  set panel(panel) {
    this._panel = panel;
  }

  connectedCallback() {
    if (this._hass && !this._unsub) this._subscribe();
  }

  disconnectedCallback() {
    if (this._unsub) {
      this._unsub.then((unsub) => unsub()).catch(() => {});
      this._unsub = null;
    }
  }

  // --- Daten ------------------------------------------------------------------

  _subscribe() {
    this._unsub = this._hass.connection.subscribeMessage(
      (data) => {
        this._data = data;
        this._error = null;
        this._renderAll();
      },
      { type: "grow_tracker/subscribe" }
    );
    this._unsub.catch((err) => {
      this._error = err.message || String(err);
      this._unsub = null;
      this._renderMain();
    });
  }

  _plant(id) {
    return this._data?.plants.find((p) => p.id === id);
  }

  // --- Hilfen -------------------------------------------------------------------

  get _lang() {
    return (this._hass?.language || "en").startsWith("de") ? "de" : "en";
  }

  _t(key, vars = {}) {
    const dict = I18N[this._lang];
    let text = key.split(".").reduce((obj, part) => obj?.[part], dict);
    if (text === undefined) text = key.split(".").reduce((obj, part) => obj?.[part], I18N.en) ?? key;
    return text.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? "");
  }

  _date(iso) {
    if (!iso) return "–";
    const [y, m, d] = iso.slice(0, 10).split("-").map(Number);
    return new Date(y, m - 1, d).toLocaleDateString(this._hass.language, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
    });
  }

  _dateTime(iso) {
    if (!iso) return "–";
    return new Date(iso).toLocaleString(this._hass.language, {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  _phaseChip(phase) {
    return `<span class="chip" style="--chip:${PHASE_COLORS[phase] || "#888"}">${esc(
      this._t(`phases.${phase}`)
    )}</span>`;
  }

  _harvestText(plant) {
    const n = plant.days_to_harvest;
    if (n === null || n === undefined) return "";
    if (n > 0) return this._t("harvest_in", { n });
    if (n === 0) return this._t("harvest_today");
    return this._t("harvest_over", { n: -n });
  }

  _navigate(path) {
    history.pushState(null, "", path);
    window.dispatchEvent(new CustomEvent("location-changed", { detail: { replace: false } }));
  }

  // --- Aufbau -------------------------------------------------------------------

  _build() {
    this._built = true;
    this.shadowRoot.innerHTML = `
      <style>${STYLES}</style>
      <div class="toolbar">
        <span class="menu"></span>
        <div class="title"></div>
        <button class="text-button" id="manage"></button>
      </div>
      <main id="main"></main>
      <div class="overlay hidden" id="overlay">
        <div class="dialog" role="dialog" aria-modal="true">
          <div class="dialog-header">
            <div id="dlg-title"></div>
            <button class="icon-button" id="dlg-close" aria-label="close">✕</button>
          </div>
          <div class="dialog-body">
            <div id="dlg-info"></div>
            <div id="dlg-forms"></div>
          </div>
        </div>
      </div>
    `;
    this._menuButton = document.createElement("ha-menu-button");
    this._menuButton.hass = this._hass;
    this._menuButton.narrow = this._narrow;
    this.shadowRoot.querySelector(".menu").appendChild(this._menuButton);

    this.shadowRoot.getElementById("manage").addEventListener("click", () =>
      this._navigate(INTEGRATION_URL)
    );
    this.shadowRoot.getElementById("dlg-close").addEventListener("click", () => this._closeDialog());
    this.shadowRoot.getElementById("overlay").addEventListener("click", (ev) => {
      if (ev.target.id === "overlay") this._closeDialog();
    });
    this.shadowRoot.getElementById("main").addEventListener("click", (ev) => {
      const row = ev.target.closest("[data-plant]");
      if (row) this._openDialog(row.dataset.plant);
    });
    this.shadowRoot.getElementById("dlg-info").addEventListener("click", (ev) => {
      const link = ev.target.closest("[data-plant]");
      if (link) this._openDialog(link.dataset.plant);
    });
    this.shadowRoot.addEventListener("keydown", (ev) => {
      if (ev.key === "Escape") this._closeDialog();
    });
  }

  _renderAll() {
    if (!this._built) return;
    this.shadowRoot.querySelector(".title").textContent = this._t("title");
    this.shadowRoot.getElementById("manage").textContent = this._t("manage");
    this._renderMain();
    if (this._selectedId) {
      if (this._plant(this._selectedId)) {
        this._renderDialogInfo();
      } else {
        this._closeDialog();
      }
    }
  }

  // --- Übersicht ----------------------------------------------------------------

  _renderMain() {
    const main = this.shadowRoot.getElementById("main");
    if (this._error) {
      main.innerHTML = `<div class="empty error">${esc(this._error)}</div>`;
      return;
    }
    if (!this._data) {
      main.innerHTML = `<div class="empty">…</div>`;
      return;
    }
    if (!this._data.loaded) {
      main.innerHTML = `<div class="empty">${esc(this._t("not_loaded"))}</div>`;
      return;
    }
    if (!this._data.locations.length) {
      main.innerHTML = `<div class="empty">${esc(this._t("no_locations"))}</div>`;
      return;
    }

    const plants = this._data.plants;
    const counts = {};
    for (const p of plants) counts[p.phase] = (counts[p.phase] || 0) + 1;
    const summary = PHASES.filter((ph) => counts[ph])
      .map((ph) => `<span class="summary-item">${this._phaseChip(ph)}<b>${counts[ph]}</b></span>`)
      .join("");

    const cards = this._data.locations.map((loc) =>
      this._locationCard(
        loc.name,
        this._t(`location_types.${loc.type}`),
        plants.filter((p) => p.location_id === loc.id)
      )
    );
    const known = new Set(this._data.locations.map((l) => l.id));
    const homeless = plants.filter((p) => !known.has(p.location_id));
    if (homeless.length) cards.push(this._locationCard(this._t("without_location"), "", homeless));

    main.innerHTML = `
      ${summary ? `<div class="summary">${summary}</div>` : ""}
      <div class="grid">${cards.join("")}</div>
    `;
  }

  _locationCard(name, typeLabel, plants) {
    const order = (p) => PHASES.indexOf(p.phase);
    const rows = plants
      .slice()
      .sort((a, b) => order(a) - order(b) || a.name.localeCompare(b.name))
      .map((p) => this._plantRow(p))
      .join("");
    return `
      <section class="card">
        <header>
          <div>
            <div class="card-title">${esc(name)}</div>
            ${typeLabel ? `<div class="secondary">${esc(typeLabel)}</div>` : ""}
          </div>
          <div class="count">${plants.length} ${esc(this._t(plants.length === 1 ? "plant_one" : "plants"))}</div>
        </header>
        ${rows || `<div class="secondary pad">${esc(this._t("no_plants"))}</div>`}
      </section>
    `;
  }

  _plantRow(p) {
    let extra = "";
    if (p.phase === "flowering" && p.flower_weeks) {
      const pct = Math.min(100, Math.round((p.days_in_phase / (p.flower_weeks * 7)) * 100));
      extra = `
        <div class="progress"><div style="width:${pct}%"></div></div>
        <div class="secondary small">${esc(this._harvestText(p))}</div>`;
    } else if (p.phase === "mother" && p.cuttings_taken) {
      extra = `<div class="secondary small">✂ ${esc(this._t("cuttings", { n: p.cuttings_taken }))}</div>`;
    }
    return `
      <button class="plant" data-plant="${esc(p.id)}">
        <span class="dot" style="background:${PHASE_COLORS[p.phase]}"></span>
        <span class="plant-main">
          <span class="plant-name">${esc(p.name)}</span>
          <span class="secondary small">${esc(p.strain || "")}</span>
          ${extra}
        </span>
        <span class="plant-side">
          ${this._phaseChip(p.phase)}
          <span class="secondary small">${esc(this._t("week"))} ${p.week_in_phase} · ${esc(
      this._t("day")
    )} ${p.days_total}</span>
        </span>
      </button>
    `;
  }

  // --- Detail-Dialog --------------------------------------------------------------

  _openDialog(id) {
    this._selectedId = id;
    this.shadowRoot.getElementById("overlay").classList.remove("hidden");
    this._renderDialogInfo();
    this._renderDialogForms();
    this.shadowRoot.querySelector(".dialog-body").scrollTop = 0;
  }

  _closeDialog() {
    this._selectedId = null;
    this.shadowRoot.getElementById("overlay").classList.add("hidden");
  }

  _renderDialogInfo() {
    const p = this._plant(this._selectedId);
    if (!p) return;
    this.shadowRoot.getElementById("dlg-title").innerHTML = `
      <div class="dlg-name">${esc(p.name)}</div>
      <div class="secondary">${[p.strain, p.location_name].filter(Boolean).map(esc).join(" · ")}</div>`;

    const origin =
      p.origin === "cutting"
        ? p.mother_id && this._plant(p.mother_id)
          ? `<a class="link" data-plant="${esc(p.mother_id)}">${esc(
              this._t("cutting_of", { name: p.mother_name })
            )}</a>`
          : esc(this._t("cutting_of", { name: p.mother_name || "?" }))
        : esc(this._t("seed"));

    const stats = [
      [this._t("total"), `${p.days_total} ${this._t("days")}`],
      [this._t("in_phase"), `${p.days_in_phase} ${this._t("days")} (${this._t("week")} ${p.week_in_phase})`],
      [this._t("at_location"), `${p.days_at_location} ${this._t("days")}`],
    ];
    if (p.expected_harvest) {
      stats.push([this._t("expected_harvest"), `${this._date(p.expected_harvest)} – ${this._harvestText(p)}`]);
    }

    const phaseHistory = p.history
      .slice()
      .reverse()
      .map(
        (h) => `<li>${this._phaseChip(h.phase)}<span>${esc(this._t("since"))} ${this._date(h.start)}</span></li>`
      )
      .join("");
    const locationHistory = p.location_history
      .slice()
      .reverse()
      .map((h) => `<li><b>${esc(h.location)}</b><span>${esc(this._t("since"))} ${this._date(h.start)}</span></li>`)
      .join("");
    const notes = p.notes.length
      ? p.notes
          .slice()
          .reverse()
          .map(
            (n) => `
          <li class="note">
            <div class="secondary small">${this._dateTime(n.date)} · ${esc(this._t(`phases.${n.phase}`))} · ${esc(
              this._t("day")
            )} ${n.day}</div>
            <div>${esc(n.text)}</div>
          </li>`
          )
          .join("")
      : `<li class="secondary">${esc(this._t("no_notes"))}</li>`;

    let cuttings = "";
    if (p.cuttings_taken || p.children.length) {
      const log = p.cuttings_log
        .slice()
        .reverse()
        .map((c) => `<li><b>${esc(this._t("cuttings", { n: c.count }))}</b><span>${this._date(c.date)}</span></li>`)
        .join("");
      const children = p.children
        .map((id) => this._plant(id))
        .filter(Boolean)
        .map(
          (c) =>
            `<li><a class="link" data-plant="${esc(c.id)}">${esc(c.name)}</a>${this._phaseChip(c.phase)}</li>`
        )
        .join("");
      cuttings = `
        <h3>${esc(this._t("cuttings_log"))} (${p.cuttings_taken})</h3>
        <ul class="list">${log}</ul>
        ${children ? `<h3>${esc(this._t("tracked_cuttings"))}</h3><ul class="list">${children}</ul>` : ""}`;
    }

    this.shadowRoot.getElementById("dlg-info").innerHTML = `
      <div class="badges">${this._phaseChip(p.phase)}<span class="secondary">${origin}</span></div>
      <dl class="stats">${stats.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>
      <div class="columns">
        <div><h3>${esc(this._t("phase_history"))}</h3><ul class="list">${phaseHistory}</ul></div>
        <div><h3>${esc(this._t("location_history"))}</h3><ul class="list">${locationHistory}</ul></div>
      </div>
      ${cuttings}
      <h3>${esc(this._t("notes"))}</h3>
      <ul class="list notes">${notes}</ul>
    `;
  }

  _renderDialogForms() {
    const p = this._plant(this._selectedId);
    if (!p) return;
    const today = this._data.today;
    const phaseOptions = PHASES.map(
      (ph) => `<option value="${ph}" ${ph === p.phase ? "selected" : ""}>${esc(this._t(`phases.${ph}`))}</option>`
    ).join("");
    const locationOptions = (selected) =>
      this._data.locations
        .map(
          (l) =>
            `<option value="${esc(l.name)}" ${l.id === selected ? "selected" : ""}>${esc(l.name)}</option>`
        )
        .join("");

    const cuttingsForm =
      p.phase === "mother"
        ? `
      <form data-action="take_cuttings">
        <h3>✂ ${esc(this._t("take_cuttings"))}</h3>
        <div class="row">
          <label>${esc(this._t("count"))}<input type="number" name="count" min="1" max="100" value="1" required></label>
          <label>${esc(this._t("date"))}<input type="date" name="date" value="${today}" max="${today}"></label>
          <label>${esc(this._t("target_location"))}
            <select name="location"><option value="">${esc(this._t("automatic"))}</option>${locationOptions(null)}</select>
          </label>
        </div>
        <label class="check"><input type="checkbox" name="create_plants" checked> ${esc(this._t("create_plants"))}</label>
        <button class="primary" type="submit">${esc(this._t("save"))}</button>
      </form>`
        : "";

    this.shadowRoot.getElementById("dlg-forms").innerHTML = `
      <div class="forms">
        <form data-action="set_phase">
          <h3>${esc(this._t("change_phase"))}</h3>
          <div class="row">
            <select name="phase">${phaseOptions}</select>
            <input type="date" name="date" value="${today}" max="${today}">
          </div>
          <button class="primary" type="submit">${esc(this._t("save"))}</button>
        </form>
        <form data-action="set_location">
          <h3>${esc(this._t("change_location"))}</h3>
          <div class="row">
            <select name="location">${locationOptions(p.location_id)}</select>
            <input type="date" name="date" value="${today}" max="${today}">
          </div>
          <button class="primary" type="submit">${esc(this._t("save"))}</button>
        </form>
        <form data-action="add_note" class="wide">
          <h3>${esc(this._t("add_note"))}</h3>
          <textarea name="note" rows="3" required placeholder="${esc(this._t("note_placeholder"))}"></textarea>
          <button class="primary" type="submit">${esc(this._t("save"))}</button>
        </form>
        ${cuttingsForm}
      </div>
      <div class="status" id="status" role="status"></div>
      <div class="footer">
        <button class="text-button" id="edit">${esc(this._t("edit"))}</button>
        ${this._hass.user?.is_admin ? `<div id="delete-area"></div>` : ""}
      </div>
    `;

    const forms = this.shadowRoot.getElementById("dlg-forms");
    forms.querySelectorAll("form").forEach((form) =>
      form.addEventListener("submit", (ev) => {
        ev.preventDefault();
        this._submit(form);
      })
    );
    forms.querySelector("#edit").addEventListener("click", () => this._navigate(INTEGRATION_URL));
    this._renderDeleteArea(false);
  }

  _renderDeleteArea(confirming) {
    const area = this.shadowRoot.getElementById("delete-area");
    const p = this._plant(this._selectedId);
    if (!area || !p) return;

    if (!confirming) {
      area.innerHTML = `<button class="text-button danger-text" id="delete">${esc(this._t("delete_plant"))}</button>`;
      area.querySelector("#delete").addEventListener("click", () => this._renderDeleteArea(true));
      return;
    }

    const childNote = p.children.length
      ? `<p>${esc(this._t("delete_children_note", { n: p.children.length }))}</p>`
      : "";
    area.innerHTML = `
      <div class="confirm" role="alertdialog">
        <p><b>${esc(this._t("delete_confirm", { name: p.name }))}</b></p>
        <p>${esc(this._t("delete_warning"))}</p>
        ${childNote}
        <div class="confirm-buttons">
          <button class="text-button" id="delete-cancel">${esc(this._t("cancel"))}</button>
          <button class="danger" id="delete-final">${esc(this._t("delete_final"))}</button>
        </div>
      </div>`;
    area.querySelector("#delete-cancel").addEventListener("click", () => this._renderDeleteArea(false));
    area.querySelector("#delete-final").addEventListener("click", () => this._deletePlant(p));
    area.querySelector("#delete-cancel").focus();
  }

  async _deletePlant(plant) {
    const status = this.shadowRoot.getElementById("status");
    const area = this.shadowRoot.getElementById("delete-area");
    area.querySelectorAll("button").forEach((b) => (b.disabled = true));
    try {
      await this._hass.callWS({
        type: "config_entries/subentries/delete",
        entry_id: this._data.entry_id,
        subentry_id: plant.id,
      });
      this._closeDialog();
    } catch (err) {
      status.className = "status error";
      status.textContent = err?.message || String(err);
      this._renderDeleteArea(false);
    }
  }

  async _submit(form) {
    const p = this._plant(this._selectedId);
    if (!p || !p.phase_entity_id) return;
    const action = form.dataset.action;
    const fd = new FormData(form);
    const data = { entity_id: p.phase_entity_id };

    if (action === "set_phase") {
      data.phase = fd.get("phase");
      if (fd.get("date")) data.date = fd.get("date");
    } else if (action === "set_location") {
      data.location = fd.get("location");
      if (fd.get("date")) data.date = fd.get("date");
    } else if (action === "add_note") {
      data.note = String(fd.get("note")).trim();
      if (!data.note) return;
    } else if (action === "take_cuttings") {
      data.count = Number(fd.get("count"));
      data.create_plants = fd.get("create_plants") === "on";
      if (fd.get("date")) data.date = fd.get("date");
      if (fd.get("location")) data.location = fd.get("location");
    }

    const status = this.shadowRoot.getElementById("status");
    const buttons = form.querySelectorAll("button");
    buttons.forEach((b) => (b.disabled = true));
    status.className = "status";
    status.textContent = "";
    try {
      await this._hass.callService("grow_tracker", action, data);
      // Formulare neu aufbauen (z. B. erscheint "Stecklinge schneiden" bei Mutterpflanzen)
      this._renderDialogForms();
      const fresh = this.shadowRoot.getElementById("status");
      fresh.className = "status ok";
      fresh.textContent = `✓ ${this._t("saved")}`;
    } catch (err) {
      status.className = "status error";
      status.textContent = err?.message || String(err);
      buttons.forEach((b) => (b.disabled = false));
    }
  }
}

const STYLES = `
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
  }
  .toolbar {
    display: flex;
    align-items: center;
    gap: 4px;
    height: var(--header-height, 56px);
    padding: 0 12px 0 4px;
    background: var(--app-header-background-color, var(--primary-color));
    color: var(--app-header-text-color, #fff);
    border-bottom: var(--app-header-border-bottom, none);
    position: sticky;
    top: 0;
    z-index: 2;
  }
  .title { flex: 1; font-size: 20px; margin-left: 8px; }
  main { padding: 16px; max-width: 1400px; margin: 0 auto; box-sizing: border-box; }
  .empty { padding: 48px 16px; text-align: center; color: var(--secondary-text-color); }
  .error { color: var(--error-color, #db4437); }
  .summary { display: flex; flex-wrap: wrap; gap: 12px; margin-bottom: 16px; }
  .summary-item { display: inline-flex; align-items: center; gap: 6px; }
  .grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 16px;
    align-items: start;
  }
  .card {
    background: var(--ha-card-background, var(--card-background-color, #fff));
    border-radius: var(--ha-card-border-radius, 12px);
    border: 1px solid var(--divider-color);
    box-shadow: var(--ha-card-box-shadow, none);
    overflow: hidden;
  }
  .card header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 16px 16px 8px;
  }
  .card-title { font-size: 18px; font-weight: 500; }
  .count { color: var(--secondary-text-color); font-size: 14px; white-space: nowrap; }
  .secondary { color: var(--secondary-text-color); }
  .small { font-size: 12px; }
  .pad { padding: 8px 16px 16px; }
  .plant {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    padding: 10px 16px;
    border: none;
    border-top: 1px solid var(--divider-color);
    background: none;
    color: inherit;
    font: inherit;
    text-align: left;
    cursor: pointer;
  }
  .plant:hover, .plant:focus-visible { background: var(--secondary-background-color); outline: none; }
  .dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
  .plant-main { flex: 1; display: flex; flex-direction: column; gap: 2px; min-width: 0; }
  .plant-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .plant-side { display: flex; flex-direction: column; align-items: flex-end; gap: 4px; flex: none; }
  .chip {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 500;
    color: var(--chip);
    background: color-mix(in srgb, var(--chip) 18%, transparent);
    white-space: nowrap;
  }
  .progress {
    height: 4px;
    border-radius: 2px;
    background: var(--divider-color);
    margin: 4px 0 2px;
    overflow: hidden;
  }
  .progress div { height: 100%; background: ${PHASE_COLORS.flowering}; }
  button { font: inherit; }
  .text-button {
    background: none;
    border: none;
    color: inherit;
    padding: 8px 12px;
    border-radius: 4px;
    cursor: pointer;
    text-transform: uppercase;
    font-size: 14px;
    font-weight: 500;
    letter-spacing: 0.05em;
  }
  .text-button:hover { background: rgba(127, 127, 127, 0.15); }
  .dialog .text-button { color: var(--primary-color); margin-top: 8px; }
  .icon-button {
    background: none;
    border: none;
    color: inherit;
    font-size: 18px;
    width: 40px;
    height: 40px;
    border-radius: 50%;
    cursor: pointer;
  }
  .icon-button:hover { background: rgba(127, 127, 127, 0.15); }
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 10;
    padding: 16px;
  }
  .overlay.hidden { display: none; }
  .dialog {
    background: var(--card-background-color, #fff);
    color: var(--primary-text-color);
    border-radius: var(--ha-dialog-border-radius, 24px);
    width: min(860px, 100%);
    max-height: calc(100vh - 32px);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  .dialog-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 20px 16px 12px 24px;
    border-bottom: 1px solid var(--divider-color);
  }
  .dlg-name { font-size: 22px; }
  .dialog-body { overflow-y: auto; padding: 16px 24px 24px; }
  .badges { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 12px;
    margin: 16px 0;
  }
  .stats div { background: var(--secondary-background-color); border-radius: 8px; padding: 10px 12px; }
  .stats dt { font-size: 12px; color: var(--secondary-text-color); }
  .stats dd { margin: 2px 0 0; font-weight: 500; }
  h3 { font-size: 14px; font-weight: 500; margin: 20px 0 8px; color: var(--secondary-text-color); text-transform: uppercase; letter-spacing: 0.05em; }
  .columns { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 0 24px; }
  .list { list-style: none; margin: 0; padding: 0; }
  .list li {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 6px 0;
    border-bottom: 1px solid var(--divider-color);
  }
  .list li.note { display: block; }
  .notes { max-height: 280px; overflow-y: auto; }
  .link { color: var(--primary-color); cursor: pointer; text-decoration: underline; }
  .forms {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 0 24px;
    border-top: 1px solid var(--divider-color);
    margin-top: 24px;
  }
  .forms .wide { grid-column: 1 / -1; }
  form { display: flex; flex-direction: column; gap: 8px; }
  .row { display: flex; gap: 8px; flex-wrap: wrap; }
  .row > * { flex: 1; min-width: 120px; }
  label { display: flex; flex-direction: column; gap: 4px; font-size: 12px; color: var(--secondary-text-color); }
  label.check { flex-direction: row; align-items: center; font-size: 14px; color: var(--primary-text-color); }
  select, input, textarea {
    font: inherit;
    font-size: 14px;
    color: var(--primary-text-color);
    background: var(--input-fill-color, var(--secondary-background-color));
    border: 1px solid var(--divider-color);
    border-radius: 6px;
    padding: 8px;
    box-sizing: border-box;
  }
  label.check input { width: auto; }
  textarea { resize: vertical; width: 100%; }
  .primary {
    align-self: flex-start;
    background: var(--primary-color);
    color: var(--text-primary-color, #fff);
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    cursor: pointer;
    font-weight: 500;
  }
  .primary:disabled { opacity: 0.5; cursor: default; }
  .footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
  }
  .dialog .footer .text-button { margin-top: 0; }
  .dialog .danger-text { color: var(--error-color, #db4437); }
  .confirm {
    border: 1px solid var(--error-color, #db4437);
    border-radius: 12px;
    padding: 12px 16px;
    max-width: 420px;
    background: color-mix(in srgb, var(--error-color, #db4437) 8%, transparent);
  }
  .confirm p { margin: 0 0 8px; font-size: 14px; }
  .confirm-buttons { display: flex; justify-content: flex-end; gap: 8px; margin-top: 4px; }
  .danger {
    background: var(--error-color, #db4437);
    color: #fff;
    border: none;
    border-radius: 18px;
    padding: 8px 20px;
    cursor: pointer;
    font-weight: 500;
  }
  .danger:disabled { opacity: 0.5; cursor: default; }
  .status { min-height: 20px; margin-top: 12px; font-size: 14px; }
  .status.ok { color: var(--success-color, #43a047); }
  .status.error { color: var(--error-color, #db4437); }
  @media (max-width: 600px) {
    main { padding: 8px; }
    .grid { grid-template-columns: 1fr; }
    .overlay { padding: 0; }
    .dialog { border-radius: 0; max-height: 100vh; height: 100vh; }
    .dialog-body { padding: 12px 16px 24px; }
  }
`;

if (!customElements.get("grow-tracker-panel")) {
  customElements.define("grow-tracker-panel", GrowTrackerPanel);
}
