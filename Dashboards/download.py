from dash import Dash, html, dcc, Output, Input, dash_table, callback
import pandas as pd
import sys
from pathlib import Path
from my_data.data_download import get_download_data

# Initialize Dash app
app = Dash(__name__)

# Get data
data = get_download_data()

# Define app layout with a hidden input
app.layout = html.Div([
    html.H1("POC Table Download", style={'textAlign': 'center'}),
    html.P("Permettre le téléchargement des éléments à partir d'une table depuis la base de données", style={'textAlign': 'center'}),
    html.Div([
        html.Button(
            "Export CSV", 
            id="btn_csv", 
            style={
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
            data.to_dict('records'), 
            [{"name": i, "id": i} for i in data.columns],
            style_table={
                'height': 500,
                'width': '280%',
                'overflowX': 'auto', 
                'maxWidth': '280%',  
                'margin': '10px auto'
            },
            style_data={
                'width': '350px', 
                'minWidth': '150px', 
                'maxWidth': '150px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
            },
            fixed_columns={'headers': True, 'data': 1},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        ),
        style={
            'display': 'flex', 
            # 'justifyContent': 'center', 
            'width': '100%'
        }
    )
])

@callback(
    Output("download-dataframe-csv", "data"),
    Input("btn_csv", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    return dcc.send_data_frame(data.to_csv, "lichengo_frequency.csv")

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)