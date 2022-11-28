import numpy as np
import geopy

industries = {'10': 'Total, all industries',
 '11': 'Agriculture, forestry, fishing and hunting',
 '21': 'Mining, quarrying, and oil and gas extraction',
 '22': 'Utilities',
 '23': 'Construction',
 '31-33': 'Manufacturing',
 '42': 'Wholesale trade',
 '44-45': 'Retail trade',
 '48-49': 'Transportation and warehousing',
 '51': 'Information',
 '52': 'Finance and insurance',
 '53': 'Real estate and rental and leasing',
 '54': 'Professional and technical services',
 '55': 'Management of companies and enterprises',
 '56': 'Administrative and waste services',
 '61': 'Educational services',
 '62': 'Health care and social assistance',
 '71': 'Arts, entertainment, and recreation',
 '72': 'Accommodation and food services',
 '81': 'Other services, except public administration',
 '92': 'Public administration',
 '99': 'Unclassified'}

def calculations(data):
    """
    Salary = data[0]
    savings = data[1]
    debt = data[2]
    goal = data[3]
    rent = data[4]
    location = data[5]
    industry = data[6]
    """

def goal(goal):
    """
    Receives a goal and procedes with teh proper calcs for achieving the gaol
    "Buy a home", "Save money","Pay off debt", "Retire"
    """
    
    if goal == "Buy a home":
        pass
    if goal == "Save money":
        pass
    if goal == "Pay off debt":
        pass
    if goal == "Retire":
        pass

def calc_home():
    """
    Calculate the amount of home afforded based on salary
    Returns the down payment and the amount of house
    """
    pass

def debt(data):
    """
    debt should include the different debt types
    Credit Cards: [num of cards, apr, amounts] per card
    Car Loan: [amount, rate, years]
    Student Loans: [Amount, rate]
    """
    

def savings(salary, rate):
    """
    calculates expected savings 
    """
    return salary * rate

def d_income(salary, rent):
    """
    Calculate the disposable income index
    """
    retval = salary - (rent * 12)
    return [retval, retval - (.35 * salary)]
    

def locations(location_data):
    """
    Receives a tuple of data containing current location and either ideal locations
    or an int value for range in miles.
    If user is not willing to move, it should contain two current locations.
    """
    pass

# def main():

#     pass

# if __name__ == "__main__":
#     main()