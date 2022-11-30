import pandas as pd
from Calculations import *
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


retval = {}

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

  retval['Current Location'] = [d_income(data[0],data[4]), data[4], get_info(data[6])[1]]
  
  
  
  """
  Receives a goal and procedes with teh proper calcs for achieving the gaol
  "Buy a home", "Save money","Pay off debt", "Retire"
  """
  
  if data[3] == "Buy a home":
      """
      calculate how much house they can afford and the down payment.
      calculate where they can buy the home based on locations returned from industry.
      Data Used: industry dataset, rent dataset, 
      """
      #collect industry dataframe
      ind_df = get_industry_df(industries.get(str(data[8])))
      #convert fips to city and state
      locs = get_industry_loc(ind_df)
      locs = location.confirm_locations(locs)
      rent = location.get_rent(locs.values, data[5])

  if data[3] == "Improve quality of life":
      """
      the goal is to improve the dii by as much as possible.
      """
  if data[3] == "Investment Property":
      pass

def get_industry_df(industry):
  """
  collect the top ten rows for employee level by industry.
  """
  df = pd.read_csv('./Clean/location_industry.csv')
  # codes = df['industry_code'].unique()
  return df[df['industry_code'] == industry].sort_values('annual_avg_emplvl', axis=0, ascending=False)[:10]

def get_industry_loc(df):
  """
  returns the top ten cities for the industry 
  """
  lf = pd.read_csv('./Clean/location_codes.csv')
  return lf[lf['area_fips'].isin(df['area_fips'].values)].loc[:,['City','State']]

# def get_rent(data, ):
#   locs = []
#   for line in data:
#     location.location_info()