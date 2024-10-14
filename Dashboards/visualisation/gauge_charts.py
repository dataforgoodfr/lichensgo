import sys
import pandas as pd
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, dcc, Output, Input
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.computed_datasets import df_frequency
from Dashboards.charts import create_gauge_chart


# Initialize Dash app
app = Dash(__name__)

# Load the dataset
grouped_df = df_frequency()

# Calcul du degrés d'artificialisation
def calc_deg_artif(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    base_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['poleotolerance'] == 'resistant')]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)

# Calcul de la pollution acidé
def calc_pollution_acide(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    acid_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['ph'] == 'acidophilous')]['freq'].sum()

    return round((acid_freq / global_freq) * 100, 2)

# Calcul de la pollution azoté
def calc_pollution_azote(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    azote_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['eutrophication'] == 'eutrophic')]['freq'].sum()

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

def update_graph(observation_id):
    deg_artif = calc_deg_artif(observation_id)
    pollution_acide = calc_pollution_acide(observation_id)
    pollution_azote = calc_pollution_azote(observation_id)

    fig1 = create_gauge_chart(deg_artif, "Degré d'artificialisation")
    fig2 = create_gauge_chart(pollution_acide, "Pollution acide")
    fig3 = create_gauge_chart(pollution_azote, "Pollution azoté")
    return fig1, fig2, fig3


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
