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

### Dependencies
This component relies on [gkeepapi](https://github.com/kiwiz/gkeepapi), an unofficial client for the Google Keep API.

## Usage
I use this to keep Google Keep in sync with the Home Assistant shopping list and vice versa, allowing us to ask Google what is on the shopping list and add to HA through there.

### Home Assistant service
With this custom component loaded the following services are available.

#### Add to List
This service call has two data inputs: `title` and `things`, where `title` is the title of the Google Keep list to update, and `things` is a either a list or string of things to add to the list.
A string input for `things` is parsed for multiple things separated by 'and' and/or commas.

Here is an example of using the service in an automation to add batteries for smart home devices to a list titled "Home Supplies":
```yaml
automation:
  - alias: Low Battery Notification
    trigger:
      - platform: numeric_state
        entity_id:
        - sensor.front_door_battery
        - sensor.hallway_smoke_co_alarm_battery
        - sensor.bedroom_sensor_battery
        below: 20
    action:
      service: gkeep.add_to_list
      data:
        title: 'Home Supplies'
        things: 'Batteries for {{ trigger.to_state.name }}.'
```

#### Sync Shopping List
If the Home Assistant Shopping List integration is enabled, you can use this service to synchronize your google keep list into the home assistant shopping list.
This service call has just one data input: `title` that is the Google Keep list to sync.

Here is an example of using the service in an automation to sync the list after adding an items:
```yaml
automation:
  - alias: Low Battery Notification
    trigger:
      - platform: numeric_state
        entity_id:
        - sensor.front_door_battery
        - sensor.hallway_smoke_co_alarm_battery
        - sensor.bedroom_sensor_battery
        below: 20
    action:
      - service: gkeep.add_to_list
        data:
          title: 'Home Supplies'
          things: 'Batteries for {{ trigger.to_state.name }}.'
      - delay:
        seconds: 10
      - service: gkeep.sync_shopping_list
        data:
          title: 'Home Supplies'
```

Another approach could be to schedule the sync once in a while:
```yaml
automation:
  - alias: Sync google keep
    trigger:
      - platform: time_pattern
        hours: "07"
        minutes: 0
        seconds: 0
    action:
      - service: gkeep.sync_shopping_list
        data:
          title: 'Home Supplies'
```

#### Clear Shopping List
You can use this service to delete a list, this intakes a title parameter.

#### Share Shopping List
You can use this service to share a shopping list

#### Todo
- Make readthedocs
- Add rest of gkeepapi endpoints
- Change current services to be more generic (clear_shopping_list should be clear_list for example as we're not just for shopping lists)