import pandas as pd
from db_connect import get_session
from datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species

session = get_session()

# Récupération des datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()
tree_species_df = get_tree_species()

# Affichage des datasets > test dataset
print("\nEnvironment Data")
print(environment_df.head())

print("\nLichen Data")
print(lichen_df.head())

print("\nLichen Species Data")
print(lichen_species_df.head())

print("\nObservation Data")
print(observation_df.head())

print("\nTable Data")
print(table_df.head())

print("\nTree Data")
print(tree_df.head())

print("\nTree Species Data")
print(tree_species_df.head())
