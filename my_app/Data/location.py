from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

coder = Nominatim(user_agent='geopytest')

def get_info(location):
    return coder.geocode(location)

def distance_calc(location1, location2):
    """
    input: current location and radius
    output: all cities within the radius
    """
    return geodesic(location1[1], location2[1]).miles
    
def get_rent(locs, rooms):
    rent = pd.read_csv('./Clean/rent.csv')

def confirm_dist(locations, range):
    """
    receives a list of locations and check if they are within the specified range. 
    if not, they are removed from the list. If so, then they get to stay.
    """

    # for location in locations:
