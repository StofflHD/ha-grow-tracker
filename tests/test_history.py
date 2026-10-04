"""Tests für das Bearbeiten von Phasen- und Standort-Historie."""

from __future__ import annotations

import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    area_registry as ar,
    device_registry as dr,
    entity_registry as er,
)
from homeassistant.setup import async_setup_component

from .conftest import LOC_FLOWER, LOC_MOTHER, LOC_PROP, PLANT_SEED


async def _client(hass: HomeAssistant, hass_ws_client: WebSocketGenerator):
    assert await async_setup_component(hass, "websocket_api", {})
    return await hass_ws_client(hass)


def _state(hass: HomeAssistant, platform: str, key: str):
    entity_id = er.async_get(hass).async_get_entity_id(
        platform, "grow_tracker", f"{PLANT_SEED}_{key}"
    )
    return hass.states.get(entity_id)


async def test_edit_phase_history(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await _client(hass, hass_ws_client)
    events = async_capture_events(hass, "grow_tracker_phase_changed")

    await client.send_json_auto_id(
        {
            "type": "grow_tracker/set_history",
            "plant_id": PLANT_SEED,
            "kind": "phase",
            "history": [
                {"value": "flowering", "start": "2026-09-08"},
                {"value": "germination", "start": "2026-08-25"},
                {"value": "vegetative", "start": "2026-08-30"},
                {"value": "vegetative", "start": "2026-09-01"},  # wird zusammengefasst
            ],
        }
    )
    assert (await client.receive_json())["success"]
    await hass.async_block_till_done()

    plant = setup_entry.runtime_data.plants[PLANT_SEED]
    assert plant.history == [
        {"phase": "germination", "start": "2026-08-25"},
        {"phase": "vegetative", "start": "2026-08-30"},
        {"phase": "flowering", "start": "2026-09-08"},
    ]
    # Entities folgen der korrigierten Historie
    assert _state(hass, "select", "phase").state == "flowering"
    assert _state(hass, "sensor", "days_total").state == "21"
    assert _state(hass, "sensor", "expected_harvest").state == "2026-11-10"
    # Korrektur löst keine Wechsel-Events aus
    assert events == []


async def test_edit_location_history_moves_area(
    hass: HomeAssistant, mock_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    area = ar.async_get(hass).async_create("Anzuchtraum")
    sub = mock_entry.subentries[LOC_PROP]
    mock_entry.add_to_hass(hass)
    hass.config_entries.async_update_subentry(
        mock_entry, sub, data={**sub.data, "area_id": area.id}
    )
    assert await hass.config_entries.async_setup(mock_entry.entry_id)
    await hass.async_block_till_done()

    client = await _client(hass, hass_ws_client)
    await client.send_json_auto_id(
        {
            "type": "grow_tracker/set_history",
            "plant_id": PLANT_SEED,
            "kind": "location",
            "history": [
                {"value": LOC_MOTHER, "start": "2026-09-01"},
                {"value": LOC_PROP, "start": "2026-09-10"},
            ],
        }
    )
    assert (await client.receive_json())["success"]
    await hass.async_block_till_done()

    plant = mock_entry.runtime_data.plants[PLANT_SEED]
    assert plant.location_id == LOC_PROP
    assert _state(hass, "select", "location").state == "Anzucht"
    assert _state(hass, "sensor", "days_at_location").state == "5"
    device = dr.async_get(hass).async_get_device(identifiers={("grow_tracker", PLANT_SEED)})
    assert device.area_id == area.id
    counts = mock_entry.runtime_data.locations
    assert len(counts[LOC_FLOWER].plants()) == 0
    assert len(counts[LOC_PROP].plants()) == 1


@pytest.mark.parametrize(
    ("kind", "history"),
    [
        ("phase", []),  # mindestens ein Eintrag
        ("phase", [{"value": "blühen", "start": "2026-09-01"}]),  # unbekannte Phase
        ("phase", [{"value": "vegetative", "start": "2026-09-30"}]),  # Zukunft
        ("location", [{"value": "gibt_es_nicht", "start": "2026-09-01"}]),
    ],
)
async def test_edit_history_invalid(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    kind: str,
    history: list,
) -> None:
    client = await _client(hass, hass_ws_client)
    plant = setup_entry.runtime_data.plants[PLANT_SEED]
    before = (list(plant.history), list(plant.location_history))

    await client.send_json_auto_id(
        {"type": "grow_tracker/set_history", "plant_id": PLANT_SEED, "kind": kind, "history": history}
    )
    result = await client.receive_json()
    assert not result["success"]
    assert result["error"]["code"] == "invalid_format"
    assert (plant.history, plant.location_history) == before


async def test_edit_history_persists(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = await _client(hass, hass_ws_client)
    await client.send_json_auto_id(
        {
            "type": "grow_tracker/set_history",
            "plant_id": PLANT_SEED,
            "kind": "phase",
            "history": [{"value": "vegetative", "start": "2026-08-20"}],
        }
    )
    assert (await client.receive_json())["success"]

    assert await hass.config_entries.async_reload(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert setup_entry.runtime_data.plants[PLANT_SEED].history == [
        {"phase": "vegetative", "start": "2026-08-20"}
    ]
