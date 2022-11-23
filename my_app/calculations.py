import numpy as np
import geopy

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