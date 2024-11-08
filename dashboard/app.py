import pandas as pd
import os
import dash_mantine_components as dmc

from dash import Dash, _dash_renderer, html, dcc, Output, Input, callback
from dash.dependencies import State
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify
from datetime import datetime

from my_data.datasets import get_useful_data
from my_data.computed_datasets import merge_tables, calc_degrees_pollution, calc_vdl, count_lichen, count_lichen_per_species, count_species_per_observation, count_lichen_per_lichen_id, group_lichen_by_observation_and_thallus
from dashboard.charts import blank_figure, create_map_observations, create_map_species_present, create_hist1_nb_species, create_hist2_vdl, create_hist3, create_pie_thallus, create_hist4, create_gauge_chart
from dashboard.constants import MAP_COLOR_PALETTES, BASE_COLOR_PALETTE, BODY_FONT_FAMILY, POSITIVE_GAUGE_COLOR_PALETTE, NEGATIVE_GAUGE_COLOR_PALETTE, GRID_STYLE, CARD_STYLE, MAP_STYLE, FLEX_COLUMNS_CONTAINER_STYLE
from dashboard.utils.translations import get_translation
from dashboard.utils.location import get_address_from_lat_lon

_dash_renderer._set_react_version('18.2.0')

# Set the language (could be dynamically set based on user preference)
lang = 'fr' # allowed values: 'en', 'fr'

# Get the datasets
print("Fetching data...")
lichen_df, merged_lichen_species_df, observation_df, table_df, tree_df = get_useful_data()

# Format the date for the hover labels
observation_df['date_obs_formatted'] = pd.to_datetime(observation_df['date_obs']).dt.strftime('%d/%m/%Y')

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

# Initialize the options and selections
date_range = [merged_observation_df['date_obs'].min(), datetime.now().date()]
map_column_selected = list(MAP_COLOR_PALETTES.keys())[0]

# Convert DataFrame to list of dictionaries
species_options = [{'value': str(row['species_id']), 'label': row['name']} for _, row in merged_lichen_species_df.sort_values(by='name').iterrows()]
species_id_selected = species_options[0]['value'] # Default to the first species ID

# Callback to reset the date range
@callback(
    Output('date-picker-range', 'value'),
    Input('reset-date-button', 'n_clicks'),
    State('date-picker-range', 'minDate'),
    State('date-picker-range', 'maxDate'),
    State('date-picker-range', 'value')
)
def reset_date_range(n_clicks, min_date, max_date, date_range):
    if n_clicks is None or date_range == [min_date, max_date]:
        raise PreventUpdate

    return [min_date, max_date]

# First callback to update the dashboard based on date and map selection
@callback(
    Output('map-nb_species-vdl', 'figure'),
    Output('selected-address-badge', 'children'),
    Output('selected-address-badge', 'style'),
    Output('hist1-nb_species', 'figure'),
    Output('hist2-vdl', 'figure'),
    Output('gauge-chart-toxitolerance', 'figure'),
    Output('gauge-chart-eutrophication', 'figure'),
    Output('gauge-chart-acidity', 'figure'),
    Output('hist3-species', 'figure'),
    Output('pie-thallus', 'figure'),
    Input('date-picker-range', 'value'),
    Input('map-column-select', 'value'),
    Input('map-style-dropdown', 'value'),
    Input('map-nb_species-vdl', 'clickData'),
    State('map-nb_species-vdl', 'relayoutData')
)
def update_dashboard(date_range, map_column_selected, map_style, clickData, relayoutData):
    if None in date_range:
        raise PreventUpdate

    start_date = pd.to_datetime(date_range[0]).date()
    end_date = pd.to_datetime(date_range[1]).date()

    filtered_observation_df = merged_observation_df[
        (merged_observation_df['date_obs'] >= start_date) &
        (merged_observation_df['date_obs'] <= end_date)
    ]

    if relayoutData and 'map.zoom' in relayoutData and 'map.center' in relayoutData:
        current_zoom = relayoutData['map.zoom']
        current_center = relayoutData['map.center']
    else:
        current_zoom = 4.8
        current_center = {'lat': filtered_observation_df['localisation_lat'].mean() + 0.5, 'lon': filtered_observation_df['localisation_long'].mean()}

    fig_map = create_map_observations(filtered_observation_df, map_column_selected, current_zoom, current_center, map_style, lang=lang, observation_clicked=None)
    hist1_nb_species = create_hist1_nb_species(filtered_observation_df, None, lang=lang)
    hist2_vdl = create_hist2_vdl(filtered_observation_df, None, lang=lang)

    if clickData is None:
        selected_adress = ''
        selected_adress_style = {'display': 'none'}

        return fig_map, selected_adress, selected_adress_style, hist1_nb_species, hist2_vdl, blank_fig, blank_fig, blank_fig, blank_fig, blank_fig

    lat_clicked = clickData['points'][0]['lat']
    lon_clicked = clickData['points'][0]['lon']

    observation_clicked = filtered_observation_df[
        (filtered_observation_df['localisation_lat'] == lat_clicked) &
        (filtered_observation_df['localisation_long'] == lon_clicked)
    ]

    if observation_clicked.empty:
        print('No observation found')

        selected_adress = ''
        selected_adress_style = {'display': 'none'}

        return (
            fig_map, selected_adress, selected_adress_style, hist1_nb_species, hist2_vdl, blank_fig, blank_fig, blank_fig, blank_fig, blank_fig
        )

    observation_clicked = observation_clicked.iloc[0]
    observation_id_clicked = observation_clicked['observation_id']
    nb_species_clicked = observation_clicked['nb_species']
    vdl_clicked = observation_clicked['VDL']
    deg_toxitolerance_clicked = observation_clicked['deg_toxitolerance']
    deg_acidity_clicked = observation_clicked['deg_acidity']
    deg_eutrophication_clicked = observation_clicked['deg_eutrophication']

    # Get the location name and address from the latitude and longitude
    selected_adress = get_address_from_lat_lon(
        observation_clicked['localisation_lat'], observation_clicked['localisation_long'], language=lang)

    if selected_adress:
        selected_adress_style = {'display': 'block'}
    else:
        selected_adress = ''
        selected_adress_style = {'display': 'none'}



    filtered_nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df[
        nb_lichen_per_lichen_id_df['observation_id'] == observation_id_clicked
    ]

    filtered_grouped_lichen_by_observation_and_thallus_df = grouped_lichen_by_observation_and_thallus_df[
        grouped_lichen_by_observation_and_thallus_df['observation_id'] == observation_id_clicked
    ]

    fig_map = create_map_observations(filtered_observation_df, map_column_selected, current_zoom, current_center, map_style, lang=lang, observation_clicked=observation_clicked)

    gauge_chart_toxitolerance = create_gauge_chart(deg_toxitolerance_clicked, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE, lang=lang)
    gauge_chart_acidity = create_gauge_chart(deg_acidity_clicked, intervals=[0, 25, 50, 75, 100], color_scale=POSITIVE_GAUGE_COLOR_PALETTE, lang=lang)
    gauge_chart_eutrophication = create_gauge_chart(deg_eutrophication_clicked, intervals=[0, 25, 50, 75, 100], color_scale=NEGATIVE_GAUGE_COLOR_PALETTE, lang=lang)

    hist1_nb_species = create_hist1_nb_species(filtered_observation_df, nb_species_clicked, lang=lang)
    hist2_vdl = create_hist2_vdl(filtered_observation_df, vdl_clicked, lang=lang)
    hist3_species = create_hist3(filtered_nb_lichen_per_lichen_id_df, lang=lang)
    pie_thallus = create_pie_thallus(filtered_grouped_lichen_by_observation_and_thallus_df, lang=lang)

    return fig_map, selected_adress, selected_adress_style, hist1_nb_species, hist2_vdl, gauge_chart_toxitolerance, gauge_chart_eutrophication, gauge_chart_acidity, hist3_species, pie_thallus


## Dashboard on species tab
# Define callback to update the bar chart based on selected species
@callback(
    Output(component_id='map-species_present', component_property='figure'),
    Output(component_id='hist4-species', component_property='figure'),
    Output(component_id='species-name', component_property='children'),
    Output(component_id='species-image', component_property='src'),
    Output(component_id='acid-badge', component_property='children'),
    Output(component_id='eutro-badge', component_property='children'),
    Output(component_id='toxitolerance-badge', component_property='children'),
    Output(component_id='species-thallus', component_property='children'),
    Output(component_id='species-rarity', component_property='children'),
    Input(component_id='species-dropdown', component_property='value'),
    Input('map-species-style-dropdown', 'value'),
    State('map-species_present', 'relayoutData')
)
def update_dashboard2(species_id_selected, map_style, relayoutData):
    if isinstance(species_id_selected, str):
        species_id_selected = int(species_id_selected)

    hist4_species = create_hist4(nb_lichen_per_species_df, species_id_selected, lang=lang)

    # Create a column indicating for each observation if the selected species is present or not
    observation_with_selected_species_col_df['selected_species_present'] = observation_df['observation_id'].isin(
        lichen_df.loc[lichen_df['species_id'] == species_id_selected, 'observation_id']
    )

    if relayoutData and 'mapbox.zoom' in relayoutData and 'mapbox.center' in relayoutData:
        current_zoom = relayoutData['mapbox.zoom']
        current_center = relayoutData['mapbox.center']
    else:
        current_zoom = 4.8
        current_center = {'lat': observation_with_selected_species_col_df['localisation_lat'].mean() + 0.5, 'lon': observation_with_selected_species_col_df['localisation_long'].mean()}

    fig_map = create_map_species_present(observation_with_selected_species_col_df, 'selected_species_present', current_zoom, current_center, map_style, lang=lang)

    # Filter on the selected species
    species_selected = merged_lichen_species_df[merged_lichen_species_df['species_id'] == species_id_selected].iloc[0]

    species_name = species_selected['name']
    species_img = species_selected['picture']
    species_img_path = os.path.join(lichen_img_dir, species_img)

    species_acidity = species_selected['pH']
    species_eutrophication = species_selected['eutrophication']
    species_toxitolerance = species_selected['poleotolerance']
    species_thallus = species_selected['thallus']
    species_rarity = species_selected['rarity']

    # Translate with the dictionary
    species_acidity = get_translation(species_acidity, lang)
    species_eutrophication = get_translation(species_eutrophication, lang)
    species_toxitolerance = get_translation(species_toxitolerance, lang)
    species_thallus = get_translation(species_thallus, lang)
    species_rarity = get_translation(species_rarity, lang)

    return fig_map, hist4_species, species_name, species_img_path, species_acidity, species_eutrophication, species_toxitolerance, species_thallus, species_rarity


# Reusable component for title and tooltip
def title_and_tooltip(title, tooltip_text):
    # Split the title into all words
    words = title.split()

     # Check if the last word ends with a parenthesis pattern
    if len(words) > 1 and words[-1].startswith("(") and words[-1].endswith(")"):
        # If the last word is in parentheses, keep it with the previous word
        main_text = ' '.join(words[:-2]) # All words except the last two
        last_word = ' '.join(words[-2:])   # Combine the last two words
    else:
        # Otherwise, split as usual
        if len(words) > 1:
            main_text = ' '.join(words[:-1])  # All words except the last one
            last_word = words[-1]             # Last word
        else:
            main_text = ''
            last_word = words[0]              # If only one word, set it as last_word

    return html.Div(
        children=[
            # Main part of the title (only if main_text is not empty)
            dmc.Title(main_text, order=4, pr='5px') if main_text else None,
            # Last word and tooltip grouped together
            dmc.Group(
                children=[
                    dmc.Title(last_word, order=4),
                    dmc.Tooltip(
                        children=DashIconify(
                            icon='material-symbols:info-outline',
                            height=15,
                        ),
                        label=tooltip_text,
                        withArrow=True,
                        position='top',
                        maw='50%',  # max width
                        # Wrap text on multiple lines
                            style={'white-space': 'normal',
                                   'word-wrap': 'break-word'},
                    ),
                ],
                align='center',
                gap=2,
            )
        ],
        style={'margin': 0, 'padding': 0,
               'display': 'flex', 'flex-wrap': 'wrap'}
    )

# Reusable component for gauge cards
def gauge_card(title, tooltip_text, graph_id, max_height='200px'):
    return dmc.Card(
        children=[
            title_and_tooltip(title, tooltip_text),
            dcc.Graph(
                id=graph_id,
                figure=blank_fig,
                style={
                    'height': '100px',
                    'width': '100%',
                },
                config={'displayModeBar': False},
            ),
        ],
        style={
            'display': 'flex',
            'flexDirection': 'column',
            'justifyContent': 'space-between',
            'flexGrow': 1,
            'maxHeight': max_height
        },
        **CARD_STYLE
    )

# Reusable component for histogram cards
def histogram_card(title, tooltip_text, graph_id, height='330px'):
    return dmc.Card(
        children=[
            title_and_tooltip(title, tooltip_text),
            dcc.Graph(
                id=graph_id,
                figure=blank_fig,
                style={'height': height},
                config={'displaylogo': False},
            ),
        ],
        **CARD_STYLE
    )

# Layout for the sites (observations)
sites_layout = html.Div(
    style=FLEX_COLUMNS_CONTAINER_STYLE,
    children=[
        # First column with map and gauge
        html.Div(
            style={'flex-grow': '1', 'flex-basis': '50%'},
            children=[
                dmc.Group(
                    [
                        DashIconify(icon='mdi:calendar', width=26, height=26),
                        dmc.DatePicker(
                            id='date-picker-range',
                            minDate=merged_observation_df['date_obs'].min(),
                            maxDate=datetime.now().date(),
                            type='range',
                            value=[
                                merged_observation_df['date_obs'].min(),
                                datetime.now().date(),
                            ],
                            valueFormat='DD/MM/YYYY',
                            w=170,
                        ),
                        dmc.Button(
                            id='reset-date-button',
                            children='✖',
                            variant='outline',
                            color='red',
                            size='xs',
                        ),
                        dmc.Badge(
                            id='selected-address-badge',
                            variant='light',
                            size='lg',
                            maw='940px',
                            style={'display': 'none'}  # Initially hidden
                        ),
                    ],
                    align='center',
                    gap='xs',
                    mb='xs',
                ),
                dmc.Card(
                    children=[
                        title_and_tooltip(
                            title=get_translation('map_title', lang),
                            tooltip_text=get_translation('map_tooltip', lang)
                        ),
                        dmc.SegmentedControl(
                            id='map-column-select',
                            value=list(MAP_COLOR_PALETTES.keys())[0],
                            data=[
                                {'label': get_translation(col, lang), 'value': col}
                                for col in ['nb_species_cat', 'VDL_cat', 'deg_toxitolerance_cat', 'deg_eutrophication_cat', 'deg_acidity_cat']
                            ],
                            transitionDuration=600,
                            transitionTimingFunction='ease-in-out',
                            mb='xs'
                        ),
                        html.Div(
                            children=[
                                dmc.Card(
                                    children=[
                                        dmc.Select(
                                            id='map-style-dropdown',
                                            value='streets',  # Default value
                                            data=[
                                                {'label': 'Streets',
                                                 'value': 'streets'},
                                                {'label': 'OpenStreetMap',
                                                 'value': 'open-street-map'},
                                                {'label': 'Satellite',
                                                 'value': 'satellite'},
                                                {'label': 'Satellite with streets',
                                                 'value': 'satellite-streets'},
                                                {'label': 'Dark',
                                                 'value': 'dark'},
                                            ],
                                            clearable=False,
                                            allowDeselect=False,
                                            searchable=False,
                                            style={
                                                'position': 'absolute',
                                                'top': '15px',
                                                'left': '15px',
                                                'zIndex': '1000',
                                                'width': '200px',
                                                'opacity': '0.8'
                                            }
                                        ),
                                        dcc.Graph(
                                            id='map-nb_species-vdl',
                                            figure=blank_fig,
                                            style={'height': '469px'},
                                            config={'displaylogo': False},
                                        ),
                                    ],
                                    **MAP_STYLE
                                ),
                            ],
                        ),
                    ],
                    **CARD_STYLE,
                    mb='md',
                ),
                dmc.Grid(
                    **GRID_STYLE,
                    children=[
                        dmc.GridCol(
                            gauge_card(
                                title=get_translation('toxitolerance_gauge_title', lang),
                                tooltip_text=get_translation('toxitolerance_gauge_tooltip', lang),
                                graph_id='gauge-chart-toxitolerance',
                            ),
                            span=4,
                            style={'display': 'flex',
                                   'flexDirection': 'column'}
                        ),
                        dmc.GridCol(
                            gauge_card(
                                title=get_translation('eutrophication_gauge_title', lang),
                                tooltip_text=get_translation('eutrophication_gauge_tooltip', lang),
                                graph_id='gauge-chart-eutrophication',
                            ),
                            span=4,
                            style={'display': 'flex',
                                   'flexDirection': 'column'}
                        ),
                        dmc.GridCol(
                            gauge_card(
                                title=get_translation('acidity_gauge_title', lang),
                                tooltip_text=get_translation('acidity_gauge_tooltip', lang),
                                graph_id='gauge-chart-acidity',
                            ),
                            span=4,
                            style={'display': 'flex',
                                   'flexDirection': 'column'}
                        ),
                    ],
                )
            ],
        ),
        # Second column with histograms
        html.Div(
            style={'flex-grow': '1', 'flex-basis': '50%'},
            children=[
                dmc.Grid(
                    **GRID_STYLE,
                    children=[
                        dmc.GridCol(
                            span=6,
                            children=[
                                histogram_card(
                                    title=get_translation('species_number_distribution_hist1_title', lang),
                                    tooltip_text=get_translation('species_number_distribution_hist1_tooltip', lang),
                                    graph_id='hist1-nb_species',
                                ),
                            ],
                        ),
                        dmc.GridCol(
                            span=6,
                            children=[
                                histogram_card(
                                    title=get_translation('vdl_distribution_hist2_title', lang),
                                    tooltip_text=get_translation('vdl_distribution_hist2_tooltip', lang),
                                    graph_id='hist2-vdl',
                                ),
                            ],
                        ),
                        dmc.GridCol(
                            span=7,
                            children=[
                                histogram_card(
                                    title=get_translation('species_distribution_hist3_title', lang),
                                    tooltip_text=get_translation('species_distribution_hist3_tooltip', lang),
                                    graph_id='hist3-species',
                                ),
                            ],
                        ),
                        dmc.GridCol(
                            span=5,
                            children=[
                                histogram_card(
                                    title=get_translation('thallus_pie_chart_title', lang),
                                    tooltip_text=get_translation('thallus_pie_chart_tooltip', lang),
                                    graph_id='pie-thallus',
                                ),
                            ],
                        ),
                    ],
                ),
            ],
        ),
    ],
)

urls = [
    'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-1.png',
    'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-2.png',
    'https://raw.githubusercontent.com/mantinedev/mantine/master/.demo/images/bg-3.png',
]

images = [dmc.Image(radius='sm', src=url) for url in urls]

species_card = dmc.Card(
    children=[
        dmc.CardSection(
            children=[
                dmc.Text(
                    id='species-name',
                    size='lg',
                    style={'fontStyle': 'italic', 'fontWeight': 'bold'},
                    ),
            ],
            withBorder=True,
            inheritPadding=True,
            py='xs',
        ),
        dmc.Text(
            children=[
                get_translation('species_description1', lang),
                ' ',
                dmc.Text(
                    id='species-thallus',
                    c='blue',
                    style={'display': 'inline'},
                ),
                ' ',
                get_translation('species_description2', lang),
                ' ',
                dmc.Text(
                    id='species-rarity',
                    c='blue',
                    style={'display': 'inline'},
                ),
                ' ',
                get_translation('species_description3', lang),
                '.',
            ],
            mt='sm',
            c='dimmed',
            size='sm',
        ),
        dmc.CardSection(
            dmc.Image(
                id='species-image',
                mt='sm',
                src=None,
                fallbackSrc='https://placehold.co/600x400?text=No%20image%20found',
            ),
        ),
        dmc.CardSection(
            children=[
                dmc.Stack(
                    [
                        dmc.Group(
                            [
                                get_translation('toxitolerance_badge', lang),
                                dmc.Badge(id='toxitolerance-badge', variant='light'),
                            ]
                        ),
                        dmc.Group(
                            [
                                get_translation('eutrophication_badge', lang),
                                dmc.Badge(id='eutro-badge', variant='light'),
                            ]
                        ),
                        dmc.Group(
                            [
                                get_translation('acidity_badge', lang),
                                dmc.Badge(id='acid-badge', variant='light'),
                            ]
                        ),
                    ],
                    align='left',
                    gap='md',
                ),
            ],
            inheritPadding=True,
            mt='sm',
            pb='md',
        ),
    ],
    withBorder=True,
    shadow='sm',
    radius='md',
    maw=300,
    miw=250,
)

# Layout for the 'Espèces' tab
species_layout = html.Div(
    children=[
        dmc.Select(
            id='species-dropdown',
            label=get_translation('species_dropdown_label', lang),
            description=get_translation('species_dropdown_description', lang),
            value=species_id_selected,
            data=species_options,
            clearable=False,
            allowDeselect=False,
            searchable=True,
            w=400,
        ),
        dmc.Space(h=10),
        html.Div(
            style=FLEX_COLUMNS_CONTAINER_STYLE,
            children=[
                html.Div(species_card),
                html.Div(
                    style={'flex-basis': '40%', 'flex-grow': '1'},
                    children=[
                        dmc.Card(
                            children=[
                                title_and_tooltip(
                                    title=get_translation('species_presence_map_title', lang),
                                    tooltip_text=get_translation('species_presence_map_tooltip', lang)
                                ),
                                dmc.Card(
                                    children=[
                                        dmc.Select(
                                            id='map-species-style-dropdown',
                                            value='streets',  # Default value
                                            data=[
                                                {'label': 'Streets',
                                                 'value': 'streets'},
                                                {'label': 'OpenStreetMap',
                                                 'value': 'open-street-map'},
                                                {'label': 'Satellite',
                                                 'value': 'satellite'},
                                                {'label': 'Satellite with streets',
                                                 'value': 'satellite-streets'},
                                                {'label': 'Dark',
                                                 'value': 'dark'},
                                            ],
                                            clearable=False,
                                            allowDeselect=False,
                                            searchable=False,
                                            style={
                                                'position': 'absolute',
                                                'top': '15px',
                                                'left': '15px',
                                                'zIndex': '1000',
                                                'width': '200px',
                                                'opacity': '0.8'
                                            }
                                        ),
                                        dcc.Graph(
                                            id='map-species_present',
                                            figure=blank_fig,
                                            config={
                                                'displaylogo': False,  # Remove plotly logo
                                            },
                                            style={'height': '578px'},
                                        ),
                                    ],
                                    **MAP_STYLE,
                                    mt='xs',
                                ),
                            ],
                            **CARD_STYLE,
                        ),
                    ],
                ),
                html.Div(
                    style={'flex-basis': '40%', 'flex-grow': '1'},
                    children=[
                        histogram_card(
                            title=get_translation('species_distribution_hist4_title', lang),
                            tooltip_text=get_translation('species_distribution_hist4_tooltip', lang),
                            graph_id='hist4-species',
                            height='590px',
                        ),
                    ],
                ),
            ],
        ),
    ],
)


# Toggle to switch between light and dark theme
theme_toggle = dmc.ActionIcon(
    [
        dmc.Paper(DashIconify(icon='radix-icons:sun', width=25),  darkHidden=True),
        dmc.Paper(DashIconify(icon='radix-icons:moon', width=25), lightHidden=True),
    ],
    variant='transparent',
    id='color-scheme-toggle',
    size='lg',
    style={
        'position': 'fixed',
        'top': '20px',
        'right': '26px',
        'zIndex': 1000,
    }
)


# Callback to switch between light and dark theme
@callback(
    Output('mantine-provider', 'forceColorScheme'),
    Input('color-scheme-toggle', 'n_clicks'),
    State('mantine-provider', 'forceColorScheme'),
    prevent_initial_call=True,
)
def switch_theme(_, theme):
    return 'dark' if (theme == 'light' or theme is None) else 'light'


# Theme for the app
dmc_theme = {
    'colors': {
            'myBlue': BASE_COLOR_PALETTE[::-1], # Reverse the color palette
        },
    'primaryColor': 'myBlue',
    'fontFamily': BODY_FONT_FAMILY,
    'defaultRadius': 'md', # Default radius for cards
}


# Initialize the Dash app
app = Dash(__name__,
           external_stylesheets=[
               dmc.styles.ALL,
               dmc.styles.DATES,
              'https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;600&display=swap'
           ],
           title=get_translation('app_title', lang),
    )

server = app.server # For Heroku deployment

dashboards_layout = dmc.Box(
    children=[
        dmc.Accordion(
            id='accordion',
            disableChevronRotation=True,
            chevronPosition='left',
            variant='contained',
            multiple=True,
            children=[
                dmc.AccordionItem(
                    children=[
                        dmc.AccordionControl(
                            [
                                dmc.Group(
                                    children=[
                                        DashIconify(
                                            icon='tabler:map-pin',
                                            height=25,
                                            color=BASE_COLOR_PALETTE[0],
                                        ),
                                        dmc.Tooltip(
                                            label=get_translation('observation_tab_tooltip', lang),
                                            position='right',
                                            withArrow=True,
                                            children=dmc.Title(
                                                get_translation('observation_tab_title', lang),
                                                order=3,
                                            ),
                                        ),
                                    ],
                                    align='center',
                                ),
                            ],
                        ),
                        dmc.AccordionPanel(sites_layout),
                    ],
                    value='sites',
                ),
                dmc.AccordionItem(
                    children=[
                        dmc.AccordionControl(
                            dmc.Group(
                                children=[
                                    DashIconify(
                                        icon='ph:plant',
                                        height=25,
                                        color=BASE_COLOR_PALETTE[0],
                                    ),
                                    dmc.Title(
                                        get_translation('species_tab_title', lang),
                                        order=3,
                                    ),
                                ],
                                align='bottom',
                            ),
                        ),
                        dmc.AccordionPanel(species_layout),
                    ],
                    value='species',
                ),
            ],
            # open both toggles by default
            value=['sites', 'species'],
        )
    ],
    style={'flex': 1, 'padding': '10px'},
)

# Define the main layout with toggle and accordion
app.layout = dmc.MantineProvider(
    id='mantine-provider',
    theme=dmc_theme,
    children=[
        dmc.Group(
            children=[
                dashboards_layout,
                theme_toggle,
            ],
            align='start',
        )
    ],
)


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
