from sgp4.api import Satrec, WGS72
from skyfield.api import EarthSatellite, load

satrec = Satrec()

satrec.sgp4init(
    WGS72,           # gravity model
    'i',             # 'a' = old AFSPC mode, 'i' = improved mode
    5,               # satnum: Satellite number
    18441.785,       # epoch: days since 1949 December 31 00:00 UT
    2.8098e-05,      # bstar: drag coefficient (/earth radii)
    6.969196665e-13, # ndot: ballistic coefficient (radians/minute^2)
    0.0,             # nddot: second derivative of mean motion (radians/minute^3)
    0.1859667,       # ecco: eccentricity
    5.7904160274885, # argpo: argument of perigee (radians)
    0.5980929187319, # inclo: inclination (radians)
    0.3373093125574, # mo: mean anomaly (radians)
    0.0472294454407, # no_kozai: mean motion (radians/minute)
    6.0863854713832, # nodeo: right ascension of ascending node (radians)
)

ts = load.timescale()
sat = EarthSatellite.from_satrec(satrec, ts)

print('Satellite number:', sat.model.satnum)
print('Epoch:', sat.epoch.utc_jpl())