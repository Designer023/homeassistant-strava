# Strava Sensor

## Install

*Note:* This only works with a docker install of home assistant currently!

- Copy the whole folder into the ```custom_components``` directory. Make sure it's in a directory named ```strava```.
- Create a Strava developer API account and copy the ID, secret & token to your ```secrets.yaml```.
- Navigate to your profile page and get your user id from the URL & copy this to your ```secrets.yaml```.
- Add the strava platform to your ```configuration.yaml```

```yaml
# configuration.yaml

strava:
  id: !secret strava_id
  secret: !secret strava_secret
  token: !secret strava_token
  user: !secret strava_user
  stats:
    - biggest_ride_distance
    - biggest_climb_elevation_gain
    - recent_ride_totals
    - recent_run_totals
    - recent_swim_totals
    - ytd_ride_totals
    - ytd_run_totals
    - ytd_swim_totals
    - all_ride_totals
    - all_run_totals
    - all_swim_totals
```

## Options

All stat fields are optional. Options are:

```biggest_ride_distance```
```biggest_climb_elevation_gain```
```recent_ride_totals```
```recent_run_totals```
```recent_swim_totals```
```ytd_ride_totals```
```ytd_run_totals```
```ytd_swim_totals```
```all_ride_totals```
```all_run_totals```
```all_swim_totals```


## Credits

Based on the [custom Strava sensor](https://github.com/worgarside/.homeassistant/blob/master/custom_components/sensor/strava.py) created by [worgarside](https://github.com/worgarside).
