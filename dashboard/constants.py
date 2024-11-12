from collections import OrderedDict

BODY_FONT_FAMILY = "'Source Sans Pro', sans-serif"
PLOTLY_FONT_COLOR = '#868e96' # Grey


# Generated with https://omatsuri.app/color-shades-generator
BASE_COLOR_PALETTE = [
    '#387CA6',
    '#4A86AB',
    '#608FAD',
    '#799AAF',
    '#90A7B5',
    '#A6B6BF',
    '#BDC6CC',
]

PASTEL_COLOR_PALETTE = [
    '#c3d7e4',
    '#c8dae5',
    '#cfdde6',
    '#d6e0e7',
    '#dde4e8',
    '#e4e9eb',
    '#ebedef',
]

GREEN = 'rgba(34, 139, 34, 1)'
YELLOW = 'rgba(255, 215, 0, 1)'
ORANGE = 'rgba(255, 165, 0, 1)'
RED = 'rgba(255, 0, 0, 1)'

# Color palette for negative gauge, from green to red
NEGATIVE_GAUGE_COLOR_PALETTE = [GREEN, YELLOW, ORANGE, RED]

# Color palette for positive gauge, from red to green
POSITIVE_GAUGE_COLOR_PALETTE = NEGATIVE_GAUGE_COLOR_PALETTE[::-1]

SQUARE_COLUMNS = [f'sq{i}' for i in range(1, 6)]

ORIENTATIONS = ['N', 'E', 'S', 'O']

MAP_COLOR_PALETTES = {
    'nb_species_cat': OrderedDict([('< 7', RED), ('7 - 10', ORANGE), ('11 - 14', YELLOW), ('> 14', GREEN)]),
    'VDL_cat': OrderedDict([('< 25', RED), ('25 - 50', ORANGE), ('50 - 75', YELLOW), ('> 75', GREEN)]),
    'deg_acidity_cat': OrderedDict([('0 - 25%', RED), ('25 - 50%', ORANGE), ('50 - 75%', YELLOW), ('75 - 100%', GREEN)]),
    'deg_eutrophication_cat': OrderedDict([('0 - 25%', GREEN), ('25 - 50%', YELLOW), ('50 - 75%', ORANGE), ('75 - 100%', RED)]),
    'deg_toxitolerance_cat': OrderedDict([('0 - 25%', GREEN), ('25 - 50%', YELLOW), ('50 - 75%', ORANGE), ('75 - 100%', RED)]),
    'selected_species_present': OrderedDict([(True, BASE_COLOR_PALETTE[0]), (False, RED)]),
}


# Constants for common styles
FLEX_COLUMNS_CONTAINER_STYLE = {'display': 'flex', 'gap': '16px'}
GRID_STYLE = {'gutter': 'md', 'align': 'stretch'}
CARD_STYLE = {
    'pt':'xs',
    'pb': 'cs',
    'shadow': 'sm',
    'withBorder': True
    }

MAP_STYLE = {
    'withBorder': True,
    'p': 0,
}


# Define the plotly style for hover labels
PLOTLY_HOVER_STYLE = {
        'font': dict(
            family=BODY_FONT_FAMILY,
        )
}

# Define the plotly layout for all plots
PLOTLY_LAYOUT = {
    'font': dict(family=BODY_FONT_FAMILY,
                 color='grey',
                 #color=PLOTLY_FONT_COLOR
                 ),
    'template': 'plotly_white',
    'margin': dict(l=0, r=0, t=10, b=10),
    'barcornerradius': '30%',
    'hoverlabel': PLOTLY_HOVER_STYLE,
    'plot_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent plot background
    'paper_bgcolor': 'rgba(0, 0, 0, 0)',  # Transparent paper background
}
