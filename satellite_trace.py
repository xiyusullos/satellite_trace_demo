from sgp4.model import WGS84
from sgp4.api import Satrec, jday
import pandas as pd

UNIT_M = 1
UNIT_KM = 2


def load_twoline_data(filepath='starlink.txt'):
    twoline_data = []
    with open(filepath, 'r') as file:
        i = 0
        twoline_datum = [0, 0, 0]
        for line in file:
            line = line.strip()
            if len(line) == 0: break
            twoline_datum[i % 3] = line.strip()
            i += 1
            if i % 3 == 0:
                twoline_data.append(twoline_datum)
                twoline_datum = [0, 0, 0]

    print(len(twoline_data))
    return twoline_data


def load_satellite_info(name, filepath='starlink_info.xls'):
    df = pd.read_excel(filepath)
    column_of_name = df.columns[0]
    for index, row in df.iterrows():
        if row[column_of_name] == name:
            return dict(row)
    return {}


class Satellite(object):
    def __init__(self, name, line1, line2, whichconst=WGS84):
        self.name = name.strip()
        self.line1 = line1.strip()
        self.line2 = line2.strip()

        self.whichconst = whichconst
        self.satellite = Satrec.twoline2rv(
            self.line1, self.line2, self.whichconst)

        self.trace = {
            'start_datetime': None,
            'data': [],
        }

    def __repr__(self) -> str:
        return '\n'.join([self.name, self.line1, self.line2])

    def generate_trace(self, start_datetime, interval=300, unit=UNIT_M, total_second=None):
        self.trace['start_datetime'] = start_datetime
        scale = 1000 if unit == UNIT_M else 1

        if total_second is None:
            total_second = 86400 + interval

        for second in range(0, total_second, interval):
            args = start_datetime + (second,)
            error, position, v = self.satellite.sgp4(*jday(*args))
            if error == 0:
                # has no error
                self.trace['data'].append({
                    'time': second,
                    'x': position[0] * scale,
                    'y': position[1] * scale,
                    'z': position[2] * scale,
                })
        return self

    def transform_to_frontend(self):
        l = []
        for _ in self.trace['data']:
            l.append(_['time'])
            l.append(_['x'])
            l.append(_['y'])
            l.append(_['z'])
        return l


if __name__ == '__main__':
    # startlink_path = 'starlink.txt'
    # starlink_twoline_data = load_twoline_data(startlink_path)
    # start_datetime = (2021, 5, 11, 13, 0)
    # for name, line1, line2 in starlink_twoline_data[:1]:
    #     data = Satellite(name, line1, line2).generate_trace(
    #         start_datetime).transform_to_frontend()
    #     print(data)

    name = 'STARLINK-24'
    l1 = '1 44238U 19029D   21129.81825469  .00002569  00000-0  14948-3 0  9991'
    l2 = '2 44238  52.9944 164.4950 0000919  99.7483 260.3613 15.15637519106847'
