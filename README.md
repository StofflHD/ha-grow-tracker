# Grow Tracker for Home Assistant

Track your plants through every phase of the grow – from seed or cutting to curing –
across all of your grow locations (tents, cabinets, chambers).

*The user interface is available in English and German.*

## Features

- **Sidebar panel** with an overview of all locations and plants – change phases and locations, add notes and take cuttings right there
- **Setup wizard** for your grow locations (mother cabinet, flower tents, propagation, drying …)
- **Locations** with a type and an optional Home Assistant area – plants are moved to that area automatically
- **Plants** with phase history: germination · rooting · vegetative · mother plant · flowering · drying · curing · finished
- **Mother plants & cuttings**: log cuttings taken, optionally create every cutting as a new plant linked to its mother
- **Plants** with strain, breeder/cutter and phenotype
- **Diary notes** per plant – add notes for any past time, edit or delete them; current notes also appear in the logbook
- Days total / in phase / at location, flowering week, expected harvest date
- Events for automations

Requires Home Assistant **2025.6** or newer.

## Installation

### HACS (custom repository)
Grow Tracker is not part of the HACS default list, but can be added as a custom repository:

1. HACS → ⋮ → *Custom repositories*
2. Repository: `https://github.com/StofflHD/ha-grow-tracker`, type: *Integration*
3. Install **Grow Tracker** and restart Home Assistant

### Manual
Download `grow_tracker.zip` from the [latest release](https://github.com/StofflHD/ha-grow-tracker/releases/latest),
extract it to `/config/custom_components/grow_tracker/` and restart.

## Setup

*Settings → Devices & services → Add integration → Grow Tracker*

1. Enter your locations, one per line (e.g. `Mother cabinet`, `Flower large`, `Flower small`).
2. For each location choose its type and optionally an area. The type is suggested from the name.

Afterwards the integration page offers **Add location** and **Add plant**.
Locations and plants can be edited (⋮ → *Reconfigure*) or deleted there.

## Sidebar panel

After setup, **Grow Tracker** appears in the Home Assistant sidebar:

- One card per occupied location with its plants, phase, week, day and – while flowering – a progress bar and harvest countdown (empty locations are hidden)
- Click a plant to see its phase and location history, cuttings and notes
- Change phase or location (with date), add notes (also for a past time) and take cuttings directly in the panel
- Edit or delete existing notes
- Edit the phase history, location history and a mother plant's cuttings log: change entries, remove or add them (corrections do not fire change events)
- Delete plants (administrators only, with confirmation) – cuttings of a deleted mother plant are kept; deleting a cutting created via *take cuttings* also removes it from its mother's cuttings log
- Updates live, also when changes come from automations

You can hide or reorder the entry like any other sidebar item (long-press the sidebar title).

## Entities

**Per location** (device)

| Entity | Description |
|---|---|
| `sensor.<location>_plants` | Number of plants; attribute `plants` lists `name` (strain), `strain` (breeder/cutter), `phenotype`, phase and days |

**Per plant** (device)

| Entity | Description |
|---|---|
| `select.<plant>_phase` | Current phase. Attributes: history, duration of each phase, mother, origin |
| `select.<plant>_location` | Current location. Attributes: location history |
| `sensor.<plant>_days_total` | Days since start |
| `sensor.<plant>_days_in_phase` | Days in current phase |
| `sensor.<plant>_week_in_phase` | e.g. flowering week 5 |
| `sensor.<plant>_days_at_location` | Days at current location |
| `sensor.<plant>_phase_start` | Start date of current phase |
| `sensor.<plant>_expected_harvest` | Only while flowering: flowering start + expected weeks |
| `sensor.<plant>_cuttings` | Mother plants: number of cuttings currently existing as plants; attributes: tracked cuttings, cuttings log, `taken_total` |
| `sensor.<plant>_last_note` | Latest diary entry; attribute `notes` holds the last 20 |

## Actions

All actions target a plant's `select` entity (phase or location).

```yaml
# Change phase (date optional, may be in the past)
action: grow_tracker.set_phase
target:
  entity_id: select.gelato_1_phase
data:
  phase: flowering
  date: "2026-09-20"

# Move to another location (by name)
action: grow_tracker.set_location
target:
  entity_id: select.gelato_1_phase
data:
  location: Flower large

# Take cuttings from a mother plant
action: grow_tracker.take_cuttings
target:
  entity_id: select.mother_gelato_phase
data:
  count: 6
  create_plants: true        # creates "Mother Gelato #1" … "#6"
  location: Propagation      # optional

# Diary entry
action: grow_tracker.add_note
target:
  entity_id: select.gelato_1_phase
data:
  note: "Repotted into 11 L, 1 ml/L nutrients"
  date: "2026-09-20 18:30:00"   # optional: add a note for a past time
```

When a mother plant is edited (⋮ → *Reconfigure*), changed breeder/cutter, phenotype and flowering time are passed on to
its cuttings (and their cuttings) as long as they still have the mother's previous value; automatically named cuttings
(`<mother> #n`) are renamed with her.

New cuttings start in phase *rooting*, inherit breeder/cutter, phenotype and flowering time from the mother and are
placed at the first location of type *propagation* (or the mother's location) unless a location is given.

## Events

| Event | Data |
|---|---|
| `grow_tracker_phase_changed` | `plant`, `plant_id`, `from_phase`, `to_phase`, `date` |
| `grow_tracker_location_changed` | `plant`, `plant_id`, `from_location`, `to_location`, `date` |
| `grow_tracker_cuttings_taken` | `plant`, `plant_id`, `count`, `date`, `created_plants` |
| `grow_tracker_note_added` | `plant`, `plant_id`, `location`, `phase`, `day`, `text` |

Example – reminder when a plant starts flowering:

```yaml
triggers:
  - trigger: event
    event_type: grow_tracker_phase_changed
    event_data:
      to_phase: flowering
actions:
  - action: notify.notify
    data:
      message: "{{ trigger.event.data.plant }} started flowering – switch light to 12/12!"
```

## Data

History, notes and cuttings are stored in `/config/.storage/grow_tracker`.
Deleting a plant removes its history; deleting the integration removes all data.

## Development

```bash
python -m venv .venv
.venv/bin/pip install -r requirements_test.txt
.venv/bin/ruff check custom_components tests
.venv/bin/pytest -q
```

Home Assistant does not support Windows – use Linux, macOS or WSL for running the tests.

The sidebar panel can be previewed without Home Assistant using sample data:

```bash
python -m http.server 8765
```

Then open `http://localhost:8765/dev/panel-preview.html` (`?lang=en`, `?theme=dark`).

### Releasing
1. Create a GitHub release with a tag like `v0.2.0`.
2. The release workflow writes the version into `manifest.json`, builds `grow_tracker.zip` and attaches it to the release.
3. HACS offers the new version to users automatically.

## License

[MIT](LICENSE)
