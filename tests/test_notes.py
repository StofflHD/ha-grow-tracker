"""Tests für Phänotyp und bearbeitbare Notizen."""

from __future__ import annotations

from typing import Any

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_capture_events
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.config_entries import SOURCE_RECONFIGURE, SOURCE_USER
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from .conftest import LOC_MOTHER, LOC_PROP, PLANT_MOTHER, PLANT_SEED


def _eid(hass: HomeAssistant, platform: str, plant_id: str, key: str) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(platform, DOMAIN, f"{plant_id}_{key}")
    assert entity_id is not None
    return entity_id


async def _call(hass: HomeAssistant, service: str, plant_id: str, **data: Any) -> None:
    await hass.services.async_call(
        DOMAIN,
        service,
        {"entity_id": _eid(hass, "select", plant_id, "phase"), **data},
        blocking=True,
    )
    await hass.async_block_till_done()


# --- Phänotyp ------------------------------------------------------------------


async def test_phenotype_shown(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    state = hass.states.get(_eid(hass, "select", PLANT_MOTHER, "phase"))
    assert state.attributes["phenotype"] == "Pheno #3"
    assert hass.states.get(_eid(hass, "select", PLANT_SEED, "phase")).attributes["phenotype"] is None


async def test_cuttings_inherit_phenotype(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    await _call(hass, "take_cuttings", PLANT_MOTHER, count=1, create_plants=True)
    await hass.async_block_till_done()
    cutting = next(p for p in setup_entry.runtime_data.plants.values() if p.mother_id)
    assert cutting.phenotype == "Pheno #3"
    assert cutting.strain == "Gelato"


async def test_plant_flow_phenotype(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    # Neue Pflanze mit Phänotyp
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"name": "Zkittlez", "phenotype": "Pheno #7", "location": LOC_PROP, "flower_weeks": 9},
    )
    await hass.async_block_till_done()
    plant = next(p for p in setup_entry.runtime_data.plants.values() if p.name == "Zkittlez")
    assert plant.phenotype == "Pheno #7"

    # Steckling von Hand: Phänotyp und Breeder/Cutter von der Mutter
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "plant"), context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {"name": "Klon", "mother": PLANT_MOTHER, "location": LOC_MOTHER, "flower_weeks": 9},
    )
    await hass.async_block_till_done()
    clone = next(p for p in setup_entry.runtime_data.plants.values() if p.name == "Klon")
    assert clone.phenotype == "Pheno #3"

    # Bearbeiten: Phänotyp leeren entfernt ihn
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "plant"),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": PLANT_MOTHER},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Mutter Gelato", "strain": "Gelato", "flower_weeks": 9}
    )
    await hass.async_block_till_done()
    assert setup_entry.runtime_data.plants[PLANT_MOTHER].phenotype is None
    assert setup_entry.runtime_data.plants[PLANT_MOTHER].strain == "Gelato"


# --- Notizen -------------------------------------------------------------------


async def test_add_note_now_goes_to_logbook(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    logbook = async_capture_events(hass, "logbook_entry")
    await _call(hass, "add_note", PLANT_SEED, note="Gegossen")
    note = setup_entry.runtime_data.plants[PLANT_SEED].notes[-1]
    assert note["id"]
    assert note["date"].startswith("2026-09-15T12:00")
    assert len(logbook) == 1


async def test_add_past_note(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    await _call(hass, "set_phase", PLANT_SEED, phase="vegetative", date="2026-09-10")
    await _call(hass, "set_location", PLANT_SEED, location="Anzucht", date="2026-09-12")
    await _call(hass, "add_note", PLANT_SEED, note="Heute")
    logbook = async_capture_events(hass, "logbook_entry")

    await _call(hass, "add_note", PLANT_SEED, note="Erste Blätter", date="2026-09-05 10:30:00")

    notes = setup_entry.runtime_data.plants[PLANT_SEED].notes
    assert [n["text"] for n in notes] == ["Erste Blätter", "Heute"]  # nach Zeitpunkt sortiert
    past = notes[0]
    assert past["date"] == "2026-09-05T10:30+02:00"
    assert past["phase"] == "germination"  # Phase an diesem Tag
    assert past["location"] == "Blüte groß"  # Standort an diesem Tag
    assert past["day"] == 4
    assert logbook == []  # nachgetragen → kein Logbuch-Eintrag
    # "Letzte Notiz" bleibt die neueste
    assert hass.states.get(_eid(hass, "sensor", PLANT_SEED, "last_note")).state == "Heute"


async def test_add_note_in_future_rejected(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError):
        await _call(hass, "add_note", PLANT_SEED, note="Später", date="2026-09-20 10:00:00")
    assert setup_entry.runtime_data.plants[PLANT_SEED].notes == []


async def test_ws_update_and_delete_note(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await _call(hass, "set_phase", PLANT_SEED, phase="vegetative", date="2026-09-10")
    await _call(hass, "add_note", PLANT_SEED, note="A")
    await _call(hass, "add_note", PLANT_SEED, note="B", date="2026-09-12 08:00:00")
    plant = setup_entry.runtime_data.plants[PLANT_SEED]
    note_a = next(n for n in plant.notes if n["text"] == "A")

    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    # Text und Zeitpunkt ändern → neu sortiert, Phase passend zum neuen Datum
    await client.send_json_auto_id(
        {
            "type": "grow_tracker/update_note",
            "plant_id": PLANT_SEED,
            "note_id": note_a["id"],
            "text": "A korrigiert",
            "date": "2026-09-03T09:15",
        }
    )
    assert (await client.receive_json())["success"]
    assert [n["text"] for n in plant.notes] == ["A korrigiert", "B"]
    assert plant.notes[0]["phase"] == "germination"
    assert plant.notes[0]["day"] == 2
    assert plant.notes[0]["id"] == note_a["id"]

    # Zukunft und leerer Text werden abgelehnt
    for payload in ({"text": "x", "date": "2026-10-01T09:00"}, {"text": " ", "date": "2026-09-03T09:00"}):
        await client.send_json_auto_id(
            {"type": "grow_tracker/update_note", "plant_id": PLANT_SEED, "note_id": note_a["id"], **payload}
        )
        result = await client.receive_json()
        assert result["error"]["code"] == "invalid_format"

    # Löschen
    await client.send_json_auto_id(
        {"type": "grow_tracker/delete_note", "plant_id": PLANT_SEED, "note_id": note_a["id"]}
    )
    assert (await client.receive_json())["success"]
    assert [n["text"] for n in plant.notes] == ["B"]

    # Unbekannte Notiz
    await client.send_json_auto_id(
        {"type": "grow_tracker/delete_note", "plant_id": PLANT_SEED, "note_id": "gibt_es_nicht"}
    )
    assert (await client.receive_json())["error"]["code"] == "invalid_format"


async def test_legacy_notes_get_ids(
    hass: HomeAssistant, mock_entry: MockConfigEntry, hass_storage: dict[str, Any]
) -> None:
    hass_storage[DOMAIN] = {
        "version": 1,
        "key": DOMAIN,
        "data": {
            "plants": {
                PLANT_SEED: {
                    "history": [{"phase": "germination", "start": "2026-09-01"}],
                    "locations": [],
                    "cuttings": [],
                    "notes": [
                        {"date": "2026-09-02T10:00+02:00", "phase": "germination", "day": 1, "text": "Alt"}
                    ],
                }
            }
        },
    }
    mock_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    note = mock_entry.runtime_data.plants[PLANT_SEED].notes[0]
    assert note["text"] == "Alt"
    assert len(note["id"]) == 32
