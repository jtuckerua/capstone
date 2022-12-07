from ast import IsNot
import difflib
from logging import PlaceHolder
import math
from tkinter import CENTER
from turtle import width
from shiny import App, render, ui, reactive, Outputs
from shinywidgets import output_widget, register_widget, reactive_read, render_widget
from shiny.types import SilentException
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
    return []

###### Load data ######
rent_df = pd.read_csv('./Data/Clean/rent.csv')
wages_df = pd.read_csv('./Data/Clean/cln_wages.csv')
housing_df = pd.read_csv('./Data/Clean/housing.csv')
ind_series = wages_df['OCC_TITLE'].values.tolist()
ind_series = sorted(ind_series)


###### Create App ######
    
app_ui = ui.page_fluid(
    # create a user interface that features a horizontal navbar that contains a title and a button
    # in the middle of the title and the button will be 3 text boxes that will be used to input data
    # and two dropdown menus that will be used to select data from the database
    # the navbar will also have a slider that will be used to change the size of the plots
    #Row tells shiny that these UI elements should be next to eachother horizontally.
    ui.row(
        ui.page_navbar(*nav_controls("page_navbar"), title="Where Should I Live?", bg="#0062cc", inverse=True, id="navbar_id",
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
        ui.input_slider("dis", "Distance", value=300, min=1, max=2900, step=50, post="mi", width='20%'),
        ui.output_ui("ui_select"),
        ui.input_action_button("predict","Predict"),
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
    def filter_wages_by_industry():
        ''' 
        filter the wages_df to only include the industry specified by the user
        '''
        ind = input.industry()
        df = wages_df[wages_df['OCC_TITLE'] == ind]
        return df
    
    @reactive.Calc
    def calc_top_three_cities():
        '''
        Determine the top 3 cities to move to based on the user's salary and the industry they work in
        '''
        # get the filtered wage dataframe
        
        wages_df = filter_wages_by_industry()
        
        # order cities by 'Mean_Annual_wage' from highest to lowest
        cities = wages_df[['City', 'State', 'Mean_Annual_wage']]
        cities = cities.sort_values(by='Mean_Annual_wage', ascending=False)

        # get lat and lon of the inputted zip
        zip = input.zip()
        geolocator = Nominatim(user_agent="my_app")
        loc1_city, _ = get_city_state_from_zip()
        
        loc1_zip = zip_df[zip_df['ZIP Code'] == zip]['City'].values[0]
        loc1 = geolocator.geocode(zip, addressdetails=True)
        loc1_lat, loc1_lon = loc1.latitude, loc1.longitude

        print("ranking cities...")

        # get the top 3 cities
        eligible_cities = []
        # backup list of lowest three distance cities in-case distance given is too small
        lowest_three = []
        # check every row of cities
        for _, row in cities.iterrows():
            # get the city value of this row
            city = row['City']
            try:
                zip2 = zip_df[zip_df['City'] == city]['ZIP Code'].values[0]
            except:
                continue
            loc2 = geolocator.geocode(zip2, addressdetails=True)
            loc2_lat, loc2_lon = loc2.latitude, loc2.longitude
            miles = geodesic((loc1_lat, loc1_lon), (loc2_lat, loc2_lon)).miles
            if len(lowest_three) < 3:
                lowest_three.append((city, miles))
            elif miles < lowest_three[2][1]:
                lowest_three[2] = (city, miles)
                lowest_three = sorted(lowest_three, key=lambda x: x[1])
            if miles <= input.dis():
                print(city, ":", miles)
                eligible_cities.append(city)
            
        if len(eligible_cities) < 3:
            eligible_cities = [city for city, miles in lowest_three]

        eligible_cities_df = cities[cities['City'].isin(eligible_cities)]
        eligible_cities_df = eligible_cities_df[['City', 'State', 'Mean_Annual_wage']]

        for index, row in eligible_cities_df.iterrows():
            annual_income = row['Mean_Annual_wage']
            #print('annual',annual_income)
            annual_income = annual_income.replace(',', '')
            annual_income = int(annual_income)
            monthly_income = annual_income / 12
            bedrooms = input.bedrooms()
            if bedrooms == 'Studio':
                bedrooms = 'studio'

            # get the 'City' value for the input zip code
            city = row['City']
            zip = zip_df.loc[zip_df['City'] == city]['ZIP Code'].values[0]
            # filter the rent data to only be the [bedroom] column where the 'City' == city
            rent = rent_df[rent_df['City'] == city][bedrooms]

            rent = round(rent.mean(), 2)
            disposable_income = monthly_income - rent
            eligible_cities_df.loc[index, 'Mean_Annual_wage'] = disposable_income

        # get the a df from wages_df that matches the eligible_cities_df but uses ['City', 'State', calc_rent_cost()] as the index
        top_three_cities = eligible_cities_df.sort_values(by='Mean_Annual_wage', ascending=False).head(3)


        
        top_three_cities = top_three_cities['City'].values
        print("attempting to update...")

        zip_a = zip_df[zip_df['City'] == top_three_cities[0]]['ZIP Code'].values[0]
        zip_b = zip_df[zip_df['City'] == top_three_cities[1]]['ZIP Code'].values[0]
        zip_c = zip_df[zip_df['City'] == top_three_cities[2]]['ZIP Code'].values[0]

        # convert the zipcodes to native int
        zip_a = int(zip_a)
        zip_b = int(zip_b)
        zip_c = int(zip_c)
        
        return ui.update_numeric("zip", value=zip_a)

    @reactive.Calc
    def calc_rent_diff():
        cur_rent = input.rent()
        mean_rent = calc_estimated_rent()
        city, state = get_city_state_from_zip()
        if cur_rent < mean_rent:
            return f"Your rent is {mean_rent - cur_rent} below the average rent in {city}, {state}."
        elif cur_rent > mean_rent:
            return f"Your rent is {cur_rent - mean_rent} above the average rent in {city}, {state}."
        else:
            return f"Your rent is the same as the average rent in {city}, {state}."

    @reactive.Calc
    def get_city_state_from_zip():
        zip = input.zip()

        

        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(zip, addressdetails=True)
        location = location.raw
        
        try:
            city = location['address']['city']
            state = location['address']['state']
            
        except:
            # use the zip code to get the city and state from the zip_df
            df = zip_df[zip_df['ZIP Code'] == zip]
            city = df['City'].values[0]
            state = df['State'].values[0]

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
        print('enter buy a home function')
        savings = input.sav()
        city, _ = get_city_state_from_zip()
        print('BUY HOME CITY',city)
        # filter data
        for _, value in housing_costs['Metro'].items():
            # get the city value of this row
            met = value
            if met.startswith(city):
                break
        print('MET', met)
        housing_costs_df = housing_costs[housing_costs['Metro'] == met]
        mean_housing_price = housing_costs_df['2020-09-30'].mean()

        # calculate the amount of money needed for a 10% down payment
        down_payment = mean_housing_price * .1
        money_needed = down_payment - savings

        # calculate the estimated amount of time it will take
        # for their current savings to arrive at a point to put a 10% down
        # payment on the mean housing price of the current tab city
        time = money_needed / (calc_disposable_income() * .1)
        time = round(time, 2)
        print("Home goal calculated!")
        return f"Your current savings will take {time} months to arrive at a 10% down payment on the mean housing price of {city}."


    @reactive.Calc
    def calc_investment_property():
        '''
        This function will calculate the estimated amount of time it will take
        for their current savings to arrive at a point to put a 10% down
        payment on the mean housing price of the current tab city
        '''
        print('enter calc investment function')
        savings = input.sav()
        city, _ = get_city_state_from_zip()

        for _, value in housing_costs['Metro'].items():
            # get the city value of this row
            met = value
            if met.contains(city):
                break
        
        # filter data
        housing_costs_df = housing_costs[housing_costs['Metro'] == met]
        mean_housing_price = housing_costs_df['2020-09-30'].mean()

        # calculate the amount of money needed for a 15% down payment
        down_payment = mean_housing_price * .15
        money_needed = down_payment - savings

        # calculate the estimated amount of time it will take
        # for their current savings to arrive at a point to put a 10% down
        # payment on the mean housing price of the current tab city
        time = money_needed / (calc_disposable_income() * .10)
        time = round(time, 2)
        print("Investment goal calculated!")
        return f"Your current savings will take {time} months to arrive at a 15% down payment on the mean housing price of {city}."

    @reactive.Calc
    def calc_improve_qol():
        print('enter calc improve')
        debt = input.pay()
        interest = input.int()
        disp_income = calc_disposable_income()
        
        # calculate the how many months it will take to pay off
        # all debt if each month, ten percent of disposable income is spent
        # paying off debt
        months = 0
        while debt > 0:
            debt_payment = disp_income * .1
            debt -= debt_payment
            months += 1

        # calculate the total amount of interest paid over the course of
        # paying off the debt
        total_interest = 0
        for i in range(months):
            total_interest += debt * (interest *.01)
        print("Debt goal calculated!")
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
        with ui.Progress(min=1, max=5) as p:
            p.set(message="Calculation in progress", detail="This may take a while...")

            for i in range(1, 5):
                city, _ = get_city_state_from_zip()

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
        ax.set_xlabel('Distribution')
        ax.set_title('Average Salary for ' + input.industry())
        plt.xticks([])
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
                zip = input.zip()
                
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
        ax.set_ylabel('Inventory')
        ax.set_title('Rent for ' + bedrooms + ' in ' + city)
        return fig

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
    @reactive.event(input.predict)
    def out():
        '''
        This function will create a text box that will show the user's specific calculations
        '''
        zip = str(input.zip())
        
        # get the 'City' value for the input zip code
        city = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['City'].values[0]
        state = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['State'].values[0]

        print(city)
        calc_top_three_cities()
        print('Determining Goals')
        if input.goal() == 'Buy a home':
            goal = calc_buy_a_home()
        elif input.goal() == 'Improve Quality of Life':
            goal = calc_improve_qol()
        elif input.goal() == 'Investment Property':
            goal = calc_investment_property()
        print(input.goal())
        out = f"Ideal City: {city}, {state}\n"+ \
                f"Estimated Salary: ${calc_estimated_salary()}\n" + \
                f"Estimated Rent: ${calc_estimated_rent()} {input.bedrooms()} \n" + \
                f"Savings (Age: {input.age() + 5}): ${calc_estimated_savings()} (Assuming 10% of Disposable Income)\n" + \
                f"Estimated Disposable Income: ${input.sal()} Per Month\n" + \
                f"Rent Difference: {calc_rent_diff()}\n" + \
                f"Goal: {goal}"
        print(out)

        return out

app = App(app_ui, server)