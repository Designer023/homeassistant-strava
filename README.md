# Strava Sensor

Setup strava API

```yaml
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