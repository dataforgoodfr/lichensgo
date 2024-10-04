from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
# import pandas as pd
import sys
import os
from pathlib import Path
import plotly.express as px
import dash_mantine_components as dmc

_dash_renderer._set_react_version("18.2.0")

# # Ajoute le dossier parent à sys.path
# chemin_dossier_parent = Path(__file__).parent.parent
# sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_tree_data, get_observation_data, get_table_data

# run with : python Dashboards/dashboard.py

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

session = get_session()

# Get the datasets
# environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()

# Rename columns ids for easier merge
lichen_df.rename(columns={'id':'lichen_id'}, inplace=True)
lichen_species_df.rename(columns={'id':'species_id'}, inplace=True)
observation_df.rename(columns={'id':'observation_id'}, inplace=True)
tree_df.rename(columns={'id':'tree_id'}, inplace=True)

# Merge table_df with lichen_df and lichen_species_df
def merge_table():
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


# Function used to filter the table based on the selected observation ID (for hist 3)
def filter_table_on_observation_and_aggregate_per_lichen(merged_table, obs):
    # Filter the table for the selected observation
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

# Group by species' type and count them
def count_lichen_per_species():

    count_lichen = (
        lichen_df
        .groupby("species_id", as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    # Merge with species names
    count_lichen_merged = count_lichen.merge(lichen_species_df[['species_id', 'name']], on='species_id', how='left')

    # Sort based on occurrences in descending order
    count_lichen_merged = count_lichen_merged.sort_values(by='count', ascending=False).reset_index(drop=True)

    return count_lichen_merged

# Create the hist3 bar plot
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
        # title_text="Espèces observées sur le site sélectionné",
        # title_font=dict(size=24),
        # title={"x": 0.5, "y": 0.95, "xanchor": "center"},
        margin=dict(l=20, r=20, t=40, b=20),
        legend_title_text="Orientation",
        template="plotly_white",
        barcornerradius="30%"
    )

    # Update axes
    hist3.update_xaxes(
        title_text="Nombre",
        showgrid=True,
        # gridcolor='rgba(200, 200, 200, 0.5)',
        # tickfont=dict(size=14)
    )
    hist3.update_yaxes(
        title_text="",
        # tickfont=dict(size=14)
    )

    # Update hover template
    hist3.update_traces(hovertemplate="<b>%{y}</b><br><b>Nombre:</b> %{x}<extra></extra>")

    # Update the legend labels based on the mapping
    hist3.for_each_trace(lambda t: t.update(name=orientations_mapping.get(t.name, t.name)))

    return hist3


# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist3', component_property='figure'),
    Input(component_id='obs-dropdown', component_property='value')
)
def update_hist3(user_selection_obs_id):
    site_table_per_lichen = filter_table_on_observation_and_aggregate_per_lichen(merged_table, user_selection_obs_id)
    return create_hist3(site_table_per_lichen)


def create_hist4(count_lichen_merged, user_selection_species_id):
    # Find the index of the selected species ID in the merged table
    user_selection_idx = count_lichen_merged[count_lichen_merged["species_id"] == user_selection_species_id].index

    # Adjust the color of the selected specie to be darker
    pastel_color = pastel_color_palette[0]
    selected_color = base_color_palette[0]
    color_hist4 = [pastel_color] * len(count_lichen_merged)
    color_hist4[int(user_selection_idx[0])] = selected_color

    # Bar plot
    hist4 = px.bar(
        count_lichen_merged,
        x="count",
        y="name",
        orientation="h",
        color="name",
        color_discrete_sequence=color_hist4,
        # title="Espèces les plus observées par les observateurs Lichens GO",
    )

    # Update layout
    hist4.update_layout(
        # title={"x": 0.5, "y": 0.95, "xanchor": "center"},
        margin=dict(l=10, r=10, t=30, b=10),
        template="plotly_white",
        barcornerradius="30%"
)

    # Remove the legend
    hist4.update(layout_showlegend=False)

    # Update axes
    hist4.update_xaxes(
        title_text="Nombre",
        showgrid=True,
        # gridcolor='rgba(200, 200, 200, 0.5)',
    )
    hist4.update_yaxes(
        title="",
        # tickfont=dict(size=10)  # Adjust tick font size
    )

    # Customize hover information
    hist4.update_traces(hovertemplate="""
        <b>Espèce:</b> %{y}<br>
        <b>Nombre:</b> %{x}<extra></extra>
    """)

    return hist4

# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist4', component_property='figure'),
    Input(component_id='species-dropdown', component_property='value')
)
def update_hist4(user_selection_species_id):

    # Find the lichen species name based on the selected species ID
    user_selection_species_name = lichen_species_df[lichen_species_df["species_id"] == user_selection_species_id]["name"]

    return create_hist4(count_lichen_merged, user_selection_species_id)


# Initialize the Dash app
app = Dash(external_stylesheets=dmc.styles.ALL)

# Merge the tables
merged_table = merge_table()

count_lichen_merged = count_lichen_per_species()

# Create initial filtered table for the first observation ID
observation_ids = merged_table['observation_id'].unique() # Get unique observation IDs for the dropdown
initial_user_selection_obs_id = observation_ids[0]  # Default to the first observation ID

hist3 = update_hist3(initial_user_selection_obs_id)


# Create options for the user species dropdown
user_species_options = [
    {"label": row["name"], "value": row["species_id"]}
    for _, row in count_lichen_merged.sort_values(by="name").iterrows()
]

initial_user_selection_species_id = user_species_options[0]['value'] # Default to the first species ID
hist4 = update_hist4(initial_user_selection_species_id)


style = {
    "border": f"1px solid {dmc.DEFAULT_THEME['colors']['indigo'][4]}",
    "textAlign": "center",
}

app.layout = dmc.MantineProvider(
    dmc.Grid(
        children=[
            dmc.GridCol(
                [
                    html.H3(
                        "Carte des observations",
                        style={
                            "text-align": "left",
                            "margin-left": "20px",
                        },
                    ),
                    html.Img(
                        src="/assets/sample_map.png",
                        style={
                            "width": "60%",  # Set the image width to 100% to fit the column
                            "margin-left": "20px",  # Space between image and text
                        },
                    ),
                ],
                span=7
            ),
            dmc.GridCol(
                [
                    html.H3(
                        "Espèces observées sur le site sélectionné",
                        style={
                            "text-align": "left",
                            "margin-left": "20px",
                        },
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Sélectionner un id d'observation:",
                                style={
                                    "margin-right": "10px",
                                    # "font-weight": "bold",
                                },
                            ),
                            dcc.Dropdown(
                                id="obs-dropdown",
                                options=observation_ids,
                                value=initial_user_selection_obs_id,  # Default value
                                clearable=False,
                                style={"width": "50%"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "center",
                            "margin": "20px",
                        },
                    ),
                    dcc.Graph(id="hist3", figure=hist3),
                ],
                span=5,
            ),
            dmc.GridCol(
                [
                    html.H3(
                        "Espèces les plus observées par les observateurs Lichens GO",
                        style={
                            "text-align": "left",
                            "margin": "20px",
                        },
                    ),
                    html.Div(
                        [
                            html.Label(
                                "Sélectionner une espèce:",
                                style={
                                    "margin-right": "10px",
                                    # "font-weight": "bold",
                                },
                            ),
                            dcc.Dropdown(
                                id="species-dropdown",
                                options=user_species_options,
                                value=initial_user_selection_species_id,  # Default value
                                clearable=False,
                                style={"width": "400px"},
                            ),
                        ],
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "justify-content": "left",
                            "margin-left": "20px",
                        },
                    ),
                    dcc.Graph(id="hist4", figure=hist4),
                ],
                span=8,
            ),
            dmc.GridCol([dcc.Graph(figure={}, id="graph-placeholder")], span=4),
        ]
    )
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
