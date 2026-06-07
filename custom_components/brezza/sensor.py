"""Brezza sensor platform."""

import logging

import pybabyfpa
import voluptuous as vol

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers import config_validation as cv, entity_platform

from .const import ATTR_BOTTLE_ID, DOMAIN

_LOGGER = logging.getLogger(__name__)

STATE_ICONS = {
    "requesting_bottle": "mdi:transfer-down",
    "making_bottle": "mdi:transfer-down",
    "full_bottle": "mdi:cup",
    "funnel_cleaning": "mdi:liquid-spot",
    "funnel_missing": "mdi:filter-off-outline",
    "lid_open": "mdi:projector-screen-variant-off-outline",
    "low_water": "mdi:water-off",
    "no_bottle": "mdi:cup-off-outline",
    "ready": "mdi:cup-outline",
}


async def async_setup_entry(hass, config_entry, async_add_entities, discovery_info=None):
    """Set up Brezza sensors."""
    api = hass.data[DOMAIN][config_entry.entry_id]

    if not api.has_me:
        await api.get_me()

    for device in api.devices:
        await api.connect_to_device(device.device_id)

    entities = [BrezzaSensor(api, device) for device in api.devices]
    async_add_entities(entities)

    platform = entity_platform.async_get_current_platform()

    platform.async_register_entity_service(
        "make_bottle",
        {vol.Required(ATTR_BOTTLE_ID): cv.positive_int},
        "make_bottle",
    )

    platform.async_register_entity_service(
        "turn_on",
        {vol.Required(ATTR_BOTTLE_ID): cv.positive_int},
        "make_bottle",
    )


class BrezzaSensor(SensorEntity):
    """Represents the Brezza machine state."""

    def __init__(self, api: pybabyfpa.Fpa, device: pybabyfpa.FpaDevice):
        """Initialize."""
        self._api = api
        self._device = device
        self._bottle_requested = False
        self._bottle_ready = False
        self._prev_making = False
        self._prev_no_bottle = False

    async def async_added_to_hass(self):
        """Subscribe to device updates."""
        self._prev_making = False
        self._prev_no_bottle = False

        def on_update(device: pybabyfpa.FpaDevice):
            if device.device_id != self._device.device_id:
                return
            if not self._prev_making and device.shadow.making_bottle:
                self._bottle_requested = False
            if (
                self._prev_making
                and not device.shadow.making_bottle
                and not device.shadow.bottle_missing
            ):
                self._bottle_ready = True
            if not self._prev_no_bottle and device.shadow.bottle_missing:
                self._bottle_requested = False
                self._bottle_ready = False
            self._prev_making = device.shadow.making_bottle
            self._prev_no_bottle = device.shadow.bottle_missing
            self._device = device
            self.schedule_update_ha_state()

        self.async_on_remove(self._api.add_listener(on_update))

    @property
    def unique_id(self) -> str:
        return self._device.device_id

    @property
    def name(self) -> str:
        return self._device.title

    @property
    def available(self) -> bool:
        return self._device.connected

    @property
    def should_poll(self) -> bool:
        return False

    @property
    def device_info(self) -> dict:
        return {
            "identifiers": {(DOMAIN, self._device.device_id)},
            "manufacturer": "Baby Brezza",
            "model": "Formula Pro Advanced WiFi",
            "name": self._device.title,
        }

    @property
    def state(self) -> str:
        if self._bottle_requested:
            return "requesting_bottle"
        if self._device.shadow.making_bottle:
            return "making_bottle"
        if self._bottle_ready:
            return "full_bottle"
        if self._device.shadow.funnel_cleaning_needed:
            return "funnel_cleaning"
        if self._device.shadow.funnel_out:
            return "funnel_missing"
        if self._device.shadow.lid_open:
            return "lid_open"
        if self._device.shadow.low_water:
            return "low_water"
        if self._device.shadow.bottle_missing:
            return "no_bottle"
        return "ready"

    @property
    def assumed_state(self) -> bool:
        return self._bottle_requested

    @property
    def icon(self) -> str:
        return STATE_ICONS.get(self.state, "mdi:baby-bottle")

    @property
    def extra_state_attributes(self) -> dict:
        attrs = {
            "temperature": self._device.shadow.temperature,
            "powder": self._device.shadow.powder,
            "volume": self._device.shadow.volume,
            "volume_unit": self._device.shadow.volume_unit,
            "making_bottle": self._device.shadow.making_bottle,
            "water_only": self._device.shadow.water_only,
            "no_bottle": self._device.shadow.bottle_missing,
            "low_water": self._device.shadow.low_water,
            "lid_open": self._device.shadow.lid_open,
            "funnel_missing": self._device.shadow.funnel_out,
            "funnel_cleaning": self._device.shadow.funnel_cleaning_needed,
        }
        for bottle in self._device.bottles:
            attrs[f"bottle_{bottle.id}"] = (
                f"{bottle.volume}{bottle.volume_unit} - {str(bottle.formula)}"
            )
        return attrs

    async def make_bottle(self, **kwargs):
        """Start making a bottle. Only runs when machine is ready."""
        bottle_id = kwargs.get(ATTR_BOTTLE_ID)
        if self.state != "ready":
            _LOGGER.warning(
                "Brezza cannot make a bottle right now. Current state: %s", self.state
            )
            return
        _LOGGER.info("Brezza: starting bottle preset %s", bottle_id)
        self._bottle_requested = True
        self.schedule_update_ha_state()
        await self._api.start_bottle(bottle_id)
