# Setup

## Setup wizard

*Settings → Devices & services → Add integration → **Grow Tracker***

**Step 1 – locations:** enter your grow locations, one per line, e.g.

```
Mother cabinet
Flower large
Flower small
Propagation box
```

**Step 2 – per location:** choose

- **Type** – suggested from the name (e.g. "Flower …" → *Flowering*):

  | Type | Used for |
  |---|---|
  | Propagation / cuttings | default location for new cuttings |
  | Mother plants | |
  | Vegetative | |
  | Flowering | |
  | Drying | |
  | Other | |

- **Area** (optional) – a Home Assistant area. Plants at this location are automatically assigned to this area,
  so the area page shows your plants together with the sensors of that tent.

Grow Tracker can only be set up once. Everything else is added on the integration page.

## Adding locations and plants

On *Settings → Devices & services → Grow Tracker* you find the buttons:

- **Add location** – name, type, area
- **Add plant**:

  | Field | Description |
  |---|---|
  | **Strain** | e.g. `Gelato #41` – becomes the device name |
  | **Breeder/Cutter** | optional |
  | **Phenotype** | optional, e.g. `Pheno #3` |
  | **Mother plant** | only shown if a plant is in phase *mother plant* – select it for cuttings |
  | **Current phase** | leave empty: *germination* (seed) or *rooting* (cutting) |
  | **Location** | |
  | **Start of current phase** | leave empty for today – use it for plants that are already growing |
  | **Expected flowering time (weeks)** | used for the expected harvest date |

  For cuttings, empty *Breeder/Cutter* and *Phenotype* are taken from the mother.

Cuttings are usually created directly from the mother plant – see [Mother Plants and Cuttings](Mother-Plants-and-Cuttings.md).

## Editing and deleting

On the integration page, every location and plant has a **⋮** menu:

- **Reconfigure** – locations: name, type, area. Plants: strain, breeder/cutter, phenotype, flowering time.
  Changes to a mother plant are passed on to its cuttings ([details](Mother-Plants-and-Cuttings.md#passing-changes-on-to-cuttings)).
- **Delete** – removes the location or plant. Plants can also be deleted in the [Sidebar Panel](Sidebar-Panel.md#deleting-a-plant).

Phase, location, history and notes are not edited here but in the [Sidebar Panel](Sidebar-Panel.md).

## Moving existing plants into Grow Tracker

For plants that are already growing:

1. **Add plant** with the current phase and its start date (e.g. *flowering* since 2026-09-01).
2. Optional: complete the earlier phases afterwards in the panel via **Phase history → Edit**
   (e.g. *germination* 2026-07-01, *vegetative* 2026-07-08, *flowering* 2026-09-01).

---

[← Documentation overview](README.md)
