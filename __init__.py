from .constants import DOMAIN, CLIENT_SECRETS_FILE, DATA_KEY
from homeassistant.helpers.discovery import load_platform

from .utils import _refresh_access_token


def setup(hass, config):

    # Load data from configuration.yaml
    cfg = config.get(DOMAIN)

    # Refresh strava tokens
    _ = _refresh_access_token(cfg, cfg.get('token'))

    # Push the config to the data layer
    hass.data[DATA_KEY] = cfg

    # Load platform sensor so it's not required to add to config
    load_platform(hass, component='sensor', platform=DOMAIN, discovered=None, hass_config=cfg)

    return True
