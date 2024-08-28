import streamlit as st
import pandas as pd
import my_data.datasets as df
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
import sys

chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology

# Source : https://discuss.streamlit.io/t/develop-a-dashboard-app-with-streamlit-using-plotly/37148/4
# run with : streamlit run Dashboards/demo_streamlit.py

# Récupération des datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()
tree_species_df = get_tree_species()
ecology_df = get_lichen_ecology()

# Fonction pour calculer la fréquence des valeurs E, N, O, S
def calculate_frequency(column):
    return column.apply(lambda x: sum(1 for char in x if char in ['E', 'N', 'O', 'S']))

# Calculer la fréquence
table_df['freq'] = (
    table_df['sq1'].apply(lambda x: len(x) if pd.notnull(x).any() else 0)  +
    table_df['sq2'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq3'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq4'].apply(lambda x: len(x) if pd.notnull(x).any() else 0) +
    table_df['sq5'].apply(lambda x: len(x) if pd.notnull(x).any() else 0)
)

# Joindre table avec lichen et observation
merged_df = table_df.merge(lichen_df, left_on='lichen_id', right_on='id', suffixes=('', '_l'))
merged_df = merged_df.merge(lichen_species_df, left_on='species_id', right_on='id', suffixes=('', '_ls'))
merged_df = merged_df.merge(observation_df, left_on='observation_id', right_on='id', suffixes=('', '_o'))

# Grouper par 'species' et 'observation_id' et additionner les fréquences
grouped_df = merged_df.groupby(['name', 'observation_id'])['freq'].sum().reset_index()

# Regrouper les deux tables afficher les données écologiques
grouped_df = grouped_df.merge(ecology_df, left_on='name', right_on='cleaned_taxon', suffixes=('', '_e'))

# ajustement des noms finaux
grouped_df = grouped_df[['observation_id', 'name', 'freq','pH','eutrophication', 'poleotolerance']]
grouped_df = grouped_df.rename(
    columns={
        'observation_id': 'id', 
        'name': 'lichen', 
        'freq': 'freq',
        'pH': 'ph',
        'eutrophication': 'eutrophication', 
        'poleotolerance': 'poleotolerance'
        })

# Calcul du degrés d'artificialisation
def deg_artif(my_input: int, species: str):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    base_freq = grouped_df[(grouped_df['id']== my_input) & (grouped_df['lichen'] == species)]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)



# Sélection du site 
id_site = st.selectbox(
    "Sur quel site voulez-vous ?",
    grouped_df["id"].unique(),
    index=None,
    placeholder="site n°",
)

# Sélection des espèces 
species_name = st.selectbox(
    "Sur quel espèce voulez-vous ?",
    grouped_df["lichen"].unique(),
    index=None,
    placeholder="Je sélectionne l'espèce...",
)

# Affichage des éléments
if id_site and species_name != None:
    pass
else:
    id_site = 465
    species_name = 'Amandinea punctata/Lecidella elaeochroma'

artificialisation_proportions = deg_artif(id_site, species_name)

# # Dataviz charts
st.write("# Gauge bar")
fig1 = go.Figure(go.Indicator(
    domain = {'x': [0, 1], 'y': [0, 1]},
    value = artificialisation_proportions,
    mode = "gauge+number",
    title = {'text': "Degré d'artificialisation"},
    gauge = {'axis': {'range': [0, 100], 'dtick': 25},
             'bar': {'color': "#000000"},
             'steps' : [
                #  {'range': [0, 25], 'color': "#E3D7FF"},
                #  {'range': [25, 50], 'color': "#AFA2FF"},
                #  {'range': [50, 75], 'color': "#7A89C2"},
                #  {'range': [75, 100], 'color': "#72788D"}
                 {'range': [0, 25], 'color': "green"},
                 {'range': [25, 50], 'color': "yellow"},
                 {'range': [50, 75], 'color': "orange"},
                 {'range': [75, 100], 'color': "red"}
                 ],
             'threshold' : {'line': {'color': "#000000", 'width': 4}, 'thickness': 0.75, 'value': artificialisation_proportions}
             }))
st.plotly_chart(fig1)