# Actions

All actions target a plant's **phase or location select** (`select.<plant>_phase` or `select.<plant>_location`).
They can be used in automations, scripts and *Developer tools → Actions*.

## set_phase

Switch to a new phase, or correct the start date of the current phase.

| Field | Required | Description |
|---|---|---|
| `phase` | yes | `germination`, `rooting`, `vegetative`, `mother`, `flowering`, `drying`, `curing`, `finished` |
| `date` | no | start of the phase (default: today) |

```yaml
action: grow_tracker.set_phase
target:
  entity_id: select.gelato_41_phase
data:
  phase: flowering
  date: "2026-09-20"
```

## set_location

Move the plant to another location.

| Field | Required | Description |
|---|---|---|
| `location` | yes | name of the location (case-insensitive) |
| `date` | no | date of the move (default: today) |

```yaml
action: grow_tracker.set_location
target:
  entity_id: select.gelato_41_phase
data:
  location: Flower large
```

## take_cuttings

Only for plants in phase *mother plant* – see [Mother Plants and Cuttings](Mother-Plants-and-Cuttings.md).

| Field | Required | Description |
|---|---|---|
| `count` | yes | number of cuttings (1–100) |
| `create_plants` | no | create one plant per cutting (default: `false`) |
| `location` | no | location of the new cuttings (default: first *propagation* location, otherwise the mother's) |
| `date` | no | date (default: today) |

```yaml
action: grow_tracker.take_cuttings
target:
  entity_id: select.gelato_41_phase
data:
  count: 6
  create_plants: true
```

## add_note

| Field | Required | Description |
|---|---|---|
| `note` | yes | text |
| `date` | no | time of the note (default: now) – see [Notes](Notes.md#notes-for-a-past-time) |

```yaml
action: grow_tracker.add_note
target:
  entity_id: select.gelato_41_phase
data:
  note: "EC 1.6, pH 6.1"
```

## Several plants at once

All actions accept several entities:

```yaml
action: grow_tracker.set_phase
target:
  entity_id:
    - select.gelato_41_1_phase
    - select.gelato_41_2_phase
    - select.gelato_41_3_phase
data:
  phase: vegetative
```

---

[← Documentation overview](README.md)
