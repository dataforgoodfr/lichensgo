from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
import plotly.express as px
import dash_mantine_components as dmc
from dash_iconify import DashIconify
# from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_tree_data, get_observation_data, get_table_data
from my_data.computed_datasets import frequency_table, lichen_frequency, count_lichen_per_species
from utils.css_reader import get_css_properties

from constants import BASE_COLOR_PALETTE, PASTEL_COLOR_PALETTE, ORIENTATIONS, ORIENTATIONS_MAPPING, SQUARE_COLUMNS
_dash_renderer._set_react_version("18.2.0")
# run with : python Dashboards/dashboard.py


# Get the datasets
# environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()

frequency_table_df = frequency_table(lichen_df, lichen_species_df, observation_df, table_df)
count_lichen_per_species_df = count_lichen_per_species(lichen_df, lichen_species_df)

# Extract the font family from the CSS file for plotly (doesn't support CSS)
body_style = get_css_properties("body")

# Define the plotly layout for all plots
plotly_layout = {
    "font": dict(
        family=body_style.get("font-family", "Arial"),
        color=body_style.get("color", "grey"),  # Set grey as fallback color
    ),
    "template": "plotly_white",
    "margin": dict(l=20, r=20, t=40, b=20),
    "barcornerradius":"30%",
}


plotly_hover_style = {
        "font": dict(
            family=body_style.get("font-family", "Arial")
        )
}
# Create the hist3 bar plot
def create_hist3(lichen_frequency_df):
   # Create the bar plot
    hist3 = px.bar(
        lichen_frequency_df,
        x=ORIENTATIONS,
        y="name",
        orientation="h",
        color_discrete_sequence=BASE_COLOR_PALETTE,
    )

    # Update layout
    hist3.update_layout(
        # plotly_layout,
        # hoverlabel=plotly_hover_style,
        legend_title_text="Orientation",
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
    hist3.for_each_trace(lambda t: t.update(name=ORIENTATIONS_MAPPING.get(t.name, t.name)))

    return hist3


# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist3', component_property='figure'),
    Input(component_id='obs-dropdown', component_property='value')
)
def update_hist3(user_selection_obs_id):
    # Filter the table for the selected observation (also called site)
    filtered_frequency_table_df = frequency_table_df.query("observation_id == @user_selection_obs_id")

    # Sum by lichen_id
    lichen_frequency_df = lichen_frequency(filtered_frequency_table_df)

    return create_hist3(lichen_frequency_df)


def create_hist4(count_lichen_per_species_df, user_selection_species_id):
    # Find the index of the selected species ID in the merged table
    user_selection_idx = count_lichen_per_species_df[count_lichen_per_species_df["species_id"] == user_selection_species_id].index

    # Adjust the color of the selected specie to be darker
    pastel_color = PASTEL_COLOR_PALETTE[0]
    selected_color = BASE_COLOR_PALETTE[0]
    color_hist4 = [pastel_color] * len(count_lichen_per_species_df)
    color_hist4[int(user_selection_idx[0])] = selected_color

    # Bar plot
    hist4 = px.bar(
        count_lichen_per_species_df,
        x="count",
        y="name",
        orientation="h",
        color="name",
        color_discrete_sequence=color_hist4,
        # title="Espèces les plus observées par les observateurs Lichens GO"
    )

    # Update layout
    hist4.update_layout(
        # plotly_layout,
        # margin=dict(l=10, r=10, t=30, b=10),
        showlegend=False,
        # hoverlabel=plotly_hover_style
    )

    # Update axes
    hist4.update_xaxes(
        title_text="Nombre",
        showgrid=True,
    )
    hist4.update_yaxes(
        title="",
        # tickfont=dict(size=10)  # Adjust tick font size
    )
    hist4.update_traces(
        hovertemplate="<b>%{y}</b><br><b>Nombre:</b> %{x}<extra></extra>"
    )

    return hist4

# Define callback to update the bar chart based on selected observation ID
@callback(
    Output(component_id='hist4', component_property='figure'),
    Input(component_id='species-dropdown', component_property='value')
)
def update_hist4(user_selection_species_id):
    return create_hist4(count_lichen_per_species_df, user_selection_species_id)


# Create initial filtered table for the first observation ID
observation_ids = frequency_table_df['observation_id'].unique() # Get unique observation IDs for the dropdown
initial_user_selection_obs_id = observation_ids[0]  # Default to the first observation ID

hist3 = update_hist3(initial_user_selection_obs_id)

# Create options for the user species dropdown
user_species_options = [
    {"label": row["name"], "value": row["species_id"]}
    for _, row in count_lichen_per_species_df.sort_values(by="name").iterrows()
]

initial_user_selection_species_id = user_species_options[0]['value'] # Default to the first species ID
hist4 = update_hist4(initial_user_selection_species_id)


# Initialize the Dash app
app = Dash(__name__,
           external_stylesheets=[
               dmc.styles.ALL,
               "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap"
           ]
    )

hist3_layout = dmc.GridCol(
    [
        html.Div(
            [
                html.H3(
                    "Espèces observées sur le site sélectionné",
                    className="graph-title",
                ),
                dmc.Tooltip(
                    label="Distribution des espèces observées, sur le site sélectionné",
                    position="top",
                    withArrow=True,
                    children=DashIconify(
                        icon="material-symbols:info-outline",
                        className="info-icon"
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
)

# Layout for the "Sites" tab
sites_tab = dmc.TabsPanel(
    children=[
        dmc.Grid(
            children=[
                dmc.GridCol(
                    [
                        html.H3(
                            "Carte des observations",
                            className="graph-title",
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
                hist3_layout
            ]
        )
    ],
    value="1",
)

hist4_layout = dmc.GridCol(
    [
        html.Div(
            [
                html.H3(
                    "Espèces les plus observées par les observateurs Lichens GO",
                    className="graph-title"
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
)


# Layout for the "Espèces" tab
species_tab = dmc.TabsPanel(
    children=[
        dmc.Grid(
            children=[
                hist4_layout,
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
    [
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
    ]
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
