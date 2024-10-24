import sys
from pathlib import Path
from dash import Dash, html, dcc, Output, Input
from my_data.datasets import get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_species, get_lichen_ecology
from my_data.computed_datasets import df_frequency
from dashboard.charts import create_gauge_chart

chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))

# Initialize Dash app
app = Dash(__name__)

# Load the dataset

lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_species_df = get_tree_species()
ecology_df = get_lichen_ecology()
grouped_df = df_frequency(lichen_df, lichen_species_df, observation_df, table_df, ecology_df)

# Calcul du degrés d'artificialisation
def calc_deg_artif(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    base_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['poleotolerance'] == 'resistant')]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)

# Calcul de la pollution acidé
def calc_pollution_acide(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    acid_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['ph'] == 'acidophilous')]['freq'].sum()

    return round((acid_freq / global_freq) * 100, 2)

# Calcul de la pollution azoté
def calc_pollution_azote(observation_id: int):
    global_freq = grouped_df[grouped_df['id']== observation_id]['freq'].sum()
    azote_freq = grouped_df[(grouped_df['id'] == observation_id) & (grouped_df['eutrophication'] == 'eutrophic')]['freq'].sum()

    return round((azote_freq / global_freq) * 100, 2)

# Define app layout with a hidden input
app.layout = html.Div([
    html.H1("Gauge bar Dash", style={'textAlign': 'center'}),
    dcc.Dropdown(grouped_df["id"].unique(), 419, id='dropdown-selection', style={'width': '50%', 'margin': 'auto'}),
    html.Div([
        dcc.Graph(id='graph-content1', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='graph-content2', style={'flex': '1', 'margin': '10px'}),
        dcc.Graph(id='graph-content3', style={'flex': '1', 'margin': '10px'})
    ], style={'display': 'flex', 'justify-content': 'space-around', 'width': '100%'})
])

# Define callback to update graph
@app.callback(
    [
        Output('graph-content1', 'figure'),
        Output('graph-content2', 'figure'),
        Output('graph-content3', 'figure')
    ],
    Input('dropdown-selection', 'value')
)

def update_gauge_charts(observation_id):
    deg_artif = calc_deg_artif(observation_id)
    pollution_acide = calc_pollution_acide(observation_id)
    pollution_azote = calc_pollution_azote(observation_id)

    fig1 = create_gauge_chart(deg_artif, "Degré d'artificialisation")
    fig2 = create_gauge_chart(pollution_acide, "Pollution acide")
    fig3 = create_gauge_chart(pollution_azote, "Pollution azoté")
    return fig1, fig2, fig3


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
