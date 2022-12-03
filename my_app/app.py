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
from Data import controller_program as ctl

sns.set_theme()

rent_df = pd.read_csv('C:\\Users\\andre\\Desktop\\Classes\\capstone\\my_app\\Data\\Clean\\rent.csv')
wages_df = pd.read_csv('C:\\Users\\andre\\Desktop\\Classes\\capstone\\my_app\\Data\\Clean\\cln_wages.csv')

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
        ui.input_numeric("sal", "Salary", 10000, min=0, max=1000000, width='20%'),
        ui.input_numeric("sav", "Savings", 0, min=0, max=1000000, width='20%'),
        ui.input_numeric("age", "Age", 18, min=1, max=100, width='10%'),
    ),
    ui.row(
        ui.input_numeric("zip", "Current Zip Code", 0, min=10000, max=99999, width='20%'),
        ui.input_numeric("rent", "Rent", 500, min=0, max=10000, width='20%'),
        ui.input_select("bedrooms", "Number of Bedrooms", ["Studio", "One Bedroom", "Two Bedroom", "Three Bedroom", "Four Bedroom", "Five Bedroom"], width='20%'),
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

    @reactive.Effect
    def ui_select():
        x = input.checkbox_item()
        if x == 'Yes':
            dis = 'nationwide'
            ui.remove_ui(selector="div:has(> #dis)")
            return dis 
        else: 
            return
    
    user_provided_values = reactive.Value([])
    @reactive.Effect
    @reactive.event(input.predict)
    def add_value_to_list():
        user_provided_values.set(user_provided_values() + [input.goal(), input.industry(), input.sal(), input.sav(),
        input.age(), input.zip(), input.rent(), input.bedrooms(), input.dis()])
        values = user_provided_values()
        goal = values[0]
        industry = values[1]
        salary = values[2]
        saving = values[3]
        age = values[4]
        zipcode = values[5]
        rent = values[6]
        bed = values[7]
        dist = values[8]
        return goal, industry, salary, saving, age, zipcode, rent, bed, dist
    
    @reactive.Calc
    def calcs(salary, location, rent, saving, industry, bed, dist):
        """
        Salary = data[0]
        savings = data[1]
        debt = data[2]
        goal = data[3]
        rent = data[4]
        bedroom = data[5]
        location = data[6]
        industry = data[7]
        """
        retval = {}
        cur_location = get_info(location)
        retval['Current Location'] = [d_income(salary,rent), rent]
    
        """
        Receives a goal and procedes with teh proper calcs for achieving the gaol
        "Buy a home", "Save money","Pay off debt", "Retire"
        """

        #collect industry dataframe
        ind_df = get_industry_df(industries.get(str(industry)))
        #convert fips to city and state
        locs = get_industry_loc(ind_df)
        retval['Location one'] = [ind_df['avg_annual_pay'][0],locs[0]]
        retval['Location two'] = [ind_df['avg_annual_pay'][1],locs[0]]
        retval['Location three'] = [ind_df['avg_annual_pay'][2],locs[0]]
        return retval
    
    @reactive.Calc
    def get_industry_df(industry):
        """
        collect the top three rows for employee level by industry.
        return the fips and their average annual pay
        """
        df = pd.read_csv('C:\\Users\\andre\\Desktop\\Classes\\capstone\\my_app\\Data\\Clean\\location_industry.csv')
        return df[df['industry_code'] == industry].sort_values('annual_avg_emplvl', axis=0, ascending=False)[:3].loc[:,['area_fips','avg_annual_pay']]

    @reactive.calc
    def get_industry_loc(df):
        """
        returns the top cities for the industry 
        """
        lf = pd.read_csv('.\\my_app\\Data\\Clean\\location_codes.csv')
        tmp = lf[lf['area_fips'].isin(df['area_fips'].values)].loc[:,['City','State']]
        return (get_info(",".join(tmp.values[0])),get_info(",".join(tmp.values[1])),get_info(",".join(tmp.values[2])))




    """
    Below are all of the calculation functions!
    ********************************************
    """

    @reactive.calc
    def calc_home_buy(salary):
        """
        Calculate the amount of home afforded based on salary
        Returns the down payment and the amount of house for both 15 and 30 year
        """
        m_sal =  salary * .28
        return ((m_sal * 15,(m_sal * 15)*.1), (m_sal * 30,(m_sal * 30)*.1))

    @reactive.calc
    def total_debt(data):
        """
        calc totat debt amount
        """
        tot = 0
        for i in data:
            tot += int(i[0])
        return tot
        
    @reactive.calc
    def savings(savings, salary, goal):
        """
        takes current savings, current salary, and goal
        and calculates how long until that goal is reached. 
        returns the amount of months to reach goal.
        """
        dif = goal - savings
        return dif / (salary/12)*.2

    @reactive.Calc
    def d_income(salary, rent):
        """
        Calculate the disposable income index
        """
        return (salary/12) - rent




    """
    Below are all of the location functions!
    ******************************************
    """

    coder = Nominatim(user_agent='geopytest')
    @reactive.calc
    def get_info(location):
        return coder.geocode(location)
    @reactive.calc
    def distance_calc(location1, location2):
        """
        input: current location and radius
        output: all cities within the radius
        """
        return geodesic(location1[1], location2[1]).miles
    @reactive.calc
    def get_rent(locs, rooms):
        rent = pd.read_csv('./Clean/rent.csv')


    @output
    @render.text
    def out():
        return f"Values: {user_provided_values()}"
        
    # Initialize map
    map = L.Map(center=(32.2540,-110.9742), zoom=12, scroll_wheel_zoom=True)
    register_widget("map", map)

    # create a function that will be used to update the map whenever the tab is switched
    @reactive.Calc
    def predict():
        debt = []
        for i in range(1, 4):
            debt.append((input[f"pay{i}"], input[f"int{i}"], input[f"term{i}"]))
        # Get data from database
        # Run calculations
        results = ctl.calcs([input.sal, input.sav, debt, input.goal, input.rent, input.bedrooms, input.location, input.industry])

        # get the current tab
        tab = input.tab()

        if tab == 'City A':
            city = results['Location one'][1][0].split(',')[0]
            lat, lon = results['Location one'][1][1]

        elif tab == 'City B':
            city = results['Location two'][1][0].split(',')[0]
            state = results['Location two'][0][1]
        return city, state, lat, lon

    # make two seaborn histplots to display on the initiali app state, before any data is input
    @output
    @render.plot
    async def plot():
        city, _, _, _ = predict()
        
        # create an initial seaborn plot
        fig, ax = plt.subplots()

        # get the data
        rent = pd.read_csv('C:\\Users\\andre\\Desktop\\Classes\\capstone\\my_app\\Data\\Clean\\rent.csv')

        # filter the data to only the outputted zipcode
        rent = rent[rent['ZIP Code'] == zipcode]

        # set the title
        ax.set_title(f"Rent in {city}")

        # plot the data
        sns.histplot(rent, x="Rent", ax=ax)

        # return the plot
        return sns.histplot(data=rent, x="Rent", kde=True, ax=ax)

    @output
    @render.plot
    async def plot_3():
        #get output from calculations
        city, _, _, _ = predict()

        # create an initial seaborn plot
        fig, ax = plt.subplots()

        # get the data
        wages = pd.read_csv('C:\\Users\\andre\\Desktop\\Classes\\capstone\\my_app\\Data\\Clean\\rent.csv')

        # modify the data to the city and industry data
        wages = wages[wages['City'] == 'Tucson']
        wages = wages[wages['Industry'] == 'Total, all industries']

        # set the title
        ax.set_title(f"Wages in {city}")

        # plot the data
        sns.histplot(wages, x="Wages", ax=ax)

        # return the plot
        return sns.histplot(data=wages, x="Wages", kde=True, ax=ax)

    @output
    @render.ui
    def map():
        city, state, lat, lon = predict()
        # update the panel title
        ui.panel_title(city + ' ' + state + ' ' + 'Map', 'Capstone')

        # update the map
        map.set_center((lat, lon))
        map.set_zoom(12)
        map.clear_layers()
        L.Marker(location=(lat, lon)).add_to(map)
        return map

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