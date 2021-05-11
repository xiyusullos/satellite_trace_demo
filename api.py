import json
from datetime import datetime as dt

from flask import Flask

from satellite_trace import load_twoline_data, Satellite

app = Flask(__name__)


@app.route('/')
def index():
    return 'no data'


@app.route('/satellites', methods=('GET',))
def satellites_list():
    '''satellites?name=<>
    '''
    data = load_twoline_data()
    # print(data)
    return json.dumps([name for name, line1, line2 in data])


@app.route('/satellites/<string:name>', methods=('GET',))
def satellite_detail(name):
    '''GET /satellites/<string:name>
    '''
    data = load_twoline_data()
    for satellite_name, line1, line2 in data:
        if name == satellite_name:
            now = dt.now()
            start_datetime = (now.year, now.month, now.day, now.hour, now.minute)
            satellite = Satellite(satellite_name, line1, line2).generate_trace(start_datetime)
            satellite.transform_to_frontend()
            response = satellite.transform_to_frontend()
            # response = {
            #     'name': satellite.name,
            #     'trace_data': satellite.transform_to_frontend(),
            # }
            return json.dumps(response)
    # print(data)
    return json.dumps([])


if __name__ == '__main__':
    app.run(debug=True)
