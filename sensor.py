from datetime import timedelta

from homeassistant.const import LENGTH_METERS, LENGTH_KILOMETERS
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle


from .constants import THROTTLE_MINS

from .utils import _get_athlete_data

import custom_components.strava as strava

import logging

_LOGGER = logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Create platform for Strava """

    # Load the config to the data layer
    cfg = hass.data[strava.DATA_KEY]

    # Add the athlete sensor
    add_devices([
        StravaAthleteEntity(cfg, "strava.athlete")
    ])

    _LOGGER.info("The Strava component is ready!")


class StravaStatSensor:

    def __init__(self, base, sensor_name, value, unit=None):
        self.base = base
        self.sensor_name = sensor_name
        self.value = value
        self.unit = unit

    def _gen_friendly_name(self):
        return self.sensor_name.replace("_", " ").capitalize()

    def get_stats_hours(self):
        sensor_name, state, attrs = self.get_stats()

        sensor_name = f"{sensor_name}_hours"

        state = round(state / 3600, 2)

        attrs.update({
            "unit_of_measurement": "hours"
        })

        return sensor_name, state, attrs


    def get_stats_km(self):
        sensor_name, state, attrs = self.get_stats()

        sensor_name = f"{sensor_name}_km"

        state = round(state / 1000, 2)

        attrs.update({
            "unit_of_measurement": LENGTH_KILOMETERS
        })

        return sensor_name, state, attrs

    def get_stats(self):

        sensor_name = f"strava.{self.base}_{ self.sensor_name }"

        attrs = {
            "friendly_name": self._gen_friendly_name()
        }

        if self.unit:
            attrs.update({
                "unit_of_measurement": self.unit
            })

        value = round(self.value, 2)

        return sensor_name, value, attrs



class StravaAthleteEntity(Entity):

    def __init__(self, hass_domain_config, name):
        self._state = None
        self.hass_domain_config = hass_domain_config
        self._name = name
        self._attrs = None

    @property
    def device_state_attributes(self):
        return self._attrs

    @property
    def hidden(self):
        return True

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return None

    @Throttle(timedelta(minutes=THROTTLE_MINS))
    def update(self):

        # Load categories from config
        stat_categories = self.hass_domain_config.get('stats')

        # Get the stats dict from Strava API
        attrs = _get_athlete_data(self.hass_domain_config)

        strava_sensors = list()

        # Assign stats to sensor states
        for key, sensor_value in attrs.items():

            # If in the tracked categories
            if key in stat_categories:

                # If dict then decode
                if type(sensor_value) is dict:

                    for sub_key, sub_sensor_value in sensor_value.items():

                        # Set attrs for DISTANCE
                        if sub_key in ['distance', "elevation_gain"]:

                            sensor = StravaStatSensor(key, sub_key, sub_sensor_value, unit=LENGTH_METERS)

                            n, v, a = sensor.get_stats()
                            self.hass.states.set(n, v, attributes=a)

                            n, v, a = sensor.get_stats_km()
                            self.hass.states.set(n, v, attributes=a)

                        # Set attrs for TIME
                        if sub_key in ["moving_time", "elapsed_time"]:

                            sensor = StravaStatSensor(key, sub_key, sub_sensor_value, unit='seconds')

                            n, v, a = sensor.get_stats()
                            self.hass.states.set(n, v, attributes=a)

                            n, v, a = sensor.get_stats_hours()
                            self.hass.states.set(n, v, attributes=a)

                else:
                    # Assign directly to sensor e.g DOMAIN.KEY
                    sensor_name = self.gen_sensor_name("strava", key)
                    state_attrs = self.gen_attributes(key, LENGTH_METERS)

                    self.hass.states.set(sensor_name, sensor_value, attributes=state_attrs)

        # Set state and attrs
        self._attrs = attrs
        self._state = "OK"

    # Distance
    def m_as_km(self, meters):
        return meters / 1000

    # Time
    def sec_as_minutes(self, seconds):
        return seconds / 60

    def sec_as_hours(self, seconds):
        return seconds / 3600

    # Speed
    def mps(self, meters, seconds):
        return meters / seconds

    def kmph(self, meters, seconds):
        # (meters / 1000) / (seconds / 3600)
        return self.m_as_km(meters) / self.sec_as_hours(seconds)

    def gen_sensor_name(self, domain, sensor, sub_type=None):
        name = f"{domain}.{sensor}"

        if sub_type:
            name = f"{name}_{sub_type}"

        return name

    def gen_friendly_name(self, name):
        return name.replace("_", " ").capitalize()

    def gen_attributes(self, sensor_name, unit=None):

        attrs = {
            "friendly_name": self.gen_friendly_name(sensor_name)
        }

        if unit:
            attrs.update({
                "unit_of_measurement": unit
            })

        return attrs