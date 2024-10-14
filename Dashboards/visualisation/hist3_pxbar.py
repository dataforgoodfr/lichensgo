import pandas as pd
import sys
import plotly.express as px
from pathlib import Path
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_tree_data, get_observation_data, get_table_data

# Ajoute le dossier parent à sys.path
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))

session = get_session()

# Récupération des datasets
environment_df = get_environment_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
observation_df = get_observation_data()
table_df = get_table_data()
tree_df = get_tree_data()

# Affichage des datasets
# print("\nEnvironment Data")
# print(environment_df.head())

# print("\nLichen Data")
# print(lichen_df.head())

# print("\nLichen Species Data")
# print(lichen_species_df.head())

# print("\nObservation Data")
# print(observation_df.head())

print("\nTable Data")
print(table_df.head())

# print("\nTree Data")
# print(tree_df.head())

# Select one site based on latitude, longitude, date et user id
# Filtering with query method
user = 2
date = "2022-01-20"
lat = 45.822677
long = 1.242670
obs = 500

site = observation_df.query("user_id == @user"
                          and "date_obs == @date"
                          and "localisation_lat == @lat"
                          and "localisation_long == @long")

# Tree data of the selected site
site_tree = tree_df.query("observation_id == @obs")

print("\nTree Data of the selected site")
print(site_tree)

# Lichen data of the selected site
site_lichen = lichen_df.query("observation_id == @obs")

print("\nLichen Data of the selected site")
print(site_lichen)

# Table data of the selected site
lichen_species = site_lichen["id"].unique()

# For each lichen observed per site, count the total number of quadrat
quadrat = []

for i in lichen_species:
    site_lichen_table = table_df[table_df["lichen_id"] == i]

    print("\nTable Data lichen")
    print(site_lichen_table)

    # Sum of the non-empty quadrat
    sum_sq1 = site_lichen_table['sq1'].sum()
    sum_sq2 = site_lichen_table['sq2'].sum()
    sum_sq3 = site_lichen_table['sq3'].sum()
    sum_sq4 = site_lichen_table['sq4'].sum()
    sum_sq5 = site_lichen_table['sq5'].sum()

    sum_quadrat = sum_sq1 + sum_sq2 + sum_sq3 + sum_sq4 + sum_sq5

    # Letters to check
    letters_to_check = ['N', 'E', 'S', 'O']

    # Count based on the orientation
    count_dict = {}
    for letter in sum_quadrat:
        if letter in count_dict:
            count_dict[letter] += 1
        else:
            count_dict[letter] = 1

    # Complete with 0 for any missing orientation
    result_dict = []
    for letter in letters_to_check:
        if letter not in count_dict:
            result_dict.append(0)
        else:
            result_dict.append(count_dict[letter])

    # print("\nNon-empty quadrat")
    # print(sum_quadrat)

    # Append the results to the quadrat output
    quadrat.append({"id": i,
                    "sum_quadrat":len(sum_quadrat),
                    "N":result_dict[0],
                    "E":result_dict[1],
                    "S":result_dict[2],
                    "O":result_dict[3]})

# Convert the quadrat list to a DataFrame
quadrat_df = pd.DataFrame(quadrat)

print("\nLichen Data of the selected site with orientation")
print(quadrat_df)

# Merge the DataFrame
site_lichen_quadrat = pd.merge(site_lichen, quadrat_df)

### Histogram 3 with Plotly express bar: ###
# Espèces observées sur le site sélectionné

# concatenate dataframe "site_lichen_quadrat" with the lichen species' names
idx = site_lichen_quadrat["species_id"]
df = lichen_species_df.loc[idx-1,"name"].reset_index(drop=True)

site_lichen_quadrat_species=pd.concat([site_lichen_quadrat, df], axis=1)

# sort based on occurence
# (note): update_xaxes(categoryorder="total descending") does not work
site_lichen_quadrat_species=(
    site_lichen_quadrat_species
    .sort_values(by="sum_quadrat", ignore_index=True)
)

print("\n Final table for histogram")
print(site_lichen_quadrat_species)

### Design bar plot ###

hist3=px.bar(
    site_lichen_quadrat_species,
    x=["N", "E", "S", "O"],
    y="name",
    orientation="h",
    # width=1500,
    # height=800,
    title="Espèces observées sur le site sélectionné"
)

# remove the legend
#hist3.update(layout_showlegend=False)

# update the title
hist3.update_layout(
    title_font=dict(color="grey",size=20),
    title={"x": .5,"y": .9,"xanchor": "center"},
)

# update axes
hist3.update_xaxes(title="Count",showgrid=False)
hist3.update_yaxes(title="")

hist3.show()
