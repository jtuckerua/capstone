import numpy as np
import pandas as pd
from Data import location


def calc_home_buy(salary):
    """
    Calculate the amount of home afforded based on salary
    Returns the down payment and the amount of house
    """
    m_sal =  salary * .28
    return (m_sal * 15, m_sal * 30)



def total_debt(data):
    """
    calc totat debt amount
    """
    tot = 0
    for i in data:
        tot += int(i[0])
    return tot
    

def savings(salary, rate):
    """
    calculates expected savings 
    """
    return salary * rate

def d_income(salary, rent):
    """
    Calculate the disposable income index
    """
    return (salary/12) - rent 

