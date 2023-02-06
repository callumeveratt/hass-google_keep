"""Schemas for Google Keep"""

from .const import (
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_LIST_NAME,
    SERVICE_LIST_NAME,
    SERVICE_LIST_ITEM,
    DEFAULT_LIST_NAME,
    SERVICE_LIST_EMAIL
)

import voluptuous as vol
import homeassistant.helpers.config_validation as cv

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_LIST_NAME, default=DEFAULT_LIST_NAME): cv.string,
    }),
}, extra=vol.ALLOW_EXTRA)

SERVICE_LIST_SCHEMA = vol.Schema({
    vol.Optional(SERVICE_LIST_NAME): cv.string,
    vol.Required(SERVICE_LIST_ITEM): cv.ensure_list_csv,
})

SERVICE_LIST_NAME_SCHEMA = vol.Schema({
    vol.Optional(SERVICE_LIST_NAME): cv.string,
})

SERVICE_LIST_EMAIL_SCHEMA = vol.Schema({
    vol.Optional(SERVICE_LIST_NAME): cv.string,
    vol.Required(SERVICE_LIST_EMAIL): cv.string
})
