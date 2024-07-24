import pandas as pd
import sys
from pathlib import Path
import plotly
import plotly.express as px

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data

session = get_session()

# Récupération des datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()

# Affichage des datasets > test dataset
print("\nEnvironment Data")
print(environment_df.head())

print("\nLichen Data")
print(lichen_df.head())

print("\nLichen Species Data")
print(lichen_species_df.head())

### Histogram 4 with Plotly express bar: ###
# Espèces les plus observées par les observateurs Lichens GO

# group by species' type + add a column with the count occurence
df_grouped=(
    lichen_df
    .groupby("species_id", as_index=False)
    .agg(count_col=pd.NamedAgg(column="species_id", aggfunc="count"))
)

# concatenate dataframe "df_grouped" with the lichen species' names
df_grouped_species=pd.concat([df_grouped, lichen_species_df.loc[:,"name"]], axis=1)

# sort based on occurence 
# (note): update_xaxes(categoryorder="total descending") does not work
df_grouped_species=(
    df_grouped_species
    .sort_values(by="count_col", ascending=False, ignore_index=True)
)

print("df_grouped_species:\n")
print(df_grouped_species)

### Design bar plot ###

# TODO: the user's selection should be interactive -> to modify in the final Dash
user_selection_species=lichen_species_df.loc[30,"name"] 
print("Species selected by the user:",user_selection_species)

# index in "df_grouped_species" corresponding to the selected species
idx=df_grouped_species["name"].loc[lambda x: x==user_selection_species].index
#print("idx is:",idx)

# adjust the color based on the selected species
color_discrete_sequence=['#ec7c34']*len(df_grouped_species)
color_discrete_sequence[int(idx[0])]='#609cd4'

hist4=px.bar(
    df_grouped_species, 
    x="count_col", 
    y="name",
    labels={
            "count_col": "count",
            "name": "species name"},
    orientation="h",
    color="name",
    color_discrete_sequence=color_discrete_sequence,
    # width=1500,
    # height=800,
    title="Espèces les plus observées par les observateurs Lichens GO"
)

# remove the legend
hist4.update(layout_showlegend=False)

hist4.show()