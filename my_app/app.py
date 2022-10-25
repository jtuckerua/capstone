from tkinter import CENTER
from shiny import App, render, ui
from shinywidgets import output_widget, register_widget, reactive_read
import ipyleaflet as L
import matplotlib.pyplot as plt
import numpy as np

app_ui = ui.page_fluid(
    ui.panel_title("Capstone"),
    #Creating sidebar for inputs
    ui.layout_sidebar(
        ui.panel_sidebar(
            #Creating different input fields
            ui.input_numeric("age", "Age", 21, min=1, max=100),
            ui.input_numeric("fam", "Family_Size", 1, min=1, max=50),
            ui.input_numeric("sal", "Salary", 0),
            #Drop down list of industries
            ui.input_select(
                "industry",
                "Choose your industry:",
                choices=["Doctor", "Nurse", "EMT", "Server", "Bartender", "Janitor","Financial Advisor", "Accountant", "Stock Broker"]
            ),
            ui.input_numeric("sav", "Current Savings", 0),
            ui.input_numeric("debt", "Current Debt", 0),
            ui.input_select(
                "goal",
                "Choose your financial goal:",
                choices=["Buy a home", "Save money","Pay off debt", "Retire"]
            ),
            #Desired distance from current place for moving reccomendations
            ui.input_slider("dis", "Distance", value=1, min=1, max=1000, step=100, post="mi"),
        ),
        ui.panel_main(
            ui.row(
                ui.column(6, output_widget("map")),
                ui.column(6, ui.output_plot("plot")),
            ),
            ui.row(
                ui.column(6, ui.output_plot("plot_2")),
                ui.column(6, ui.output_plot("plot_3")),
            ),
            
           
    ),  
    ),
)


def server(input, output, session):
    # Initialize map
    map = L.Map(center=(32.2540,-110.9742), zoom=12, scroll_wheel_zoom=True)
    register_widget("map", map)
    @output
    @render.plot(alt="Test")
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

app = App(app_ui, server)
