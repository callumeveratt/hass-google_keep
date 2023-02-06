# hass-google_keep
Custom component for [Home Assistant](https://home-assistant.io/) to enable adding to and updating lists on [Google Keep](https://keep.google.com/).

## Installation
Add the `gkeep` folder and its contents to the `custom_components` folder in your Home Assistant configuration directory, and add the `gkeep` component to your `configuration.yaml` file.

### Example configuration.yaml entry
```yaml
gkeep:
  username: "this_is_my_username@gmail.com"
  password: "this_is_my_Google_App_password"
  list_name: "Grocery"
```
`list_name` is an optional configuration key that sets a default name for the Keep list to update.