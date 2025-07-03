"""Sensor for Work From Home Tracker."""

from datetime import datetime, timedelta
import os
import csv
import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.const import STATE_ON
from homeassistant.util import dt as dt_util
from .const import DOMAIN, CONF_PRESENCE_SENSORS, CONF_WORK_DEVICE_SENSORS, CONF_CLIMATE_ENTITY, CONF_LOG_FILE, DEFAULT_NAME, DEFAULT_LOG_FILE

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=5)

class WorkFromHomeSensor(SensorEntity):
    def __init__(self, hass, presence_sensors, work_device_sensors, climate_entity, log_file):
        self._hass = hass
        self._presence_sensors = presence_sensors
        self._work_device_sensors = work_device_sensors
        self._climate_entity = climate_entity
        self._attr_name = DEFAULT_NAME
        self._attr_unique_id = "work_from_home_status"
        self._state = None
        self._attributes = {}
        self._last_logged_date = None

        if log_file:
            self._log_file_path = (
                log_file if os.path.isabs(log_file)
                else hass.config.path(log_file)
            )
        else:
            self._log_file_path = hass.config.path(DEFAULT_LOG_FILE)

    async def async_update(self):
        now = dt_util.now()
        is_home = any(
            self._hass.states.get(e).state == STATE_ON
            for e in self._presence_sensors
            if self._hass.states.get(e) is not None
        )
        work_device_connected = any(
            self._hass.states.get(e).state == STATE_ON
            for e in self._work_device_sensors
            if self._hass.states.get(e) is not None
        )

        climate_state = self._hass.states.get(self._climate_entity)
        ac_running = False
        hvac_mode = None

        if climate_state:
            hvac_mode = climate_state.attributes.get("hvac_action", "unknown")
            ac_running = hvac_mode in ["cooling", "heating"]

        working_from_home = is_home and work_device_connected

        self._state = "on" if working_from_home else "off"
        self._attributes = {
            "working_from_home": working_from_home,
            "ac_running": ac_running,
            "hvac_mode": hvac_mode,
            "last_updated": now.isoformat()
        }

        if working_from_home and (self._last_logged_date != now.date()):
            self._write_log(now.date(), now.time(), working_from_home, ac_running, hvac_mode)
            self._last_logged_date = now.date()

    def _write_log(self, date, time, working_from_home, ac_running, hvac_mode):
        try:
            file_exists = os.path.isfile(self._log_file_path)
            with open(self._log_file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                if not file_exists:
                    writer.writerow(["date", "time", "working_from_home", "ac_running", "hvac_mode"])
                writer.writerow([date, time.replace(microsecond=0), working_from_home, ac_running, hvac_mode])
            _LOGGER.debug("Logged WFH data to %s", self._log_file_path)
        except Exception as e:
            _LOGGER.error("Failed to log WFH data: %s", e)

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes
