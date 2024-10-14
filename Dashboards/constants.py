from utils.css_reader import get_css_properties

# Constants for color palettes, font families, etc.
BASE_COLOR_PALETTE = [
    "#387CA6",
    "#1C6C8C",
    "#3887A6",
    "#ADCCD9",
    "#F2F2F2"
]

PASTEL_COLOR_PALETTE = [
    '#c3d7e4',
    '#bad2dc',
    '#c3dbe4',
    '#e6eff3',
    '#fbfbfb'
]

ORIENTATIONS_MAPPING = {
    "N": "Nord",
    "E": "Est",
    "S": "Sud",
    "O": "Ouest"
}

ORIENTATIONS = list(ORIENTATIONS_MAPPING.keys())

SQUARE_COLUMNS = ['sq1', 'sq2', 'sq3', 'sq4', 'sq5']

BODY_STYLE = get_css_properties("body")
BODY_FONT_FAMILY = BODY_STYLE.get("font-family", "Arial")
BODY_FONT_COLOR = BODY_STYLE.get("color", "grey")

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
        color=BODY_FONT_COLOR
    ),
    "template": "plotly_white",
    "margin": dict(l=10, r=10, t=10, b=10),
    "barcornerradius":"30%",
    "hoverlabel": PLOTLY_HOVER_STYLE
}
