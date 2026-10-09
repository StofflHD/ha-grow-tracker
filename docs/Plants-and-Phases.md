# Plants and Phases

## Plant fields

| Field | Example | Note |
|---|---|---|
| **Strain** | `Gelato #41` | device name of the plant |
| **Breeder/Cutter** | `Seed Junky` | attribute `strain` (name kept for compatibility) |
| **Phenotype** | `Pheno #3` | attribute `phenotype` |
| **Expected flowering time** | `9` weeks | used for the expected harvest |

Edit them on the integration page: plant → **⋮ → Reconfigure**.

## Phases

| Phase | German | Note |
|---|---|---|
| `germination` | Keimung | default for plants from seed |
| `rooting` | Bewurzelung | default for cuttings |
| `vegetative` | Wachstum | |
| `mother` | Mutterpflanze | enables *take cuttings* |
| `flowering` | Blüte | starts the harvest countdown |
| `drying` | Trocknung | |
| `curing` | Curing | |
| `finished` | Abgeschlossen | |

Phases can be switched in any order.

## Changing the phase

- **Panel:** plant → *Change phase* (with date)
- **Dashboard:** the plant's phase select
- **Action:** `grow_tracker.set_phase` – see [Actions](Actions.md#set_phase)

A date in the past is allowed (e.g. if you enter the change later), but not before the start of the current phase.
To correct older entries, edit the phase history.

Changing the phase with the **same phase and a date** corrects the start date of the current phase.

## Locations

- **Panel:** plant → *Change location* (with date)
- **Action:** `grow_tracker.set_location` with the location **name** (case-insensitive) – see [Actions](Actions.md#set_location)
- When the location has an **area**, the plant's device is moved to that area.

## Counters

| Value | Calculated from |
|---|---|
| Days total | first entry of the phase history |
| Days / week in phase | start of the current phase |
| Days at location | start of the current location |
| Expected harvest | flowering start + expected flowering weeks (only while flowering) |

All counters are updated at midnight.

## Correcting the history

Phase and location history can be edited in the panel – see [Sidebar Panel](Sidebar-Panel.md#editing-histories).
Changing the first phase entry changes *days total*; changing the flowering start changes the expected harvest.

---

[← Documentation overview](README.md)
