# Brezza

Custom Home Assistant integration for the Baby Brezza Formula Pro Advanced WiFi machine.

This integration creates a sensor for your Baby Brezza machine and exposes services that can start a saved bottle preset. It is designed so the service can be called from Home Assistant scripts, Google Home routines, and eventually Alexa routines.

Credit to [@joncar](https://github.com/joncar/ha-fpa) for the original Baby Brezza cloud API research.

## Quick Links

[![Open your Home Assistant instance and open this repository in HACS.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=RyanHamze&repository=brezza&category=integration)

[![Open your Home Assistant instance and start setting up Brezza.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start?domain=brezza)

[![Open your Home Assistant Cloud settings.](https://my.home-assistant.io/badges/cloud.svg)](https://my.home-assistant.io/redirect/cloud/)

[![Open your Home Assistant voice assistants settings.](https://my.home-assistant.io/badges/voice_assistants.svg)](https://my.home-assistant.io/redirect/voice_assistants/)

[![Open your Home Assistant scripts.](https://my.home-assistant.io/badges/scripts.svg)](https://my.home-assistant.io/redirect/scripts/)

[![Open your Home Assistant overview dashboard.](https://my.home-assistant.io/badges/overview.svg)](https://my.home-assistant.io/redirect/overview/)

These buttons open the right page in your own Home Assistant instance. They do not make changes automatically, so you still need to confirm downloads, enter credentials, create scripts, expose entities, and add dashboard cards yourself.

## Installation With HACS

1. In Home Assistant, open HACS.
2. Go to **Integrations**.
3. Open the three-dot menu and choose **Custom repositories**.
4. Add this repository URL:

   ```text
   https://github.com/RyanHamze/brezza
   ```

5. Set the category to **Integration**.
6. Install **Brezza**.
7. Restart Home Assistant.

## Setup

1. In Home Assistant, go to **Settings > Devices & services**.
2. Click **Add Integration**.
3. Search for **Brezza**.
4. Enter the email and password you use in the Baby Brezza app.

After setup, Home Assistant should create a sensor for your machine, likely named `sensor.brezza` if the machine is named "Brezza" in the Baby Brezza app.

## Finding Your Bottle ID

The Baby Brezza cloud API uses numeric IDs for saved bottle presets.

After the integration is installed:

1. Open the Brezza sensor in Home Assistant.
2. Check its attributes.
3. Look for attributes like:

   ```text
   bottle_1: 4oz - Formula Name
   bottle_2: 6oz - Formula Name
   ```

Use only the number after `bottle_` as your `bottle_id`.

## Services

### `brezza.make_bottle`

Starts the selected bottle preset.

```yaml
service: brezza.make_bottle
target:
  entity_id: sensor.brezza
data:
  bottle_id: 1
```

The machine must be in the `ready` state. If it is not ready, the service logs a warning and does nothing.

### `brezza.turn_on`

Alias for `brezza.make_bottle`. This exists for voice assistant compatibility with Google Home and Alexa-style routines.

```yaml
service: brezza.turn_on
target:
  entity_id: sensor.brezza
data:
  bottle_id: 1
```

## Google Home Setup

The easiest path is Home Assistant Cloud / Nabu Casa.

1. Confirm Home Assistant Cloud is active.
2. Create a Home Assistant script using `brezza.make_bottle`.
3. Give the script a natural name like **Make Bottle**.
4. Assign the script to an area, such as **Kitchen**. Google Assistant may not show exposed scripts unless they belong to an area.
5. Expose the script to Google Assistant under **Settings > Voice assistants > Expose**.
6. Sync devices in Google Home.
7. Create a Google Home routine that triggers the Home Assistant script.

Example phrase:

```text
Hey Google, make a bottle
```

## Example Script

See [example_script.yaml](example_script.yaml).

Update the `entity_id` and `bottle_id` after installation.

## Dashboard Button

Create a Home Assistant dashboard button and use your own `entity_id` and `bottle_id`:

```yaml
show_name: true
show_icon: true
show_state: true
type: button
entity: sensor.brezza
name: Make Bottle
icon: mdi:baby-bottle
tap_action:
  action: perform-action
  perform_action: brezza.make_bottle
  target:
    entity_id: sensor.brezza
  data:
    bottle_id: 1
```

If your Home Assistant version uses the older dashboard action syntax, use:

```yaml
tap_action:
  action: call-service
  service: brezza.make_bottle
  target:
    entity_id: sensor.brezza
  data:
    bottle_id: 1
```

## FAQ

### Can the README buttons create my script, expose Google/Alexa, or add my dashboard button automatically?

No. My Home Assistant links are navigation shortcuts. They can open the right page in your Home Assistant instance, but they do not make configuration changes automatically.

### Google Assistant sees my other Home Assistant devices, but not Make Bottle.

Make sure **Make Bottle** is a Home Assistant script, not only a dashboard button. Google Assistant cannot press Home Assistant dashboard buttons.

Then check these settings:

1. Go to **Settings > Automations & scenes > Scripts**.
2. Open the **Make Bottle** script.
3. Assign it to an area, such as **Kitchen**.
4. Go to **Settings > Voice assistants > Expose**.
5. Expose the `script.make_bottle` entity to Google Assistant.
6. Say, "Hey Google, sync my devices."

After syncing, try "Hey Google, turn on Make Bottle" or create a Google Home routine with the phrase "make a bottle."

## Notes

- This integration uses the Baby Brezza cloud through `pybabyfpa`.
- It requires the machine to be connected to WiFi and visible in the Baby Brezza app.
- It does not bypass any physical machine checks. If the machine reports low water, missing bottle, lid open, funnel issue, or another non-ready state, bottle creation is blocked.
