from logging import PlaceHolder
from tkinter import CENTER
from turtle import width
from shiny import App, render, ui, reactive, Outputs
from shinywidgets import output_widget, register_widget, reactive_read
import asyncio
import ipyleaflet as L
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
from Data import controller_program as ctl


def nav_controls(prefix):
    return [
        ui.nav("City A"),
        ui.nav("City B"),
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
            ui.column(4, ui.output_plot("plot_3")),
        ),
    ))),
    ui.row(
        ui.input_select("goal", "Financial Goal", ["Buy a home", "Improve Quality of Life","Investment Property"], width='20%'),
        ui.input_select("industry", "Job Industry", ['Total, all industries','Agriculture, forestry, fishing and hunting','Mining, quarrying, and oil and gas extraction', 'Utilities',
       'Construction', 'Manufacturing', 'Wholesale trade', 'Retail trade','Transportation and warehousing', 'Information','Finance and insurance', 'Real estate and rental and leasing',
       'Professional and technical services','Management of companies and enterprises','Administrative and waste services', 'Educational services','Health care and social assistance',
       'Arts, entertainment, and recreation','Accommodation and food services','Other services, except public administration','Public administration', 'Unclassified'], width='20%'),
        ui.input_numeric("sal", "Salary", 10000, min=10000, max=1000000, width='20%'),
        ui.input_numeric("sav", "Savings", 0, min=0, max=1000000, width='20%'),
        ui.input_numeric("age", "Age", 18, min=1, max=100, width='10%'),
    ),
    ui.row(
        ui.input_numeric("zip", "Current Zip Code", 0, min=10000, max=99999, width='20%'),
        ui.input_numeric("rent", "Rent", 0, min=0, max=10000, width='20%'),
        ui.input_select("bedrooms", "Number of Bedrooms", ["Studio", "One Bedroom", "Two Bedroom", "Three Bedroom", "Four Bedroom", "Five Bedroom"], width='20%'),
        ui.input_slider("dis", "Distance", value=1, min=1, max=500, step=50, post="mi", width='20%'),
        ui.input_checkbox_group("checkbox_item", "Nationwide?", choices=["Yes"], width='10%'),
        ui.output_ui("ui_select"),
    ),
    ui.row(
        ui.input_action_button("predict","Predict", width='20%'),
        ui.output_text_verbatim("results", placeholder=True)
    ),
)
        

def server(input, output, session):
    # Initialize map
    @reactive.Effect
    def ui_select():
        x = input.checkbox_item()
        if x == 'Yes':
            dis = 'nationwide'
            ui.remove_ui(selector="div:has(> #dis)")
            return dis 
        else: 
            return

        #return ui.input_select(
            #"in_select",
            #label=f"Select input ({len(x)} options)",
            #choices=x,
            #selected=None,
        
    map = L.Map(center=(32.2540,-110.9742), zoom=12, scroll_wheel_zoom=True)
    register_widget("map", map)
    @output
    @render.text
    @reactive.event(input.predict)
    async def predict():
        #Get input data
        goal = input.goal
        industry = input.industry
        salary = input.sal
        savings = input.sav
        rent = input.rent
        rooms = input.bedrooms
        # distance = input.dis
        location = input.loc
        # get debt data from input as a list of 3-element integer tuples (pay, int, term)
        # where each tuple corresponds to a financial goal and the list is the
        # debt for each goal
        debt = []
        for i in range(1, 4):
            debt.append((input[f"pay{i}"], input[f"int{i}"], input[f"term{i}"]))
        # Get data from database
        # Run calculations
        results = ctl.calcs([salary, savings, debt, goal, rent, rooms, location, industry])
        #Return results 
        return results
    # This function is used to display data that is returned from the db
    async def results():
        #get output from calculations
        results = predict()
        # display results
        return results
    # make two seaborn histplots to display on the initiali app state, before any data is input
    @output
    @render.plot
    @reactive.event(input.predict)
    async def plot():
        #get output from calculations
        results = predict()

        zipcode = None
        lat = None
        long = None
        
        # create an initial seaborn plot
        fig, ax = plt.subplots()

        # get the data
        rent = ctl.get_rent()

        # filter the data to only the outputted zipcode
        rent = rent[rent['ZIP Code'] == zipcode]

        # create the plot
        sns.histplot(data=rent, x="Rent", kde=True, ax=ax)

        # set the title
        ax.set_title(f"Rent in {zipcode}")

        # return the plot
        return fig

    @output
    @render.plot
    @reactive.event(input.predict)
    async def plot_3():
        #get output from calculations
        results = predict()

        # location = results[]

        zipcode = None

        # create an initial seaborn plot
        fig, ax = plt.subplots()

        # get the data
        wages = pd.read_csv('Data/Clean/cln_wages.csv')

        # modify the data to the city and industry data
        wages = wages[wages['City'] == 'Tucson']
        wages = wages[wages['Industry'] == 'Total, all industries']

        # create the plot
        sns.histplot(data=wages, x="Rent", kde=True, ax=ax)

        # set the title
        ax.set_title(f"Wages in {zipcode}")

        # return the plot
        return fig

    # create a function that will be used to update the map whenever the tab is switched
    @reactive.Calc
    def locate():
        # get the predict() data
        results = predict()

        # get the current tab
        tab = input.tab()

        if tab == 'City A':
            city = results['Location one'][0][0]
            state = results['Location one'][0][1]
            lat, lon = results['Current Location'][3]

        elif tab == 'City B':
            city = results['Location two'][0][0]
            state = results['Location two'][0][1]
            lat, lon = results['Current Location'][3]
        return city, state, lat, lon

    @output
    @render.ui
    def map():
        city, state, lat, lon = locate()
        # update the panel title
        ui.panel_title(city + ' ' + state + ' ' + 'Map', 'Capstone')

        # update the map
        map.set_center((lat, lon))
        map.set_zoom(12)
        map.clear_layers()
        L.Marker(location=(lat, lon)).add_to(map)
        return
        
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

    
app = App(app_ui, server)