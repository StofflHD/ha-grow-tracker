"""Websocket-API für das Seitenleisten-Panel."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .const import DATA_HUB, SIGNAL_PANEL_UPDATE, WS_SUBSCRIBE
from .hub import GrowHub
from .plant import GrowPlant


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_subscribe)


@websocket_api.websocket_command({vol.Required("type"): WS_SUBSCRIBE})
@callback
def ws_subscribe(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Übersicht senden und bei jeder Änderung erneut senden."""

    @callback
    def send_overview() -> None:
        connection.send_message(websocket_api.event_message(msg["id"], async_overview(hass)))

    connection.subscriptions[msg["id"]] = async_dispatcher_connect(
        hass, SIGNAL_PANEL_UPDATE, send_overview
    )
    connection.send_result(msg["id"])
    send_overview()


@callback
def async_overview(hass: HomeAssistant) -> dict[str, Any]:
    hub: GrowHub | None = hass.data.get(DATA_HUB)
    if hub is None:
        return {"loaded": False, "locations": [], "plants": []}

    return {
        "loaded": True,
        "entry_id": hub.entry.entry_id,
        "today": dt_util.now().date().isoformat(),
        "locations": [
            {
                "id": loc.subentry_id,
                "name": loc.name,
                "type": loc.location_type,
                "area_id": loc.area_id,
            }
            for loc in hub.locations.values()
        ],
        "plants": [_plant(plant) for plant in hub.plants.values()],
    }


def _plant(plant: GrowPlant) -> dict[str, Any]:
    harvest = plant.expected_harvest
    return {
        "id": plant.subentry_id,
        "name": plant.name,
        "strain": plant.strain,
        "origin": plant.origin,
        "logged_cutting": plant.logged_cutting,
        "mother_id": plant.mother_id,
        "mother_name": plant.mother_name,
        "phase": plant.phase,
        "phase_start": plant.phase_start.isoformat(),
        "grow_start": plant.grow_start.isoformat(),
        "days_total": plant.days_total,
        "days_in_phase": plant.days_in_phase,
        "week_in_phase": plant.week_in_phase,
        "flower_weeks": plant.flower_weeks,
        "expected_harvest": harvest.isoformat() if harvest else None,
        "days_to_harvest": (harvest - dt_util.now().date()).days if harvest else None,
        "location_id": plant.location_id,
        "location_name": plant.location_name,
        "location_start": plant.location_start.isoformat(),
        "days_at_location": plant.days_at_location,
        "history": plant.history,
        "phase_durations": plant.phase_durations(),
        "location_history": plant.location_history_named(),
        "cuttings_taken": plant.cuttings_taken,
        "cuttings_log": plant.cuttings_log[-20:],
        "children": [child.subentry_id for child in plant.children()],
        "notes": plant.data["notes"][-50:],
        "phase_entity_id": plant.phase_entity_id,
        "location_entity_id": plant.location_entity_id,
    }
