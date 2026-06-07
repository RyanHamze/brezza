"""Brezza integration for Home Assistant."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

import pybabyfpa

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brezza from a config entry."""
    api = pybabyfpa.Fpa()
    await api.refresh(entry.data["refresh_token"])
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = api
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    _LOGGER.info("Brezza integration loaded successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Brezza config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        api = hass.data[DOMAIN].pop(entry.entry_id)
        if api:
            await api.close()
    return unload_ok
