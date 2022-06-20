import urllib.request
import json
from pprint import pprint
body = {
    "end":  {
        "Longitude": 32.11373035636576,
        "Latitude": 34.8058324089434
    },
    "start": {
        "Longitude": 32.123458696068184,
        "Latitude": 34.80682195595362
    },
    "midpoints": [
        {
            "Longitude": 32.12262873057995,
            "Latitude": 34.802691456068274
        },
        {
            "Longitude": 32.110645105693465,
            "Latitude": 34.78818997566331
        },
        {
            "Longitude": 32.116365083646365,
            "Latitude": 34.79480298789226
        }
    ]
}

myurl = "http://taucarpool.herokuapp.com/taucarpoolalgo"
# myurl = "http://127.0.0.1:5000/taucarpoolalgo"

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
