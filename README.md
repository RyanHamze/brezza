# Brezza

Custom Home Assistant integration for the Baby Brezza Formula Pro Advanced WiFi machine.

This integration creates a sensor for your Baby Brezza machine and exposes services that can start a saved bottle preset. It is designed so the service can be called from Home Assistant scripts, Google Home routines, and eventually Alexa routines.

Credit to [@joncar](https://github.com/joncar/ha-fpa) for the original Baby Brezza cloud API research.

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
2. Expose the script or entity you want Google Home to see.
3. Create a Home Assistant script using `brezza.make_bottle`.
4. Give the script a natural name like **Make Bottle**.
5. Sync devices in Google Home.
6. Create a Google Home routine that triggers the Home Assistant script.

Example phrase:

```text
Hey Google, make a bottle
```

## Example Script

See [example_script.yaml](example_script.yaml).

Update the `entity_id` and `bottle_id` after installation.

## Notes

- This integration uses the Baby Brezza cloud through `pybabyfpa`.
- It requires the machine to be connected to WiFi and visible in the Baby Brezza app.
- It does not bypass any physical machine checks. If the machine reports low water, missing bottle, lid open, funnel issue, or another non-ready state, bottle creation is blocked.
