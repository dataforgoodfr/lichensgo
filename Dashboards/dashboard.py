import pandas as pd
import os
import dash_mantine_components as dmc

from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime

from Dashboards.my_data.datasets import get_useful_data
from Dashboards.my_data.computed_datasets import merge_tables, vdl_value, count_lichen, count_lichen_per_species, count_species_per_observation, count_lichen_per_lichen_id, group_table_by_observation_and_species, group_table_by_observation_and_thallus, calc_deg_artif, calc_pollution_acide, calc_pollution_azote
from Dashboards.charts import blank_figure, create_map, create_hist1_nb_species, create_hist2_vdl, create_hist3, create_pie_thallus, create_hist4, create_gauge_chart
from Dashboards.constants import MAP_SETTINGS, BASE_COLOR_PALETTE, BODY_FONT_FAMILY, POSITIVE_GAUGE_COLOR_PALETTE, NEGATIVE_GAUGE_COLOR_PALETTE

_dash_renderer._set_react_version("18.2.0")


# Get the datasets
print("Fetching data...")
lichen_df, merged_lichen_species_df, observation_df, table_df, tree_df = get_useful_data()


# For tab on observations
table_with_nb_lichen_df = count_lichen(table_df)
merged_table_with_nb_lichen_df = merge_tables(table_with_nb_lichen_df, lichen_df, observation_df)
grouped_table_by_observation_and_species_df = group_table_by_observation_and_species(merged_table_with_nb_lichen_df, merged_lichen_species_df) # data for the gauge charts
grouped_table_by_observation_and_thallus_df = group_table_by_observation_and_thallus(merged_table_with_nb_lichen_df, merged_lichen_species_df) # data for pie chart

observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
observation_with_vdl_df = vdl_value(observation_with_species_count_df, merged_table_with_nb_lichen_df)

# For tab on species
nb_lichen_per_species_df = count_lichen_per_species(lichen_df, merged_lichen_species_df)

# For the lichen images
current_dir = os.path.dirname(__file__)
lichen_img_dir = os.path.join('assets', 'img')

# Initialize a blank figure to show during loading
blank_fig = blank_figure()

# Initialize the selections
date_range = [observation_with_vdl_df["date_obs"].min(), datetime.now().date()]
map_column_selected = list(MAP_SETTINGS.keys())[0]


# Callback to update the dashboard on the observation
@callback(
    Output('species-map', 'figure'),
    Output('gauge-chart1-artif', 'figure'),
    Output('gauge-chart2-acide', 'figure'),
    Output('gauge-chart3-azote', 'figure'),
    Output('hist1-nb_species', 'figure'),
    Output('hist2-vdl', 'figure'),
    Output('hist3-species','figure'),
    Output('pie-thallus', 'figure'),

    Input('date-picker-range', 'value'),
    Input('map-column-select', 'value'),
    Input('species-map', 'clickData'),

    State('species-map', 'relayoutData')  # État actuel du zoom et de la position de la carte

)
def update_dashboard1(date_range, map_column_selected, clickData, relayoutData):
    # Avoid updating when one of the date is None (not selected)
    if None in date_range:
        raise PreventUpdate

    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    # Filter the data based on the selected date range
    filtered_observation_with_vdl_df = observation_with_vdl_df[(observation_with_vdl_df['date_obs'] >= start_date) & (observation_with_vdl_df['date_obs'] <= end_date)]
    filtered_table_with_nb_lichen_df = merged_table_with_nb_lichen_df[(merged_table_with_nb_lichen_df['date_obs'] >= start_date) & (merged_table_with_nb_lichen_df['date_obs'] <= end_date)]


    # Count lichen per lichen_id on filtered table
    filtered_nb_lichen_per_lichen_id_df = count_lichen_per_lichen_id(filtered_table_with_nb_lichen_df, lichen_df, merged_lichen_species_df)

    # Si le zoom et la position actuels sont disponibles, les utiliser, sinon définir des valeurs par défaut
    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8  # Valeur par défaut du zoom
        current_center = {"lat": filtered_observation_with_vdl_df['localisation_lat'].mean() + 0.5, "lon": filtered_observation_with_vdl_df['localisation_long'].mean()}

    fig_map = create_map(filtered_observation_with_vdl_df, map_column_selected, current_zoom, current_center)

    # Initialize variables
    nb_species_clicked = None
    vdl_clicked = None

    gauge_chart1_artif = blank_fig
    gauge_chart2_acide = blank_fig
    gauge_chart3_azote = blank_fig
    hist3_species = blank_fig
    pie_thallus = blank_fig

    # If a point on the map is clicked, identify the observation ID, number of species, and VDL
    if clickData is not None:
        lat_clicked = clickData['points'][0]['lat']
        lon_clicked = clickData['points'][0]['lon']

        observation_clicked = filtered_observation_with_vdl_df[
            (filtered_observation_with_vdl_df['localisation_lat'] == lat_clicked) &
            (filtered_observation_with_vdl_df['localisation_long'] == lon_clicked)
        ]

        if not observation_clicked.empty:

            observation_clicked = observation_clicked.iloc[0]  # Take the first element matching the latitude and longitude
            observation_id_clicked = observation_clicked['observation_id']
            nb_species_clicked = observation_clicked['nb_species']
            vdl_clicked = observation_clicked['VDL']


            # Filter the data based on the clicked observation
            filtered_nb_lichen_per_lichen_id_df =  filtered_nb_lichen_per_lichen_id_df[filtered_nb_lichen_per_lichen_id_df['observation_id'] == observation_id_clicked]

            filtered_grouped_table_by_observation_and_species_df = grouped_table_by_observation_and_species_df[
                grouped_table_by_observation_and_species_df['observation_id'] == observation_id_clicked
            ]

            filtered_grouped_table_by_observation_and_thallus_df = grouped_table_by_observation_and_thallus_df[
                grouped_table_by_observation_and_thallus_df['observation_id'] == observation_id_clicked
            ]


            deg_artif = calc_deg_artif(filtered_grouped_table_by_observation_and_species_df)
            pollution_acide = calc_pollution_acide(filtered_grouped_table_by_observation_and_species_df)
            pollution_azote = calc_pollution_azote(filtered_grouped_table_by_observation_and_species_df)

            gauge_chart1_artif = create_gauge_chart(deg_artif, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)
            gauge_chart2_acide = create_gauge_chart(pollution_acide, intervals=[0, 25, 50, 75, 100], color_scale=POSITIVE_GAUGE_COLOR_PALETTE)
            gauge_chart3_azote = create_gauge_chart(pollution_azote, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)

            hist3_species = create_hist3(filtered_nb_lichen_per_lichen_id_df)

            pie_thallus = create_pie_thallus(filtered_grouped_table_by_observation_and_thallus_df)

    # Those figures are still needed even if no observation is clicked
    hist1_nb_species = create_hist1_nb_species(filtered_observation_with_vdl_df, nb_species_clicked)
    hist2_vdl = create_hist2_vdl(filtered_observation_with_vdl_df, vdl_clicked)

    return fig_map, gauge_chart1_artif, gauge_chart2_acide, gauge_chart3_azote, hist1_nb_species, hist2_vdl, hist3_species, pie_thallus

## Dashboard on species tab
# Define callback to update the bar chart based on selected species
@callback(
    Output(component_id='hist4-species', component_property='figure'),
    Output(component_id='lichen-image', component_property='src'),
    Input(component_id='species-dropdown', component_property='value')
)
def update_dashboard2(species_id_selected):

    hist4_species = create_hist4(nb_lichen_per_species_df, species_id_selected)

    filtered_nb_lichen_per_species_df = nb_lichen_per_species_df[nb_lichen_per_species_df['species_id'] == species_id_selected].iloc[0]
    species_name_selected = filtered_nb_lichen_per_species_df['name']

    lichen_img = merged_lichen_species_df[merged_lichen_species_df['species_id'] == species_id_selected]['picture'].iloc[0]
    lichen_img_path = os.path.join(lichen_img_dir, lichen_img)

    return hist4_species, lichen_img_path


# Create options for the user species dropdown, sorted by name
species_options = [
    {"label": row["name"], "value": row["species_id"]}
    for _, row in nb_lichen_per_species_df.sort_values(by="name").iterrows()
]
species_id_selected = species_options[0]['value'] # Default to the first species ID


# Layout for the sites (observations)
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
                                        figure=blank_fig,
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
                                                "% Espèces toxitolérantes",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart1-artif",
                                                figure=blank_fig,
                                                style={"height": "100px"},
                                                config={
                                                    "displayModeBar": False, # Remove plotly tool bar
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
                                                "% Espèces eutrophes",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart3-azote",
                                                figure=blank_fig,
                                                style={"height": "100px"},
                                                config={
                                                    "displayModeBar": False, # Remove plotly tool bar
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
                                                "% Espèces acidophiles",
                                                order=4,
                                                style={
                                                    "textAlign": "left",
                                                    "margin": "0px",
                                                    "padding": "0px",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="gauge-chart2-acide",
                                                figure=blank_fig,
                                                style={"height": "100px"},
                                                config={
                                                    "displayModeBar": False, # Remove plotly tool bar
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
                    dmc.Grid(
                        gutter="md",
                        align="stretch",
                        children=[
                            # Column for hist1
                            dmc.GridCol(
                                span=6,
                                children=[
                                    # Divider for title and tooltip
                                    html.Div(
                                        style={"display": "flex",
                                               "align-items": "center"},
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
                                        id="hist1-nb_species",
                                        figure=blank_fig,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                            ),
                            # Column for hist2
                            dmc.GridCol(
                                span=6,
                                children=[
                                    # Divider for title and tooltip
                                    html.Div(
                                        style={"display": "flex",
                                               "align-items": "center"},
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
                                        id="hist2-vdl",
                                        figure=blank_fig,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                            ),
                            # Column for hist3
                            dmc.GridCol(
                                span=8,
                                children=[
                                    # Divider for the title and tooltip
                                    html.Div(
                                        style={"display": "flex",
                                               "align-items": "center"},
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
                                        id="hist3-species",
                                        figure=blank_fig,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                            ),
                            # Column for pie chart
                            dmc.GridCol(
                                span=4,
                                children=[
                                    # Divider for the title and tooltip
                                    html.Div(
                                        style={"display": "flex",
                                               "align-items": "center"},
                                        children=[
                                            dmc.Title(
                                                "Pie chart",
                                                order=4,
                                                className="graph-title",
                                            ),
                                            dmc.Tooltip(
                                                label="",
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
                                        id="pie-thallus",
                                        figure=blank_fig,
                                        style={"height": "300px"},
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                            ),
                        ],
                    )
                ],
            ),
        ],
    ),
]

# Layout for the "Espèces" tab
species_layout = dmc.Grid(
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
                    options=species_options,
                    value=species_id_selected,
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
            id="hist4-species",
            figure=blank_fig,
            config={
                "displaylogo": False,  # Remove plotly logo
            },
        ),
        dmc.Image(
            id="lichen-image",
            radius="md",
            src=None,
            h=200,
            fallbackSrc="https://placehold.co/600x400?text=No%20image%20found",
        ),
    ],
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


# Initialize the Dash app
app = Dash(__name__,
           external_stylesheets=[
               dmc.styles.ALL,
               dmc.styles.DATES,
              "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap"
           ],
           title="Lichens GO"
    )


# Define the main layout with toggle and accordion
app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=dmc_theme,
    children=[
        theme_toggle,
        dmc.Accordion(
            disableChevronRotation=True,
            chevronPosition="left",
            variant="contained",
            multiple=True,
            children=[
                dmc.AccordionItem(
                            children=[
                                dmc.AccordionControl(
                                    dmc.Group(
                                        children=[
                                            DashIconify(
                                                icon="tabler:map-pin",
                                                height=25,
                                            ),
                                            dmc.Title("Sites", order=3)
                                        ],
                                        align="bottom",
                                    ),
                                ),
                                dmc.AccordionPanel(sites_layout)
                            ],
                    value="sites",
                ),
                dmc.AccordionItem(
                    children=[
                        dmc.AccordionControl(
                            dmc.Group(
                                children=[
                                    DashIconify(
                                        icon="ph:plant",
                                        height=25,
                                    ),
                                    dmc.Title("Espèces", order=3)
                                ],
                                align="bottom",
                            ),
                        ),
                        dmc.AccordionPanel(species_layout)
                    ],
                    value="species",
                ),
            ],
            value=["sites", "species"],  # open both toggles by default
        )
    ],
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
