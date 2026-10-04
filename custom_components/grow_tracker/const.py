"""Konstanten für Grow Tracker."""

DOMAIN = "grow_tracker"

# Subentry-Typen
SUBENTRY_LOCATION = "location"
SUBENTRY_PLANT = "plant"

# Setup-Assistent / Standort
CONF_LOCATIONS = "locations"
CONF_LOCATION_TYPE = "location_type"
CONF_AREA = "area_id"

LOCATION_TYPE_PROPAGATION = "propagation"
LOCATION_TYPE_MOTHER = "mother"
LOCATION_TYPE_VEGETATIVE = "vegetative"
LOCATION_TYPE_FLOWERING = "flowering"
LOCATION_TYPE_DRYING = "drying"
LOCATION_TYPE_OTHER = "other"

LOCATION_TYPES = [
    LOCATION_TYPE_PROPAGATION,
    LOCATION_TYPE_MOTHER,
    LOCATION_TYPE_VEGETATIVE,
    LOCATION_TYPE_FLOWERING,
    LOCATION_TYPE_DRYING,
    LOCATION_TYPE_OTHER,
]

# Pflanze
# Anzeige: CONF_NAME = "Sorte", CONF_STRAIN = "Breeder/Cutter" (Schlüssel bleiben aus Kompatibilität)
CONF_STRAIN = "strain"
CONF_PHENOTYPE = "phenotype"
CONF_START_DATE = "start_date"
CONF_FLOWER_WEEKS = "flower_weeks"
CONF_LOCATION = "location"
CONF_PHASE = "phase"
CONF_MOTHER = "mother"
CONF_MOTHER_NAME = "mother_name"
# Steckling wurde über take_cuttings angelegt und zählt im Schnitt-Protokoll der Mutter
CONF_LOGGED_CUTTING = "logged_cutting"

DEFAULT_FLOWER_WEEKS = 9

PHASE_GERMINATION = "germination"
PHASE_ROOTING = "rooting"
PHASE_VEGETATIVE = "vegetative"
PHASE_MOTHER = "mother"
PHASE_FLOWERING = "flowering"
PHASE_DRYING = "drying"
PHASE_CURING = "curing"
PHASE_FINISHED = "finished"

PHASES = [
    PHASE_GERMINATION,
    PHASE_ROOTING,
    PHASE_VEGETATIVE,
    PHASE_MOTHER,
    PHASE_FLOWERING,
    PHASE_DRYING,
    PHASE_CURING,
    PHASE_FINISHED,
]

STORAGE_VERSION = 1
STORAGE_KEY = DOMAIN
MAX_NOTES = 200

# Ein Signal für die ganze Integration (Parameter: entry_id)
SIGNAL_UPDATE = f"{DOMAIN}_update_{{}}"
# Signal für das Seitenleisten-Panel (auch bei Setup/Unload)
SIGNAL_PANEL_UPDATE = f"{DOMAIN}_panel_update"
# Aktiver Hub für das Panel (gesetzt, sobald die Daten bereitstehen)
DATA_HUB = f"{DOMAIN}_hub"

# Seitenleisten-Panel
PANEL_URL_PATH = "grow-tracker"
PANEL_COMPONENT = "grow-tracker-panel"
PANEL_ICON = "mdi:cannabis"
PANEL_TITLE = "Grow Tracker"
STATIC_URL = "/grow_tracker_static"
WS_SUBSCRIBE = f"{DOMAIN}/subscribe"
WS_SET_CUTTINGS_LOG = f"{DOMAIN}/set_cuttings_log"
WS_SET_HISTORY = f"{DOMAIN}/set_history"
WS_UPDATE_NOTE = f"{DOMAIN}/update_note"
WS_DELETE_NOTE = f"{DOMAIN}/delete_note"

EVENT_PHASE_CHANGED = f"{DOMAIN}_phase_changed"
EVENT_LOCATION_CHANGED = f"{DOMAIN}_location_changed"
EVENT_NOTE_ADDED = f"{DOMAIN}_note_added"
EVENT_CUTTINGS_TAKEN = f"{DOMAIN}_cuttings_taken"

SERVICE_SET_PHASE = "set_phase"
SERVICE_SET_LOCATION = "set_location"
SERVICE_ADD_NOTE = "add_note"
SERVICE_TAKE_CUTTINGS = "take_cuttings"

ATTR_PHASE = "phase"
ATTR_DATE = "date"
ATTR_NOTE = "note"
ATTR_LOCATION = "location"
ATTR_COUNT = "count"
ATTR_CREATE_PLANTS = "create_plants"
