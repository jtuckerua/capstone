import pandas as pd
from calculations import *
from location import *


def calculations(data):
    """
    Salary = data[0]
    savings = data[1]
    debt = data[2]
    goal = data[3]
    rent = data[4]
    bedroom = data[5]
    location = data[6]
    distance = data[7]
    industry = data[8]
    """
    # retval = {
    #     'current location' :[location.location_info(data[6]), d_income(data[0], data[4])],
    #     'location 1' : [],
    #     'location 2': [],
    #     'location 3' : []
    # }

def get_industry(industry):
  """
  collect all rows based on industry
  """
  df = pd.read_csv('./Clean/location_industry.csv')
  codes = df['industry_code'].unique()
  fips = df[df['industry_code'] == codes[4]].sort_values('annual_avg_emplvl', axis=0, ascending=False)[:5]['area_fips'].values
  lf = pd.read_csv('/Users/jasontucker/Desktop/School/Fall 2022/Ista 498/Capstone/Project/Untitled/my_app/Data/Clean/location_codes.csv')
  rets = lf[lf['area_fips'].isin(fips)].values