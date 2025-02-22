from skyfield.api import EarthSatellite, load

text = """
GOCE
1 34602U 09013A   13314.96046236  .14220718  20669-5  50412-4 0   930
2 34602 096.5717 344.5256 0009826 296.2811 064.0942 16.58673376272979
"""
lines = text.strip().splitlines()

ts = load.timescale()
sat = EarthSatellite(lines[1], lines[2], lines[0])
print(sat.epoch.utc_jpl())

geocentric = sat.at(ts.utc(2013, 11, 9))
print('Before:')
print(geocentric.position.km)
print(geocentric.message)

geocentric = sat.at(ts.utc(2013, 11, 13))
print('\nAfter:')
print(geocentric.position.km)
print(geocentric.message)

