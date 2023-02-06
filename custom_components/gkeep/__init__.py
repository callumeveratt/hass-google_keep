"""Custom component for the Google Keep API"""

from .const import (
    DOMAIN,
    CONF_USERNAME,
    CONF_PASSWORD,
    CONF_LIST_NAME,
    SERVICE_LIST_NAME,
    SERVICE_LIST_ITEM,
    SHOPPING_LIST_DOMAIN,
    SERVICE_LIST_EMAIL
)

from .schema import (
    SERVICE_LIST_SCHEMA,
    SERVICE_LIST_NAME_SCHEMA,
    SERVICE_LIST_EMAIL_SCHEMA
)

import logging
from homeassistant.core import callback

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    """Setup the google_keep component."""

    import gkeepapi

    config = config.get(DOMAIN)

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    default_list_name = config.get(CONF_LIST_NAME)

    keep = gkeepapi.Keep()

    # Attempt to login
    login_success = keep.login(username, password)
    if not login_success:
        _LOGGER.error("Google Keep login failed.")
        return False

    def add_to_list(call):
        """Add things to a Google Keep list."""

        list_name = call.data.get(SERVICE_LIST_NAME, default_list_name)
        things = call.data.get(SERVICE_LIST_ITEM)

        # Split any things in the list separated by ' and '
        things = [x for thing in things for x in thing.split(' and ')]

        # Sync with Google servers
        keep.sync()

        list_to_update = _get_or_create_list_name_(list_name)

        _LOGGER.info("Things to add: {}".format(things))
        # For each thing,
        for thing in things:
            # ...is the thing already on the list?
            for old_thing in list_to_update.items:
                # Compare the new thing to each existing thing
                if old_thing.text.lower() == thing.lower():
                    # Uncheck the thing if it is already on the list.
                    old_thing.checked = False
                    break
            # If the thing is not already on the list,
            else:
                # ...add the thing to the list, unchecked.
                list_to_update.add(thing, False)

        # Sync with Google servers
        keep.sync()
    
    def sync_shopping_list(call):
        """Get things from a Google Keep list."""

        list_name = call.data.get(SERVICE_LIST_NAME, default_list_name)

        # Sync with Google servers
        keep.sync()

        google_keep_list = _get_or_create_list_name_(list_name)
        google_keep_list_items = []

        for item in google_keep_list.items: google_keep_list_items.append({"text": item.text.lower().strip(), "checked": item.checked})
        google_keep_list_items.sort(key=lambda x: x["text"])
        google_keep_distinct_items = []

        from itertools import groupby
        for _, g in groupby(google_keep_list_items, key=lambda item: item["text"]):
            group = list(g)
            checked = [item for item in group if not item["checked"]]
            thing = checked[0] if checked else group[0]
            google_keep_distinct_items.append(thing)

        google_keep_set = set([item["text"] for item in google_keep_distinct_items])
        shopping_set = set([item["name"].lower().strip() for item in SHOPPING_LIST.items])

        elements_to_add = google_keep_set - shopping_set
        elements_to_check = google_keep_set & shopping_set

        items_to_add = [item for item in google_keep_distinct_items if item["text"] in elements_to_add]
        for item in items_to_add:
            if not item["checked"]:
                hass.services.call("shopping_list", 'add_item', {"name": item["text"]}, True)

        items_to_update = [item for item in google_keep_distinct_items if item["text"] in elements_to_check]
        for item in items_to_update:
            if item["checked"]:
                shopping_list_service = "complete_item"
            else:
                shopping_list_service = "incomplete_item"

            hass.services.call("shopping_list", shopping_list_service, {"name": item["text"]}, True)

    def clear_shopping_list(call):
        """Clear a google keep shopping list."""        
        list_name = call.data.get(SERVICE_LIST_NAME, default_list_name)

        google_keep_list = _get_or_create_list_name_(list_name)
        google_keep_list.delete()
        keep.sync()

    def share_shopping_list(call):
        """Share a google keep list"""
        list_name = call.data.get(SERVICE_LIST_NAME, default_list_name)
        email = call.data.get(SERVICE_LIST_EMAIL)

        google_keep_list = _get_or_create_list_name_(list_name)

        if not email in google_keep_list.collaborators.all():
            google_keep_list.collaborators.add(email)
            keep.sync()

    def _get_or_create_list_name_(list_name):
        """ Find the target list amongst all the Keep notes/lists """

        for l in keep.all():
            if l.title == list_name:
                list_object = l
                break
        else:
            _LOGGER.info("List with name {} not found on Keep. Creating new list.".format(list_name))
            list_object = keep.createList(list_name)
        
        return list_object


    # Register the service google_keep.add_to_list with Home Assistant.
    hass.services.register(DOMAIN, 'add_to_list', add_to_list, schema=SERVICE_LIST_SCHEMA)
    hass.services.register(DOMAIN, 'clear_shopping_list', clear_shopping_list, schema=SERVICE_LIST_SCHEMA)
    hass.services.register(DOMAIN, 'share_shopping_list', share_shopping_list, schema=SERVICE_LIST_EMAIL_SCHEMA)

    # Register the service google_keep.sync_shopping_list with Home Assistant.
    SHOPPING_LIST = hass.data.get(SHOPPING_LIST_DOMAIN)
    if SHOPPING_LIST:
        hass.services.register(DOMAIN, 'sync_shopping_list', sync_shopping_list, schema=SERVICE_LIST_NAME_SCHEMA)

    # Return boolean to indicate successful initialization.
    return True
