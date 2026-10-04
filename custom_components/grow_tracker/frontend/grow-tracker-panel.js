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
    no_plants_yet: "No plants yet. Add plants on the integration page (Manage).",
    hidden_location_one: "1 empty location hidden",
    hidden_locations: "{n} empty locations hidden",
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
    cuttings_log: "Cuttings log",
    tracked_cuttings: "Cuttings",
    cutting_one: "1 cutting",
    no_cuttings: "No cuttings at the moment",
    edit_log: "Edit",
    expand: "Show cuttings",
    collapse: "Hide cuttings",
    phenotype: "Phenotype",
    breeder: "Breeder/Cutter",
    note_time: "Time",
    edit_note: "Edit note",
    delete: "Delete",
    delete_note_confirm: "Really delete?",
    note_invalid: "The note needs a text and a time that is not in the future.",
    log_empty: "No entries yet",
    add_entry: "Add entry",
    remove_entry: "Remove entry",
    log_invalid: "Every entry needs a date (not in the future) and a count of at least 1.",
    history_invalid: "At least one entry is needed, each with a date that is not in the future.",
    phase: "Phase",
    start: "Start",
    no_notes: "No notes yet",
    edit: "Edit plant",
    close: "Close",
    saved: "Saved",
    delete_plant: "Delete plant",
    delete_confirm: "Really delete “{name}”?",
    delete_warning: "Phase and location history, notes and the cuttings log will be lost. This cannot be undone.",
    delete_children_note: "Its {n} tracked cuttings are kept.",
    delete_mother_note: "The cutting is also removed from “{name}”.",
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
    no_plants_yet: "Noch keine Pflanzen. Pflanzen legst du auf der Integrationsseite an (Verwalten).",
    hidden_location_one: "1 leerer Standort ausgeblendet",
    hidden_locations: "{n} leere Standorte ausgeblendet",
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
    cuttings_log: "Schnitt-Protokoll",
    tracked_cuttings: "Stecklinge",
    cutting_one: "1 Steckling",
    no_cuttings: "Aktuell keine Stecklinge",
    edit_log: "Bearbeiten",
    expand: "Stecklinge anzeigen",
    collapse: "Stecklinge ausblenden",
    phenotype: "Phänotyp",
    breeder: "Breeder/Cutter",
    note_time: "Zeitpunkt",
    edit_note: "Notiz bearbeiten",
    delete: "Löschen",
    delete_note_confirm: "Wirklich löschen?",
    note_invalid: "Die Notiz braucht einen Text und einen Zeitpunkt, der nicht in der Zukunft liegt.",
    log_empty: "Noch keine Einträge",
    add_entry: "Eintrag hinzufügen",
    remove_entry: "Eintrag entfernen",
    log_invalid: "Jeder Eintrag braucht ein Datum (nicht in der Zukunft) und eine Anzahl von mindestens 1.",
    history_invalid: "Mindestens ein Eintrag ist nötig, jeder mit einem Datum, das nicht in der Zukunft liegt.",
    phase: "Phase",
    start: "Beginn",
    no_notes: "Noch keine Notizen",
    edit: "Pflanze bearbeiten",
    close: "Schließen",
    saved: "Gespeichert",
    delete_plant: "Pflanze löschen",
    delete_confirm: "„{name}“ wirklich löschen?",
    delete_warning: "Phasen- und Standort-Historie, Notizen und das Stecklings-Protokoll gehen verloren. Das lässt sich nicht rückgängig machen.",
    delete_children_note: "Die {n} erfassten Stecklinge bleiben erhalten.",
    delete_mother_note: "Der Steckling wird auch bei „{name}“ ausgetragen.",
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
    // Aufgeklappte Stecklings-Gruppen (bleiben bei Live-Updates offen)
    this._expanded = new Set();
  }

  // --- Eigenschaften, die Home Assistant setzt ------------------------------

  set hass(hass) {
    const languageChanged = this._hass && this._hass.language !== hass.language;
    this._hass = hass;
    if (!this._built) this._build();
    this._menuButton.hass = hass;
    // Native Auswahllisten, Datumsfelder und Kalender passend zum HA-Theme zeichnen
    this.style.colorScheme = hass.themes?.darkMode ? "dark" : "light";
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
      const group = ev.target.closest("[data-group]");
      if (group) {
        const key = group.dataset.group;
        if (this._expanded.has(key)) this._expanded.delete(key);
        else this._expanded.add(key);
        this._renderMain();
        return;
      }
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

    // Nur Standorte anzeigen, an denen gerade Pflanzen stehen
    const occupied = this._data.locations
      .map((loc) => ({ loc, plants: plants.filter((p) => p.location_id === loc.id) }))
      .filter(({ plants: here }) => here.length);
    const hidden = this._data.locations.length - occupied.length;

    const cards = occupied.map(({ loc, plants: here }) =>
      this._locationCard(loc.name, this._t(`location_types.${loc.type}`), here, loc.id)
    );
    const known = new Set(this._data.locations.map((l) => l.id));
    const homeless = plants.filter((p) => !known.has(p.location_id));
    if (homeless.length) cards.push(this._locationCard(this._t("without_location"), "", homeless));

    if (!cards.length) {
      main.innerHTML = `<div class="empty">${esc(this._t("no_plants_yet"))}</div>`;
      return;
    }

    main.innerHTML = `
      ${summary ? `<div class="summary">${summary}</div>` : ""}
      <div class="grid">${cards.join("")}</div>
      ${
        hidden
          ? `<div class="hidden-note secondary small">${esc(
              this._t(hidden === 1 ? "hidden_location_one" : "hidden_locations", { n: hidden })
            )}</div>`
          : ""
      }
    `;
  }

  _locationCard(name, typeLabel, plants, cardKey = "") {
    const order = (p) => PHASES.indexOf(p.phase);
    const byName = (a, b) => a.localeCompare(b, undefined, { numeric: true });

    // Stecklinge derselben Mutter in derselben Phase zu einer Gruppe zusammenfassen
    const groups = new Map();
    const items = [];
    for (const p of plants) {
      const mother = p.mother_id || p.mother_name;
      if (p.origin === "cutting" && mother) {
        const key = `${cardKey}|${mother}|${p.phase}`;
        if (!groups.has(key)) groups.set(key, []);
        groups.get(key).push(p);
      } else {
        items.push({ phase: order(p), name: p.name, html: this._plantRow(p) });
      }
    }
    for (const [key, members] of groups) {
      const first = members[0];
      items.push(
        members.length === 1
          ? { phase: order(first), name: first.name, html: this._plantRow(first) }
          : { phase: order(first), name: this._groupTitle(first), html: this._groupRow(key, members) }
      );
    }
    const rows = items
      .sort((a, b) => a.phase - b.phase || byName(a.name, b.name))
      .map((item) => item.html)
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

  _groupTitle(cutting) {
    // Sorte der Mutter (aktueller Name, sonst der beim Steckling hinterlegte)
    return this._plant(cutting.mother_id)?.name || cutting.mother_name || cutting.name;
  }

  _groupRow(key, members) {
    const first = members[0];
    const expanded = this._expanded.has(key);
    const range = (values) => {
      const min = Math.min(...values);
      const max = Math.max(...values);
      return min === max ? `${min}` : `${min}–${max}`;
    };

    let extra = "";
    if (first.phase === "flowering") {
      // Fortschritt der am weitesten entwickelten, Erntetext der frühesten Pflanze
      const pct = Math.max(
        ...members.map((m) => (m.flower_weeks ? Math.min(100, Math.round((m.days_in_phase / (m.flower_weeks * 7)) * 100)) : 0))
      );
      const soonest = members
        .filter((m) => m.days_to_harvest !== null && m.days_to_harvest !== undefined)
        .sort((a, b) => a.days_to_harvest - b.days_to_harvest)[0];
      extra = `
        <div class="progress"><div style="width:${pct}%"></div></div>
        ${soonest ? `<div class="secondary small">${esc(this._harvestText(soonest))}</div>` : ""}`;
    }

    const details = [this._t("cuttings", { n: members.length }), first.phenotype, first.strain]
      .filter(Boolean)
      .map(esc)
      .join(" · ");
    const memberRows = expanded
      ? `<div class="group-members">${members
          .slice()
          .sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }))
          .map((m) => this._plantRow(m))
          .join("")}</div>`
      : "";

    return `
      <div class="group">
        <button class="plant group-head" data-group="${esc(key)}" aria-expanded="${expanded}"
          title="${esc(this._t(expanded ? "collapse" : "expand"))}">
          <span class="dot" style="background:${PHASE_COLORS[first.phase]}"></span>
          <span class="plant-main">
            <span class="plant-name">${esc(this._groupTitle(first))} <span class="count-badge">✂ ×${members.length}</span></span>
            <span class="secondary small">${details}</span>
            ${extra}
          </span>
          <span class="plant-side">
            ${this._phaseChip(first.phase)}
            <span class="secondary small">${esc(this._t("week"))} ${range(members.map((m) => m.week_in_phase))} · ${esc(
      this._t("day")
    )} ${range(members.map((m) => m.days_total))}</span>
          </span>
          <span class="chevron" aria-hidden="true">${expanded ? "▾" : "▸"}</span>
        </button>
        ${memberRows}
      </div>`;
  }

  _plantRow(p) {
    let extra = "";
    if (p.phase === "flowering" && p.flower_weeks) {
      const pct = Math.min(100, Math.round((p.days_in_phase / (p.flower_weeks * 7)) * 100));
      extra = `
        <div class="progress"><div style="width:${pct}%"></div></div>
        <div class="secondary small">${esc(this._harvestText(p))}</div>`;
    } else if (p.phase === "mother" && p.cuttings_count) {
      extra = `<div class="secondary small">✂ ${esc(
        this._t(p.cuttings_count === 1 ? "cutting_one" : "cuttings", { n: p.cuttings_count })
      )}</div>`;
    }
    return `
      <button class="plant" data-plant="${esc(p.id)}">
        <span class="dot" style="background:${PHASE_COLORS[p.phase]}"></span>
        <span class="plant-main">
          <span class="plant-name">${esc(p.name)}</span>
          <span class="secondary small">${[p.phenotype, p.strain].filter(Boolean).map(esc).join(" · ")}</span>
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
    this._edit = null;
    this.shadowRoot.getElementById("overlay").classList.remove("hidden");
    this._renderDialogInfo();
    this._renderDialogForms();
    this.shadowRoot.querySelector(".dialog-body").scrollTop = 0;
  }

  _closeDialog() {
    this._selectedId = null;
    this._edit = null;
    this.shadowRoot.getElementById("overlay").classList.add("hidden");
  }

  _renderDialogInfo() {
    const p = this._plant(this._selectedId);
    if (!p) return;
    // Während eine Liste bearbeitet wird, keine Live-Updates (Eingaben bleiben erhalten)
    if (this._edit) return;
    this.shadowRoot.getElementById("dlg-title").innerHTML = `
      <div class="dlg-name">${esc(p.name)}</div>
      <div class="secondary">${[
        p.phenotype && `${this._t("phenotype")}: ${p.phenotype}`,
        p.strain && `${this._t("breeder")}: ${p.strain}`,
        p.location_name,
      ]
        .filter(Boolean)
        .map(esc)
        .join(" · ")}</div>`;

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

    let cuttings = "";
    if (p.phase === "mother" || p.cuttings_log.length || p.children.length) {
      const children = p.children
        .map((id) => this._plant(id))
        .filter(Boolean)
        .map(
          (c) =>
            `<li><a class="link" data-plant="${esc(c.id)}">${esc(c.name)}</a>${this._phaseChip(c.phase)}</li>`
        )
        .join("");
      // Zuerst die aktuell vorhandenen Stecklinge, darunter der Schnitt-Verlauf
      cuttings = `
        <h3>${esc(this._t("tracked_cuttings"))} (${p.cuttings_count})</h3>
        <ul class="list">${children || `<li class="secondary">${esc(this._t("no_cuttings"))}</li>`}</ul>
        ${this._editableSection("log", this._t("cuttings_log"))}`;
    }

    this.shadowRoot.getElementById("dlg-info").innerHTML = `
      <div class="badges">${this._phaseChip(p.phase)}<span class="secondary">${origin}</span></div>
      <dl class="stats">${stats.map(([k, v]) => `<div><dt>${esc(k)}</dt><dd>${esc(v)}</dd></div>`).join("")}</dl>
      <div class="columns">
        <div>${this._editableSection("phase", this._t("phase_history"))}</div>
        <div>${this._editableSection("location", this._t("location_history"))}</div>
      </div>
      ${cuttings}
      <h3>${esc(this._t("notes"))}</h3>
      <ul class="list notes" id="notes-list"></ul>
    `;
    this._renderEditAreas();
    this._renderNotes();
  }

  // --- Notizen (Anzeige / Bearbeiten) ---------------------------------------------

  _localInput(value) {
    // "YYYY-MM-DDTHH:MM" in lokaler Zeit für <input type="datetime-local">
    const d = value instanceof Date ? value : new Date(value);
    const pad = (n) => String(n).padStart(2, "0");
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(
      d.getMinutes()
    )}`;
  }

  _renderNotes() {
    const list = this.shadowRoot.getElementById("notes-list");
    const p = this._plant(this._selectedId);
    if (!list || !p) return;
    if (!p.notes.length) {
      list.innerHTML = `<li class="secondary">${esc(this._t("no_notes"))}</li>`;
      return;
    }

    const editingId = this._edit?.kind === "note" ? this._edit.id : null;
    const now = this._localInput(new Date());
    list.innerHTML = p.notes
      .slice()
      .reverse()
      .map((n) => {
        if (n.id === editingId) {
          return `
          <li class="note editing">
            <form class="note-form" novalidate>
              <label>${esc(this._t("note_time"))}
                <input type="datetime-local" name="date" value="${this._localInput(n.date)}" max="${now}">
              </label>
              <textarea name="text" rows="3" aria-label="${esc(this._t("notes"))}">${esc(n.text)}</textarea>
              <div class="status" data-status role="status"></div>
              <div class="note-buttons">
                <button type="button" class="text-button danger-text" data-delete>${esc(this._t("delete"))}</button>
                <span class="spacer"></span>
                <button type="button" class="text-button" data-cancel>${esc(this._t("cancel"))}</button>
                <button type="submit" class="primary">${esc(this._t("save"))}</button>
              </div>
            </form>
          </li>`;
        }
        const location = n.location ? ` · ${esc(n.location)}` : "";
        return `
          <li class="note">
            <div class="note-head">
              <div class="secondary small">${this._dateTime(n.date)} · ${esc(this._t(`phases.${n.phase}`))} · ${esc(
          this._t("day")
        )} ${n.day}${location}</div>
              <button class="icon-button small-icon" data-edit-note="${esc(n.id)}" ${this._edit ? "hidden" : ""}
                aria-label="${esc(this._t("edit_note"))}" title="${esc(this._t("edit_note"))}">✎</button>
            </div>
            <div class="note-text">${esc(n.text)}</div>
          </li>`;
      })
      .join("");

    list.querySelectorAll("[data-edit-note]").forEach((btn) =>
      btn.addEventListener("click", () => {
        this._edit = { kind: "note", id: btn.dataset.editNote };
        this._renderEditAreas();
        this._renderNotes();
        list.querySelector("textarea")?.focus();
      })
    );

    const form = list.querySelector(".note-form");
    if (!form) return;
    const status = form.querySelector("[data-status]");
    const showError = (err) => {
      status.className = "status error";
      status.textContent = err?.message || String(err);
      form.querySelectorAll("button").forEach((b) => (b.disabled = false));
    };
    form.querySelector("[data-cancel]").addEventListener("click", () => {
      this._edit = null;
      this._renderDialogInfo();
    });
    const deleteButton = form.querySelector("[data-delete]");
    deleteButton.addEventListener("click", async () => {
      // Zweistufig: erster Klick fragt nach, zweiter löscht
      if (!deleteButton.dataset.armed) {
        deleteButton.dataset.armed = "1";
        deleteButton.textContent = this._t("delete_note_confirm");
        return;
      }
      form.querySelectorAll("button").forEach((b) => (b.disabled = true));
      try {
        await this._hass.callWS({ type: "grow_tracker/delete_note", plant_id: p.id, note_id: editingId });
        this._edit = null;
        this._renderDialogInfo();
      } catch (err) {
        showError(err);
      }
    });
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const text = form.querySelector("textarea").value.trim();
      const date = form.querySelector('input[name="date"]').value;
      if (!text || !date || date > this._localInput(new Date())) {
        status.className = "status error";
        status.textContent = this._t("note_invalid");
        return;
      }
      form.querySelectorAll("button").forEach((b) => (b.disabled = true));
      try {
        await this._hass.callWS({ type: "grow_tracker/update_note", plant_id: p.id, note_id: editingId, text, date });
        this._edit = null;
        this._renderDialogInfo();
      } catch (err) {
        showError(err);
      }
    });
  }

  // --- Bearbeitbare Listen (Phasen, Standorte, Schnitt-Protokoll) -----------------

  _editableSection(kind, title) {
    return `
      <div class="section-head">
        <h3>${esc(title)}</h3>
        <button class="text-button small-button" id="edit-btn-${kind}">${esc(this._t("edit_log"))}</button>
      </div>
      <div id="edit-area-${kind}"></div>`;
  }

  _editors() {
    const today = this._data.today;
    const since = esc(this._t("since"));
    const last = (rows, fallback) => (rows.length ? rows[rows.length - 1].value : fallback);
    const dateColumn = { name: "date", type: "date", label: this._t("start") };
    const locationOptions = this._data.locations.map((l) => ({ value: l.id, label: l.name }));
    return {
      phase: {
        grid: "minmax(0, 1fr) minmax(0, 1fr) 40px",
        minRows: 1,
        invalid: "history_invalid",
        columns: [
          {
            name: "value",
            type: "select",
            label: this._t("phase"),
            options: PHASES.map((ph) => ({ value: ph, label: this._t(`phases.${ph}`) })),
          },
          dateColumn,
        ],
        load: (p) => p.history.map((h) => ({ value: h.phase, date: h.start })),
        newRow: (rows) => ({ value: last(rows, PHASES[0]), date: today }),
        view: (p) =>
          p.history
            .slice()
            .reverse()
            .map((h) => `<li>${this._phaseChip(h.phase)}<span>${since} ${this._date(h.start)}</span></li>`)
            .join(""),
        message: (p, rows) => ({
          type: "grow_tracker/set_history",
          plant_id: p.id,
          kind: "phase",
          history: rows.map((r) => ({ value: r.value, start: r.date })),
        }),
      },
      location: {
        grid: "minmax(0, 1fr) minmax(0, 1fr) 40px",
        minRows: 1,
        invalid: "history_invalid",
        columns: [
          { name: "value", type: "select", label: this._t("target_location"), options: locationOptions },
          dateColumn,
        ],
        load: (p) => p.location_history.map((h) => ({ value: h.location_id, date: h.start })),
        newRow: (rows) => ({ value: last(rows, locationOptions[0]?.value ?? ""), date: today }),
        view: (p) =>
          p.location_history
            .slice()
            .reverse()
            .map((h) => `<li><b>${esc(h.location)}</b><span>${since} ${this._date(h.start)}</span></li>`)
            .join(""),
        message: (p, rows) => ({
          type: "grow_tracker/set_history",
          plant_id: p.id,
          kind: "location",
          history: rows.map((r) => ({ value: r.value, start: r.date })),
        }),
      },
      log: {
        grid: "minmax(0, 1fr) 96px 40px",
        minRows: 0,
        invalid: "log_invalid",
        columns: [
          { name: "date", type: "date", label: this._t("date") },
          { name: "count", type: "number", label: this._t("count") },
        ],
        load: (p) => p.cuttings_log.map((c) => ({ date: c.date, count: c.count })),
        newRow: () => ({ date: today, count: 1 }),
        view: (p) =>
          p.cuttings_log
            .slice()
            .reverse()
            .map(
              (c) =>
                `<li><b>${esc(this._t(c.count === 1 ? "cutting_one" : "cuttings", { n: c.count }))}</b><span>${this._date(
                  c.date
                )}</span></li>`
            )
            .join(""),
        message: (p, rows) => ({
          type: "grow_tracker/set_cuttings_log",
          plant_id: p.id,
          log: rows.map((r) => ({ date: r.date, count: r.count })),
        }),
      },
    };
  }

  _renderEditAreas() {
    for (const kind of ["phase", "location", "log"]) this._renderEditArea(kind);
  }

  _renderEditArea(kind) {
    const area = this.shadowRoot.getElementById(`edit-area-${kind}`);
    const button = this.shadowRoot.getElementById(`edit-btn-${kind}`);
    const p = this._plant(this._selectedId);
    if (!area || !button || !p) return;
    const cfg = this._editors()[kind];

    if (this._edit?.kind !== kind) {
      // Immer nur eine Liste gleichzeitig bearbeiten
      button.hidden = Boolean(this._edit);
      button.onclick = () => {
        const rows = cfg.load(p);
        if (!rows.length) rows.push(cfg.newRow(rows));
        this._edit = { kind, rows };
        this._renderEditAreas();
      };
      const items = cfg.view(p);
      area.innerHTML = `<ul class="list">${items || `<li class="secondary">${esc(this._t("log_empty"))}</li>`}</ul>`;
      return;
    }

    button.hidden = true;
    const today = this._data.today;
    const rows = this._edit.rows;
    const canRemove = rows.length > cfg.minRows;
    const field = (col, row) => {
      const label = `aria-label="${esc(col.label)}"`;
      if (col.type === "select") {
        const options = col.options
          .map(
            (o) =>
              `<option value="${esc(o.value)}" ${o.value === row[col.name] ? "selected" : ""}>${esc(o.label)}</option>`
          )
          .join("");
        return `<select name="${col.name}" ${label}>${options}</select>`;
      }
      if (col.type === "date") {
        return `<input type="date" name="${col.name}" value="${esc(row[col.name])}" max="${today}" ${label}>`;
      }
      return `<input type="number" name="${col.name}" value="${esc(row[col.name])}" min="1" max="1000" ${label}>`;
    };

    area.innerHTML = `
      <form class="edit-form" novalidate>
        <div class="edit-row edit-labels secondary small" style="grid-template-columns:${cfg.grid}" aria-hidden="true">
          ${cfg.columns.map((c) => `<span>${esc(c.label)}</span>`).join("")}<span></span>
        </div>
        ${rows
          .map(
            (row, i) => `
          <div class="edit-row" data-index="${i}" style="grid-template-columns:${cfg.grid}">
            ${cfg.columns.map((c) => field(c, row)).join("")}
            <button type="button" class="icon-button" data-remove="${i}" ${canRemove ? "" : "disabled"}
              aria-label="${esc(this._t("remove_entry"))}" title="${esc(this._t("remove_entry"))}">✕</button>
          </div>`
          )
          .join("")}
        <button type="button" class="text-button small-button" data-add>+ ${esc(this._t("add_entry"))}</button>
        <div class="status" data-status role="status"></div>
        <div class="confirm-buttons">
          <button type="button" class="text-button" data-cancel>${esc(this._t("cancel"))}</button>
          <button type="submit" class="primary">${esc(this._t("save"))}</button>
        </div>
      </form>`;

    const form = area.querySelector("form");
    form.querySelectorAll("[data-remove]").forEach((btn) =>
      btn.addEventListener("click", () => {
        this._syncEdit(area, cfg);
        this._edit.rows.splice(Number(btn.dataset.remove), 1);
        this._renderEditArea(kind);
      })
    );
    form.querySelector("[data-add]").addEventListener("click", () => {
      this._syncEdit(area, cfg);
      this._edit.rows.push(cfg.newRow(this._edit.rows));
      this._renderEditArea(kind);
      const fields = area.querySelectorAll(".edit-row[data-index] select, .edit-row[data-index] input");
      fields[fields.length - cfg.columns.length]?.focus();
    });
    form.querySelector("[data-cancel]").addEventListener("click", () => {
      this._edit = null;
      this._renderDialogInfo();
    });
    form.addEventListener("submit", (ev) => {
      ev.preventDefault();
      this._saveEdit(area, cfg, p);
    });
  }

  _syncEdit(area, cfg) {
    this._edit.rows = [...area.querySelectorAll(".edit-row[data-index]")].map((rowEl) => {
      const row = {};
      for (const col of cfg.columns) {
        const value = rowEl.querySelector(`[name="${col.name}"]`).value;
        row[col.name] = col.type === "number" ? Number(value) : value;
      }
      return row;
    });
  }

  async _saveEdit(area, cfg, plant) {
    this._syncEdit(area, cfg);
    const rows = this._edit.rows;
    const status = area.querySelector("[data-status]");
    const invalid =
      rows.length < cfg.minRows ||
      rows.some((row) =>
        cfg.columns.some((col) => {
          const value = row[col.name];
          if (col.type === "date") return !value || value > this._data.today;
          if (col.type === "number") return !Number.isInteger(value) || value < 1;
          return !value;
        })
      );
    if (invalid) {
      status.className = "status error";
      status.textContent = this._t(cfg.invalid);
      return;
    }
    const buttons = area.querySelectorAll("button");
    buttons.forEach((b) => (b.disabled = true));
    try {
      await this._hass.callWS(cfg.message(plant, rows));
      this._edit = null;
      this._renderDialogInfo();
    } catch (err) {
      status.className = "status error";
      status.textContent = err?.message || String(err);
      buttons.forEach((b) => (b.disabled = false));
    }
  }

  _renderDialogForms() {
    const p = this._plant(this._selectedId);
    if (!p) return;
    const today = this._data.today;
    const nowLocal = this._localInput(new Date());
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
        <form data-action="add_note" class="wide" data-default-time="${nowLocal}">
          <h3>${esc(this._t("add_note"))}</h3>
          <div class="row">
            <label class="note-time">${esc(this._t("note_time"))}
              <input type="datetime-local" name="date" value="${nowLocal}" max="${nowLocal}">
            </label>
          </div>
          <textarea name="note" rows="3" required placeholder="${esc(this._t("note_placeholder"))}"
            aria-label="${esc(this._t("add_note"))}"></textarea>
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
    const mother = p.logged_cutting && p.mother_id ? this._plant(p.mother_id) : null;
    const motherNote = mother
      ? `<p>${esc(this._t("delete_mother_note", { name: mother.name }))}</p>`
      : "";
    area.innerHTML = `
      <div class="confirm" role="alertdialog">
        <p><b>${esc(this._t("delete_confirm", { name: p.name }))}</b></p>
        <p>${esc(this._t("delete_warning"))}</p>
        ${childNote}
        ${motherNote}
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
      // Nur einen Zeitpunkt senden, wenn er geändert wurde – sonst gilt "jetzt" (inkl. Logbuch)
      const when = fd.get("date");
      if (when && when !== form.dataset.defaultTime) data.date = when;
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
  .hidden-note { text-align: center; margin-top: 16px; }
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
  .count-badge {
    display: inline-block;
    margin-left: 4px;
    padding: 0 6px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 500;
    background: var(--secondary-background-color);
    color: var(--secondary-text-color);
  }
  .chevron { flex: none; width: 20px; text-align: center; font-size: 18px; color: var(--secondary-text-color); }
  .group-members { background: color-mix(in srgb, var(--secondary-background-color) 50%, transparent); }
  .group-members .plant { padding-left: 38px; }
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
  .note-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
  .note-text { white-space: pre-wrap; overflow-wrap: anywhere; }
  .dialog .small-icon { width: 32px; height: 32px; font-size: 16px; flex: none; }
  .note-form { display: flex; flex-direction: column; gap: 8px; padding: 4px 0; }
  .note-form label, .note-time { max-width: 260px; }
  .note-buttons { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  .note-buttons .spacer { flex: 1; }
  .dialog .note-buttons .text-button { margin-top: 0; }
  .section-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
  .section-head h3 { margin-bottom: 8px; }
  .dialog .small-button { padding: 4px 8px; font-size: 12px; margin-top: 12px; }
  .edit-form { display: flex; flex-direction: column; gap: 8px; }
  /* Die bearbeitete Historie nutzt die volle Breite, damit Auswahl und Datum lesbar bleiben */
  .columns > div:has(.edit-form) { grid-column: 1 / -1; }
  .edit-row { display: grid; gap: 8px; align-items: center; }
  .edit-row select, .edit-row input { min-width: 0; width: 100%; }
  .edit-labels { margin-bottom: -4px; }
  .edit-form .small-button { align-self: flex-start; margin-top: 0; }
  .icon-button:disabled { opacity: 0.3; cursor: default; }
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
    /* Deckende Theme-Farbe (--input-fill-color kann halbtransparent sein) */
    background-color: var(--secondary-background-color);
    border: 1px solid var(--divider-color);
    border-radius: 6px;
    padding: 8px;
    box-sizing: border-box;
  }
  option, optgroup {
    background-color: var(--card-background-color, var(--primary-background-color));
    color: var(--primary-text-color);
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
