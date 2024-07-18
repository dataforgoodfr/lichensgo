import pandas as pd
import sys
from pathlib import Path
import plotly
import plotly.express as px

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology

session = get_session()

# Récupération des datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
# observation_df = get_observation_data()
# table_df = get_table_data()
# tree_df = get_tree_data()
# tree_species_df = get_tree_species()
# lichen_ecology_df = get_lichen_ecology()

# Affichage des datasets > test dataset
print("\nEnvironment Data")
print(environment_df.head())

print("\nLichen Data")
print(lichen_df.head())

print("\nLichen Species Data")
print(lichen_species_df.head())

# Histogram 4 with plotly express histogram: 
# Espèces les plus observées par les observateurs Lichens GO

# ISSUES : 
# - update_xaxes(categoryorder="total descending") does not work 

hist4 = px.histogram(
    lichen_df, 
    x="species_id",
    title="Espèces les plus observées par les observateurs Lichens GO",
    labels={'species_id':"species"},
)

hist4.update_xaxes(categoryorder="total descending")
hist4.show()
