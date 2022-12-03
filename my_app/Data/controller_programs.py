import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from shiny import App, render, ui, reactive, Outputs


"""
Below are all of the control flow functions!
***********************************************

"""
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

retval = {
}

def calcs(data):
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
  cur_location = get_info(data[6])
  retval['Current Location'] = [d_income(data[0],data[4]), data[4]]
  
  """
  Receives a goal and procedes with teh proper calcs for achieving the gaol
  "Buy a home", "Save money","Pay off debt", "Retire"
  """

  #collect industry dataframe
  ind_df = get_industry_df(industries.get(str(data[8])))
  #convert fips to city and state
  locs = get_industry_loc(ind_df)
  retval['Location one'] = [ind_df['avg_annual_pay'][0],locs[0]]
  retval['Location two'] = [ind_df['avg_annual_pay'][1],locs[0]]
  retval['Location three'] = [ind_df['avg_annual_pay'][2],locs[0]]
  return retval
  
  # if data[3] == "Buy a home":
  #     """
  #     calculate how much house they can afford and the down payment.
  #     calculate where they can buy the home based on locations returned from industry.
  #     Data Used: industry dataset, rent dataset, 
  #     """
  #     return retval
  # if data[3] == "Improve quality of life":
  #     """
  #     the goal is to improve the dii by as much as possible.
  #     """
  #     return retval
  # if data[3] == "Investment Property":
  #   return retval


def get_industry_df(industry):
  """
  collect the top three rows for employee level by industry.
  return the fips and their average annual pay
  """
  df = pd.read_csv('./Clean/location_industry.csv')
  return df[df['industry_code'] == industry].sort_values('annual_avg_emplvl', axis=0, ascending=False)[:3].loc[:,['area_fips','avg_annual_pay']]

def get_industry_loc(df):
  """
  returns the top cities for the industry 
  """
  lf = pd.read_csv('./Clean/location_codes.csv')
  tmp = lf[lf['area_fips'].isin(df['area_fips'].values)].loc[:,['City','State']]
  return (get_info(",".join(tmp.values[0])),get_info(",".join(tmp.values[1])),get_info(",".join(tmp.values[2])))




"""
Below are all of the calculation functions!
********************************************
"""


def calc_home_buy(salary):
    """
    Calculate the amount of home afforded based on salary
    Returns the down payment and the amount of house for both 15 and 30 year
    """
    m_sal =  salary * .28
    return ((m_sal * 15,(m_sal * 15)*.1), (m_sal * 30,(m_sal * 30)*.1))

def total_debt(data):
    """
    calc totat debt amount
    """
    tot = 0
    for i in data:
        tot += int(i[0])
    return tot
    

def savings(savings, salary, goal):
    """
    takes current savings, current salary, and goal
    and calculates how long until that goal is reached. 
    returns the amount of months to reach goal.
    """
    dif = goal - savings
    return dif / (salary/12)*.2

@reactive.Calc
def d_income(salary, rent):
    """
    Calculate the disposable income index
    """
    return (salary/12) - rent




"""
Below are all of the location functions!
******************************************
"""

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




