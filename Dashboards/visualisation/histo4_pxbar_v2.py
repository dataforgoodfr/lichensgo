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

# Histogram 4 with Plotly express bar:
# Espèces les plus observées par les observateurs Lichens GO

# group by species' type and count occurence
df_grouped=(
    lichen_df
    .groupby("species_id", as_index=False)
    .agg(count_col=pd.NamedAgg(column="species_id", aggfunc="count"))
)

print("df_grouped:\n")
print(df_grouped)

# concatenate dataframe with lichen species' name
df_grouped_species=pd.concat([df_grouped, lichen_species_df.loc[:,"name"]], axis=1)

# sort based on occurence 
# (note): update_xaxes(categoryorder="total descending") does not work
df_grouped_species=(
    df_grouped_species
    .sort_values(by="count_col", ascending=False, ignore_index=True)
)

print("df_grouped_species:\n")
print(df_grouped_species)

# design bar plot

# adjust the color based on User's selection
color_discrete_sequence = ['#ec7c34']*len(df_grouped_species)
color_discrete_sequence[10] = '#609cd4'

hist4=px.bar(
    df_grouped_species, 
    x="count_col", 
    y="name",
    orientation="h",
    labels={
            "count_col": "count",
            "name": "species name"},
    color="name",
    color_discrete_sequence=color_discrete_sequence,
    title="Espèces les plus observées par les observateurs Lichens GO"
)

hist4.show()