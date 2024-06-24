from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4 
# Dash version
# run with : python Dashboard/demo_dash.py

# Load data function
def load_data():
    return pd.read_csv("https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv")

# Initialize Dash app
app = Dash(__name__)

# Load data
df = load_data()

# Define app layout with a hidden input
app.layout = html.Div([
    html.H1("Air Travel Time Series Plot", style={'textAlign': 'center'}),
    html.Div("This chart shows the number of air passengers traveled in each month from 1949 to 1960", style={'textAlign': 'center'}),
    dcc.Graph(id='air-travel-graph'),
    html.Div(id='dummy-div', style={'display': 'none'})  # Hidden div acting as a placeholder
])


# Define callback to update graph
@app.callback(
    Output('air-travel-graph', 'figure'),
    Input('dummy-div', 'children')  # Use the hidden div as input
)
def update_graph(value):
    fig = px.line(df, x="Month", y=df.columns[1:], title="Air Passenger Travel")
    return fig


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
