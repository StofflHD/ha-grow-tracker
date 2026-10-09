# Mother Plants and Cuttings

## Mother plants

Set a plant to phase **mother plant** (panel, phase select or `set_phase`). Mother plants

- can **take cuttings**,
- show the number of **existing cuttings** and the **cuttings log**,
- can be selected as *mother plant* when adding a plant manually.

## Taking cuttings

**Panel:** mother plant → **Take cuttings**

| Field | Description |
|---|---|
| Count | number of cuttings |
| Date | default: today |
| Location | default: first location of type *propagation*, otherwise the mother's location |
| Create as plants | creates one plant per cutting |

**Action:**

```yaml
action: grow_tracker.take_cuttings
target:
  entity_id: select.gelato_41_phase
data:
  count: 6
  create_plants: true
  location: Propagation box   # optional
  date: "2026-09-28"          # optional
```

With **create as plants**, each cutting

- is named `<mother> #<n>`, e.g. `Gelato #41 #1`,
- starts in phase **rooting** at the chosen location,
- inherits **breeder/cutter, phenotype and flowering time** from the mother,
- is linked to the mother (*Cutting of …*).

Without *create as plants* the cuttings are only written to the cuttings log.

## Cuttings count and cuttings log

| | Meaning |
|---|---|
| **Cuttings** (sensor state, panel) | number of plants that currently exist as cuttings of this mother – rises with new cuttings, falls when one is deleted |
| **Cuttings log** | history of when how many cuttings were taken (attribute `log`, total in `taken_total`) |

The cuttings log can be edited in the panel (**Edit**): change date and count, remove or add entries –
e.g. to add cuttings you took before using Grow Tracker.

Deleting a cutting that was created via *take cuttings* also removes it from the mother's cuttings log.
Cuttings added manually were never counted in the log and are therefore not subtracted.

## Passing changes on to cuttings

When you edit a mother plant (integration page → plant → **⋮ → Reconfigure**):

- **Breeder/cutter, phenotype and flowering time** are passed on to all cuttings that still have the mother's
  previous value. Values you changed individually on a cutting are kept. A field you clear on the mother is cleared on its cuttings too.
- Cuttings named automatically (`<mother> #n`) are **renamed** with the mother. Cuttings with their own name keep it.
- Cuttings of cuttings are updated as well.
- Phase, location, history and notes of the cuttings are not changed.

**Example:** you rename `Mother Gelato` to `Gelato #41` and set the phenotype to `Pheno #5`
→ `Mother Gelato #1` becomes `Gelato #41 #1` with phenotype `Pheno #5`.

## Grouping in the panel

Cuttings at the same location, from the same mother and in the same phase are grouped into one row in the panel
(e.g. *Gelato #41 ✂ ×5*). Click it to see the individual cuttings.

## Deleting a mother plant

Its cuttings are kept and still show the mother's name. They are no longer linked to a mother in the panel.

---

[← Documentation overview](README.md)
