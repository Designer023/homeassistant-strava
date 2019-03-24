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

        # Assign stats to sensor states
        for key, sensor_value in attrs.items():

            # If in the tracked categories
            if key in stat_categories:

                # If dict then decode
                if type(sensor_value) is dict:

                    for sub_key, sub_sensor_value in sensor_value.items():

                        # Assign directly to sensor e.g DOMAIN.KEY_SUB
                        sub_sensor_name = f"strava.{key}_{sub_key}"

                        state_attrs = {}

                        # Set attrs for distance
                        if sub_key in ['distance', "elevation_gain"]:
                            state_attrs.update({
                                "unit_of_measurement": LENGTH_METERS
                            })

                            # Create KM versions of sensors
                            km_sub_sensor_name = f'{sub_sensor_name}_km'

                            # Set state of sub km sensor
                            self.hass.states.set(km_sub_sensor_name, round(sub_sensor_value / 1000, 2), attributes={
                                "unit_of_measurement": LENGTH_KILOMETERS
                            })

                        # Set attrs for time
                        if sub_key in ["moving_time", "elapsed_time"]:
                            state_attrs.update({
                                "unit_of_measurement": "hours"
                            })
                            sub_sensor_value = round(sub_sensor_value / 3600, 2)

                        # Set state of sub sensors
                        self.hass.states.set(sub_sensor_name, sub_sensor_value, attributes=state_attrs)

                else:
                    # Assign directly to sensor e.g DOMAIN.KEY
                    sensor_name = f"strava.{key}"
                    state_attrs = {
                        "unit_of_measurement": LENGTH_METERS
                    }
                    self.hass.states.set(sensor_name, sensor_value, attributes=state_attrs)

        # Set state and attrs
        self._attrs = attrs
        self._state = "OK"
