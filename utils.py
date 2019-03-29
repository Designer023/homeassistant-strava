from .constants import CLIENT_SECRETS_FILE


def _refresh_access_token(cfg, access_token):
    from requests import post
    from json import dump

    JSON = {
        'grant_type': 'refresh_token',
        'client_id': cfg.get('id'),
        'client_secret': cfg.get('secret'),
        'refresh_token': cfg.get('token')
    }

    res = post('https://www.strava.com/oauth/token', headers={'Authorization': 'Bearer {}'.format(access_token)},
               json=JSON)

    with open(CLIENT_SECRETS_FILE, 'w') as f:
        dump(res.json(), f)

    return res.json()['access_token']


def _get_athlete_data(hass_domain_config):
    from json import load
    from datetime import datetime
    from requests import get
    from json.decoder import JSONDecodeError

    STRAVA_USER_ID = hass_domain_config.get('user')

    def _get_athlete():
        return get('https://www.strava.com/api/v3/athletes/{}/stats'.format(STRAVA_USER_ID),
                   headers={'Authorization': 'Bearer {}'.format(access_token)})

    try:
        with open(CLIENT_SECRETS_FILE, 'r') as f:
            client_secrets = load(f)
            access_token = client_secrets['access_token']

        if client_secrets['expires_at'] - 3000 < int(datetime.now().timestamp()):
            access_token = _refresh_access_token(hass_domain_config, access_token)
    except (JSONDecodeError, KeyError) as e:
        print(e)
        access_token = _refresh_access_token(hass_domain_config, 'abcdefghijklmnopqrstuvwxyz')

    athlete = _get_athlete()

    if 'errors' in athlete.json() and athlete.json()['message'] == 'Authorization Error':
        access_token = _refresh_access_token(hass_domain_config, access_token)
        athlete = _get_athlete()

    return athlete.json()  # ['ytd_run_totals' if ytd else 'all_run_totals'][datum]

