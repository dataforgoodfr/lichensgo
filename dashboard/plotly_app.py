# -*- coding: utf-8 -*-
# Import packages
import os
from datetime import datetime
import pandas as pd

from dash import html, dcc, Dash, Output, Input, _dash_renderer
import dash_mantine_components as dmc
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

# from django.utils.translation import get_language
# from django.utils.translation import gettext_lazy as _

# from django_plotly_dash import DjangoDash
# from django.templatetags.static import static

from dashboard.translation import get_lazy_translation as _
from dashboard.translation import get_language

# import flask # only for DjangoDash
from flask_caching import Cache

from dashboard.datasets import get_useful_data
from dashboard.datasets_computed import (
    merge_tables, calc_degrees_pollution, calc_vdl, count_lichen,
    count_lichen_per_species, count_species_per_observation,
    count_lichen_per_lichen_id, group_lichen_by_observation_and_thallus
)
from dashboard.charts import (
    blank_figure, create_map_observations, create_map_species_present,
    create_hist1_nb_species, create_hist2_vdl, create_hist3, create_pie_thallus,
    create_hist4, create_gauge_chart
)
from dashboard.constants import (
    MAP_COLOR_PALETTES, BASE_COLOR_PALETTE, BODY_FONT_FAMILY,
    POSITIVE_GAUGE_COLOR_PALETTE, NEGATIVE_GAUGE_COLOR_PALETTE,
    CARD_STYLE, MAP_STYLE, PLOTLY_CONFIG, PLOTLY_GAUGE_CONFIG
)
from dashboard.utils.location import get_address_from_lat_lon

# Constants
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLANK_FIG = blank_figure()

_dash_renderer._set_react_version("18.2.0")

external_stylesheets = [
    dmc.styles.ALL,
    dmc.styles.DATES,
]

# Need version of plolty.js > 2.29.1 to render map and charts properly (https://github.com/plotly/plotly.py/issues/4535 ),
# but not automatically loaded as dash version < 2.13 (https://dash.plotly.com/external-resources) and django 3 not compatible with that
external_scripts = [
    "https://cdn.plot.ly/plotly-2.35.2.min.js",
    "https://cdn.plot.ly/plotly-locale-fr-latest.js",
    "https://cdn.plot.ly/plotly-locale-en-latest.js",
]

# Theme for the app
dmc_theme = {
    "fontSmoothing": True,
    "forceColorScheme":"light",
    "colors": {
        "myBlue": BASE_COLOR_PALETTE[::-1],  # Reverse the color palette
        "dark": [
            "#C9C9C9", "#b8b8b8", "#828282", "#696969", "#424242",
            "#3b3b3b", "#2e2e2e", "#242424", "#1f1f1f", "#141414"
        ],
    },
    "primaryColor": "myBlue",
    "fontFamily": BODY_FONT_FAMILY,
    "defaultRadius": "md",  # Default radius for cards
}

# Reusable components
def title_and_tooltip(title, tooltip_text):
    return html.Span(
                children=[
                     dmc.Title(
                        title,
                        order=4,
                        display="inline",
                        mr="2px",
                        style={"color": "var(--text-color)"} # Use the text color defined in the theme (white in dark mode was not applied without that)
                    ),
                        dmc.Tooltip(
                        children=DashIconify(icon="material-symbols:info-outline", height=15),
                        label=tooltip_text,
                        withArrow=True,
                        position="top",
                        maw="50%",
                        style={"white-space": "normal", "word-wrap": "break-word", "display": "inline"},
                    ),
                ],
                style={"display": "inline-flex", "align-items": "top"},
            )

def gauge_card(title, tooltip_text, graph_id, max_height):
    return dmc.Card(
        children=[
            title_and_tooltip(title, tooltip_text),
            dcc.Graph(
                id=graph_id,
                figure=BLANK_FIG,
                style={
                    "height": "100px",
                    "width": "100%",
                    "marginRight": "1px",
                },
                config=PLOTLY_GAUGE_CONFIG,
            ),
        ],
        style={
            "display": "flex",
            "flexDirection": "column",
            "justifyContent": "space-between",
            "flexGrow": 1,
            "maxHeight": max_height,
        },
        **CARD_STYLE,
    )

def histogram_card(title, tooltip_text, graph_id, min_width):

    return dmc.Card(
        children=[
            html.Div(
                children=[
                    title_and_tooltip(title, tooltip_text),
                    dcc.Graph(
                        id=graph_id,
                        figure=BLANK_FIG,
                        style={"height": "100%"},
                        config={
                            **PLOTLY_CONFIG,
                            "locale": get_language()[0:2] if get_language() else "fr",
                        },
                    ),
                ],
                style={
                    "display": "flex",
                    "flexDirection": "column",
                    "flex": "1 1 auto",
                    "margin": 0,
                    "padding": 0,
                },
            ),
        ],
        **CARD_STYLE,
        miw=min_width,
        style={"height": "100%"},
    )

# Utils
def filter_dates_observation_df(merged_observation_df, date_range):
    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    # Ensure the date_obs column is in datetime format
    merged_observation_df["date_obs"] = pd.to_datetime(merged_observation_df["date_obs"]).dt.date

    return merged_observation_df[
        (merged_observation_df["date_obs"] >= start_date) &
        (merged_observation_df["date_obs"] <= end_date)
    ]

def get_observation_clicked(filtered_observation_df, clickData):
    if clickData is None:
        return None
    lat_clicked = clickData["points"][0]["lat"]
    lon_clicked = clickData["points"][0]["lon"]
    observation_clicked = filtered_observation_df[
        (filtered_observation_df["localisation_lat"] == lat_clicked) &
        (filtered_observation_df["localisation_long"] == lon_clicked)
    ]
    return observation_clicked.iloc[0] if not observation_clicked.empty else None

def get_selected_address(observation_clicked):
    if observation_clicked is None:
        return "", {"display": "none"}

    selected_address = get_address_from_lat_lon(
        observation_clicked["localisation_lat"], observation_clicked["localisation_long"], get_language())
    selected_address_style = {"display": "block"} if selected_address else {"display": "none"}
    return selected_address, selected_address_style


def serve_layout():

    data = fetch_data()
    observation_df = data["observation_df"]
    lichen_species_df = data["merged_lichen_species_df"]

    # Initialize options and selections
    calendar_range = [observation_df["date_obs"].min(), datetime.now().date()]
    species_options = [{"value": str(row["species_id"]), "label": row["name"]} for _, row in lichen_species_df.sort_values(by="name").iterrows()]
    species_id_selected = species_options[0]["value"]
    species_name_selected = species_options[0]["label"]

    # Toggle to switch between light and dark theme
    theme_toggle = dmc.ActionIcon(
        [
            dmc.Paper(DashIconify(icon="radix-icons:sun", width=25),  darkHidden=True),
            dmc.Paper(DashIconify(icon="radix-icons:moon", width=25), lightHidden=True),
        ],
        variant="transparent",
        id="color-scheme-toggle",
        size="lg",
        style={
            "position": "fixed",
            "top": "20px",
            "right": "26px",
            "zIndex": 1000,
        }
    )

    # Layout for the sites (observations)
    sites_layout = html.Div(
        style={
            "display": "flex",
            "flexDirection": "row",  # horizontal layout with flex columns
            "gap": "16px",
            "height": "800px",
        },
        children=[
            # First column with map and gauge
            html.Div(
                style={
                    "flex": "1 1 50",
                    "display": "flex",
                    "flexDirection": "column",
                    "height": "100%",
                },
                children=[
                    dmc.Group(
                        [
                            DashIconify(icon="mdi:calendar", width=26, height=26),
                            dmc.DatePicker(
                                id="date-picker-range",
                                minDate=calendar_range[0],
                                maxDate=calendar_range[1],
                                type="range",
                                value=calendar_range,
                                valueFormat="DD/MM/YYYY",
                                w=190,
                                popoverProps={
                                    "width": 292  # set fixed width to avoid overflow
                                },
                            ),
                            dmc.Button(
                                id="reset-date-button",
                                children="✖",
                                variant="outline",
                                color="red",
                                size="xs",
                            ),
                        ],
                        align="center",
                        gap="xs",
                        mb="xs",
                    ),
                    dmc.Card(
                        style={"flex": "1 1 auto"},
                        children=[
                            title_and_tooltip(
                                title=_("observation_map_title"),
                                tooltip_text=_("observation_map_tooltip"),
                            ),
                            dmc.SegmentedControl(
                                id="map-column-select",
                                value=list(MAP_COLOR_PALETTES.keys())[0],
                                data=[
                                    {"label": _(col), "value": col}
                                    for col in [
                                        "nb_species_cat",
                                        "VDL_cat",
                                        "deg_toxitolerance_cat",
                                        "deg_eutrophication_cat",
                                        "deg_acidity_cat",
                                    ]
                                ],
                                transitionDuration=600,
                                transitionTimingFunction="ease-in-out",
                                mb="xs",
                                style={"display": "flex", "justifyContent": "flex-start", "flexWrap": "wrap"},
                            ),
                            html.Div(
                                style={"flex": "1 1 auto"},
                                children=[
                                    dmc.Card(
                                        children=[
                                            dmc.Select(
                                                id="map-style-dropdown",
                                                placeholder=_("map_style_selector"),
                                                data=[
                                                    {
                                                        "label": "Streets",
                                                        "value": "streets",
                                                    },
                                                    {
                                                        "label": "OpenStreetMap",
                                                        "value": "open-street-map",
                                                    },
                                                    {
                                                        "label": "Satellite",
                                                        "value": "satellite",
                                                    },
                                                ],
                                                clearable=True,
                                                allowDeselect=False,
                                                searchable=False,
                                                style={
                                                    "position": "absolute",
                                                    "top": "15px",
                                                    "left": "15px",
                                                    "zIndex": "1",
                                                    "width": "150px",
                                                    "opacity": "0.8",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="map-nb_species-vdl",
                                                figure=BLANK_FIG,
                                                style={"height": "100%"},
                                                config={
                                                    **PLOTLY_CONFIG,
                                                    "locale": get_language(),
                                                },
                                            ),
                                        ],
                                        style={"height": "97%"},
                                        **MAP_STYLE,
                                    ),
                                ],
                            ),
                        ],
                        **CARD_STYLE,
                        mb="md",
                    ),
                    dmc.Grid(
                        gutter="md",
                        align="strech",
                        children=[
                            dmc.GridCol(
                                gauge_card(
                                    title=_("toxitolerance_gauge_title"),
                                    tooltip_text=_("toxitolerance_gauge_tooltip"),
                                    graph_id="gauge-chart-toxitolerance",
                                    max_height="200px",
                                ),
                                span=4,
                                style={"display": "flex", "flexDirection": "column"},
                            ),
                            dmc.GridCol(
                                gauge_card(
                                    title=_("eutrophication_gauge_title"),
                                    tooltip_text=_("eutrophication_gauge_tooltip"),
                                    graph_id="gauge-chart-eutrophication",
                                    max_height="200px",
                                ),
                                span=4,
                                style={"display": "flex", "flexDirection": "column"},
                            ),
                            dmc.GridCol(
                                gauge_card(
                                    title=_("acidity_gauge_title"),
                                    tooltip_text=_("acidity_gauge_tooltip"),
                                    graph_id="gauge-chart-acidity",
                                    max_height="200px",
                                ),
                                span=4,
                                style={"display": "flex", "flexDirection": "column"},
                            ),
                        ],
                    ),
                ],
            ),
            # Second column with histograms
            html.Div(
                style={
                    "height": "100%",
                    "flex": "1 1 auto",
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "16px",  # vertical gap between the 2 histograms
                },
                children=[
                    html.Div(
                        style={
                            "display": "flex",
                            "flexWrap": "nowrap",
                            "justifyContent": "space-between",
                            "height": "50%",
                            "gap": "16px",  # horizontal gap between the 2 histograms
                        },
                        children=[
                            html.Div(
                                style={
                                    "flex": "1 1 50%",
                                    "height": "100%",
                                },
                                children=[
                                    histogram_card(
                                        title=_(
                                            "species_number_distribution_hist1_title"
                                        ),
                                        tooltip_text=_(
                                            "species_number_distribution_hist1_tooltip"
                                        ),
                                        graph_id="hist1-nb_species",
                                        min_width="220px",
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "flex": "1 1 50%",
                                },
                                children=[
                                    histogram_card(
                                        title=_("vdl_distribution_hist2_title"),
                                        tooltip_text=_(
                                            "vdl_distribution_hist2_tooltip"
                                        ),
                                        graph_id="hist2-vdl",
                                        min_width="220px",
                                    ),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        style={
                            "display": "flex",
                            "height": "50%",
                            "gap": "16px",  # horizontal gap between the 2 histograms
                        },
                        children=[
                            html.Div(
                                style={
                                    "flex": "1 1 60%",
                                    "height": "100%",
                                },
                                children=[
                                    histogram_card(
                                        title=_("species_distribution_hist3_title"),
                                        tooltip_text=_(
                                            "species_distribution_hist3_tooltip"
                                        ),
                                        graph_id="hist3-species",
                                        min_width="260px",
                                    ),
                                ],
                            ),
                            html.Div(
                                style={
                                    "flex": "1 1 40%",
                                    "height": "100%",
                                },
                                children=[
                                    histogram_card(
                                        title=_("thallus_pie_chart_title"),
                                        tooltip_text=_("thallus_pie_chart_tooltip"),
                                        graph_id="pie-thallus",
                                        min_width="170px",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    species_card = dmc.Card(
        children=[
            dmc.CardSection(
                children=[
                    dmc.Text(
                        id="species-name",
                        size="lg",
                        style={"fontStyle": "italic", "fontWeight": "bold"},
                        children=[species_name_selected], # initial value
                    ),
                ],
                withBorder=True,
                inheritPadding=True,
                py="xs",
            ),
            dmc.Text(
                id="species-description",
                style={"display": "none"},  # hide initially
                children=[
                    _("Ce lichen"),
                    " ",
                    dmc.Text(
                        id="species-thallus",
                        c="myBlue",
                        style={"display": "inline"},
                    ),
                    " ",
                    _("est"),
                    " ",
                    dmc.Text(
                        id="species-rarity",
                        c="myBlue",
                        style={"display": "inline"},
                    ),
                    " ",
                    _("en milieu urbain"),
                    ".",
                ],
                mt="sm",
                c="dimmed",
                size="sm",
            ),
            dmc.CardSection(
                id="species-image-section",
                children=[
                    dmc.Image(
                        id="species-image",
                        mt="sm",
                        src=None,
                        fallbackSrc="https://placehold.co/600x400?text=No%20image%20found",
                    ),
                ],
                style={"display": "none"},  # hide initially
            ),
            dmc.CardSection(
                id="species-badges-section",
                children=[
                    dmc.Stack(
                        [
                            dmc.Group(
                                [
                                    _("toxitolerance_badge"),
                                    dmc.Badge(
                                        id="toxitolerance-badge", variant="light"
                                    ),
                                ]
                            ),
                            dmc.Group(
                                [
                                    _("eutrophication_badge"),
                                    dmc.Badge(id="eutro-badge", variant="light"),
                                ]
                            ),
                            dmc.Group(
                                [
                                    _("acidity_badge"),
                                    dmc.Badge(id="acid-badge", variant="light"),
                                ]
                            ),
                        ],
                        align="left",
                        gap="md",
                    ),
                ],
                style={"display": "none"},  # hide initially
                inheritPadding=True,
                mt="sm",
                pb="md",
            ),
        ],
        withBorder=True,
        shadow="sm",
        radius="md",
        maw=300,
        miw=250,
    )

    # Layout for the "Espèces" tab
    species_layout = html.Div(
        children=[
            dmc.Select(
                id="species-dropdown",
                label=_("species_dropdown_label"),
                description=_("species_dropdown_description"),
                value=species_id_selected,
                data=species_options,
                clearable=False,
                allowDeselect=False,
                searchable=True,
                w=400,
            ),
            dmc.Space(h=10),
            html.Div(
                style={
                    "display": "flex",
                    "flexDirection": "row",  # horizontal layout with flex columns
                    "gap": "16px",
                    "height": "670px",
                },
                children=[
                    html.Div(species_card),
                    html.Div(
                        style={
                            "flex": "1 1 40%",
                            "height": "100%",
                        },
                        children=[
                            dmc.Card(
                                id="species-presence-card",
                                children=[
                                    title_and_tooltip(
                                        title=_("species_presence_map_title"),
                                        tooltip_text=_("species_presence_map_tooltip"),
                                    ),
                                    dmc.Card(
                                        children=[
                                            dmc.Select(
                                                id="map-species-style-dropdown",
                                                placeholder=_("map_style_selector"),
                                                data=[
                                                    {
                                                        "label": "Streets",
                                                        "value": "streets",
                                                    },
                                                    {
                                                        "label": "OpenStreetMap",
                                                        "value": "open-street-map",
                                                    },
                                                    {
                                                        "label": "Satellite",
                                                        "value": "satellite",
                                                    },
                                                ],
                                                clearable=True,
                                                allowDeselect=False,
                                                searchable=False,
                                                style={
                                                    "position": "absolute",
                                                    "top": "15px",
                                                    "left": "15px",
                                                    "zIndex": "1",
                                                    "width": "150px",
                                                    "opacity": "0.8",
                                                },
                                            ),
                                            dcc.Graph(
                                                id="map-species_present",
                                                figure=BLANK_FIG,
                                                config={
                                                    **PLOTLY_CONFIG,
                                                    "locale": (
                                                        get_language()[0:2]
                                                        if get_language()
                                                        else "fr"
                                                    ),
                                                },
                                                style={"height": "100%"},
                                            ),
                                        ],
                                        **MAP_STYLE,
                                        style={"height": "100%"},
                                        mt="xs",
                                    ),
                                ],
                                miw="400px",
                                style={"height": "100%"},
                                **CARD_STYLE,

                            ),
                        ],
                    ),
                    html.Div(
                        id="hist4-card",
                        style={
                            "flex": "1 1 40%",
                            "height": "100%",
                        },
                        children=[
                            histogram_card(
                                title=_("species_distribution_hist4_title"),
                                tooltip_text=_("species_distribution_hist4_tooltip"),
                                graph_id="hist4-species",
                                min_width="400px",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    dashboards_layout = html.Div(
        style={"width": "100%"},
        children=[
            dmc.Accordion(
                style={
                    "width": "fit-content",
                    "min-width": "100%",
                },  # min-width to avoid resizing when closing the accordion
                disableChevronRotation=True,
                chevronPosition="left",
                variant="contained",
                multiple=True,
                children=[
                    dmc.AccordionItem(
                        children=[
                            dmc.AccordionControl(
                                [
                                    dmc.Group(
                                        children=[
                                            DashIconify(
                                                icon="tabler:map-pin",
                                                height=25,
                                                color=BASE_COLOR_PALETTE[0],
                                            ),
                                            dmc.Tooltip(
                                                label=_("observation_tab_tooltip"),
                                                position="top",
                                                withArrow=True,
                                                children=dmc.Title(
                                                    _("observation_tab_title"),
                                                    order=3,
                                                ),
                                            ),
                                            dmc.Badge(
                                                id="selected-address-badge",
                                                variant="light",
                                                size="lg",
                                                maw="1000px",
                                                ml="lg",
                                                style={
                                                    "display": "none"
                                                },  # Initially hidden
                                            ),
                                        ],
                                        align="center",
                                    ),
                                ],
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
                                            color=BASE_COLOR_PALETTE[0],
                                        ),
                                        dmc.Title(
                                            _("species_tab_title"),
                                            order=3,
                                        ),
                                    ],
                                    align="bottom",
                                ),
                            ),
                            dmc.AccordionPanel(species_layout),
                        ],
                        value="species",
                    ),
                ],
                # open both toggles by default
                value=["sites", "species"],
            )
        ],
    )

    layout = dmc.MantineProvider(
        id="mantine-provider",
        theme=dmc_theme,
        children=[
            dmc.Group(
                children=[
                    dashboards_layout,
                    theme_toggle,
                ],
                align="start",
            ),
        ],
    )

    return layout

app = Dash(
    name="lgresults",
    external_stylesheets=external_stylesheets,
    external_scripts=external_scripts,
)

# Initialize cache to store data and avoid recomputing it at each callback
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': '.cache',
    'CACHE_THRESHOLD': 100,
}

# server = flask.Flask(__name__) # to use for DjangoDash
server = app.server # to remove when using DjangoDash
cache = Cache(server, config=CACHE_CONFIG)

@cache.memoize(timeout=2*60)  # Cache timeout set to 2 minutes
def fetch_data():
    # Fetch datasets
    print("Fetching data...")
    lichen_df, merged_lichen_species_df, observation_df, table_df = get_useful_data()

    # Format date for hover labels
    observation_df["date_obs_formatted"] = pd.to_datetime(observation_df["date_obs"]).dt.strftime("%d/%m/%Y")

    # Data processing for observations tab
    lichen_df = lichen_df.merge(observation_df[["observation_id", "user_id"]], on="observation_id") # Add user_id to lichen_df
    table_with_nb_lichen_df = count_lichen(table_df)
    merged_table_with_nb_lichen_df = merge_tables(table_with_nb_lichen_df, lichen_df, observation_df)
    grouped_lichen_by_observation_and_thallus_df = group_lichen_by_observation_and_thallus(merged_table_with_nb_lichen_df, merged_lichen_species_df)
    nb_lichen_per_lichen_id_df = count_lichen_per_lichen_id(table_with_nb_lichen_df, lichen_df, merged_lichen_species_df)
    observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
    observation_with_deg_pollution_df = calc_degrees_pollution(merged_table_with_nb_lichen_df, lichen_df, merged_lichen_species_df)
    observation_with_vdl_df = calc_vdl(merged_table_with_nb_lichen_df)
    merged_observation_df = observation_with_species_count_df.merge(observation_with_deg_pollution_df, on="observation_id").merge(observation_with_vdl_df, on="observation_id")

    # Data processing for species tab
    nb_lichen_per_species_df = count_lichen_per_species(lichen_df, merged_lichen_species_df)

    data = {
        "lichen_df": lichen_df,
        "merged_lichen_species_df": merged_lichen_species_df,
        "observation_df": observation_df,
        "grouped_lichen_by_observation_and_thallus_df": grouped_lichen_by_observation_and_thallus_df,
        "nb_lichen_per_lichen_id_df": nb_lichen_per_lichen_id_df,
        "merged_observation_df": merged_observation_df,
        "nb_lichen_per_species_df": nb_lichen_per_species_df
        }

    return data

app.layout = serve_layout

@app.callback(
    Output("date-picker-range", "value"),
    Input("reset-date-button", "n_clicks"),
    State("date-picker-range", "minDate"),
    State("date-picker-range", "maxDate"),
    State("date-picker-range", "value")
)
def reset_date_range(n_clicks, min_date, max_date, date_range):
    if n_clicks is None or date_range == [min_date, max_date]:
        raise PreventUpdate
    return [min_date, max_date]

@app.callback(
    Output("map-nb_species-vdl", "figure"),
    Output("map-nb_species-vdl", "config"),
    Output("selected-address-badge", "children"),
    Output("selected-address-badge", "style"),
    Input("date-picker-range", "value"),
    Input("map-column-select", "value"),
    Input("map-style-dropdown", "value"),
    Input("map-nb_species-vdl", "clickData"),
    State("map-nb_species-vdl", "relayoutData"),
)
def update_observation_map(date_range, map_column_selected, map_style, clickData, relayoutData):

    if None in date_range:
        raise PreventUpdate

    data = fetch_data()
    merged_observation_df = data["merged_observation_df"]

    filtered_observation_df = filter_dates_observation_df(merged_observation_df, date_range)

    if relayoutData and "map.zoom" in relayoutData and "map.center" in relayoutData:
        current_zoom = relayoutData["map.zoom"]
        current_center = relayoutData["map.center"]
    else:
        current_zoom = 4.8
        if filtered_observation_df.empty:
            current_center = { # Paris
            "lat": 48.866667,
            "lon": 2.333333
            }
        else:
            current_center = {
                "lat": filtered_observation_df["localisation_lat"].mean(),
                "lon": filtered_observation_df["localisation_long"].mean()
            }

    observation_clicked = get_observation_clicked(filtered_observation_df, clickData)
    selected_address, selected_address_style = get_selected_address(observation_clicked)

    fig_map = create_map_observations(filtered_observation_df, map_column_selected, current_zoom, current_center, map_style, observation_clicked=observation_clicked)
    config = PLOTLY_CONFIG
    config["locale"] = get_language()[0:2] if get_language() else "fr"

    return fig_map, config, selected_address, selected_address_style

@app.callback(
    Output("hist1-nb_species", "figure"),
    Output("hist1-nb_species", "config"),
    Output("hist2-vdl", "figure"),
    Output("hist2-vdl", "config"),
    Input("date-picker-range", "value"),
    Input("map-nb_species-vdl", "clickData"),
)
def update_histograms(date_range, clickData):
    if None in date_range:
        raise PreventUpdate

    config = PLOTLY_CONFIG
    config["locale"] = get_language()[0:2] if get_language() else "fr"

    data = fetch_data()
    merged_observation_df = data["merged_observation_df"]

    filtered_observation_df = filter_dates_observation_df(merged_observation_df, date_range)

    observation_clicked = get_observation_clicked(filtered_observation_df, clickData)

    if observation_clicked is None:
        hist1_nb_species = create_hist1_nb_species(filtered_observation_df, None)
        hist2_vdl = create_hist2_vdl(filtered_observation_df, None)

        return hist1_nb_species, config, hist2_vdl, config

    nb_species_clicked = observation_clicked["nb_species"]
    vdl_clicked = observation_clicked["VDL"]

    if not isinstance(nb_species_clicked, float):
        nb_species_clicked = None

    hist1_nb_species = create_hist1_nb_species(filtered_observation_df, nb_species_clicked)
    hist2_vdl = create_hist2_vdl(filtered_observation_df, vdl_clicked)

    return hist1_nb_species, config, hist2_vdl, config

@app.callback(
    Output("gauge-chart-toxitolerance", "figure"),
    Output("gauge-chart-eutrophication", "figure"),
    Output("gauge-chart-acidity", "figure"),
    Output("hist3-species", "figure"),
    Output("hist3-species", "config"),
    Output("pie-thallus", "figure"),
    Output("pie-thallus", "config"),
    Input("date-picker-range", "value"),
    Input("map-nb_species-vdl", "clickData"),
    prevent_initial_call=True,
)
def update_gauge_hist_pie(date_range, clickData):
    if None in date_range:
        raise PreventUpdate

    config = PLOTLY_CONFIG
    config["locale"] = get_language()[0:2] if get_language() else "fr"

    if clickData is None:
        return BLANK_FIG, BLANK_FIG, BLANK_FIG, BLANK_FIG, config, BLANK_FIG, config

    data = fetch_data()
    merged_observation_df = data["merged_observation_df"]

    filtered_observation_df = filter_dates_observation_df(merged_observation_df, date_range)

    observation_clicked = get_observation_clicked(filtered_observation_df, clickData)

    if observation_clicked is None:
        return BLANK_FIG, BLANK_FIG, BLANK_FIG, BLANK_FIG, config, BLANK_FIG, config

    observation_id_clicked = observation_clicked["observation_id"]

    gauge_chart_toxitolerance = create_gauge_chart(observation_clicked["deg_toxitolerance"], intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)
    gauge_chart_acidity = create_gauge_chart(observation_clicked["deg_acidity"], intervals=[0, 25, 50, 75, 100], color_scale=POSITIVE_GAUGE_COLOR_PALETTE)
    gauge_chart_eutrophication = create_gauge_chart(observation_clicked["deg_eutrophication"], intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE)

    nb_lichen_per_lichen_id_df = data["nb_lichen_per_lichen_id_df"]
    grouped_lichen_by_observation_and_thallus_df = data["grouped_lichen_by_observation_and_thallus_df"]

    filtered_nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df[
        nb_lichen_per_lichen_id_df["observation_id"] == observation_id_clicked
    ]
    hist3_species = create_hist3(filtered_nb_lichen_per_lichen_id_df)

    filtered_grouped_lichen_by_observation_and_thallus_df = grouped_lichen_by_observation_and_thallus_df[
        grouped_lichen_by_observation_and_thallus_df["observation_id"] == observation_id_clicked
    ]
    pie_thallus = create_pie_thallus(filtered_grouped_lichen_by_observation_and_thallus_df)

    return gauge_chart_toxitolerance, gauge_chart_eutrophication, gauge_chart_acidity, hist3_species, config, pie_thallus, config

@app.callback(
    Output("map-species_present", "figure"),
    Output("map-species_present", "config"),
    Input("species-dropdown", "value"),
    Input("map-species-style-dropdown", "value"),
    State("map-species_present", "relayoutData"),
)
def update_species_map(species_id_selected, map_style, relayoutData):
    if isinstance(species_id_selected, str):
        species_id_selected = int(species_id_selected)

    data = fetch_data()
    lichen_df = data["lichen_df"]
    observation_df = data["observation_df"]
    merged_lichen_species_df = data["merged_lichen_species_df"]

    species_name_selected = merged_lichen_species_df.loc[merged_lichen_species_df["species_id"] == species_id_selected, "name"].values[0]

    observation_with_selected_species_col_df = observation_df.copy()

    observation_with_selected_species_col_df["selected_species_present"] = observation_with_selected_species_col_df["observation_id"].isin(
        lichen_df.loc[lichen_df["species_id"] == species_id_selected, "observation_id"]
    )

    if relayoutData and "map.zoom" in relayoutData and "map.center" in relayoutData:
        current_zoom = relayoutData["map.zoom"]
        current_center = relayoutData["map.center"]
    else:
        current_zoom = 4.8
        if observation_with_selected_species_col_df.empty:
            current_center = { # Paris
            "lat": 48.866667,
            "lon": 2.333333
            }
        else:
            current_center = {
                "lat": observation_with_selected_species_col_df["localisation_lat"].mean(),
                "lon": observation_with_selected_species_col_df["localisation_long"].mean()
            }

    fig_map = create_map_species_present(observation_with_selected_species_col_df, species_name_selected, "selected_species_present", current_zoom, current_center, map_style)
    config = PLOTLY_CONFIG
    config["locale"] = get_language()[0:2] if get_language() else "fr"

    return fig_map, config

@app.callback(
    Output("hist4-species", "figure"),
    Output("species-description", "style"),
    Output("species-image-section", "style"),
    Output("species-badges-section", "style"),
    Output("species-name", "children"),
    Output("species-image", "src"),
    Output("acid-badge", "children"),
    Output("eutro-badge", "children"),
    Output("toxitolerance-badge", "children"),
    Output("species-thallus", "children"),
    Output("species-rarity", "children"),
    Input("species-dropdown", "value"),
)
def update_species_info(species_id_selected):
    if isinstance(species_id_selected, str):
        species_id_selected = int(species_id_selected)

    data = fetch_data()
    merged_lichen_species_df = data["merged_lichen_species_df"]

    filtered_nb_lichen_per_species_df = data["nb_lichen_per_species_df"]

    hist4_species = create_hist4(filtered_nb_lichen_per_species_df, species_id_selected)

    species_selected = merged_lichen_species_df[merged_lichen_species_df["species_id"] == species_id_selected].iloc[0]

    species_card_style = {"display": "block"} if species_id_selected else {"display": "none"}
    species_name = species_selected["name"]
    species_img = species_selected["picture"]
    species_img_url = app.get_asset_url(species_img)

    species_acidity = _(species_selected["pH"])
    species_eutrophication = _(species_selected["eutrophication"])
    species_toxitolerance = _(species_selected["poleotolerance"])
    species_thallus = _(species_selected["thallus"])
    species_rarity = _(species_selected["rarity"])

    return hist4_species, species_card_style, species_card_style, species_card_style, species_name, species_img_url, species_acidity, species_eutrophication, species_toxitolerance, species_thallus, species_rarity

# Callback to switch between light and dark theme
@app.callback(
    Output("mantine-provider", "forceColorScheme"),
    Input("color-scheme-toggle", "n_clicks"),
    State("mantine-provider", "forceColorScheme"),
    prevent_initial_call=True,
)
def switch_theme(_, theme):
    return "dark" if (theme == "light" or theme is None) else "light"


if __name__ == "__main__":
    app.run_server(debug=True)
