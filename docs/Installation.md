# Installation

## Requirements

- Home Assistant **2025.6** or newer
- One of:
  - Home Assistant **2026.11** or newer: the built-in **Marketplace** (recommended)
  - older versions: [HACS](https://hacs.xyz)
  - access to the `/config` folder for a manual installation

## Installation via the Marketplace (Home Assistant 2026.11+)

Since Home Assistant 2026.11, HACS is built in as the **Marketplace**. Grow Tracker is not in its default catalog
and is added from its GitHub link:

1. *Settings → **Marketplace***.
2. Top right: **Add from link**.
3. GitHub link: `https://github.com/StofflHD/ha-grow-tracker` – **Add**.
   If asked for the type, choose **Integration** and select **Add** again.
4. Open **Grow Tracker** in the Marketplace and install it.
5. **Restart** Home Assistant.

The Marketplace needs a GitHub connection for repositories added from a link, and asks you once to accept its risk
notice. Both are explained in the Marketplace itself.

Then continue with the [Setup](Setup.md).

## Installation via HACS (before Home Assistant 2026.11)

1. Open **HACS** in Home Assistant.
2. Top right: **⋮ → Custom repositories**.
3. Repository: `https://github.com/StofflHD/ha-grow-tracker` – Type: **Integration** – **Add**.
4. Search for **Grow Tracker** in HACS and click **Download**.
5. **Restart** Home Assistant.

When you update Home Assistant to 2026.11 or newer, HACS is replaced by the Marketplace automatically and
Grow Tracker stays installed.

## Manual installation

1. Download `grow_tracker.zip` from the [latest release](https://github.com/StofflHD/ha-grow-tracker/releases/latest).
2. Extract it to `/config/custom_components/grow_tracker/`
   (so that `manifest.json` is located at `/config/custom_components/grow_tracker/manifest.json`).
3. **Restart** Home Assistant.

You can copy the files e.g. with the *Samba share* or *File editor* add-on.

## Updates

**Marketplace:** new versions appear under *Settings → **Updates***, together with Home Assistant updates.
There you can read the release notes and install the update. The Marketplace checks for new versions regularly,
so a new release may take a while to show up.

**HACS:** open **Grow Tracker** in HACS → **Update**. If no update is shown yet: **⋮ → Update information**.

**Manual:** replace the folder with the content of the new `grow_tracker.zip`.

After every update:

1. **Restart** Home Assistant.
2. Reload the browser page with **Ctrl + F5** (Mac: **Cmd + Shift + R**) so the new sidebar panel is loaded.

The changes of each version are listed in the [releases](https://github.com/StofflHD/ha-grow-tracker/releases).

## Removal

1. *Settings → Devices & services → Grow Tracker → ⋮ → Delete*.
   This removes all locations, plants and their history.
2. Remove Grow Tracker in the Marketplace or in HACS (or delete `/config/custom_components/grow_tracker/`).
3. Restart Home Assistant.

---

[← Documentation overview](README.md)
