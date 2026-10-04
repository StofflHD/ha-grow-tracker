"""Websocket-API für das Seitenleisten-Panel."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

import voluptuous as vol

from homeassistant.components import websocket_api
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.util import dt as dt_util

from .const import (
    DATA_HUB,
    SIGNAL_PANEL_UPDATE,
    WS_DELETE_NOTE,
    WS_SET_CUTTINGS_LOG,
    WS_SET_HISTORY,
    WS_SUBSCRIBE,
    WS_UPDATE_NOTE,
)
from .hub import GrowHub
from .plant import GrowPlant


@callback
def async_setup_websocket(hass: HomeAssistant) -> None:
    websocket_api.async_register_command(hass, ws_subscribe)
    websocket_api.async_register_command(hass, ws_set_cuttings_log)
    websocket_api.async_register_command(hass, ws_set_history)
    websocket_api.async_register_command(hass, ws_update_note)
    websocket_api.async_register_command(hass, ws_delete_note)


async def _async_plant_action(
    hass: HomeAssistant,
    connection: websocket_api.ActiveConnection,
    msg: dict[str, Any],
    action: Callable[[GrowPlant], Awaitable[None]],
) -> None:
    """Pflanze suchen, Aktion ausführen und Ergebnis/Fehler an das Panel senden."""
    hub: GrowHub | None = hass.data.get(DATA_HUB)
    plant = hub.plants.get(msg["plant_id"]) if hub else None
    if plant is None:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown plant")
        return
    try:
        await action(plant)
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_UPDATE_NOTE,
        vol.Required("plant_id"): str,
        vol.Required("note_id"): str,
        vol.Required("text"): str,
        vol.Required("date"): cv.datetime,
    }
)
@websocket_api.async_response
async def ws_update_note(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    await _async_plant_action(
        hass,
        connection,
        msg,
        lambda plant: plant.async_update_note(msg["note_id"], msg["text"], msg["date"]),
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_DELETE_NOTE,
        vol.Required("plant_id"): str,
        vol.Required("note_id"): str,
    }
)
@websocket_api.async_response
async def ws_delete_note(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    await _async_plant_action(
        hass, connection, msg, lambda plant: plant.async_delete_note(msg["note_id"])
    )


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SET_HISTORY,
        vol.Required("plant_id"): str,
        vol.Required("kind"): vol.In(["phase", "location"]),
        vol.Required("history"): [
            {vol.Required("value"): str, vol.Required("start"): cv.date},
        ],
    }
)
@websocket_api.async_response
async def ws_set_history(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Phasen- oder Standort-Historie einer Pflanze ersetzen."""
    hub: GrowHub | None = hass.data.get(DATA_HUB)
    plant = hub.plants.get(msg["plant_id"]) if hub else None
    if plant is None:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown plant")
        return
    try:
        await plant.async_set_history(msg["kind"], msg["history"])
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
        return
    connection.send_result(msg["id"])


@websocket_api.websocket_command(
    {
        vol.Required("type"): WS_SET_CUTTINGS_LOG,
        vol.Required("plant_id"): str,
        vol.Required("log"): [
            {
                vol.Required("date"): cv.date,
                vol.Required("count"): vol.All(vol.Coerce(int), vol.Range(min=1, max=1000)),
            }
        ],
    }
)
@websocket_api.async_response
async def ws_set_cuttings_log(
    hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
) -> None:
    """Schnitt-Protokoll einer Pflanze ersetzen."""
    hub: GrowHub | None = hass.data.get(DATA_HUB)
    plant = hub.plants.get(msg["plant_id"]) if hub else None
    if plant is None:
        connection.send_error(msg["id"], websocket_api.ERR_NOT_FOUND, "Unknown plant")
        return
    try:
        await plant.async_set_cuttings_log(msg["log"])
    except ServiceValidationError as err:
        connection.send_error(msg["id"], websocket_api.ERR_INVALID_FORMAT, str(err))
        return
    connection.send_result(msg["id"])


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
        "phenotype": plant.phenotype,
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
        # Mit IDs, damit das Panel die Historie bearbeiten kann
        "location_history": [
            {"location_id": item["location"], **named}
            for item, named in zip(
                plant.location_history, plant.location_history_named(), strict=True
            )
        ],
        "cuttings_count": len(plant.children()),
        "cuttings_taken": plant.cuttings_taken,
        # Vollständig, da das Panel das Protokoll als Ganzes bearbeitet und zurückschreibt
        "cuttings_log": plant.cuttings_log,
        "children": [child.subentry_id for child in plant.children()],
        "notes": plant.data["notes"][-50:],
        "phase_entity_id": plant.phase_entity_id,
        "location_entity_id": plant.location_entity_id,
    }
