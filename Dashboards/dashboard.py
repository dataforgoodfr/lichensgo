from dash import Dash, html, dcc, Output, Input
# import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import os

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_tree_data, get_observation_data, get_table_data

# run with : python Dashboards/dashboard.py

session = get_session()

square_columns = ['sq1', 'sq2', 'sq3', 'sq4', 'sq5']
orientations = ['N', 'E', 'S', 'O']

# Create a mapping dictionary for legend items (orientations)
orientations_mapping = {
    "N": "Nord",
    "E": "Est",
    "S": "Sud",
    "O": "Ouest"
}

# Color palette (other options here: https://plotly.com/python/discrete-color/)
base_color_palette = px.colors.qualitative.Set2
pastel_color_palette = px.colors.qualitative.Pastel2

def load_table():

    # Get the datasets
    # environment_df = get_environment_data()
    lichen_df = get_lichen_data()
    lichen_species_df = get_lichen_species_data()
    observation_df = get_observation_data()
    table_df = get_table_data()
    tree_df = get_tree_data()

    # Rename columns ids for easyer merge
    lichen_df.rename(columns={'id':'lichen_id'}, inplace=True)
    lichen_species_df.rename(columns={'id':'species_id'}, inplace=True)
    observation_df.rename(columns={'id':'observation_id'}, inplace=True)
    tree_df.rename(columns={'id':'tree_id'}, inplace=True)

    # Calculate the number of lichens per orientation for each lichen in the table
    for orientation in orientations:
        table_df[orientation] = table_df[square_columns].apply(
            lambda row: sum(orientation in sq for sq in row), axis=1
        )

    # Sum of N + E + S + O for each lichen
    table_df['sum_quadrat'] = table_df[orientations].sum(axis=1)

    # Merge tables
    merged_table = table_df.merge(right=lichen_df, how='left').merge(right=lichen_species_df, how='left')

    return merged_table


def filter_and_aggregate_table_per_lichen(merged_table, obs):
    # Filter the table for the observation
    site_table = merged_table.query("observation_id == @obs")

    # Group by lichen_id
    site_table_per_lichen = site_table.groupby(by='lichen_id', as_index=False).agg(
        {
            'name': 'first',
            'N': 'sum',
            'O': 'sum',
            'S': 'sum',
            'E': 'sum',
            'sum_quadrat': 'sum'
        }).sort_values(by='sum_quadrat', ascending=True, ignore_index=True)

    return site_table_per_lichen


# Initialize the Dash app
app = Dash(__name__)

# Load the data
table = load_table()

# Get unique observation IDs for the dropdown
observation_ids = table['observation_id'].unique()

# Create initial filtered table for the first observation ID
initial_obs = observation_ids[0]  # Default to the first observation ID
site_table_per_lichen = filter_and_aggregate_table_per_lichen(table, initial_obs)

# Create the bar plot
def create_hist3(site_table_per_lichen):

    # Create the bar plot
    hist3 = px.bar(
        site_table_per_lichen,
        x=orientations,
        y="name",
        orientation="h",
        color_discrete_sequence=base_color_palette
    )

    # Update layout
    hist3.update_layout(
        title_text="Espèces observées sur le site sélectionné",
        title={"x": 0.5, "y": 0.95, "xanchor": "center"},
        margin=dict(l=20, r=20, t=40, b=20),
        legend_title_text="Orientation",
        template="plotly_white",
        barcornerradius="30%"
    )

    # Update axes
    hist3.update_xaxes(
        title_text="Nombre",
        showgrid=True,
        gridcolor='rgba(200, 200, 200, 0.5)',
        tickfont=dict(size=14)
    )
    hist3.update_yaxes(
        title_text="",
        tickfont=dict(size=14)  # Adjust tick font size
    )

    # Customize hover information
    hist3.update_traces(hovertemplate="""
        <b>Espèce:</b> %{y}<br>
        <b>Nombre:</b> %{x}<extra></extra>
    """)

    # Update the legend labels based on the mapping
    hist3.for_each_trace(lambda t: t.update(name=orientations_mapping.get(t.name, t.name)))

    return hist3


hist3 = create_hist3(site_table_per_lichen)


# Define the layout of the Dash app
app.layout = html.Div([
    html.H1("Observations de Lichens", style={'text-align': 'center'}),
    html.Div([
        html.Label("Sélectionner un id d'observation:", style={'margin-right': '10px', 'font-weight': 'bold'}),
        dcc.Dropdown(
            id='obs-dropdown',
            options=observation_ids,
            value=initial_obs,  # Default value
            clearable=False,
            style={'width': '50%'}
        )
    ], style={'display': 'flex', 'align-items': 'center', 'justify-content': 'center', 'margin': '20px'}),
    dcc.Graph(
        id='lichens-bar-chart',
        figure=hist3
    )
])


# Define callback to update the bar chart based on selected observation ID
@app.callback(
    Output('lichens-bar-chart', 'figure'),
    Input('obs-dropdown', 'value')
)
def update_bar_chart(selected_obs):
    site_table_per_lichen = filter_and_aggregate_table_per_lichen(table, selected_obs)
    return create_hist3(site_table_per_lichen)

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
