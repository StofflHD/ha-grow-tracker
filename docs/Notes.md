# Notes

Every plant has a diary for feeding, training, observations …

## Adding a note

**Panel:** plant → **Add note** – text and **time** (default: now).

**Action:**

```yaml
action: grow_tracker.add_note
target:
  entity_id: select.gelato_41_phase
data:
  note: "Repotted into 11 L, 1 ml/L nutrients"
```

Each note stores the **phase**, **location** and **day** of the plant at the time of the note.

## Notes for a past time

Change the **time** in the panel or pass `date` to the action:

```yaml
action: grow_tracker.add_note
target:
  entity_id: select.gelato_41_phase
data:
  note: "First pistils"
  date: "2026-09-10 18:30:00"
```

- Phase, location and day are taken from the plant's history **at that time**.
- Notes are always sorted by time; *Last note* stays the newest one.
- Times in the future are rejected.
- Notes for *now* also appear in the Home Assistant **logbook**; back-dated notes do not
  (the logbook can only show the current time).

## Editing and deleting

In the panel, click **✎** next to a note:

- change text and time → **Save** (phase, location and day are recalculated),
- **Delete** → click again on *Really delete?* to confirm.

## Where notes appear

- Panel → plant details → **Notes**
- Sensor `sensor.<plant>_last_note` – state: latest note, attribute `notes`: the last 20
- Event `grow_tracker_note_added` – see [Automations and Dashboards](Automations-and-Dashboards.md)
- Logbook (only notes for *now*)

---

[← Documentation overview](README.md)
