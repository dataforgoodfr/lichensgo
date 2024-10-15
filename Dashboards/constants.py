BODY_FONT_FAMILY = '"Source Sans Pro", sans-serif'
PLOTLY_FONT_COLOR = "#495057" # Grey

# Constants for color palettes, font families, etc.
# BASE_COLOR_PALETTE = [
#     "#387CA6",
#     "#1C6C8C",
#     "#3887A6",
#     "#ADCCD9",
#     "#F2F2F2"
# ]


# Generated with https://omatsuri.app/color-shades-generator

BASE_COLOR_PALETTE = [
    # "#333D43",
    # "#37444C",
    # "#3A4C58",
    # "#3C5665",
    # "#3D6176",
    # "#3C6D8C",
    "#387CA6",
    "#4A86AB",
    "#608FAD",
    "#799AAF",
    "#90A7B5",
    "#A6B6BF",
    "#BDC6CC",
]

PASTEL_COLOR_PALETTE = [
    # "#c1c4c6",
    # "#c3c6c9",
    # "#c3c9cc",
    # "#c4ccd0",
    # "#c4cfd5",
    # "#c4d3dc",
    "#c3d7e4",
    "#c8dae5",
    "#cfdde6",
    "#d6e0e7",
    "#dde4e8",
    "#e4e9eb",
    "#ebedef",
]


SQUARE_COLUMNS = [f'sq{i}' for i in range(1, 6)]

ORIENTATIONS_MAPPING = {
    "N": "Nord",
    "E": "Est",
    "S": "Sud",
    "O": "Ouest"
}

ORIENTATIONS = list(ORIENTATIONS_MAPPING.keys())

MAP_SETTINGS = {
    "nb_species_cat": {
        "title": "Nombre d'espèces",
        "color_map": {'<7': 'red', '7-10': 'orange', '11-14': 'yellow', '>14': 'green'}
    },
    "VDL_cat": {
        "title": "VDL",
        "color_map": {'<5': 'red', '5-10': 'orange', '10-15': 'yellow', '>15': 'green'}
    }
}

# Define the plotly style for hover labels
PLOTLY_HOVER_STYLE = {
        "font": dict(
            family=BODY_FONT_FAMILY,
        )
}

# Define the plotly layout for all plots
PLOTLY_LAYOUT = {
    "font": dict(
        family=BODY_FONT_FAMILY,
        color=PLOTLY_FONT_COLOR
    ),
    "template": "plotly_white",
    "margin": dict(l=0, r=0
                   , t=10, b=10),
    "barcornerradius":"30%",
    "hoverlabel": PLOTLY_HOVER_STYLE,
    "plot_bgcolor": "rgba(0, 0, 0, 0)",  # Transparent plot background
    "paper_bgcolor": "rgba(0, 0, 0, 0)", # Transparent paper background
}
