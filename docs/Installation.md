# Installation

## Requirements

- Home Assistant **2025.6** or newer
- [HACS](https://hacs.xyz) (recommended) – or access to the `/config` folder for a manual installation

## Installation via HACS

Grow Tracker is not part of the HACS default list. It is added as a **custom repository**:

1. Open **HACS** in Home Assistant.
2. Top right: **⋮ → Custom repositories**.
3. Repository: `https://github.com/StofflHD/ha-grow-tracker` – Type: **Integration** – **Add**.
4. Search for **Grow Tracker** in HACS and click **Download**.
5. **Restart** Home Assistant.

Then continue with the [Setup](Setup.md).

## Manual installation

1. Download `grow_tracker.zip` from the [latest release](https://github.com/StofflHD/ha-grow-tracker/releases/latest).
2. Extract it to `/config/custom_components/grow_tracker/`
   (so that `manifest.json` is located at `/config/custom_components/grow_tracker/manifest.json`).
3. **Restart** Home Assistant.

You can copy the files e.g. with the *Samba share* or *File editor* add-on.

## Updates

**HACS:** HACS shows new versions automatically. Open **Grow Tracker** in HACS → **Update**.
If no update is shown yet: **⋮ → Update information**.

**Manual:** replace the folder with the content of the new `grow_tracker.zip`.

After every update:

1. **Restart** Home Assistant.
2. Reload the browser page with **Ctrl + F5** (Mac: **Cmd + Shift + R**) so the new sidebar panel is loaded.

The changes of each version are listed in the [releases](https://github.com/StofflHD/ha-grow-tracker/releases).

## Removal

1. *Settings → Devices & services → Grow Tracker → ⋮ → Delete*.
   This removes all locations, plants and their history.
2. Remove Grow Tracker in HACS (or delete `/config/custom_components/grow_tracker/`).
3. Restart Home Assistant.

---

[← Documentation overview](README.md)
