from dash import Dash, html, dcc, Output, Input
from dash.dependencies import State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random 
import numpy as np
import my_data.datasets as df

###################################################
############# Préparation des données #############
###################################################


observations = df.get_observation_data()
lichen_observes = df.get_lichen_data()
lichen_observes = lichen_observes['observation_id'].value_counts().to_frame()

observations = observations.merge(lichen_observes, how = 'left', left_on = 'id', right_on = 'observation_id')

observations["number_species"] = pd.cut(observations["count"], bins = [0, 6, 11, 15,999], labels = ["<7", "7-10", "11-14", ">14"])

# Dictionnaire de couleurs à utiliser pour la carte
color_dict = {'<7': 'red', '7-10': 'orange', '11-14': 'yellow', '>14': 'green'}

###################################################
################ Calcul de la VDL #################
###################################################
# Calcul de la Valeur de Diversité Lichénique (VDL) par observation

# Chargement des données nécessaires
tree_data = df.get_tree_data()
table_data = df.get_table_data()
cols = ['observation_id', 'id_tree']

# Jointure des tables
observations_table = observations.merge(tree_data, left_on='id', right_on = 'observation_id', how = 'left', suffixes=['_obs', '_tree'])[cols]
observations_table = observations_table.merge(table_data, left_on='id_tree', right_on = 'tree_id', how = 'left')

# Calcul du nombre d'espèce observé sur chaque carré
for i in range(1,6):
    observations_table[f'sq{i}'] = observations_table[f'sq{i}'].apply(lambda x : len(x))

cols = ['observation_id'] + [f'sq{i}' for i in range(1,6)]
observations_table = observations_table[cols]

# Calcul de la VDL
observations_table = observations_table.groupby('observation_id').sum()
observations_table['sum_nb_observations'] = observations_table.sum(axis=1)

observations_table['VDL_value'] = observations_table['sum_nb_observations']/15 # /5 pour le nombre de carrés par grille, /3 pour le nombre d'arbre par observation
observations_table["VDL"] = pd.cut(observations_table["VDL_value"], bins = [0, 5, 10, 15,999], labels = ["<5", "5-10", "10-15", ">15"])

observations = observations.merge(observations_table, left_on = 'id', right_on = 'observation_id', how = 'left')

# Dictionnaire de couleurs pour la VDL (A CONFIRMER AVEC HUGO)
color_dict_vdl = {'<5': 'red', '5-10': 'orange', '10-15': 'yellow', '>15': 'green'}


###################################################
################## Application ####################
###################################################

app = Dash(__name__)
app.title = "Lichens GO"

# Liste des variables disponibles pour afficher sur la carte
columns = ['number_species', 'VDL'] 

# Dictionnaire de couleurs à utiliser pour chaque variable
color_palette = {
    'number_species': color_dict,
    'VDL': color_dict_vdl,
}

app.layout = html.Div([
    html.H1("Lichens GO", style={'textAlign': 'center'}),

    html.Div("Sélectionnez un site sur la carte pour comprendre ce qu'il s'y passe.", style={'textAlign': 'center'}),

    # Widget pour sélectionner la période de dates à afficher
    dcc.DatePickerRange(
        id='date-picker-range',
        min_date_allowed=observations['date_obs'].min(),
        max_date_allowed=observations['date_obs'].max(),
        initial_visible_month=observations['date_obs'].max(),
        start_date=observations['date_obs'].min(),
        end_date=observations['date_obs'].max(),
        display_format='DD/MM/YYYY',
        clearable=False,
        style={'margin': '10px auto', 'display': 'block'}
    ),

    # Menu déroulant pour sélectionner la variable à afficher
    dcc.Dropdown(
        id='column-dropdown',
        options=[{'label': col, 'value': col} for col in columns],
        value='number_species',  # Valeur par défaut
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

        dcc.Graph(
            id='vdl-hist',
            style={'height': '800px', 'width': '48%', 'display': 'inline-block'}
        ),
    ], style={'display': 'flex', 'justify-content': 'space-around'})
])

# Callback pour mettre à jour la carte et l'histogramme en fonction des dates sélectionnées
@app.callback(
    Output('species-map', 'figure'),
    Output('species-hist', 'figure'),
    Output('vdl-hist', 'figure'),

    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('column-dropdown', 'value'),
    Input('species-map', 'clickData'),

    State('species-map', 'relayoutData')  # État actuel du zoom et de la position de la carte
    
)

def update_map(start_date, end_date, selected_column, clickData, relayoutData):
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()
    
    # Filtrer le dataframe pour correspondre aux dates sélectionnées
    filtered_df = observations[(observations['date_obs'] >= start_date) & (observations['date_obs'] <= end_date)]

    # Si le zoom et la position actuels sont disponibles, les utiliser, sinon définir des valeurs par défaut
    if relayoutData and "mapbox.zoom" in relayoutData and "mapbox.center" in relayoutData:
        current_zoom = relayoutData["mapbox.zoom"]
        current_center = relayoutData["mapbox.center"]
    else:
        current_zoom = 4.8  # Valeur par défaut du zoom
        current_center = {"lat": filtered_df['localisation_lat'].mean() + 0.5, "lon": filtered_df['localisation_long'].mean()}


    # Afficher la carte
    fig_map = px.scatter_mapbox(filtered_df, lat='localisation_lat', lon='localisation_long', 
                                color=selected_column, 
                                hover_name='date_obs', hover_data=['localisation_lat', 'localisation_long'],
                                mapbox_style="open-street-map",
                                color_discrete_map=color_palette[selected_column],) 
    
    fig_map.update_layout(mapbox_zoom=current_zoom, mapbox_center=current_center)


    # Afficher les histogrammes
    fig_hist_nb_species = px.histogram(filtered_df, x='count', nbins=20, title='Distribution du nombre d\'espèces par site')

    fig_hist_vdl = px.histogram(filtered_df, x='VDL_value', nbins=20, title='Distribution de la Valeur de Diversité Lichénique par site')

    # Si un point sur la carte est cliqué, ajouter une ligne pointillée rouge sur les histogrammes
    if clickData is not None:
        lat_clicked = clickData['points'][0]['lat']
        lon_clicked = clickData['points'][0]['lon']
        nb_species_clicked = filtered_df[(filtered_df['localisation_lat'] == lat_clicked) & (filtered_df['localisation_long'] == lon_clicked)]['count'].values[0]
        vdl_clicked = filtered_df[(filtered_df['localisation_lat'] == lat_clicked) & (filtered_df['localisation_long'] == lon_clicked)]['VDL_value'].values[0]


        fig_hist_nb_species.add_shape(
            go.layout.Shape(
                type="line",
                x0=nb_species_clicked, x1=nb_species_clicked,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color="red", width=2, dash="dot")
            )
        )

        fig_hist_vdl.add_shape(
            go.layout.Shape(
                type="line",
                x0=vdl_clicked, x1=vdl_clicked,
                y0=0, y1=1,
                xref='x', yref='paper',
                line=dict(color="red", width=2, dash="dot")
            )
        )

    return fig_map, fig_hist_nb_species, fig_hist_vdl

# Pour lancer l'application, exécutez le script avec la commande python demo_dash.py
if __name__ == '__main__':
    app.run_server(debug=True)
