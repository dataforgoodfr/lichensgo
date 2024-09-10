from dash import Dash, html, dcc, Output, Input, dash_table, callback
import plotly.express as px
import pandas as pd
import sys
from pathlib import Path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology
from my_data.computed_datasets import df_frequency

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4 
# Dash version
# run with : python Dashboards/download.py

# Initialize Dash app
app = Dash(__name__)

# Get all data from the dataset
df_frequency = df_frequency()

# df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

# print(df.to_dict('records'))
# print([{"name": i, "id": i} for i in df.columns])

# Define app layout with a hidden input
app.layout = html.Div([
    html.H1("POC Table Download", style={'textAlign': 'center'}),
    html.P("Permettre le téléchargement des éléments à partir d'une table depuis la base de données", style={'textAlign': 'center'}),
    html.Div([
        html.Button(
            "Export CSV", 
            id="btn_csv", 
            style={
                # Injection de css pour le bouton
                'backgroundColor': '#4CAF50', 
                'color': 'white', 
                'padding': '10px 20px', 
                'border': 'none', 
                'borderRadius': '5px', 
                'cursor': 'pointer', 
                'fontSize': '16px',
                'marginBottom': '.5rem'
            }
        ),
        dcc.Download(id="download-dataframe-csv"),
    ],
    style={'display': 'flex', 'justifyContent': 'center'}),
    html.Div(
        dash_table.DataTable(
            df_frequency.to_dict('records'), 
            [{"name": i, "id": i} for i in df_frequency.columns],
            style_table={
                'height': 400,
                'width': '100%',
                'overflowX': 'auto', 
                'maxWidth': '100%',  
                'margin': '10 auto'  
            },
            style_data={
                'width': '150px', 
                'minWidth': '150px', 
                'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            }
        ),
        style={'display': 'flex', 'justifyContent': 'center'}
    )
])

@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(df_frequency.to_csv, "lichengo_frequency.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)