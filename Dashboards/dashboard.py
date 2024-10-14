import plotly.express as px
import plotly.graph_objects as go
import dash_mantine_components as dmc
import pandas as pd

from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
from dash.dependencies import State
from dash_iconify import DashIconify
from datetime import datetime, timedelta, date

from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_tree_data, get_observation_data, get_table_data, get_lichen_ecology
from my_data.computed_datasets import merge_tables, vdl_value, count_lichen, count_lichen_per_species, count_species_per_observation, count_lichen_per_lichen_id, df_frequency
from charts import create_hist1_nb_species, create_hist2_vdl, create_hist3, create_hist4, create_gauge_chart

_dash_renderer._set_react_version("18.2.0")
# run with : python Dashboards/dashboard.py

# Initialize the Dash app
app = Dash(__name__,
           external_stylesheets=[
               dmc.styles.ALL,
               dmc.styles.DATES,
              "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap"
           ],
           title="Lichens GO"
    )

# Get the datasets
# environment_df = get_environment_data()
print("Fetching data...")
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()
ecology_df = get_lichen_ecology()

## For tab on observations
merged_table_df = merge_tables(table_df, lichen_df, lichen_species_df, observation_df)
merged_table_with_nb_lichen_df = count_lichen(merged_table_df)
nb_lichen_per_lichen_id_df = count_lichen_per_lichen_id(merged_table_with_nb_lichen_df , lichen_df, lichen_species_df)

observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
observation_with_vdl_df = vdl_value(observation_with_species_count_df, merged_table_with_nb_lichen_df)

# For tab on species
nb_lichen_per_species_df = count_lichen_per_species(lichen_df, lichen_species_df)

# Dataset for the gauge charts (to be improved)
grouped_df = df_frequency(lichen_df, lichen_species_df, observation_df, table_df, ecology_df)

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

## Map

# Colors for the map
color_dict_nb_species = {'<7': 'red', '7-10': 'orange', '11-14': 'yellow', '>14': 'green'} # number of species
color_dict_vdl = {'<5': 'red', '5-10': 'orange', '10-15': 'yellow', '>15': 'green'} # VDL

# Dictionnaire de couleurs à utiliser pour chaque variable
map_color_palettes = {
    'nb_species_cat': color_dict_nb_species,
    'VDL_cat': color_dict_vdl,
}

# Liste des variables disponibles pour afficher sur la carte
map_columns = list(map_color_palettes.keys())


# Callback pour mettre à jour la carte et l'histogramme en fonction des dates sélectionnées
@callback(
    Output('species-map', 'figure'),
    Output('gauge-chart1', 'figure'),
    Output('gauge-chart2', 'figure'),
    Output('gauge-chart3', 'figure'),
    Output('species-hist1', 'figure'),
    Output('vdl-hist2', 'figure'),
    Output('hist3','figure'),

    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('column-dropdown', 'value'),
    Input('species-map', 'clickData'),

    State('species-map', 'relayoutData')  # État actuel du zoom et de la position de la carte

)
def update_map(start_date, end_date, selected_column, clickData, relayoutData):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    # Filtrer le dataframe pour correspondre aux dates sélectionnées
    filtered_df = observation_with_vdl_df[(observation_with_vdl_df['date_obs'] >= start_date) & (observation_with_vdl_df['date_obs'] <= end_date)]

    # Si le zoom et la position actuels sont disponibles, les utiliser, sinon définir des valeurs par défaut
    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8  # Valeur par défaut du zoom
        current_center = {"lat": filtered_df['localisation_lat'].mean() + 0.5, "lon": filtered_df['localisation_long'].mean()}


    # Afficher la carte
    fig_map = px.scatter_mapbox(filtered_df, lat='localisation_lat', lon='localisation_long',
                                color=selected_column,
                                hover_name='date_obs', hover_data=['localisation_lat', 'localisation_long'],
                                mapbox_style="open-street-map",
                                color_discrete_map=map_color_palettes[selected_column]
                                )

    fig_map.update_layout(mapbox_zoom=current_zoom,
                          mapbox_center=current_center,
                          margin=dict(l=10, r=10, t=0, b=0),
                          )

    # Initialize variables
    nb_species_clicked = None
    vdl_clicked = None
    observation_id_clicked = 503 # Default observation ID, to be improved

    # Initalise the filtered dataframe (unfiltered by default), and sum over all data
    filtered_nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df.groupby('species_id').agg({
        'nb_lichen': 'sum',
        'nb_lichen_N': 'sum',
        'nb_lichen_S': 'sum',
        'nb_lichen_O': 'sum',
        'nb_lichen_E': 'sum',
        'name': 'first'
    }).reset_index().rename(columns={'name': 'unique_name'}).sort_values(by='nb_lichen', ascending=True)

    # If a point on the map is clicked, identify the observation ID, number of species and VDL
    if clickData is not None:
        lat_clicked = clickData['points'][0]['lat']
        lon_clicked = clickData['points'][0]['lon']

        observation_clicked = filtered_df[(filtered_df['localisation_lat'] == lat_clicked) & (filtered_df['localisation_long'] == lon_clicked)]
        if not observation_clicked.empty:
            observation_clicked = observation_clicked.iloc[0]  # Take the first element matching the latitude and longitude
            observation_id_clicked = observation_clicked['id']
            nb_species_clicked = observation_clicked['nb_species']
            vdl_clicked = observation_clicked['VDL']

            filtered_nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df[nb_lichen_per_lichen_id_df['observation_id'] == observation_id_clicked]


    deg_artif = calc_deg_artif(observation_id_clicked)
    pollution_acide = calc_pollution_acide(observation_id_clicked)
    pollution_azote = calc_pollution_azote(observation_id_clicked)

    gauge_chart1 = create_gauge_chart(deg_artif)
    gauge_chart2 = create_gauge_chart(pollution_acide)
    gauge_chart3 = create_gauge_chart(pollution_azote)

    hist1_nb_species = create_hist1_nb_species(filtered_df, nb_species_clicked)
    hist2_vdl = create_hist2_vdl(filtered_df, vdl_clicked)
    hist3 = create_hist3(filtered_nb_lichen_per_lichen_id_df)

    return fig_map, gauge_chart1, gauge_chart2, gauge_chart3, hist1_nb_species, hist2_vdl, hist3

## Histogram 4
# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist4', component_property='figure'),
    Input(component_id='species-dropdown', component_property='value')
)
def update_hist4(user_selection_species_id):
    return create_hist4(nb_lichen_per_species_df, user_selection_species_id)

# Create options for the user species dropdown
user_species_options = [
    {"label": row["name"], "value": row["species_id"]}
    for _, row in nb_lichen_per_species_df.sort_values(by="name").iterrows()
]
initial_user_selection_species_id = user_species_options[0]['value'] # Default to the first species ID
hist4 = update_hist4(initial_user_selection_species_id)


# Layout for the "Sites" tab
sites_layout = [
    # Divider for the date picker
    html.Div(
        [
            dcc.DatePickerRange(
                id="date-picker-range",
                min_date_allowed=observation_with_vdl_df["date_obs"].min(),
                max_date_allowed=datetime.now().date(),
                start_date=observation_with_vdl_df["date_obs"].min(),
                end_date=datetime.now().date(),
                initial_visible_month=datetime.now().date(),
                display_format="DD/MM/YYYY",
                clearable=False,
                updatemode="bothdates",  # Only update callback when both dates are selected
                first_day_of_week=2,  # Monday
            ),
        ]
    ),
    # Divider for the 2 columns
    html.Div(
        style={"display": "flex", "gap": "10px"},
        children=[
            # Divider for the first column with map and gauge
            html.Div(
                style={
                    "flex": "6",
                    "padding": "5px",
                    # "border": "1px solid black",
                },
                children=[
                    # Divider for the map
                    html.Div(
                        style={
                            "display": "flex",
                            "align-items": "center",
                            "gap": "10px",
                        },
                        children=[
                            html.H3(
                                "Carte des observations",
                                className="graph-title",
                            ),
                            dcc.Dropdown(
                                id="column-dropdown",
                                options=[
                                    {"label": col, "value": col} for col in map_columns
                                ],
                                value="nb_species_cat",  # Default value
                                style={"width": "50%"},
                                clearable=False,
                            ),
                        ],
                    ),
                    dcc.Graph(
                        id="species-map",
                        style={
                            "width": "100%",
                            "display": "inline-block",
                            "margin": "5px auto",
                        },
                    ),
                    # Divider for the gauge charts, with 3 columns each
                    html.Div(
                        style={
                            "display": "flex",
                            "gap": "10px"
                        },
                        children=[
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    html.H3(
                                        "Degré d'artificialisation",
                                        className="graph-title",
                                        style={"textAlign": "center"}
                                    ),
                                    dcc.Graph(
                                        id="gauge-chart1",
                                        style={"height": "100px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    html.H3(
                                        "Pollution acide",
                                        className="graph-title",
                                        style={"textAlign": "center"}
                                    ),
                                    dcc.Graph(
                                        id="gauge-chart2",
                                        style={"height": "100px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    html.H3(
                                        "Pollution azote",
                                        className="graph-title",
                                        style={"textAlign": "center"},
                                    ),
                                    dcc.Graph(
                                        id="gauge-chart3",
                                        style={"height": "100px"}
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Divider for the second column with histograms
            html.Div(
                style={
                    "flex": "5",
                    "padding": "5px",
                    # "border": "1px solid black",
                },
                children=[
                    # Divider for 2 columns for hist1 and hist2
                    html.Div(
                        style={"display": "flex", "gap": "10px"},
                        children=[
                            # Divider for hist1
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    # Divider for title and tooltip
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "align-items": "center",
                                        },
                                        children=[
                                            html.H3(
                                                "Distribution du nombre d'espèces",
                                                className="graph-title",
                                            ),
                                            dmc.Tooltip(
                                                label="Distribution du nombre d'espèces par site. Si vous cliquez sur un site sur la carte, son nombre d'espèce sera affiché en trait pointillé rouge.",
                                                position="top",
                                                withArrow=True,
                                                children=DashIconify(
                                                    icon="material-symbols:info-outline",
                                                    className="info-icon",
                                                ),
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="species-hist1",
                                        style={"height": "300px"},
                                    ),
                                ],
                            ),
                            # Divider for hist2
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    # Divider for title and tooltip
                                    html.Div(
                                        style={
                                            "display": "flex",
                                            "align-items": "center",
                                        },
                                        children=[
                                            html.H3(
                                                "Distribution de VDL",
                                                className="graph-title",
                                            ),
                                            dmc.Tooltip(
                                                label="Distribution des valeurs de Diversité Lichénique (VDL) sur l'ensemble des sites. Si vous cliquez sur un site sur la carte, sa VDL sera affichée en trait pointillé rouge.",
                                                position="top",
                                                withArrow=True,
                                                children=DashIconify(
                                                    icon="material-symbols:info-outline",
                                                    className="info-icon",
                                                ),
                                            ),
                                        ],
                                    ),
                                    dcc.Graph(
                                        id="vdl-hist2",
                                        style={"height": "300px"},
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        [
                            html.Div(
                                style={"display": "flex", "align-items": "center"},
                                children=[
                                    html.H3(
                                        "Espèces observées sur le site sélectionné",
                                        className="graph-title",
                                    ),
                                    dmc.Tooltip(
                                        label="Distribution des espèces observées sur le site sélectionné",
                                        position="top",
                                        withArrow=True,
                                        children=DashIconify(
                                            icon="material-symbols:info-outline",
                                            className="info-icon",
                                        ),
                                    ),
                                ],
                            ),
                            dcc.Graph(
                                id="hist3",
                                style={"height": "300px"},
                            ),
                        ]
                    ),
                ],
            ),
        ],
    ),
]

# Layout for the "Espèces" tab
species_layout = dmc.Grid(
    [
        dmc.GridCol(
            [
                html.Div(
                    [
                        html.H3(
                            "Espèces les plus observées par les observateurs Lichens GO",
                            className="graph-title",
                        ),
                        dmc.Tooltip(
                            label="Distribution des espèces observées, sur l'ensemble des sites",
                            position="top",
                            withArrow=True,
                            children=DashIconify(
                                icon="material-symbols:info-outline",
                                className="info-icon",
                            ),
                        ),
                    ],
                    style={
                        "display": "flex",
                        "align-items": "center",
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
)

# Define the main layout with tabs
app.layout = dmc.MantineProvider(
    [
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.TabsTab("Sites", value="1"),
                        dmc.TabsTab("Espèces", value="2"),
                    ]
                ),
                dmc.TabsPanel(sites_layout, value="1"),
                dmc.TabsPanel(species_layout, value="2"),
            ],
            value="1",  # Default to the first tab
        )
    ]
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
