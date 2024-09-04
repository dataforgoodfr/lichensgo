import sys
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.computed_datasets import df_frequency


# Initialize Dash app
app = Dash(__name__)

# Load the dataset
grouped_df = df_frequency()

# Calcul du degrés d'artificialisation
def deg_artif(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    base_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['poleotolerance'] == 'resistant')]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)

# Calcul de la pollution acidé 
def pollution_acide(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    acid_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['ph'] == 'acidophilous')]['freq'].sum()

    return round((acid_freq / global_freq) * 100, 2)

# Calcul de la pollution azoté
def pollution_azote(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    azote_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['eutrophication'] == 'eutrophic')]['freq'].sum()

    return round((azote_freq / global_freq) * 100, 2)

# Define app layout with a hidden input
app.layout = html.Div([
    html.H1("Gauge bar Dash", style={'textAlign': 'center'}),
    dcc.Dropdown(grouped_df["id"].unique(), 419, id='dropdown-selection', style={'width': '50%', 'margin': 'auto'}),
    html.Div([
        dcc.Graph(id='graph-content1', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='graph-content2', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='graph-content3', style={'flex': '1', 'margin': '10px'})
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '100%'})
])

# Define callback to update graph
@app.callback(
    [
        Output('graph-content1', 'figure'),
        Output('graph-content2', 'figure'),
        Output('graph-content3', 'figure')
    ],
    Input('dropdown-selection', 'value')
)

def update_graph(value):
    fig1 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = deg_artif(value),
        number = {'suffix': "%"},
        mode = "gauge+number",
        title = {'text': "Degré d'artificialisation"},
        gauge = {'axis': {'range': [0, 100], 'dtick': 25},
                'bar': {'color': "#000000"},
                'steps' : [
                    {'range': [0, 25], 'color': "green"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                    ],
                'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': deg_artif(value)}
                }))

    fig2 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = pollution_acide(value),
        number = {'suffix': "%"},
        mode = "gauge+number",
        title = {'text': "Pollution acide"},
        gauge = {'axis': {'range': [0, 100], 'dtick': 25},
                'bar': {'color': "#000000"},
                'steps' : [
                    {'range': [0, 25], 'color': "green"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                    ],
                'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': pollution_acide(value)}
                }))

    fig3 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = pollution_azote(value),
        number = {'suffix': "%"},
        mode = "gauge+number",
        title = {'text': "Pollution azoté"},
        gauge = {'axis': {'range': [0, 100], 'dtick': 25},
                'bar': {'color': "#000000"},
                'steps' : [
                    {'range': [0, 25], 'color': "green"},
                    {'range': [25, 50], 'color': "yellow"},
                    {'range': [50, 75], 'color': "orange"},
                    {'range': [75, 100], 'color': "red"}
                    ],
                'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': pollution_azote(value)}
                }))
    return fig1, fig2, fig3


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
