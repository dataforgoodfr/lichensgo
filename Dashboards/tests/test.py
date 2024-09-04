import pandas as pd
import sys
from pathlib import Path
import streamlit as st

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology, get_lichen_frequency

session = get_session()

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

# print(grouped_df["ph"].unique())

# entrée id
my_input = 410
# Calcul du degrés d'artificialisation
def deg_artif(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    base_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['poleotolerance'] == 'resistant')]['freq'].sum()

    return round((base_freq / global_freq) * 100, 2)

# Calcul de la pollution acidé 
def pollution_acide(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    acid_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['ph'] == 'acidophilous')]['freq'].sum()

    return round((acid_freq / global_freq) * 100, 2)

def pollution_azote(my_input: int):
    global_freq = grouped_df[grouped_df['id']== my_input]['freq'].sum()
    azote_freq = grouped_df[(grouped_df['id'] == my_input) & (grouped_df['eutrophication'] == 'eutrophic')]['freq'].sum()

    return round((azote_freq / global_freq) * 100, 2)


print(grouped_df[grouped_df['id']== 414])