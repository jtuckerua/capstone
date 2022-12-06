import difflib
from logging import PlaceHolder
import math
from tkinter import CENTER
from turtle import width
from shiny import App, render, ui, reactive, Outputs
from shinywidgets import output_widget, register_widget, reactive_read, render_widget
import asyncio
import ipyleaflet as L
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import numpy as np
import pandas as pd
import seaborn as sb

# show all dataframe columns
pd.set_option('display.max_columns', None)

def nav_controls(prefix):
    return [
        ui.nav("City A"),
        ui.nav("City B"),
        ui.nav("City C"),
    ]

###### Load data ######
wages_df = pd.read_csv('./Data/Clean/cln_wages.csv')
rent_df = pd.read_csv('./Data/Clean/rent.csv')
housing_df = pd.read_csv('./Data/housing.csv')
ind_series = wages_df['OCC_TITLE'].values.tolist()

###### Create App ######
    
app_ui = ui.page_fluid(
    # create a user interface that features a horizontal navbar that contains a title and a button
    # in the middle of the title and the button will be 3 text boxes that will be used to input data
    # and two dropdown menus that will be used to select data from the database
    # the navbar will also have a slider that will be used to change the size of the plots
    #Row tells shiny that these UI elements should be next to eachother horizontally.
    ui.row(
        ui.page_navbar(*nav_controls("page_navbar"), title="Capstone", bg="#0062cc", inverse=True, id="navbar_id",
    footer=ui.div(
    ui.row(
            ui.column(4, output_widget("map")),
            ui.column(4, ui.output_plot("plot")),
            ui.column(4, ui.output_plot("plot_2")),
        ),
    ))),
    ui.row(
        ui.input_select("goal", "Financial Goal", ["Buy a home", "Improve Quality of Life","Investment Property"], width='20%'),
        ui.input_select("industry", "Job Industry", ind_series, width='20%'),
        ui.input_numeric("sal", "Salary", 10000, min=0, max=1000000, width='20%'),
        ui.input_numeric("sav", "Savings", 0, min=0, max=1000000, width='20%'),
        ui.input_numeric("age", "Age", 18, min=1, max=100, width='10%'),
    ),
    ui.row(
        ui.input_numeric("zip", "Current Zip Code", 85701, min=10000, max=99999, width='20%'),
        ui.input_numeric("rent", "Rent", 945, min=0, max=10000, width='20%'),
        ui.input_select("bedrooms", "Number of Bedrooms", ["Studio", "1BR", "2BR", "3BR", "4BR"], width='20%'),
        ui.input_slider("dis", "Distance", value=1, min=1, max=500, step=50, post="mi", width='20%'),
        ui.input_checkbox_group("checkbox_item", "Nationwide?", choices=["Yes"], width='10%'),
        ui.output_ui("ui_select"),
    ),
    ui.row(
        ui.p(
        ui.output_text_verbatim("out"),
    ),
    ),
)
        

def server(input, output, session):
    zip_df = rent_df[['ZIP Code', 'City', 'State']]
    housing_costs = housing_df[['Metro', '2020-09-30']]

    ###### Calc Functions ########
    @reactive.Calc
    def determine_distance_by_zipcode(zip1, zip2):
        geolocator = Nominatim(user_agent="my_app")
        location1 = geolocator.geocode(zip1)
        location2 = geolocator.geocode(zip2)
        miles = geodesic((location1.latitude, location1.longitude), (location2.latitude, location2.longitude)).miles
        if miles <= input.dis():
            return [zip2]
        else:
            return []

    @reactive.Calc
    def filter_cities_within_dis():
        ''' 
        filter the rent_df to only include cities within the distance
        specified by the user. cities are determined by zipcode.
        '''
        zip = input.zip()
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(zip, addressdetails=True)
        location = location.raw
        city = location['address']['city']
        state = location['address']['state']

        df = rent_df[['ZIP Code', 'City', 'State']]
        if city.startswith('City of '):
            city = city.replace('City of ', '')

        # find the first row where the zip_df['City'].contains city and zip_df['State'] == state
        valid_zipcodes = []
        for ind in df.index:
            # get the distance between the user's zipcode and the zipcode in the dataframe
            valid_zipcodes += determine_distance_by_zipcode(zip, df['ZIP Code'][ind])

        # filter the rent_df to only include cities within the distance specified by the user
        df = rent_df[rent_df['ZIP Code'].isin(valid_zipcodes)]
        print("DATAFRAME:", df)
        return df

    @reactive.Calc
    def filter_wages_by_industry():
        ''' 
        filter the wages_df to only include the industry specified by the user
        '''
        ind = input.industry()
        df = wages_df[wages_df['OCC_TITLE'] == ind]
        return df
            
    @reactive.Calc
    def calc_top_three_cities():
        # get the filtered rent and wage dataframes
        rent_df = filter_cities_within_dis()
        wages_df = filter_wages_by_industry()

        # filter the wages_df to only include the cities in the rent_df
        wages_df = wages_df[wages_df['City'].isin(rent_df['City'])]

        # get the top three cities by 'Mean_Annual_wage'
        top_three_cities = wages_df.sort_values(by='Mean_Annual_wage', ascending=False).head(3)
        top_three_cities = top_three_cities[['City', 'State', 'Mean_Annual_wage']]
        
        if input.tab() == 'City A':
            return top_three_cities.iloc[0]
        elif input.tab() == 'City B':
            return top_three_cities.iloc[1]
        elif input.tab() == 'City C':
            return top_three_cities.iloc[2]
        return

    @reactive.Calc
    def calc_rent_diff():
        cur_rent = input.rent()
        mean_rent = calc_estimated_rent()

        if cur_rent < mean_rent:
            return f"Your rent is {mean_rent - cur_rent} below the average rent in {input.city()}, {input.state()}."
        elif cur_rent > mean_rent:
            return f"Your rent is {cur_rent - mean_rent} above the average rent in {input.city()}, {input.state()}."
        else:
            return f"Your rent is the same as the average rent in {input.city()}, {input.state()}."

    @reactive.Calc
    def get_city_state_from_zip():
        zip = input.zip()
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(zip, addressdetails=True)
        location = location.raw
        city = location['address']['city']
        state = location['address']['state']

        df = wages_df[['City', 'State']]

        if city.startswith('City of '):
            city = city.replace('City of ', '')

        # find the first row where the zip_df['City'].contains city and zip_df['State'] == state
        for ind in df.index:
            if city in df['City'][ind]:
                city = df['City'][ind]
                state = df['State'][ind]
        return city, state

    @reactive.Calc
    def calc_buy_a_home():
        '''
        This function will calculate the estimated amount of time it will take
        for their current savings to arrive at a point to put a 10% down
        payment on the mean housing price of the current tab city
        '''
        savings = input.savings()
        city, _ = get_city_state_from_zip()

        # filter data
        housing_costs_df = housing_costs[housing_costs['City'] == city]
        mean_housing_price = housing_costs_df['2020-09-30'].mean()

        # calculate the amount of money needed for a 10% down payment
        down_payment = mean_housing_price * .1
        money_needed = down_payment - savings

        # calculate the estimated amount of time it will take
        # for their current savings to arrive at a point to put a 10% down
        # payment on the mean housing price of the current tab city
        time = money_needed / (calc_disposable_income() * .1)
        time = round(time, 2)

        return f"Your current savings will take {time} months to arrive at a 10% down payment on the mean housing price of {city}."


    @reactive.Calc
    def calc_investment_property():
        '''
        This function will calculate the estimated amount of time it will take
        for their current savings to arrive at a point to put a 10% down
        payment on the mean housing price of the current tab city
        '''
        savings = input.savings()
        city, _ = get_city_state_from_zip()

        # filter data
        housing_costs_df = housing_costs[housing_costs['City'] == city]
        mean_housing_price = housing_costs_df['2020-09-30'].mean()

        # calculate the amount of money needed for a 15% down payment
        down_payment = mean_housing_price * .15
        money_needed = down_payment - savings

        # calculate the estimated amount of time it will take
        # for their current savings to arrive at a point to put a 10% down
        # payment on the mean housing price of the current tab city
        time = money_needed / (calc_disposable_income() * .10)
        time = round(time, 2)

        return f"Your current savings will take {time} months to arrive at a 15% down payment on the mean housing price of {city}."

    @reactive.Calc
    def calc_improve_qol():
        debt = input.pay()
        interest = input.int()
        disp_income = calc_disposable_income()
        
        # calculate the how many months it will take to pay off
        # all debt if each month, ten percent of disposable income is spent
        # paying off debt
        months = 0
        while debt > 0:
            debt -= disp_income * .1
            months += 1

        # calculate the total amount of interest paid over the course of
        # paying off the debt
        total_interest = 0
        for i in range(months):
            total_interest += debt * (interest *.01)

        return f"By spending 10% of your disposable income on debt, you will pay off your debt in {months} months and spend {total_interest} on interest."

    @reactive.Calc
    def calc_estimated_rent():
        '''
        This function will calculate the estimated rent based on the 
        mean cost for their selected number of bedrooms in the rent_df
        subset that their input filters for.
        It will first filter the data to the bedroom size they selected
        and then get the mean cost for that bedroom size for each zip code
        in the filtered data. It will then select the lowest cost city and
        return the estimated rent for that city.
        '''
        bedrooms = input.bedrooms()
        if bedrooms == 'Studio':
            bedrooms = 'studio'

        # get the 'City' value for the input zip code
        zip = input.zip()
        city = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['City'].values[0]

        # filter the rent data to only be the [bedroom] column where the 'City' == city
        rent = rent_df[rent_df['City'] == city][bedrooms]

        mean = round(rent.mean(), 2)
        return mean

    @reactive.Calc
    def calc_estimated_savings():
        '''
        This function will calculate the estimated savings based on the 
        mean cost for their selected number of bedrooms in the rent_df
        subset that their input filters for.
        It will first filter the data to the bedroom size they selected
        and then get the mean cost for that bedroom size for each zip code
        in the filtered data. It will then select the lowest cost city and
        return the estimated rent for that city.
        '''
        savings = input.sav()
        disposable_income = calc_disposable_income()
        monthly_savings = disposable_income / 10
        five_years_savings = monthly_savings * 12 * 5
        est_savings = savings + five_years_savings
        return round(est_savings, 2)

    @reactive.Calc
    def calc_disposable_income():
        '''
        This function will very simply calculate the disposable income
        as monthly income minus monthly rent.
        '''
        annual_income = calc_estimated_salary().replace(',', '')
        annual_income = int(annual_income)
        monthly_income = annual_income / 12
        rent = calc_estimated_rent()
        disposable_income = monthly_income - rent
        return disposable_income

    @reactive.Calc
    def calc_estimated_salary():
        '''
        This function will calculate the estimated rent based on the 
        mean cost for their selected number of bedrooms in the rent_df
        subset that their input filters for.
        It will first filter the data to the bedroom size they selected
        and then get the mean cost for that bedroom size for each zip code
        in the filtered data. It will then select the lowest cost city and
        return the estimated rent for that city.
        '''
        bedrooms = input.bedrooms()
        if bedrooms == 'Studio':
            bedrooms = 'studio'

        # get the 'City' value for the input zip code
        city, state = get_city_state_from_zip()

        # filter the rent data to only be the [bedroom] column where the 'City' == city
        wages = wages_df[wages_df['City'] == city]
        wages = wages[wages['State'] == state]
        wages = wages[wages['OCC_TITLE'] == input.industry()]

        return wages['Mean_Annual_wage'].values[0]

    ###### Update UI ######
    @reactive.Effect
    @output
    @render_widget()
    async def map(lat=32.2540, lon=-110.9742):
        '''
        Initialize the map with coordinates to Tucson, AZ.
        Will also update the map when the predictions are made
        '''
        with ui.Progress(min=1, max=5) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 5):
                p.set(i, message="Computing")
                geolocator = Nominatim(user_agent="my_app")
                zip = input.zip()
                location = geolocator.geocode(input.zip())
                lat = location.latitude
                lon = location.longitude
                # Normally use time.sleep() instead, but it doesn't yet work in Pyodide.
                # https://github.com/pyodide/pyodide/issues/2354
            return L.Map(center=(lat, lon), zoom=10, scroll_wheel_zoom=True, dragging=True)



    @reactive.Effect
    @output
    @render.plot
    def plot():
        '''
        This function will create a plot that will show the average salary for the user's specific calculations
        '''
        print(input.industry())
        with ui.Progress(min=1, max=5) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 5):
                zip = input.zip()
                city, state = get_city_state_from_zip()

                nat_wages = wages_df[wages_df['OCC_TITLE'] == input.industry()]
                nat_wages = nat_wages['Mean_Annual_wage']

                # get the mean annual wage for the selected industry
                wages = wages_df[wages_df['OCC_TITLE'] == input.industry()]
                wages = wages_df[wages_df['City'] == city]
                wages = wages['Mean_Annual_wage']

        # make the larger series only as big as the smaller one
        if len(nat_wages) > len(wages):
            nat_wages = nat_wages[:len(wages)]
        else:
            wages = wages[:len(nat_wages)]

        # create the plot
        fig, ax = plt.subplots()
        ax.hist(wages, bins=10, label=city)
        ax.hist(nat_wages, bins=10, label='Nationwide')
        ax.set_ylabel('$ by 10k')
        ax.set_title('Average Salary for ' + input.industry())
        ax.legend(loc='upper left')
        return fig

    @reactive.Effect
    @output
    @render.plot
    def plot_2():
        '''
        This function will create a plot that will show the average rent for the user's specific calculations
        '''
        with ui.Progress(min=1, max=5) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 5):
                rent = rent_df
                zip = str(input.zip())
                
                # get the 'City' value for the input zip code
                city = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['City'].values[0]

                bedrooms = input.bedrooms()
                if bedrooms == 'Studio':
                    bedrooms = 'studio'

                # filter the rent data to only be the [bedroom] column where the 'City' == city
                rent = rent_df.loc[rent_df['City'] == city]
                rent = rent[bedrooms]

        fig, ax = plt.subplots()
        ax.hist(rent, bins=10)
        ax.set_xlabel('Cost')
        ax.set_title('Rent for ' + bedrooms + ' in ' + city)

    @reactive.Effect
    def _():
        #dynamically inserts UI elements based on the selected financial goal. When pay off debt is selected it will add UI elements
        #asking what the outstanding debt amount is and what the interest rate is. If anything besides pay off deb is selected this 
        #function will remove the input UI elements for outstanding debt amount and interest rate. To position insert_ui correctly you
        #must specify a selector and tell it where to place the new ui element relative to the selector. where can = beforeBegin, afterBegin,
        #beforeEnd, or afterEnd. Selector is based on the id of each UI element and must be formatted how it is in this function. 
        goal = input.goal()
        if goal == "Improve Quality of Life":
            ui.insert_ui(ui.input_numeric("pay", "Outstanding Debt Amount ($)", 10000, min=10000, max=1000000, width='10%'), selector="div:has(> #checkbox_item)", where="beforeEnd")
            ui.insert_ui(ui.input_numeric("int", "Interest Rate (%)", 1, min=0, max=20, width='10%'), selector="div:has(> #checkbox_item)", where="beforeEnd")
        elif goal != "Improve Quality of Life":
            ui.remove_ui(selector="div:has(> #pay)")
            ui.remove_ui(selector="div:has(> #int)")
            return
        
    @reactive.Effect
    @output
    @render.text
    def out():
        '''
        This function will create a text box that will show the user's specific calculations
        '''
        zip = str(input.zip())
        # get the 'City' value for the input zip code
        city = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['City'].values[0]
        state = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['State'].values[0]

        if input.goal() == 'Buy a home':
            goal = calc_buy_a_home()
        elif input.goal() == 'Improve Quality of Life':
            goal = calc_improve_qol()
        elif input.goal() == 'Investment Property':
            goal = calc_investment_property()

        calc_top_three_cities()

        out = f"Ideal City: {city}, {state}\n"+ \
                f"Estimated Salary: ${calc_estimated_salary()}\n" + \
                f"Estimated Rent: ${calc_estimated_rent()} {input.bedrooms()} \n" + \
                f"Rent Difference: ${calc_rent_diff()}\n" + \
                f"Savings (Age: {input.age() + 5}): ${calc_estimated_savings()} (Assuming 10% of Disposable Income)\n" + \
                f"Estimated Disposable Income: ${input.sal()} Per Month\n" + \
                f"Goal: ${goal}"

        return out

app = App(app_ui, server)