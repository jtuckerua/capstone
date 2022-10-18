from tkinter import CENTER
from shiny import App, render, ui
from shinywidgets import output_widget, register_widget, reactive_read
import ipyleaflet as L

app_ui = ui.page_fluid(
    ui.panel_title("Optamization App"),
    output_widget("map")

)


def server(input, output, session):
    # Initialize map
    map = L.Map(center=(32.2540,-110.9742), zoom=12, scroll_wheel_zoom=True)
    register_widget("map", map)

app = App(app_ui, server)
