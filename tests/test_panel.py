"""Tests für Websocket-API und Seitenleisten-Panel."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.grow_tracker.const import PANEL_URL_PATH
from homeassistant.core import HomeAssistant
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


async def test_ws_not_loaded(hass: HomeAssistant, hass_ws_client: WebSocketGenerator) -> None:
    assert await async_setup_component(hass, "grow_tracker", {})
    assert await async_setup_component(hass, "websocket_api", {})
    client = await hass_ws_client(hass)

    await client.send_json_auto_id({"type": "grow_tracker/subscribe"})
    assert (await client.receive_json())["success"]
    event = (await client.receive_json())["event"]
    assert event == {"loaded": False, "locations": [], "plants": []}


async def test_panel_registration(hass: HomeAssistant, mock_entry: MockConfigEntry) -> None:
    hass.config.components.add("frontend")
    with (
        patch(
            "custom_components.grow_tracker.panel.panel_custom.async_register_panel",
            new=AsyncMock(),
        ) as register,
        patch("custom_components.grow_tracker.panel.frontend.async_remove_panel") as remove,
    ):
        mock_entry.add_to_hass(hass)
        assert await hass.config_entries.async_setup(mock_entry.entry_id)
        await hass.async_block_till_done()

        register.assert_awaited_once()
        kwargs = register.await_args.kwargs
        assert kwargs["frontend_url_path"] == PANEL_URL_PATH
        assert kwargs["webcomponent_name"] == "grow-tracker-panel"
        assert kwargs["sidebar_title"] == "Grow Tracker"
        assert kwargs["module_url"].startswith("/grow_tracker_static/grow-tracker-panel.js?v=")

        assert await hass.config_entries.async_unload(mock_entry.entry_id)
        remove.assert_called_once_with(hass, PANEL_URL_PATH, warn_if_unknown=False)
