from geopy.geocoders import Nominatim
from geopy.distance import geodesic

coder = Nominatim(user_agent='geopytest')

def get_info(location):
    return coder.geocode(location)

def distance_calc(location1, location2):
    """
    input: current location and radius
    output: all cities within the radius
    """
    return geodesic(location1[1], location2[1]).miles
    

