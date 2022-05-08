import urllib.request
import json
from pprint import pprint
body = {
    "end":  {
        "Longitude": 32.11373035636576,
        "Latitude": 34.8058324089434
    },
    "start": {
        "Longitude": 32.327247488672384,
        "Latitude": 34.85820557652936
    },
    "midpoints": [
        {
            "Longitude": 32.12510358738037,
            "Latitude": 34.80384417769697
        },
        {
            "Longitude": 32.185310157278415,
            "Latitude": 34.85437967985504
        },
        {
            "Longitude": 32.167310607900724,
            "Latitude": 34.84131225426192
        }
    ]
}

# myurl = "https://taucarpool.herokuapp.com/taucarpoolalgo"
myurl = "http://127.0.0.1:5000/taucarpoolalgo"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
}

data = json.dumps(body).encode("utf-8")
# pprint(data)

try:
    req = urllib.request.Request(myurl, data, headers)
    with urllib.request.urlopen(req) as f:
        res = f.read()
    with open("test.html", "w") as test_file:
        response = json.loads(res.decode())
        try:
            test_file.write(response['result'])
            del response['result']
            pprint(response)
        except:
            print(f"Error: \n{response['internal_error']}")
    # pprint(res.decode())
except Exception as e:
    pprint(e)
