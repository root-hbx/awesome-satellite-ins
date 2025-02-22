from skyfield.api import load
from skyfield.iokit import parse_tle_file

ts = load.timescale()

with load.open('stations.tle') as f:
    satellites = list(parse_tle_file(f, ts))

print('Loaded', len(satellites), 'satellites')
