# Work From Home Tracker

A Home Assistant custom integration to track when you're working from home and log air conditioner usage — useful for personal analytics, automations, and tax reporting.

## ✅ Features

- Determines WFH status based on:
  - Presence sensors (e.g., `device_tracker`, `person`)
  - Work device connection (e.g., binary sensor for Wi-Fi)
- Detects air conditioner running status and HVAC mode
- Creates a sensor entity: `sensor.work_from_home`
- Logs daily status to a CSV file (configurable path)

---

## 🛠 Installation (via HACS)

1. Go to HACS → Integrations → Custom Repositories.
2. Add this repository:
https://github.com/yourusername/ha-wfh-tracker
as a *"Integration"*.
3. Install it and restart Home Assistant.

---

## ⚙️ Configuration

Add to `configuration.yaml`:

```yaml
sensor:
- platform: work_from_home_tracker
 presence_sensors:
   - device_tracker.your_phone
   - person.your_name
 work_device_sensors:
   - binary_sensor.work_laptop
 climate_entity: climate.living_room
 log_file: logs/wfh_log.csv  # relative to /config/, or use absolute path like /media/wfh.csv
 ```

| Parameter             | Description                                                         | Required                      |
| --------------------- | ------------------------------------------------------------------- | ----------------------------- |
| `presence_sensors`    | List of presence-related sensors (e.g., `device_tracker`, `person`) | ✅                             |
| `work_device_sensors` | List of sensors indicating your work device is online               | ✅                             |
| `climate_entity`      | Your air conditioning/climate entity                                | ✅                             |
| `log_file`            | File path for daily log (relative to `/config/` or absolute)        | ❌ (defaults to `wfh_log.csv`) |

🧪 Sensor Output Example
state: "on"
attributes:
  working_from_home: true
  ac_running: true
  hvac_mode: "cooling"
  last_updated: 2025-07-03T08:35:00+00:00

📝 CSV Logging
A new row is appended to the log file once per day when you're working from home:

📝 CSV Logging

A new row is appended to the log file once per day when you're working from home:

```date,time,working_from_home,ac_running,hvac_mode
2025-07-03,09:00:00,True,True,cooling
```
Relative log path: `log_file: logs/my_log.csv → saved to /config/logs/my_log.csv`

Absolute log path: `log_file: /media/logs/wfh.csv`

📊 Use Cases
Tax Reporting: Export your log at tax time.

Daily Summary: Show sensor.work_from_home state on your dashboard.

Automation Example:
```
automation:
  - alias: "Announce WFH Day"
    trigger:
      - platform: state
        entity_id: sensor.work_from_home
        to: "on"
    action:
      - service: notify.mobile_app_yourdevice
        data:
          message: "You're working from home today — remember to log your hours!"
```




