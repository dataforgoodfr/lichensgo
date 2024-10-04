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
from my_data.computed_datasets import table_df_frequency, sum_frequency_per_lichen, count_lichen_per_species

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

# Get the datasets
# environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()

merged_table = table_df_frequency(lichen_df, lichen_species_df, observation_df, table_df)
count_lichen_merged = count_lichen_per_species(lichen_df, lichen_species_df)

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
    # Filter the table for the selected observation (also called site)
    site_df = merged_table.query("observation_id == @user_selection_obs_id")

    # Sum by lichen_id
    site_sum_per_lichen = sum_frequency_per_lichen(site_df)

    return create_hist3(site_sum_per_lichen)


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

    # Update hover template
    hist4.update_traces(hovertemplate="<b>%{y}</b><br><b>Nombre:</b> %{x}<extra></extra>")

    return hist4

# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist4', component_property='figure'),
    Input(component_id='species-dropdown', component_property='value')
)
def update_hist4(user_selection_species_id):

    # Find the lichen species name based on the selected species ID
    user_selection_species_name = lichen_species_df[lichen_species_df["id"] == user_selection_species_id]["name"]

    return create_hist4(count_lichen_merged, user_selection_species_id)


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


# Initialize the Dash app
app = Dash(external_stylesheets=dmc.styles.ALL)

# Layout for the "Sites" tab
sites_tab = dmc.TabsPanel(
    children=[
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
                                "width": "60%",
                                "margin-left": "20px",
                            },
                        ),
                    ],
                    span=7,
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
                                    },
                                ),
                                dcc.Dropdown(
                                    id="obs-dropdown",
                                    options=observation_ids,
                                    value=initial_user_selection_obs_id,
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
            ]
        )
    ],
    value="1",
)

# Layout for the "Espèces" tab
species_tab = dmc.TabsPanel(
    children=[
        dmc.Grid(
            children=[
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
                                    },
                                ),
                                dcc.Dropdown(
                                    id="species-dropdown",
                                    options=user_species_options,
                                    value=initial_user_selection_species_id,
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
                dmc.GridCol(
                    [dcc.Graph(figure={}, id="graph-placeholder")],
                    span=4,
                ),
            ]
        ),
    ],
    value="2",
)

# Define the main layout with tabs
app.layout = dmc.MantineProvider(
    dmc.Tabs(
        [
            dmc.TabsList(
                [
                    dmc.TabsTab("Sites", value="1"),
                    dmc.TabsTab("Espèces", value="2"),
                ]
            ),
            sites_tab,
            species_tab,
        ],
        value="1",  # Default to the first tab
    )
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
