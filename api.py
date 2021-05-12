import json
from datetime import datetime as dt

from flask import Flask
from flask_cors import CORS
from skyfield.api import load

from satellite_trace import load_twoline_data, Satellite, load_satellite_info

app = Flask(__name__)

CORS(app)


def encapulate(data):
    return {
        'code': '200',
        'data': data,
    }


@app.route('/')
def index():
    return 'no data'


@app.route('/satellites', methods=('GET',))
def satellites_list():
    '''satellites?name=<>
    '''
    data = load_twoline_data()
    res = [name for name, line1, line2 in data]
    res = encapulate(res)
    return json.dumps(res)


@app.route('/satellites/<string:name>', methods=('GET',))
def satellite_detail(name):
    '''GET /satellites/<string:name>
    '''
    data = load_twoline_data()
    res = {
        'info': {},
        'traces': [],
    }
    ts = load.timescale()
    now = dt.now()
    for satellite_name, line1, line2 in data:
        if name == satellite_name:
            res['info'] = load_satellite_info(name)

            start_datetime = (now.year, now.month, now.day, now.hour, now.minute)
            satellite = Satellite(satellite_name, line1, line2).generate_trace(start_datetime)
            res['traces'] = satellite.transform_to_frontend()
            break

            # satellite = EarthSatellite(line1, line2, name=satellite_name)
            for second in range(0, 86400 + 300, 300):
                t = ts.utc(now.year, now.month, now.day, now.hour, now.minute, second)
                l = satellite.at(t).position.m
                res['traces'].append(second)
                res['traces'].append(l[0])
                res['traces'].append(l[1])
                res['traces'].append(l[2])
            print(res['traces'])
            break
    # print(data)
    res = encapulate(res)
    return json.dumps(res)


if __name__ == '__main__':
    app.run(debug=True)
