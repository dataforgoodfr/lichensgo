# -*- coding: utf-8 -*-
# Import packages
from io import StringIO
import pandas as pd

from dash import html, dcc, Dash, Output, Input, _dash_renderer
import dash_mantine_components as dmc
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from dashboard.translation import get_lazy_translation as _
from dashboard.translation import get_language

from dashboard.datasets import get_useful_data

from dashboard.datasets_computed import (
    merge_tables, calc_degrees_pollution, calc_vdl, count_lichen,
    count_species_per_observation, count_lichen_per_species_per_observation,
    get_download_df
)

from dashboard.constants import BASE_COLOR_PALETTE

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

def fetch_download_data(lang):
    # Fetch datasets
    print("Fetching data for download...")
    lichen_df, merged_lichen_species_df, observation_df, table_df = get_useful_data()

    # Format date
    observation_df["date_obs_formatted"] = pd.to_datetime(observation_df["date_obs"]).dt.strftime("%d/%m/%Y")

    table_with_nb_lichen_df = count_lichen(table_df)
    merged_table_with_nb_lichen_df = merge_tables(table_with_nb_lichen_df, lichen_df, observation_df)
    observation_with_species_count_df = count_species_per_observation(lichen_df, observation_df)
    observation_with_deg_pollution_df = calc_degrees_pollution(merged_table_with_nb_lichen_df, lichen_df, merged_lichen_species_df)
    observation_with_vdl_df = calc_vdl(merged_table_with_nb_lichen_df)
    merged_observation_df = observation_with_species_count_df.merge(observation_with_deg_pollution_df, on="observation_id").merge(observation_with_vdl_df, on="observation_id")

    nb_lichen_per_species_per_observation_df = count_lichen_per_species_per_observation(lichen_df)

    download_df = get_download_df(merged_observation_df, merged_lichen_species_df, nb_lichen_per_species_per_observation_df, lang)

    return download_df

def convert_data_to_json(data):
    data_json = {}

    for key, value in data.items():
        data_json[key] = value.to_json(orient="split", date_format="iso")

    return data_json


# Page Les données
app = Dash("data_page", external_stylesheets=external_stylesheets)

# Define app layout with a hidden input

def serve_layout():

    return dmc.MantineProvider(
        children=[
            dcc.Store(id="download-data-update-status", data={"updated": False}),
            dcc.Store(id="download-data-store"),
            dmc.Title(_("Télécharger les données LichensGo"), order=4, p="md"),
            html.Div(
                [
                    dmc.Select(
                        id="file-format-selector",
                        data=[
                            {"label": "Excel", "value": "xlsx"},
                            {"label": "CSV", "value": "csv"},
                        ],
                        value="xlsx",
                        label=_("Format du fichier"),
                        mr="10px",
                        w="150px",
                    ),
                    dmc.Button(
                        _("Export data"),
                        id="btn_export",
                        variant="filled",
                        color=BASE_COLOR_PALETTE[0],
                        size="md",
                        disabled=True,
                        leftSection=DashIconify(icon="material-symbols:cloud-download"),
                    ),
                    dcc.Download(id="download-dataframe-file"),
                ],
                style={
                    "display": "flex",
                    "align-items": "flex-end",
                    "justify-content": "center",
                    "margin-bottom": "20px",
                },
            ),
            html.Div(
                dmc.Loader(
                    id="loader",
                    color=BASE_COLOR_PALETTE[0],
                    size="lg",
                ),
                style={"justify-content": "center", "display": "flex"},
            ),
            html.Div(
                dmc.Table(
                    id="download-table",
                    striped=True,
                    highlightOnHover=True,
                    withTableBorder=True,
                    withColumnBorders=True,
                    stickyHeader=True,
                ),
                style={
                    "overflowX": "auto",  # Enable horizontal scrolling
                    "paddingLeft": "10px",
                    "paddingRight": "10px",
                    "margin": "0px",
                    "maxHeight": "80vh",
                },
            ),
        ],
    )

app.layout = serve_layout # NB: we don"t call the function here, so that the layout and translations are reloaded at each page refresh

@app.callback(
    Output("download-data-store", "data"),
    Output("download-data-update-status", "data"),
    Input("download-data-update-status", "data"),
)
def update_data_store(status):
    if status["updated"]:
        raise PreventUpdate

    lang = get_language()
    download_df = fetch_download_data(lang)
    download_json = download_df.to_json(orient="split", date_format="iso")

    return download_json, {"updated": True}

@app.callback(
    Output("download-table", "data"),
    Output("btn_export", "disabled"),
    Output("loader", "style"),
    Input("download-data-update-status", "data"),
    State("download-data-store", "data"),
    prevent_initial_call=True,
)
def update_table(status, data):
    download_df = pd.read_json(StringIO(data), orient="split")

    # Edit the values for display
    percentage_columns = [str(_("deg_toxitolerance_export")), str(_("deg_eutrophication_export")), str(_("deg_acidity_export"))]
    for col in percentage_columns:
        if col in download_df.columns:
            download_df[col] = download_df[col].apply(lambda x: f"{x * 100:.2f}%")

    # Convert the dataframe to a dictionary for dmc.Table
    download_table = {
        "head": list(download_df.columns),
        "body": download_df.round(4).values.tolist()# round floats to 4 decimals
    }

    button_disabled = False
    loader_style = {"display": "None"} # hide the loader

    return download_table, button_disabled, loader_style

@app.callback(
    Output("download-dataframe-file", "data"),
    Input("btn_export", "n_clicks"),
    State("file-format-selector", "value"),
    State("download-data-store", "data"),
    prevent_initial_call=True,
)
def download_file(n_clicks, file_format, jsonified_download_df):
    # Read the stored dataframe in Dcc.Store in json format
    download_df = pd.read_json(StringIO(jsonified_download_df), orient="split")

    if file_format == "csv":
        export = dcc.send_data_frame(download_df.to_csv, "lichensgo_data.csv", index=False)
    elif file_format == "xlsx":
        export = dcc.send_data_frame(download_df.to_excel, "lichensgo_data.xlsx", index=False, sheet_name="lichensgo_data")

    return export

if __name__ == "__main__":
    app.run_server(debug=True)
