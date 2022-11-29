import numpy as np
import geopy

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

salary = 0
debt = []
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
        """
        calculate how much house they can afford and the down payment.
        calculate where they can buy the home based on locations returned from industry.
        Data Used: industry dataset, rent dataset, 
        """
        calc_home()
        
    if goal == "Improve quality of life":
        pass
    if goal == "Investment Property":
        pass
    if goal == "Retire":
        pass

def calc_home():
    """
    Calculate the amount of home afforded based on salary
    Returns the down payment and the amount of house
    """
    salary / 12

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

def industry():
    """
    Input is industry data 
    """