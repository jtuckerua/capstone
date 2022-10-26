from tkinter import CENTER
from shiny import App, render, ui
from shinywidgets import output_widget, register_widget, reactive_read
import ipyleaflet as L
import matplotlib.pyplot as plt
import numpy as np
import calculations

app_ui = ui.page_fluid(
    ui.panel_title("Capstone"),
    #Creating sidebar for inputs
    ui.layout_sidebar(
        ui.panel_sidebar(
            #Creating different input fields
            #Numeric input field takes id(str), label, initial value, min, max, step, and width as parameters.
            #Only the id, label, and initial value are necessary, rest are optional.
            ui.input_numeric("age", "Age", 21, min=1, max=100),
            ui.input_numeric("fam", "Family Size", 1, min=1, max=50),
            ui.input_numeric("sal", "Salary", 0),
            #Input select creates a dropdown list of selections.
            #Parameters: "id" = input id, "label" = input label, "choices" = either a list, dictionary or tuple of choices.
            #Optionally you can set the initial selection with "selected", and whether multiple selections can be made with "multiple"
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
            #Input slider allows for a dynamically changing input that can be used in plots etc.
            #Takes the same parameters as numeric input but you can add a prefix or suffix to the value with "pre" or "post".
            ui.input_slider("dis", "Distance", value=1, min=1, max=1000, step=100, post="mi"),
        ),
        #panel_main creates the main panel for UI elements to be placed in to the right of the sidebar.
        ui.panel_main(
            #Row tells shiny that these UI elements should be next to eachother horizontally.
            ui.row(
                #Column takes a size value telling shiny how much space in each row each element should occupy out of a total of 12.
                #The other parameter is for ui elements to place within the column.
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

app = App(app_ui, server)
