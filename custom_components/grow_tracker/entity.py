"""Basis-Entities für Grow Tracker."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, SIGNAL_UPDATE
from .hub import GrowHub, GrowLocation
from .plant import GrowPlant


class GrowEntity(Entity):
    """Update bei jeder Datenänderung im Hub (inkl. Mitternacht)."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(
        self, hub: GrowHub, subentry_id: str, key: str, device_name: str, model: str | None
    ) -> None:
        self.hub = hub
        self._attr_unique_id = f"{subentry_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, subentry_id)},
            name=device_name,
            manufacturer="Grow Tracker",
            model=model,
        )

    async def async_added_to_hass(self) -> None:
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass,
                SIGNAL_UPDATE.format(self.hub.entry.entry_id),
                self.async_write_ha_state,
            )
        )


class PlantEntity(GrowEntity):
    def __init__(self, plant: GrowPlant, key: str) -> None:
        super().__init__(plant.hub, plant.subentry_id, key, plant.name, plant.strain)
        self.plant = plant


class LocationEntity(GrowEntity):
    def __init__(self, location: GrowLocation, key: str) -> None:
        super().__init__(location.hub, location.subentry_id, key, location.name, None)
        self.location = location
