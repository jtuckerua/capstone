import difflib
from logging import PlaceHolder
import math
from tkinter import CENTER
from turtle import width
from shiny import App, render, ui, reactive, Outputs
from shinywidgets import output_widget, register_widget, reactive_read
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
        ui.input_numeric("zip", "Current Zip Code", 10001, min=10000, max=99999, width='20%'),
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
    
    # extract 'ZIP Code', 'City', 'State' from wages_df
    zip_df = rent_df[['ZIP Code', 'City', 'State']]

    ###### Calc Functions ######
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
        return top_three_cities

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
    @render.text
    def map(lat=32.2540, lon=-110.9742):
        '''
        Initialize the map with coordinates to Tucson, AZ.
        Will also update the map when the predictions are made
        '''
        geolocator = Nominatim(user_agent="my_app")
        zip = input.zip()
        location = geolocator.geocode(input.zip())

    
        
        lat = location.latitude
        lon = location.longitude

        print("updating map...")

        map = L.Map(center=(lat, lon), zoom=10, scroll_wheel_zoom=True, dragging=True)
        register_widget("map", map)
        return map


    @reactive.Effect
    @output
    @render.plot
    def plot():
        '''
        This function will create a plot that will show the average salary for the user's specific calculations
        '''
        print(input.industry())

        zip = input.zip()
        city, state = get_city_state_from_zip()

        nat_wages = wages_df[wages_df['OCC_TITLE'] == input.industry()]
        nat_wages = nat_wages['Mean_Annual_wage']

        # get the mean annual wage for the selected industry
        wages = wages_df[wages_df['OCC_TITLE'] == input.industry()]
        wages = wages_df[wages_df['City'] == city]
        wages = wages['Mean_Annual_wage']

        if len(wages) >= len(nat_wages):
            wages.loc[:len(nat_wages)]
        else:
            nat_wages.loc[:len(wages)]

        # create the plot
        fig, ax = plt.subplots()
        ax.hist(wages, bins=10, alpha=0.5, label=city)
        ax.hist(nat_wages, bins=10, alpha=0.5, label='Nationwide')
        ax.set_xlabel('City')
        ax.set_ylabel('$ by 10k')
        ax.set_title('Average Salary for ' + input.industry())
        ax.legend(loc='upper right')
        return fig

    @reactive.Effect
    @output
    @render.plot
    def plot_2():
        '''
        This function will create a plot that will show the average rent for the user's specific calculations
        '''
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
        ax.set_xlabel('City')
        ax.set_ylabel('Rent')
        ax.set_title('Rent for ' + bedrooms + ' in ' + city)
        
    @reactive.Effect
    @output
    @render.text
    def out():
        '''
        This function will create a text box that will show the user's specific calculations
        '''
        zip = str(input.zip())
        # the return value is a dataframe with the top cities each as one row
        top_cities = calc_top_three_cities()
        # get the 'City' value for the input zip code
        city = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['City'].values[0]
        state = zip_df.loc[zip_df['ZIP Code'] == int(zip)]['State'].values[0]

        if input.tab() == 'City A':
            # extract the city and state from the top_cities dataframe row 0
            city = top_cities[0]['City']
            state = top_cities[0]['State']
        elif input.tab() == 'City B':
            city = top_cities[1]['City']
            state = top_cities[1]['State']
        elif input.tab() == 'City C':
            city = top_cities[2]['City']
            state = top_cities[2]['State']

        out = f"Ideal City: {city}, {state}\n"+ \
                f"Estimated Salary: ${calc_estimated_salary()}\n" + \
                f"Estimated Rent: ${calc_estimated_rent()} {input.bedrooms()} \n" + \
                f"Savings (Age: {input.age() + 5}): ${calc_estimated_savings()} (Assuming 10% of Disposable Income)\n" + \
                f"Estimated Disposable Income: ${input.sal()} Per Month\n"

        return out


app = App(app_ui, server)