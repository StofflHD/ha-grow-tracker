"""Tests für Websocket-API und Seitenleisten-Panel."""

from __future__ import annotations

from collections.abc import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.grow_tracker.const import PANEL_URL_PATH
from homeassistant.config_entries import ConfigEntryDisabler
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component

from .conftest import LOC_FLOWER, PLANT_MOTHER, PLANT_SEED


async def test_ws_subscribe(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "grow_tracker/subscribe"})
    result = await client.receive_json()
    assert result["success"]

    event = (await client.receive_json())["event"]
    assert event["loaded"] is True
    assert event["today"] == "2026-09-15"
    assert [loc["name"] for loc in event["locations"]] == ["Mutterschrank", "Blüte groß", "Anzucht"]

    seed = next(p for p in event["plants"] if p["id"] == PLANT_SEED)
    assert seed["phase"] == "germination"
    assert seed["location_id"] == LOC_FLOWER
    assert seed["days_total"] == 14
    assert seed["phase_entity_id"].startswith("select.")
    assert seed["location_entity_id"].startswith("select.")

    # Änderung wird live nachgeschoben
    await hass.services.async_call(
        "grow_tracker",
        "set_phase",
        {"entity_id": seed["phase_entity_id"], "phase": "flowering"},
        blocking=True,
    )
    event = (await client.receive_json())["event"]
    seed = next(p for p in event["plants"] if p["id"] == PLANT_SEED)
    assert seed["phase"] == "flowering"
    assert seed["expected_harvest"] == "2026-11-17"
    assert seed["days_to_harvest"] == 63

    mother = next(p for p in event["plants"] if p["id"] == PLANT_MOTHER)
    assert mother["phase"] == "mother"


async def test_ws_after_creating_cuttings(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Nach dem Reload durch neue Stecklinge muss das Panel geladene Daten bekommen."""
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "grow_tracker/subscribe"})
    assert (await client.receive_json())["success"]
    event = (await client.receive_json())["event"]
    mother = next(p for p in event["plants"] if p["id"] == PLANT_MOTHER)

    await hass.services.async_call(
        "grow_tracker",
        "take_cuttings",
        {"entity_id": mother["phase_entity_id"], "count": 2, "create_plants": True},
        blocking=True,
    )
    await hass.async_block_till_done()

    # 1. Meldung: Schnitt protokolliert, 2. Meldung: nach dem Reload
    first = (await client.receive_json())["event"]
    assert first["loaded"] is True
    after_reload = (await client.receive_json())["event"]
    assert after_reload["loaded"] is True
    assert len(after_reload["plants"]) == 4
    mother = next(p for p in after_reload["plants"] if p["id"] == PLANT_MOTHER)
    assert len(mother["children"]) == 2
    assert mother["cuttings_count"] == 2
    assert mother["phase_entity_id"] is not None


async def test_ws_after_deleting_mother(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    """Löschen aus dem Panel entfernt die Subentry – Stecklinge behalten den Mutternamen."""
    phase_entity = er.async_get(hass).async_get_entity_id(
        "select", "grow_tracker", f"{PLANT_MOTHER}_phase"
    )
    await hass.services.async_call(
        "grow_tracker",
        "take_cuttings",
        {"entity_id": phase_entity, "count": 1, "create_plants": True},
        blocking=True,
    )
    await hass.async_block_till_done()

    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id({"type": "grow_tracker/subscribe"})
    assert (await client.receive_json())["success"]
    assert len((await client.receive_json())["event"]["plants"]) == 3

    # Gleicher Aufruf wie "config_entries/subentries/delete" aus dem Panel
    hass.config_entries.async_remove_subentry(setup_entry, PLANT_MOTHER)
    await hass.async_block_till_done()

    event = (await client.receive_json())["event"]
    assert event["loaded"] is True
    assert PLANT_MOTHER not in [p["id"] for p in event["plants"]]
    cutting = next(p for p in event["plants"] if p["origin"] == "cutting")
    assert cutting["mother_name"] == "Mutter Gelato"


async def test_ws_set_cuttings_log(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    mother = setup_entry.runtime_data.plants[PLANT_MOTHER]

    await client.send_json_auto_id(
        {
            "type": "grow_tracker/set_cuttings_log",
            "plant_id": PLANT_MOTHER,
            "log": [{"date": "2026-09-10", "count": 5}, {"date": "2026-08-01", "count": "3"}],
        }
    )
    assert (await client.receive_json())["success"]
    # Nach Datum sortiert, Anzahl als Zahl
    assert mother.cuttings_log == [
        {"date": "2026-08-01", "count": 3},
        {"date": "2026-09-10", "count": 5},
    ]
    sensor = hass.states.get(
        er.async_get(hass).async_get_entity_id("sensor", "grow_tracker", f"{PLANT_MOTHER}_cuttings_taken")
    )
    assert sensor.attributes["taken_total"] == 8

    # Leeres Protokoll ist erlaubt
    await client.send_json_auto_id(
        {"type": "grow_tracker/set_cuttings_log", "plant_id": PLANT_MOTHER, "log": []}
    )
    assert (await client.receive_json())["success"]
    assert mother.cuttings_log == []


@pytest.mark.parametrize(
    ("entry", "error"),
    [
        ({"date": "2026-09-20", "count": 1}, "invalid_format"),  # Zukunft
        ({"date": "2026-09-10", "count": 0}, "invalid_format"),
        ({"date": "kein-datum", "count": 1}, "invalid_format"),
    ],
)
async def test_ws_set_cuttings_log_invalid(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    entry: dict,
    error: str,
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "grow_tracker/set_cuttings_log", "plant_id": PLANT_MOTHER, "log": [entry]}
    )
    result = await client.receive_json()
    assert not result["success"]
    assert result["error"]["code"] == error
    assert setup_entry.runtime_data.plants[PLANT_MOTHER].cuttings_log == []


async def test_ws_set_cuttings_log_unknown_plant(
    hass: HomeAssistant, setup_entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)
    await client.send_json_auto_id(
        {"type": "grow_tracker/set_cuttings_log", "plant_id": "gibt_es_nicht", "log": []}
    )
    result = await client.receive_json()
    assert result["error"]["code"] == "not_found"


async def test_ws_not_loaded(hass: HomeAssistant, hass_ws_client: WebSocketGenerator) -> None:
    assert await async_setup_component(hass, "grow_tracker", {})
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "grow_tracker/subscribe"})
    assert (await client.receive_json())["success"]
    event = (await client.receive_json())["event"]
    assert event == {"loaded": False, "locations": [], "plants": []}


@pytest.fixture
def panel_mocks(hass: HomeAssistant) -> Generator[tuple[AsyncMock, MagicMock]]:
    hass.config.components.add("frontend")
    with (
        patch(
            "custom_components.grow_tracker.panel.panel_custom.async_register_panel",
            new=AsyncMock(),
        ) as register,
        patch("custom_components.grow_tracker.panel.frontend.async_remove_panel") as remove,
    ):
        yield register, remove


async def test_panel_registration(
    hass: HomeAssistant, panel_mocks: tuple[AsyncMock, MagicMock], setup_entry: MockConfigEntry
) -> None:
    register, remove = panel_mocks
    register.assert_awaited_once()
    kwargs = register.await_args.kwargs
    assert kwargs["frontend_url_path"] == PANEL_URL_PATH
    assert kwargs["webcomponent_name"] == "grow-tracker-panel"
    assert kwargs["sidebar_title"] == "Grow Tracker"
    assert kwargs["module_url"].startswith("/grow_tracker_static/grow-tracker-panel.js?v=")

    # Löschen entfernt das Panel
    assert await hass.config_entries.async_remove(setup_entry.entry_id)
    remove.assert_called_once_with(hass, PANEL_URL_PATH, warn_if_unknown=False)


async def test_panel_survives_reload(
    hass: HomeAssistant, panel_mocks: tuple[AsyncMock, MagicMock], setup_entry: MockConfigEntry
) -> None:
    """Stecklinge anlegen lädt den Eintrag neu – das Panel darf nicht verschwinden."""
    register, remove = panel_mocks
    phase_entity = er.async_get(hass).async_get_entity_id(
        "select", "grow_tracker", f"{PLANT_MOTHER}_phase"
    )
    await hass.services.async_call(
        "grow_tracker",
        "take_cuttings",
        {"entity_id": phase_entity, "count": 2, "create_plants": True},
        blocking=True,
    )
    await hass.async_block_till_done()
    assert len(setup_entry.runtime_data.plants) == 4  # Reload ist passiert

    assert await hass.config_entries.async_reload(setup_entry.entry_id)
    await hass.async_block_till_done()

    remove.assert_not_called()
    register.assert_awaited_once()


async def test_panel_removed_when_disabled(
    hass: HomeAssistant, panel_mocks: tuple[AsyncMock, MagicMock], setup_entry: MockConfigEntry
) -> None:
    _, remove = panel_mocks
    assert await hass.config_entries.async_set_disabled_by(
        setup_entry.entry_id, ConfigEntryDisabler.USER
    )
    await hass.async_block_till_done()
    remove.assert_called_once_with(hass, PANEL_URL_PATH, warn_if_unknown=False)
