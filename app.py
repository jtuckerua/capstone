from markupsafe import escape
from flask import Flask
from shiny import App as tmp
from shiny import *

app = Flask(__name__)

app_ui = ui.page_fluid(
  ui.input_slider("n", "Value of n", min=1, max=10, value=5),
  ui.output_text("n2")
)

def server(input: Inputs, output: Outputs, session: Session) -> None:
    @output
    @render.text
    def n2():
        return f"The value of n*2 is {input.n() * 2}"
tmp(app_ui,server)

@app.route('/')
@app.route('/index/')
def hello():
    return '<h1>Hello, World!</h1>'

@app.route('/about/')
def about():
    return '<h3>This is a Flask web application.</h3>'

@app.route('/capitalize/<word>/')
def capitalize(word):
    return '<h1>{}</h1>'.format(escape(word.capitalize()))

if __name__ =="__main__()":
    app.run(host='127.0.0.1',port=5000)