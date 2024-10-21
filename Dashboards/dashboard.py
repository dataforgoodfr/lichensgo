import pandas as pd
import os
import dash_mantine_components as dmc

from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime

from Dashboards.my_data.datasets import get_useful_data
from Dashboards.my_data.computed_datasets import merge_tables, calc_degrees_pollution, calc_vdl, count_lichen, count_lichen_per_species, count_species_per_observation, count_lichen_per_lichen_id, group_lichen_by_observation_and_thallus
from Dashboards.charts import blank_figure, create_map, create_hist1_nb_species, create_hist2_vdl, create_hist3, create_pie_thallus, create_hist4, create_gauge_chart
from Dashboards.constants import MAP_SETTINGS, BASE_COLOR_PALETTE, BODY_FONT_FAMILY, POSITIVE_GAUGE_COLOR_PALETTE, NEGATIVE_GAUGE_COLOR_PALETTE

_dash_renderer._set_react_version("18.2.0")


# Get the datasets
print("Fetching data...")
lichen_df, merged_lichen_species_df, observation_df, table_df, tree_df = get_useful_data()


# For tab on observations
table_with_nb_lichen_df = count_lichen(table_df)
merged_table_with_nb_lichen_df = merge_tables(table_with_nb_lichen_df, lichen_df, observation_df)
grouped_lichen_by_observation_and_thallus_df = group_lichen_by_observation_and_thallus(merged_table_with_nb_lichen_df, merged_lichen_species_df) # data for pie chart

nb_lichen_per_lichen_id_df = count_lichen_per_lichen_id(
        table_with_nb_lichen_df, lichen_df, merged_lichen_species_df
    )

observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
observation_with_deg_pollution_df = calc_degrees_pollution(merged_table_with_nb_lichen_df, lichen_df, merged_lichen_species_df)
observation_with_vdl_df = calc_vdl(merged_table_with_nb_lichen_df)

merged_observation_df = observation_with_species_count_df.merge(observation_with_deg_pollution_df, on='observation_id')
merged_observation_df = merged_observation_df.merge(observation_with_vdl_df, on='observation_id')

# For tab on species
nb_lichen_per_species_df = count_lichen_per_species(lichen_df, merged_lichen_species_df)
observation_with_selected_species_col_df = observation_df.copy()

# For the lichen images
current_dir = os.path.dirname(__file__)
lichen_img_dir = os.path.join('assets', 'img')

# Initialize a blank figure to show during loading
blank_fig = blank_figure()

# Initialize the selections
date_range = [merged_observation_df["date_obs"].min(), datetime.now().date()]
map_column_selected = list(MAP_SETTINGS.keys())[0]


# First callback to update the dashboard based on date and map selection
@callback(
    Output('map-nb_species-vdl', 'figure'),
    Output('hist1-nb_species', 'figure'),
    Output('hist2-vdl', 'figure'),
    Input('date-picker-range', 'value'),
    Input('map-column-select', 'value'),
    State('map-nb_species-vdl', 'relayoutData')
)
def update_dashboard_map(date_range, map_column_selected, relayoutData):
    if None in date_range:
        raise PreventUpdate

    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    filtered_observation_df = merged_observation_df[(merged_observation_df['date_obs'] >= start_date) & (merged_observation_df['date_obs'] <= end_date)]

    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8
        current_center = {"lat": filtered_observation_df['localisation_lat'].mean() + 0.5, "lon": filtered_observation_df['localisation_long'].mean()}

    fig_map = create_map(filtered_observation_df, map_column_selected, current_zoom, current_center)

    hist1_nb_species = create_hist1_nb_species(filtered_observation_df, None)
    hist2_vdl = create_hist2_vdl(filtered_observation_df, None)

    return fig_map, hist1_nb_species, hist2_vdl

# Second callback to update the dashboard based on observation click
@callback(
    Output('gauge-chart1-artif', 'figure'),
    Output('gauge-chart2-acide', 'figure'),
    Output('gauge-chart3-azote', 'figure'),
    Output('hist3-species', 'figure'),
    Output('pie-thallus', 'figure'),
    Output('hist1-nb_species', 'figure', allow_duplicate=True),
    Output('hist2-vdl', 'figure', allow_duplicate=True),
    Input('map-nb_species-vdl', 'clickData'),
    Input('date-picker-range', 'value'),
    prevent_initial_call=True
)
def update_dashboard_observation(clickData, date_range):
    if None in date_range or clickData is None:
        raise PreventUpdate

    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    filtered_observation_df = merged_observation_df[
        (merged_observation_df['date_obs'] >= start_date) &
        (merged_observation_df['date_obs'] <= end_date)
    ]

    lat_clicked = clickData['points'][0]['lat']
    lon_clicked = clickData['points'][0]['lon']

    observation_clicked = filtered_observation_df[
        (filtered_observation_df['localisation_lat'] == lat_clicked) &
        (filtered_observation_df['localisation_long'] == lon_clicked)
    ]

    if observation_clicked.empty:
        return (
            blank_fig, blank_fig, blank_fig, blank_fig, blank_fig,
            create_hist1_nb_species(filtered_observation_df, None),
            create_hist2_vdl(filtered_observation_df, None)
        )

    observation_clicked = observation_clicked.iloc[0]
    observation_id_clicked = observation_clicked['observation_id']
    nb_species_clicked = observation_clicked['nb_species']
    vdl_clicked = observation_clicked['VDL']
    deg_artif_clicked = observation_clicked['deg_artif']
    deg_pollution_acid_clicked = observation_clicked['deg_pollution_acid']
    deg_pollution_azote_clicked = observation_clicked['deg_pollution_azote']

    filtered_nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df[
        nb_lichen_per_lichen_id_df['observation_id'] == observation_id_clicked
    ]

    filtered_grouped_lichen_by_observation_and_thallus_df = grouped_lichen_by_observation_and_thallus_df[
        grouped_lichen_by_observation_and_thallus_df['observation_id'] == observation_id_clicked
    ]

    gauge_chart1_artif = create_gauge_chart(deg_artif_clicked, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)
    gauge_chart2_acide = create_gauge_chart(deg_pollution_acid_clicked, intervals=[0, 25, 50, 75, 100], color_scale=POSITIVE_GAUGE_COLOR_PALETTE)
    gauge_chart3_azote = create_gauge_chart(deg_pollution_azote_clicked, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)

    hist1_nb_species = create_hist1_nb_species(filtered_observation_df, nb_species_clicked)
    hist2_vdl = create_hist2_vdl(filtered_observation_df, vdl_clicked)

    hist3_species = create_hist3(filtered_nb_lichen_per_lichen_id_df)
    pie_thallus = create_pie_thallus(filtered_grouped_lichen_by_observation_and_thallus_df)

    return gauge_chart1_artif, gauge_chart2_acide, gauge_chart3_azote, hist3_species, pie_thallus, hist1_nb_species, hist2_vdl

## Dashboard on species tab
# Define callback to update the bar chart based on selected species
@callback(
    Output(component_id='map-species_present', component_property='figure'),
    Output(component_id='hist4-species', component_property='figure'),
    Output(component_id='lichen-image', component_property='src'),
    Input(component_id='species-dropdown', component_property='value'),
    State('map-species_present', 'relayoutData')
)
def update_dashboard2(species_id_selected, relayoutData):

    hist4_species = create_hist4(nb_lichen_per_species_df, species_id_selected)

    # Create a column indicating for each observation if the selected species is present or not
    observation_with_selected_species_col_df['selected_species_present'] = observation_df['observation_id'].isin(
        lichen_df.loc[lichen_df['species_id'] == species_id_selected, 'observation_id']
    )


    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8
        current_center = {"lat": observation_with_selected_species_col_df['localisation_lat'].mean() + 0.5, "lon": observation_with_selected_species_col_df['localisation_long'].mean()}


    fig_map = create_map(observation_with_selected_species_col_df, 'selected_species_present', current_zoom, current_center)

    lichen_img = merged_lichen_species_df[merged_lichen_species_df['species_id'] == species_id_selected]['picture'].iloc[0]
    lichen_img_path = os.path.join(lichen_img_dir, lichen_img)

    return fig_map, hist4_species, lichen_img_path


def title_and_tooltip(title, tooltip_text):
    return html.Div(
        style={"display": "flex", "align-items": "center"},
        children=[
            dmc.Title(title, order=4, className="graph-title"),
            dmc.Tooltip(
                label=tooltip_text,
                position="top",
                withArrow=True,
                children=DashIconify(
                    icon="material-symbols:info-outline",
                    className="info-icon",
                ),
            ),
        ],
    )


# Create options for the user species dropdown, sorted by name
species_options = [
    {"label": row["name"], "value": row["species_id"]}
    for _, row in nb_lichen_per_species_df.sort_values(by="name").iterrows()
]
species_id_selected = species_options[0]['value'] # Default to the first species ID


# Layout for the sites (observations)
sites_layout = [
    # Divider for the 2 columns
    html.Div(
        style={"display": "flex", "gap": "10px"},
        children=[
            # Divider for the first column with map and gauge
            html.Div(
                style={"flex": "5"},
                children=[
                    # Divider for the map title and selector
                    html.Div(
                        style={"display": "flex", "align-items": "center", "gap": "10px",},
                        children=[
                            dmc.Title(
                                "Carte des observations",
                                order=4,
                                className="graph-title",
                                style={"padding": "0px"},
                            ),
                            # Selector for the map column
                            dmc.SegmentedControl(
                                id="map-column-select",
                                value=list(MAP_SETTINGS.keys())[0],
                                data=[
                                    {"label": MAP_SETTINGS[col]["title"], "value": col}
                                    for col in ["nb_species_cat", "VDL_cat"]
                                ],
                                transitionDuration=500,
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            dmc.Card(
                                children=[
                                    dcc.Graph(
                                        id="map-nb_species-vdl",
                                        figure=blank_fig,
                                        config={
                                            "displaylogo": False,  # Remove plotly logo
                                        },
                                    ),
                                ],
                                withBorder=True,
                                shadow="sm",
                                style={"padding": "0"}, # Remove padding between the card and the map
                            ),
                        ],
                    ),
                    # Divider for the gauge charts, with 3 columns each
                    html.Div(
                        style={"display": "flex", "gap": "10px", "padding-top": "10px"},
                        children=[
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            title_and_tooltip(
                                                title="% Espèces toxitolérantes",
                                                tooltip_text="Pourcentage d'espèces toxitolérantes sur le site sélectionné",
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
                                        style={"padding-top":"5px", "padding-left":"5px", "padding-right":"5px"}, # Reduce padding between the card and the gauge
                                    ),
                                ],
                            ),
                                                        html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            title_and_tooltip(
                                                title="% Espèces eutophes",
                                                tooltip_text="Pourcentage d'espèces eutrophes sur le site sélectionné"
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
                                         style={"padding-top":"5px", "padding-left":"5px", "padding-right":"5px"}, # Reduce padding between the card and the gauge
                                    ),
                                ],
                            ),
                            html.Div(
                                style={"flex": "1"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            title_and_tooltip(
                                                title="% Espèces acidophiles",
                                                tooltip_text="Pourcentage d'espèces acidophiles sur le site sélectionné"
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
                                         style={"padding-top":"5px", "padding-left":"5px", "padding-right":"5px"}, # Reduce padding between the card and the gauge
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Divider for the second column with histograms
            html.Div(
                style={"flex": "5",
                    "padding": "5px",
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
                                    title_and_tooltip(
                                        title="Distribution du nombre d'espèces",
                                        tooltip_text="Distribution du nombre d'espèces par site. Si vous cliquez sur un site sur la carte, son nombre d'espèce sera affiché en trait pointillé rouge."
                                    ),
                                    dmc.Card(
                                        dcc.Graph(
                                            id="hist1-nb_species",
                                            figure=blank_fig,
                                            style={"height": "300px"},
                                            config={
                                                "displaylogo": False,  # Remove plotly logo
                                            },
                                        ),
                                        withBorder=True,
                                        shadow="sm",
                                    )
                                ],
                            ),
                            # Column for hist2
                            dmc.GridCol(
                                span=6,
                                children=[
                                    title_and_tooltip(
                                        title="Distribution de VDL",
                                        tooltip_text="Distribution des valeurs de Diversité Lichénique (VDL) sur l'ensemble des sites. Si vous cliquez sur un site sur la carte, sa VDL sera affichée en trait pointillé rouge."
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
                                    dmc.Card(
                                        children=[
                                            title_and_tooltip(
                                                title="Espèces observées sur le site sélectionné",
                                                tooltip_text="Distribution des espèces observées sur le site sélectionné"
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
                                        withBorder=True,
                                        shadow="sm",
                                    ),
                                ],
                            ),
                            # Column for pie chart
                            dmc.GridCol(
                                span=4,
                                children=[
                                    title_and_tooltip(
                                        title="Morphologie du site sélectionné",
                                        tooltip_text="Distribution des thalles sur le site sélectionné"
                                    ),
                                    dcc.Graph(
                                        id="pie-thallus",
                                        figure=blank_fig,
                                        style={"height": "250px"},
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
        html.Div(
        children=[
            dmc.Card(
                children=[
                    dcc.Graph(
                        id="map-species_present",
                        figure=blank_fig,
                        config={
                            "displaylogo": False,  # Remove plotly logo
                        },
                    ),
                ],
                withBorder=True,
                shadow="sm",
                style={"padding": "0"}, # Remove padding between the card and the map
            ),
        ],
    ),
                title_and_tooltip(
            title="Espèces les plus observées",
            tooltip_text="Distribution des espèces observées sur l'ensemble des sites"
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


sidebar = dmc.Box(
    children=[
        theme_toggle,
        dmc.DatePicker(
            id="date-picker-range",
            label="Sélectionner une plage de dates",
            minDate=merged_observation_df["date_obs"].min(),
            maxDate=datetime.now().date(),
            type="range",
            value=[
                merged_observation_df["date_obs"].min(),
                datetime.now().date(),
            ],
            valueFormat="DD/MM/YYYY",
            w=110,  # width
        ),
    ],
    style={"width": "120px", "padding": "10px"},
)

dashboards_layout = dmc.Box(
    children=[
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
                                        height=20,
                                        color=BASE_COLOR_PALETTE[0]
                                    ),
                                    dmc.Title("Sites", order=3),
                                    dmc.Tooltip(
                                        label="Cliquez sur un site pour découvrir ce que les lichens peuvent nous apprendre",
                                        position="right",
                                        withArrow=True,
                                        children=DashIconify(
                                            icon="material-symbols:info-outline",
                                            className="info-icon",
                                        )
                                    ),
                                ],
                                align="center",
                            ),
                            ),
                            dmc.AccordionPanel(sites_layout),
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
                                        color=BASE_COLOR_PALETTE[0]
                                    ),
                                    dmc.Title(
                                        "Espèces", order=3)
                                ],
                                align="bottom",
                            ),
                        ),
                        dmc.AccordionPanel(species_layout)
                    ],
                    value="species",
                ),
            ],
            # open both toggles by default
            value=["sites", "species"],
        )
    ],
    style={"flex": 1, "padding": "10px"},
)

# Define the main layout with toggle and accordion
app.layout = dmc.MantineProvider(
    id="mantine-provider",
    theme=dmc_theme,
    children=[
        dmc.Group(
            children=[
                sidebar,
                dmc.Divider(orientation="vertical"),
                dashboards_layout,
            ],
            align="start",
        )
    ],
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
