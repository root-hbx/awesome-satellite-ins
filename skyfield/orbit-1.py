from skyfield.api import load
from skyfield.elementslib import osculating_elements_of

ts = load.timescale()
t = ts.utc(2018, 4, 22)

planets = load('de421.bsp')
earth = planets['earth']
moon = planets['moon']

position = (moon - earth).at(t)

elements = osculating_elements_of(position)

i = elements.inclination.degrees
e = elements.eccentricity
a = elements.semi_major_axis.km

print('Inclination: {0:.2f} degrees'.format(i))
print('Eccentricity: {0:.5f}'.format(e))
print('Semimajor axis: {0:.0f} km'.format(a))

print('Periapsis:', elements.periapsis_time.utc_strftime())
print('Period: {0:.2f} days'.format(elements.period_in_days))

next = elements.periapsis_time + elements.period_in_days
print('Next periapsis:', next.utc_strftime())
