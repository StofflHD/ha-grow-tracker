"""Tests: Pflanze duplizieren (Angaben + Phasen-/Standort-Historie)."""

from __future__ import annotations

from types import MappingProxyType
from typing import Any
from unittest.mock import patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.grow_tracker.const import DOMAIN
from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from .conftest import LOC_FLOWER, LOC_PROP, PLANT_MOTHER, PLANT_SEED


async def _call(hass: HomeAssistant, service: str, plant_id: str, **data: Any) -> None:
    entity_id = er.async_get(hass).async_get_entity_id("select", DOMAIN, f"{plant_id}_phase")
    await hass.services.async_call(
        DOMAIN, service, {"entity_id": entity_id, **data}, blocking=True
    )
    await hass.async_block_till_done()


async def _duplicate(
    hass: HomeAssistant, hass_ws_client: WebSocketGenerator, plant_id: str, count: int, **kw
) -> dict:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass, **kw)
    await client.send_json_auto_id(
        {"type": "grow_tracker/duplicate_plant", "plant_id": plant_id, "count": count}
    )
    result = await client.receive_json()
    await hass.async_block_till_done()
    return result


def _by_name(entry: MockConfigEntry) -> dict:
    return {p.name: p for p in entry.runtime_data.plants.values()}


async def test_duplicate_seed_plant(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await _call(hass, "set_phase", PLANT_SEED, phase="vegetative", date="2026-09-08")
    await _call(hass, "add_note", PLANT_SEED, note="Nur beim Original")

    with patch.object(
        hass.config_entries, "async_reload", wraps=hass.config_entries.async_reload
    ) as reload:
        result = await _duplicate(hass, hass_ws_client, PLANT_SEED, 2)

    assert result["success"]
    assert result["result"] == {"created": ["Northern Lights #2", "Northern Lights #3"]}
    assert reload.call_count == 1

    plants = _by_name(setup_entry)
    original = plants["Northern Lights #1"]
    assert original.subentry_id == PLANT_SEED  # Original umbenannt, Daten behalten
    assert [n["text"] for n in original.notes] == ["Nur beim Original"]

    for name in ("Northern Lights #2", "Northern Lights #3"):
        copy = plants[name]
        assert copy.history == original.history
        assert copy.location_history == original.location_history
        assert copy.phase == "vegetative"
        assert copy.days_total == original.days_total
        assert copy.location_id == LOC_FLOWER
        assert copy.notes == []
        assert copy.origin == "seed"
        # Entities der Kopie existieren nach dem Reload
        assert er.async_get(hass).async_get_entity_id(
            "select", DOMAIN, f"{copy.subentry_id}_phase"
        )


async def test_duplicate_numbered_plant_continues(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await _duplicate(hass, hass_ws_client, PLANT_SEED, 1)  # → #1 (Original), #2
    second = _by_name(setup_entry)["Northern Lights #2"]

    result = await _duplicate(hass, hass_ws_client, second.subentry_id, 2)
    assert result["result"]["created"] == ["Northern Lights #3", "Northern Lights #4"]
    assert "Northern Lights #2" in _by_name(setup_entry)  # nummeriertes Original bleibt


async def test_duplicate_when_number_one_taken(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    hass.config_entries.async_add_subentry(
        setup_entry,
        ConfigSubentry(
            data=MappingProxyType({"location": LOC_PROP, "flower_weeks": 9}),
            subentry_type="plant",
            title="Northern Lights #1",
            unique_id=None,
        ),
    )
    await hass.async_block_till_done()

    result = await _duplicate(hass, hass_ws_client, PLANT_SEED, 1)
    assert result["result"]["created"] == ["Northern Lights #3"]
    assert setup_entry.runtime_data.plants[PLANT_SEED].name == "Northern Lights #2"


async def test_duplicate_cutting(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    await _call(hass, "take_cuttings", PLANT_MOTHER, count=1, create_plants=True)
    cutting = next(p for p in setup_entry.runtime_data.plants.values() if p.mother_id)

    await _duplicate(hass, hass_ws_client, cutting.subentry_id, 2)

    hub = setup_entry.runtime_data
    copies = [p for p in hub.plants.values() if p.mother_id and p.subentry_id != cutting.subentry_id]
    assert len(copies) == 2
    assert all(not p.logged_cutting for p in copies)  # nicht im Schnitt-Protokoll
    assert len(hub.plants[PLANT_MOTHER].children()) == 3

    # Kopie löschen ändert das Schnitt-Protokoll der Mutter nicht
    hass.config_entries.async_remove_subentry(setup_entry, copies[0].subentry_id)
    await hass.async_block_till_done()
    assert setup_entry.runtime_data.plants[PLANT_MOTHER].cuttings_taken == 1


async def test_duplicate_requires_admin(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
) -> None:
    result = await _duplicate(
        hass, hass_ws_client, PLANT_SEED, 1, access_token=hass_read_only_access_token
    )
    assert not result["success"]
    assert result["error"]["code"] == "unauthorized"
    assert len(setup_entry.runtime_data.plants) == 2


async def test_duplicate_unknown_plant(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    result = await _duplicate(hass, hass_ws_client, "gibt_es_nicht", 1)
    assert result["error"]["code"] == "not_found"
