import pandas as pd
from calculations import *
from location import *
industries = { 'Total, all industries': '10',
                'Agriculture, forestry, fishing and hunting':'11',
                'Mining, quarrying, and oil and gas extraction':'21',
                'Utilities':'22',
                'Construction':'23',
                'Manufacturing':'31-33',
                'Wholesale trade':'42',
                'Retail trade':'44-45',
                'Transportation and warehousing':'48-49',
                'Information':'51',
                'Finance and insurance':'52',
                'Real estate and rental and leasing':'53',
                'Professional and technical services':'54',
                'Management of companies and enterprises':'55',
                'Administrative and waste services':'56',
                'Educational services':'61',
                'Health care and social assistance':'62',
                'Arts, entertainment, and recreation':'71',
                'Accommodation and food services':'72',
                'Other services, except public administration':'81',
                'Public administration':'92',
                'Unclassified':'99'}

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
  ind_df = get_industry_df(industries.get(str(data[8])))


def get_industry_df(industry):
  """
  collect all rows based on industry
  """
  df = pd.read_csv('./Clean/location_industry.csv')
  # codes = df['industry_code'].unique()
  return df[df['industry_code'] == industry].sort_values('annual_avg_emplvl', axis=0, ascending=False)[:10]['area_fips']
  
def get_industry_loc(fips):
  lf = pd.read_csv('./Clean/location_codes.csv')
  return lf[lf['area_fips'].isin(fips)].loc[:,['City','State']]

def get_rent(data):
  locs = []
  for line in data:

    location.location_info()