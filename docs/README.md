# Grow Tracker – Documentation

Grow Tracker is a Home Assistant integration to document your grow – from seed or cutting to curing –
across all of your grow locations (tents, cabinets, chambers).

![Grow Tracker icon](../custom_components/grow_tracker/brand/icon.png)

## What it does

- **Locations** – your tents, cabinets and chambers, each with a type and an optional Home Assistant area
- **Plants** – strain, breeder/cutter, phenotype, phase and location, each with a full history
- **Mother plants & cuttings** – take cuttings, create them as plants and keep them linked to their mother
- **Notes** – a diary per plant, also for past dates
- **Sidebar panel** – an overview of everything, with all actions right there
- **Entities, actions and events** – use your grow data in dashboards and automations

The user interface is available in **English** and **German**.

## Pages

| Page | Content |
|---|---|
| [Installation](Installation.md) | Requirements, installation via HACS or manually, updates, removal |
| [Setup](Setup.md) | Setup wizard, adding and editing locations and plants |
| [Sidebar Panel](Sidebar-Panel.md) | Overview, plant details, editing in the panel |
| [Plants and Phases](Plants-and-Phases.md) | Plant fields, phases, phase and location history |
| [Mother Plants and Cuttings](Mother-Plants-and-Cuttings.md) | Taking cuttings, cuttings log, passing changes on |
| [Notes](Notes.md) | Adding, back-dating, editing and deleting notes |
| [Entities](Entities.md) | All sensors and selects with their attributes |
| [Actions](Actions.md) | All actions with examples |
| [Automations and Dashboards](Automations-and-Dashboards.md) | Events, automation and dashboard examples |
| [FAQ](FAQ.md) | Common questions and troubleshooting |

## A typical grow

1. Your mother plant lives in the **mother cabinet** in phase *mother plant*.
2. You **take 6 cuttings** – they are created as plants in phase *rooting* at your propagation location.
3. After rooting you set them to **vegetative**, later you **move** them to the flower tent and set **flowering**.
4. The panel shows the **flowering week** and counts down to the **expected harvest**.
5. Along the way you write **notes** (feeding, training, observations).
6. After harvest: **drying**, **curing**, **finished**.

## License

Grow Tracker is licensed under the [GNU General Public License v3.0](../LICENSE).
