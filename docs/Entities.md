# Entities

Every location and every plant is a **device** with its own entities.
Entity IDs are created from the device name, e.g. `select.gelato_41_phase`.
You find the exact IDs on the device page (*Settings → Devices & services → Grow Tracker → device*).

## Per location

| Entity | State | Attributes |
|---|---|---|
| `sensor.<location>_plants` | number of plants at this location | `location_type`, `plants` (list with `name` = strain, `strain` = breeder/cutter, `phenotype`, `phase`, `days_in_phase`, `days_at_location`) |

## Per plant

| Entity | State | Attributes |
|---|---|---|
| `select.<plant>_phase` | current phase (selectable) | `strain` (breeder/cutter), `phenotype`, `origin` (`seed`/`cutting`), `mother`, `location`, `grow_start`, `phase_start`, `history`, `phase_durations_days` |
| `select.<plant>_location` | current location (selectable) | `since`, `days_at_location`, `history` |
| `sensor.<plant>_days_total` | days since the first phase entry | |
| `sensor.<plant>_days_in_phase` | days in the current phase | |
| `sensor.<plant>_week_in_phase` | week in the current phase (1, 2, …) | |
| `sensor.<plant>_days_at_location` | days at the current location | |
| `sensor.<plant>_phase_start` | start date of the current phase | |
| `sensor.<plant>_expected_harvest` | expected harvest date (only while flowering) | `flower_weeks`, `days_remaining` |
| `sensor.<plant>_cuttings` | number of existing cuttings of this plant | `taken_total`, `log`, `tracked_cuttings` |
| `sensor.<plant>_last_note` | text of the latest note | `notes` (last 20), `count` |

> In installations set up before version 0.4.1, the cuttings sensor keeps its old ID `sensor.<plant>_cuttings_taken`.

## Phase values

`germination`, `rooting`, `vegetative`, `mother`, `flowering`, `drying`, `curing`, `finished` –
see [Plants and Phases](Plants-and-Phases.md#phases).

## Examples

Days until harvest of a plant:

```jinja
{{ state_attr('sensor.gelato_41_expected_harvest', 'days_remaining') }}
```

All plants currently flowering:

```jinja
{{ integration_entities('grow_tracker')
   | select('match', 'select\..*_phase$')
   | select('is_state', 'flowering')
   | map('state_attr', 'friendly_name') | list }}
```

---

[← Documentation overview](README.md)
