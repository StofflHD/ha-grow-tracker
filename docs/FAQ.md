# FAQ

## The panel does not appear in the sidebar

- Restart Home Assistant after installing or updating.
- Check that Grow Tracker is set up (*Settings → Devices & services*).
- The entry may be hidden: long-press the *Home Assistant* title in the sidebar and check the hidden items.

## The panel shows an old version or behaves strangely after an update

Reload the page with **Ctrl + F5** (Mac: **Cmd + Shift + R**). In the companion app, reset the frontend cache in the
app settings (or restart the app).

## The panel says "Grow Tracker is not set up or not loaded"

Grow Tracker is disabled or failed to load. Check *Settings → Devices & services → Grow Tracker* and the log
(*Settings → System → Logs*).

## Who can delete plants?

Only Home Assistant **administrators** – the *Delete plant* button is hidden for other users.

## Can I add a plant that is already growing?

Yes – set the current phase and its start date when adding it, and complete the history afterwards.
See [Setup](Setup.md#moving-existing-plants-into-grow-tracker).

## Why did changing the history not trigger my automation?

Edits in the history are corrections, not real changes – they intentionally do not fire events.
Use *Change phase* / *Change location* for real changes.

## Why is a back-dated note not in the logbook?

The logbook can only show entries at the current time. Back-dated notes are stored with the plant
and shown in the panel and the *Last note* sensor.

## Times of notes are shifted

Note times use the Home Assistant time zone. If your browser uses a different time zone than Home Assistant,
the times shown in the panel are shifted accordingly.

## Where is the data stored?

In `/config/.storage/grow_tracker`. It is part of every Home Assistant backup.
Deleting a plant removes its history; deleting the integration removes all data.

## I found a bug / have an idea

Please open an [issue](https://github.com/StofflHD/ha-grow-tracker/issues).

---

[← Documentation overview](README.md)
