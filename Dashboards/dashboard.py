import plotly.express as px
import dash_mantine_components as dmc
import pandas as pd

from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime

from Dashboards.my_data.datasets import get_useful_data
from Dashboards.my_data.computed_datasets import merge_tables, vdl_value, count_lichen, count_lichen_per_species, count_species_per_observation, count_lichen_per_lichen_id, df_frequency
from Dashboards.charts import create_map, create_hist1_nb_species, create_hist2_vdl, create_hist3, create_hist4, create_gauge_chart, create_kpi
from Dashboards.constants import MAP_SETTINGS, BASE_COLOR_PALETTE, BODY_FONT_FAMILY

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
lichen_df, lichen_species_df, observation_df, table_df, tree_df, ecology_df = get_useful_data()


# For tab on observations
merged_table_df = merge_tables(table_df, lichen_df, lichen_species_df, observation_df)
merged_table_with_nb_lichen_df = count_lichen(merged_table_df)

observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
observation_with_vdl_df = vdl_value(observation_with_species_count_df, merged_table_with_nb_lichen_df)

# For tab on species
nb_lichen_per_species_df = count_lichen_per_species(lichen_df, lichen_species_df)

# Dataset for the gauge charts (to be improved)
grouped_df = df_frequency(lichen_df, lichen_species_df, observation_df, table_df, ecology_df)

# Calcul du degrés d'artificialisation
def calc_deg_artif(observation_id: int):
    global_freq = grouped_df[grouped_df['observation_id']== observation_id]['freq'].sum()
    base_freq = grouped_df[(grouped_df['observation_id'] == observation_id) & (grouped_df['poleotolerance'] == 'resistant')]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)

# Calcul de la pollution acidé
def calc_pollution_acide(observation_id: int):
    global_freq = grouped_df[grouped_df['observation_id']== observation_id]['freq'].sum()
    acid_freq = grouped_df[(grouped_df['observation_id'] == observation_id) & (grouped_df['ph'] == 'acidophilous')]['freq'].sum()

    return round((acid_freq / global_freq) * 100, 2)

# Calcul de la pollution azoté
def calc_pollution_azote(observation_id: int):
    global_freq = grouped_df[grouped_df['observation_id']== observation_id]['freq'].sum()
    azote_freq = grouped_df[(grouped_df['observation_id'] == observation_id) & (grouped_df['eutrophication'] == 'eutrophic')]['freq'].sum()

    return round((azote_freq / global_freq) * 100, 2)


# Callback pour mettre à jour la carte et l'histogramme en fonction des dates sélectionnées
@callback(
    Output('species-map', 'figure'),
    Output('gauge-chart1', 'figure'),
    Output('gauge-chart2', 'figure'),
    Output('gauge-chart3', 'figure'),
    Output('species-hist1', 'figure'),
    Output('vdl-hist2', 'figure'),
    Output('hist3','figure'),

    Input('date-picker-range', 'value'),
    Input('map-column-select', 'value'),
    Input('species-map', 'clickData'),

    State('species-map', 'relayoutData')  # État actuel du zoom et de la position de la carte

)
def update_dashboard1(date_range, selected_map_column, clickData, relayoutData):
    # Avoid updating when one of the date is None (not selected)
    if None in date_range:
        raise PreventUpdate

    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    # Filter the data based on the selected date range
    filtered_observation_with_vdl_df = observation_with_vdl_df[(observation_with_vdl_df['date_obs'] >= start_date) & (observation_with_vdl_df['date_obs'] <= end_date)]
    filtered_table_with_nb_lichen_df = merged_table_with_nb_lichen_df[(merged_table_with_nb_lichen_df['date_obs'] >= start_date) & (merged_table_with_nb_lichen_df['date_obs'] <= end_date)]

    # Count lichen per lichen_id on filtered table
    filtered_nb_lichen_per_lichen_id_df = count_lichen_per_lichen_id(filtered_table_with_nb_lichen_df, lichen_df, lichen_species_df)

    # Si le zoom et la position actuels sont disponibles, les utiliser, sinon définir des valeurs par défaut
    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8  # Valeur par défaut du zoom
        current_center = {"lat": filtered_observation_with_vdl_df['localisation_lat'].mean() + 0.5, "lon": filtered_observation_with_vdl_df['localisation_long'].mean()}

    # Afficher la carte
    fig_map = create_map(filtered_observation_with_vdl_df, selected_map_column, current_zoom, current_center)

    # Initialize variables
    nb_species_clicked = None
    vdl_clicked = None
    observation_id_clicked = 503 # Default observation ID, to be improved

    # If a point on the map is clicked, identify the observation ID, number of species and VDL
    if clickData is not None:
        lat_clicked = clickData['points'][0]['lat']
        lon_clicked = clickData['points'][0]['lon']

        observation_clicked = filtered_observation_with_vdl_df[(filtered_observation_with_vdl_df['localisation_lat'] == lat_clicked) & (filtered_observation_with_vdl_df['localisation_long'] == lon_clicked)]
        if not observation_clicked.empty:
            observation_clicked = observation_clicked.iloc[0]  # Take the first element matching the latitude and longitude
            observation_id_clicked = observation_clicked['observation_id']
            nb_species_clicked = observation_clicked['nb_species']
            vdl_clicked = observation_clicked['VDL']

            filtered_nb_lichen_per_lichen_id_df =  filtered_nb_lichen_per_lichen_id_df[filtered_nb_lichen_per_lichen_id_df['observation_id'] == observation_id_clicked]

    else:
        # If no observation is clicked, show all observations data
        filtered_nb_lichen_per_lichen_id_df = filtered_nb_lichen_per_lichen_id_df.groupby('species_id').agg({
            'nb_lichen': 'sum',
            'nb_lichen_N': 'sum',
            'nb_lichen_S': 'sum',
            'nb_lichen_O': 'sum',
            'nb_lichen_E': 'sum',
            'name': 'first'
        }).reset_index().rename(columns={'name': 'unique_name'}).sort_values(by='nb_lichen', ascending=True)

    deg_artif = calc_deg_artif(observation_id_clicked)
    pollution_acide = calc_pollution_acide(observation_id_clicked)
    pollution_azote = calc_pollution_azote(observation_id_clicked)

    gauge_chart1 = create_kpi(deg_artif)
    gauge_chart2 = create_gauge_chart(pollution_acide)
    gauge_chart3 = create_gauge_chart(pollution_azote)

    hist1_nb_species = create_hist1_nb_species(filtered_observation_with_vdl_df, nb_species_clicked)
    hist2_vdl = create_hist2_vdl(filtered_observation_with_vdl_df, vdl_clicked)
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


## Initialize all the graphs (not really necessary, but improves loading time)

date_range = [observation_with_vdl_df["date_obs"].min(), datetime.now().date()]
selected_map_column = list(MAP_SETTINGS.keys())[0]
clickData = None
relayoutData = None
fig_map, gauge_chart1, gauge_chart2, gauge_chart3, hist1_nb_species, hist2_vdl, hist3 = update_dashboard1(date_range, selected_map_column, clickData, relayoutData)

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
        style={"padding": "10px"},
        children=[
            # Widget for the date filter
            dmc.DatePicker(
                id="date-picker-range",
                minDate=observation_with_vdl_df["date_obs"].min(),
                maxDate=datetime.now().date(),
                type="range",
                value=[
                    observation_with_vdl_df["date_obs"].min(),
                    datetime.now().date(),
                ],
                valueFormat="DD/MM/YYYY",
                w=200,  # width
            ),
        ],
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
                            dmc.Title(
                                "Carte des observations",
                                order=4,
                                className="graph-title",
                            ),
                            # Selector for the map column
                            dmc.SegmentedControl(
                                id="map-column-select",
                                value=list(MAP_SETTINGS.keys())[0],
                                data=[
                                    {"label": MAP_SETTINGS[col]["title"], "value": col}
                                    for col in MAP_SETTINGS
                                ],
                                transitionDuration=500,
                            ),
                        ],
                    ),
                    html.Div(
                        style={"padding": "5px"},
                        children=[
                            dmc.Card(
                                children=[
                                    dcc.Graph(
                                        id="species-map",
                                        figure=fig_map,
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                                withBorder=True,
                                shadow="sm",
                                style={"padding": "0"},
                            ),
                        ],
                    ),
                    # Divider for the gauge charts, with 3 columns each
                    html.Div(
                        style={"display": "flex", "gap": "10px", "padding": "5px"},
                        children=[
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            dmc.Title(
                                                "Degré d'artificialisation",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart1",
                                                figure=gauge_chart1,
                                                style={"height": "70px"},
                                                config={
                                                    "displayModeBar": False,
                                                },
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="sm",
                                        style={"padding-top": "5px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            dmc.Title(
                                                "Pollution acide",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart2",
                                                figure=gauge_chart2,
                                                style={"height": "100px"},
                                                config={
                                                    "displayModeBar": False,
                                                },
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="sm",
                                        style={"padding-top": "5px"},
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            dmc.Title(
                                                "Pollution azote",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart3",
                                                figure=gauge_chart3,
                                                style={"height": "100px"},
                                                config={
                                                    "displayModeBar": False,
                                                },
                                            ),
                                        ],
                                        withBorder=True,
                                        shadow="sm",
                                        style={"padding-top": "5px"},
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
                                            dmc.Title(
                                                "Distribution du nombre d'espèces",
                                                order=4,
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
                                        figure=hist1_nb_species,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
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
                                            dmc.Title(
                                                "Distribution de VDL",
                                                order=4,
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
                                        figure=hist2_vdl,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
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
                                    dmc.Title(
                                        "Espèces observées sur le site sélectionné",
                                        order=4,
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
                                figure=hist3,
                                style={"height": "300px"},
                                config={
                                    "displaylogo": False,  # Remove plotly logo
                                },
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
                        dmc.Title(
                            "Espèces les plus observées",
                            order=4,
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
                dcc.Graph(
                    id="hist4",
                    figure=hist4,
                    config={
                        "displaylogo": False,  # Remove plotly logo
                    },
                ),
            ],
            span=8,
        )
    ]
)


# Toggle to switch between light and dark theme
theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon="radix-icons:sun", width=25), darkHidden=True),
        dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
    ],
    variant="transparent",
    id="color-scheme-toggle",
    size="lg",
    ms="auto",
)


# Callback to switch between light and dark theme
@callback(
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-toggle", "n_clicks"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def switch_theme(_, theme):
    return "dark" if (theme == "light" or theme is None) else "light"


# Theme for the app
dmc_theme = {
    "colors": {
            "myBlue": BASE_COLOR_PALETTE[::-1], # Reverse the color palette
        },
    "primaryColor": "myBlue",
    "fontFamily": BODY_FONT_FAMILY,
    "defaultRadius": "md", # Default radius for cards
}


# Define the main layout with tabs
app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=dmc_theme,
    children=[
        dmc.Tabs(
            [
                dmc.TabsList(
                    [
                        dmc.TabsTab("Sites", value="1"),
                        dmc.TabsTab("Espèces", value="2"),
                        theme_toggle,
                    ],
                ),
                dmc.TabsPanel(sites_layout, value="1"),
                dmc.TabsPanel(species_layout, value="2"),
            ],
            value="1",  # Default to the first tab
        ),
    ],
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
