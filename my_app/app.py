from logging import PlaceHolder
from tkinter import CENTER
from turtle import width
from shiny import App, render, ui, reactive
from shinywidgets import output_widget, register_widget, reactive_read
import asyncio
import ipyleaflet as L
import matplotlib.pyplot as plt
import numpy as np
import calculations as calcs

def nav_controls(prefix):
    return [
        ui.nav("City A", prefix + ": tab a content"),
        ui.nav("City B", prefix + ": tab b content"),
        ui.nav("City C", prefix + ": tab c content"),
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
            ui.column(3, output_widget("map")),
            ui.column(3, ui.output_plot("plot")),
            ui.column(3, ui.output_plot("plot_2")),
            ui.column(3, ui.output_plot("plot_3")),
        ),
    ))),
    ui.row(
        ui.input_select("goal", "Financial Goal", ["Buy a home", "Save money","Pay off debt", "Retire"], width='20%'),
        ui.input_select("industry", "Job Industry", ["Doctor", "Nurse", "EMT", "Server", "Bartender", "Janitor","Financial Advisor", "Accountant", "Stock Broker"], width='20%'),
        ui.input_numeric("sal", "Salary", 10000, min=10000, max=1000000, width='10%'),
        ui.input_numeric("age", "Age", 18, min=1, max=100, width='10%'),
        ui.input_numeric("fam", "Family #", 1, min=1, max=10, width='10%'),
        ui.input_slider("dis", "Distance", value=1, min=1, max=1000, step=50, post="mi", width='20%'),
        ui.input_action_button("predict","Predict", width='10%'),
        ui.output_text_verbatim("results", placeholder=True)
    ),
)
        

def server(input, output, session):
    # Initialize map
    map = L.Map(center=(32.2540,-110.9742), zoom=12, scroll_wheel_zoom=True)
    register_widget("map", map)
    @output
    @render.text
    @reactive.event(input.predict)
    # This function is used to display data that is returned from the db
    async def results():
        vals = [input.age(), input.fam(), input.sal()]
        # print(calcs.calc_values(vals))
        await asyncio.sleep(2)
        return f"Age: {input.age()}, Family: {input.fam()}, Salary: {input.sal()}"
    #output and render.plot need to be called before every plot for it to load.
    @output
    @render.plot(alt="Test")
    #These are currently just placeholder plots that are tied to the input_slider.
    def plot():
        np.random.seed(19680001)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.dis(), density=True)
        return fig
    @output
    @render.plot(alt="Test")
    def plot_2():
        np.random.seed(19684001)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.dis(), density=True)
        return fig
    @output
    @render.plot(alt="Test")
    def plot_3():
        np.random.seed(12680001)
        x = 100 + 15 * np.random.randn(437)

        fig, ax = plt.subplots()
        ax.hist(x, input.dis(), density=True)
        return fig
    @reactive.Effect
    def _():
        #dynamically inserts UI elements based on the selected financial goal. When pay off debt is selected it will add UI elements
        #asking what the outstanding debt amount is and what the interest rate is. If anything besides pay off deb is selected this 
        #function will remove the input UI elements for outstanding debt amount and interest rate. To position insert_ui correctly you
        #must specify a selector and tell it where to place the new ui element relative to the selector. where can = beforeBegin, afterBegin,
        #beforeEnd, or afterEnd. Selector is based on the id of each UI element and must be formatted how it is in this function. 
        goal = input.goal()
        if goal == "Pay off debt":
            ui.insert_ui(ui.input_numeric("pay", "Outstanding Debt Amount ($)", 10000, min=10000, max=1000000, width='10%'), selector="div:has(> #predict)", where="beforeEnd")
            ui.insert_ui(ui.input_numeric("int", "Interest Rate (%)", 1, min=0, max=20, width='10%'), selector="div:has(> #predict)", where="beforeEnd")
        elif goal != "Pay off debt":
            ui.remove_ui(selector="div:has(> #pay)")
            ui.remove_ui(selector="div:has(> #int)")
            return
app = App(app_ui, server)

