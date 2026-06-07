"""Config flow for Brezza integration."""

from __future__ import annotations

import logging
from typing import Any

import pybabyfpa
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("email"): str,
        vol.Required("password"): str,
    }
)


async def _validate_credentials(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Attempt login with provided credentials and return auth token."""
    api = pybabyfpa.Fpa()
    try:
        await api.login(data["email"], data["password"])
    except pybabyfpa.FpaError as err:
        raise BrezzaInvalidAuth from err
    return {"title": api.email, "refresh_token": api.refresh_token}


class BrezzaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle the Brezza setup flow."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show login form and handle submission."""
        if user_input is None:
            return self.async_show_form(
                step_id="user",
                data_schema=STEP_USER_DATA_SCHEMA,
            )

        errors = {}
        try:
            info = await _validate_credentials(self.hass, user_input)
        except BrezzaCannotConnect:
            errors["base"] = "cannot_connect"
        except BrezzaInvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:
            _LOGGER.exception("Unexpected error during Brezza setup")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(
                title=info["title"],
                data={"refresh_token": info["refresh_token"]},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )


class BrezzaCannotConnect(HomeAssistantError):
    """Cannot reach Baby Brezza servers."""


class BrezzaInvalidAuth(HomeAssistantError):
    """Email or password is incorrect."""
