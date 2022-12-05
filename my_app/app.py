from logging import PlaceHolder
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
import seaborn as sns
import pandas as pd

sns.set_theme()


def nav_controls(prefix):
    return [
        ui.nav("City A"),
        ui.nav("City B"),
        ui.nav("City C"),
    ]

    
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
        ui.input_select("industry", "Job Industry", ['Total, all industries','Agriculture, forestry, fishing and hunting','Mining, quarrying, and oil and gas extraction', 'Utilities',
       'Construction', 'Manufacturing', 'Wholesale trade', 'Retail trade','Transportation and warehousing', 'Information','Finance and insurance', 'Real estate and rental and leasing',
       'Professional and technical services','Management of companies and enterprises','Administrative and waste services', 'Educational services','Health care and social assistance',
       'Arts, entertainment, and recreation','Accommodation and food services','Other services, except public administration','Public administration', 'Unclassified'], width='20%'),
        ui.input_numeric("sal", "Salary", 10000, min=0, max=1000000, width='20%'),
        ui.input_numeric("sav", "Savings", 0, min=0, max=1000000, width='20%'),
        ui.input_numeric("age", "Age", 18, min=1, max=100, width='10%'),
    ),
    ui.row(
        ui.input_numeric("zip", "Current Zip Code", 0, min=10000, max=99999, width='20%'),
        ui.input_numeric("rent", "Rent", 500, min=0, max=10000, width='20%'),
        ui.input_select("bedrooms", "Number of Bedrooms", ["Studio", "1BR", "2BR", "3BR", "4BR"], width='20%'),
        ui.input_slider("dis", "Distance", value=1, min=1, max=500, step=50, post="mi", width='20%'),
        ui.input_checkbox_group("checkbox_item", "Nationwide?", choices=["Yes"], width='10%'),
        ui.output_ui("ui_select"),
    ),
    ui.row(
        ui.input_action_button("predict","Predict", width='20%'),
        ui.output_text_verbatim("results", placeholder=True),
        ui.p(
        ui.output_text_verbatim("out"),
    ),
    ),
)
        

def server(input, output, session):
    ###### Load data ######
    wages_df = pd.read_csv('./Data/Clean/cln_wages.csv')
    rent_df = pd.read_csv('./Data/Clean/rent.csv')

    ###### Initialize UI ######
    @reactive.Effect
    @output
    @render.ui
    def map(lat=32.2540, lon=-110.9742):
        '''
        Initialize the map with coordinates to Tucson, AZ.
        Will also update the map when the predictions are made
        '''
       
        print("ZIP:", input.zip())
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(input.zip())
        if location == None:
            location = geolocator.geocode(85701)
        lat = location.latitude
        lon = location.longitude

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
        fig, ax = plt.subplots()

        # use an sns histplot to create a histogram
        # filter wages_df by the industry selected in the dropdown menu
        wages = wages_df[wages_df['OCC_TITLE'] == input.industry()]
        sns.histplot(wages, ax=ax, kde=True, bins=20)
        return fig


    @reactive.Effect
    @output
    @render.plot
    def plot_2():
        '''
        This function will create a plot that will show the average rent for the user's specific calculations
        '''
        zip = str(input.zip())
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(zip)
        city = location
        print("city:", city)

        fig, ax = plt.subplots()

        # use an sns histplot to create a histogram
        # filter rent_df by the header being equal to the value of the bedroom number
        rent = rent_df[rent_df['City'] == city]
        sns.histplot(rent, ax=ax, kde=True, bins=20)
        return fig

    @reactive.Effect
    @output
    @render.text
    def out():
        '''
        This function will create a text box that will show the user's specific calculations
        '''
        zip = str(input.zip())
        geolocator = Nominatim(user_agent="my_app")
        location = geolocator.geocode(zip)
        city = location
        print("city:", city)
        return  f"Ideal City: {city}\n" + \
                f"Estimated Salary: {input.sal()}\n" + \
                f"Estimated Rent: {input.rent()}\n" + \
                f"Estimated Savings: {input.sav()}\n" + \
                f"Estimated Disposable Income: {input.sal()}\n"


app = App(app_ui, server)