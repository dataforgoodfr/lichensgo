from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology

# Initialize Dash app
app = Dash(__name__)

# Load data
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_species_df = get_tree_species()
ecology_df = get_lichen_ecology()

# Fonction pour calculer la fréquence des valeurs E, N, O, S
def calculate_frequency(column):
    return column.apply(lambda x: sum(1 for char in x if char in ['E', 'N', 'O', 'S']))

# Calculer la fréquence
table_df['freq'] = (
    table_df['sq1'].apply(lambda x: len(x) if pd.notnull(x).any() else 0)  +
    table_df['sq2'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq3'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq4'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq5'].apply(lambda x: len(x) if pd.notnull(x).any() else 0)
)

# Joindre table avec lichen et observation
merged_df = table_df.merge(lichen_df, left_on='lichen_id', right_on='id', suffixes=('', '_l'))
merged_df = merged_df.merge(lichen_species_df, left_on='species_id', right_on='id', suffixes=('', '_ls'))
merged_df = merged_df.merge(observation_df, left_on='observation_id', right_on='id', suffixes=('', '_o'))

# Grouper par 'species' et 'observation_id' et additionner les fréquences
grouped_df = merged_df.groupby(['name', 'observation_id'])['freq'].sum().reset_index()

# Regrouper les deux tables afficher les données écologiques
grouped_df = grouped_df.merge(ecology_df, left_on='name', right_on='cleaned_taxon', suffixes=('', '_e'))

# ajustement des noms finaux
grouped_df = grouped_df[['observation_id', 'name', 'freq','pH','eutrophication', 'poleotolerance']]
grouped_df = grouped_df.rename(
    columns={
        'observation_id': 'id', 
        'name': 'lichen', 
        'freq': 'freq',
        'pH': 'ph',
        'eutrophication': 'eutrophication', 
        'poleotolerance': 'poleotolerance'
        })

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
                'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': pollution_acide(value)}
                }))

    fig3 = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = pollution_azote(value),
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
                'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': pollution_azote(value)}
                }))
    return fig1, fig2, fig3


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
