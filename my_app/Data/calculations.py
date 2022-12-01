import numpy as np
import pandas as pd
from Data import location


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

def d_income(salary, rent):
    """
    Calculate the disposable income index
    """
    return (salary/12) - rent 

