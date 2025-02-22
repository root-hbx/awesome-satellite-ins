from skyfield.api import EarthSatellite, wgs84
from skyfield.api import load

ts = load.timescale()
line1 = '1 25544U 98067A   14020.93268519  .00009878  00000-0  18200-3 0  5082'
line2 = '2 25544  51.6498 109.4756 0003572  55.9686 274.8005 15.49815350868473'
satellite = EarthSatellite(line1, line2, 'ISS (ZARYA)', ts)

t = ts.utc(2014, 1, 23, 11, 18, 7)

print("================= by at()  ===================")

geocentric = satellite.at(t)
print(geocentric.position.km)

print("================= by wgs84 ===================")

lat, lon = wgs84.latlon_of(geocentric)
print('Latitude:', lat)
print('Longitude:', lon)

print("----------------------------------------------")

height = wgs84.height_of(geocentric)
print('Height:', height.km)

print("----------------------------------------------")

pos = wgs84.geographic_position_of(geocentric)
print('Position of point:', pos)

print("================= by RA and DEC ===================")



