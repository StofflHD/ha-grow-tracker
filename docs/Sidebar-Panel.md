# Sidebar Panel

After the setup, **Grow Tracker** appears in the Home Assistant sidebar. The panel updates live – also when
changes come from automations or actions – and follows your Home Assistant theme (light/dark) and language.

## Overview

- At the top: how many plants are in which phase.
- One **card per location** that currently has plants. Empty locations are hidden (a note below the cards says how many).
- Per plant: strain, phenotype · breeder/cutter, phase, week in phase and day since start.
  - **Flowering:** progress bar and *Harvest in X days*.
  - **Mother plants:** number of existing cuttings (✂).
- **Grouped cuttings:** cuttings at the same location, from the same mother and in the same phase are shown as one row,
  e.g. *Gelato #41 ✂ ×5*. Week and day are shown as a range if they differ. Click the row to expand it.
- **Manage** (top right) opens the integration page to add locations and plants.

You can hide or move the panel entry like any other sidebar item (long-press the *Home Assistant* title in the sidebar).

## Plant details

Click a plant to open its details:

- Header: strain, phenotype, breeder/cutter, location
- Origin: *From seed* or *Cutting of …* (click to open the mother)
- Days total, days in phase, days at location, expected harvest
- **Phase history** and **location history**
- Mother plants: existing **cuttings** (click to open) and the **cuttings log**
- **Notes**

## Actions in the panel

| Section | What you can do |
|---|---|
| **Change phase** | new phase + date (can be in the past) |
| **Change location** | new location + date |
| **Add note** | text + time (default: now, can be in the past) – see [Notes](Notes.md) |
| **Take cuttings** | only for mother plants – count, date, location, *create as plants* – see [Mother Plants and Cuttings](Mother-Plants-and-Cuttings.md) |
| **Edit plant** | opens the integration page (strain, breeder/cutter, phenotype, flowering time) |

## Editing histories

**Phase history**, **location history** and the **cuttings log** each have an **Edit** button:

- Change the value and date of every entry, remove entries (✕) or add entries.
- **Save** applies all changes at once, **Cancel** discards them.
- Rules: no dates in the future; phase and location history keep at least one entry.
- Entries are sorted by date; consecutive identical entries are merged.

Editing is a **correction**: counters, expected harvest and plant counts follow the corrected history,
but no `phase_changed` / `location_changed` events are fired, so automations are not triggered.

## Editing notes

Click **✎** next to a note to change its text and time, or delete it – see [Notes](Notes.md).

## Deleting a plant

At the bottom of the plant details: **Delete plant** (administrators only).
A confirmation shows what will be lost (history, notes, cuttings log).

- Cuttings of a deleted mother plant are **kept** and still show their mother's name.
- Deleting a cutting that was created via *take cuttings* also removes it from its mother's cuttings log.

---

[← Documentation overview](README.md)
