from dash import Dash, html, dcc, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random 
import numpy as np

###################################################
############# Préparation des données #############
###################################################

# Pour le moment : données fictives pour le test

df = pd.read_csv('data/d4g.csv')
df['speciesId'] = df['speciesId'].astype(int).astype(str)
df.drop('Unnamed: 0', axis=1, inplace=True)

# Génération de dates aléatoires pour le test
df['date'] = df['year'].apply(lambda x: pd.Timestamp(year=x, month=random.randint(1,12), day=random.randint(1,28)))
df['nb_especes'] = [random.choice(['<7', '7-10', '11-14', '>14']) for _ in range(len(df))]

# Dictionnaire de couleurs à utiliser pour la carte
color_dict = {'<7': 'red', '7-10': 'orange', '11-14': 'yellow', '>14': 'green'}

# Liste des colonnes disponibles pour la sélection
columns = ['nb_especes', 'speciesId']

# Création du nombre d'espèce par site
df_hist = df[['lat', 'lon']].drop_duplicates().copy()
df_hist['Nb_species'] = np.random.normal(10, 3, len(df_hist)).astype(int)

###################################################
################## Application ####################
###################################################

app = Dash(__name__)
app.title = "Lichens GO"

app.layout = html.Div([
    html.H1("Lichens GO", style={'textAlign': 'center'}),

    html.Div("Sélectionnez un site sur la carte pour comprendre ce qu'il s'y passe.", style={'textAlign': 'center'}),

    # Widget pour sélectionner la période de dates à afficher
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=df['date'].min(),
        max_date_allowed=df['date'].max(),
        initial_visible_month=df['date'].max(),
        start_date=df['date'].min(),
        end_date=df['date'].max(),
        display_format='DD/MM/YYYY',
        clearable=False,
        style={'margin': '10px auto', 'display': 'block'}
    ),

    # Menu déroulant pour sélectionner la variable à afficher
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in columns],
        value='nb_especes',  # Valeur par défaut
        style={'width': '50%', 'margin': '10px auto'},
        clearable=False,
    ),

    # Div pour organiser la carte et l'histogramme côte à côte
    html.Div([
        # Carte
        dcc.Graph(
            id='species-map',
            style={'height': '800px', 'width': '48%', 'display': 'inline-block'} 
        ),

        # Histogramme
        dcc.Graph(
            id='species-hist',
            style={'height': '800px', 'width': '48%', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex', 'justify-content': 'space-around'})
])

# Callback pour mettre à jour la carte et l'histogramme en fonction des dates sélectionnées
@app.callback(
    Output('species-map', 'figure'),
    Output('species-hist', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('column-dropdown', 'value'),
    Input('species-map', 'clickData')
)
def update_map(start_date, end_date, selected_column, clickData):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # Filtrer le dataframe pour correspondre aux dates sélectionnées
    filtered_df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Afficher la carte
    fig_map = px.scatter_mapbox(filtered_df, lat='lat', lon='lon', color=selected_column, 
                                hover_name=selected_column, hover_data=['date'],
                                mapbox_style="open-street-map",
                                color_discrete_map=color_dict) 
    fig_map.update_layout(mapbox_zoom=4.8, mapbox_center={"lat": filtered_df['lat'].mean() + 0.5, "lon": filtered_df['lon'].mean()})

    # Afficher l'histogramme
    fig_hist = px.histogram(df_hist, x='Nb_species', nbins=20, title='Distribution of Nb_species')

    # Si un point sur la carte est cliqué, ajouter une ligne pointillée rouge sur l'histogramme
    if clickData is not None:
        lat_clicked = clickData['points'][0]['lat']
        lon_clicked = clickData['points'][0]['lon']
        nb_species_clicked = df_hist[(df_hist['lat'] == lat_clicked) & (df_hist['lon'] == lon_clicked)]['Nb_species'].values[0]

        fig_hist.add_shape(
            go.layout.Shape(
                type="line",
                x0=nb_species_clicked, x1=nb_species_clicked,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color="red", width=2, dash="dot")
            )
        )

    return fig_map, fig_hist

# Pour lancer l'application, exécutez le script avec la commande python demo_dash.py
if __name__ == '__main__':
    app.run_server(debug=True)
