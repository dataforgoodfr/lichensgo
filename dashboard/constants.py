BODY_FONT_FAMILY = '"Source Sans Pro", sans-serif'
PLOTLY_FONT_COLOR = "#868e96" # Grey


# Generated with https://omatsuri.app/color-shades-generator
BASE_COLOR_PALETTE = [
    "#387CA6",
    "#4A86AB",
    "#608FAD",
    "#799AAF",
    "#90A7B5",
    "#A6B6BF",
    "#BDC6CC",
]

PASTEL_COLOR_PALETTE = [
    "#c3d7e4",
    "#c8dae5",
    "#cfdde6",
    "#d6e0e7",
    "#dde4e8",
    "#e4e9eb",
    "#ebedef",
]

# Color palette for negative gauge, from green to red
NEGATIVE_GAUGE_COLOR_PALETTE = [
        "rgba(34, 139, 34, 1)",
        "rgba(255, 215, 0, 1)",
        "rgba(255, 140, 0, 1)",
        "rgba(255, 69, 0, 1)"
    ]

# Color palette for positive gauge, from red to green
POSITIVE_GAUGE_COLOR_PALETTE = NEGATIVE_GAUGE_COLOR_PALETTE[::-1]

SQUARE_COLUMNS = [f'sq{i}' for i in range(1, 6)]

ORIENTATIONS_MAPPING = {
    "N": "Nord",
    "E": "Est",
    "S": "Sud",
    "O": "Ouest"
}

ORIENTATIONS = list(ORIENTATIONS_MAPPING.keys())

MAP_COLOR_PALETTES = {
    "nb_species_cat": {'<7': 'red', '7-10': 'orange', '11-14': 'yellow', '>14': 'green'},
    "VDL_cat": {'<25': 'red', '25-50': 'orange', '50-75': 'yellow', '>75': 'green'},
    "deg_acidity_cat": {'0-25%': 'red', '25-50%': 'orange', '50-75%': 'yellow', '75-100%': 'green'},
    "deg_eutrophication_cat":  {'0-25%': 'green', '25-50%': 'yellow', '50-75%': 'orange', '75-100%': 'red'},
    "deg_toxitolerance_cat": {'0-25%': 'green', '25-50%': 'yellow', '50-75%': 'orange', '75-100%': 'red'},
    "selected_species_present": {True: BASE_COLOR_PALETTE[0], False: BASE_COLOR_PALETTE[-1]},
}


# Constants for common styles
FLEX_COLUMNS_CONTAINER_STYLE = {"display": "flex", "gap": "16px"}
GRID_STYLE = {"gutter": "md", "align": "stretch"}
CARD_STYLE = {
    "pt":"xs",
    "pb": "cs",
    "shadow": "sm",
    "withBorder": True
    }

MAP_STYLE = {
    "withBorder": True,
    "p": 0,
}


# Define the plotly style for hover labels
PLOTLY_HOVER_STYLE = {
        "font": dict(
            family=BODY_FONT_FAMILY,
        )
}

# Define the plotly layout for all plots
PLOTLY_LAYOUT = {
    "font": dict(family=BODY_FONT_FAMILY,
                 color="grey",
                 #color=PLOTLY_FONT_COLOR
                 ),
    "template": "plotly_white",
    "margin": dict(l=0, r=0, t=10, b=10),
    "barcornerradius": "30%",
    "hoverlabel": PLOTLY_HOVER_STYLE,
    "plot_bgcolor": "rgba(0, 0, 0, 0)",  # Transparent plot background
    "paper_bgcolor": "rgba(0, 0, 0, 0)",  # Transparent paper background
}
