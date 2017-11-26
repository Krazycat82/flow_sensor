import requests

amount = {"amount":201,"timestamp":"2017/11/06 22:00:00", "duration_in_seconds":1245}
resp = requests.post("http://localhost:5000/flow_sensor/api/v1.0/amounts", json=amount)
if resp.status_code != 201:
    raise ApiError('POST /amounts/ {}'.format(resp.status_code))
print('Created amounts. ID: {}'.format(resp.json()))
