import pandas as pd
import Calculations
import location

def get_industry():
  """
  collect all rows based on industry
  """
  pd.read_csv('./Clean/location_industry.csv')


def calculations(data):
    """
    Salary = data[0]
    savings = data[1]
    debt = data[2]
    goal = data[3]
    rent = data[4]
    bedroom = data[5]
    location = data[6]
    industry = data[7]
    """
    retval = {
        'current location' :[location.location_info(data[6]), Calculations.d_income(data[0], data[4])],
        'location 1' : [],
        'location 2': [],
        'location 3' : []
    }