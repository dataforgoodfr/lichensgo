import sys
from pathlib import Path
import pandas as pd
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology
from computed_datasets import df_frequency

# Import des données
observation = get_observation_data()
lichen_df = get_lichen_data()
lichen_species_df = get_lichen_species_data()
tree_df = get_tree_data()
table_df = get_table_data()
frequency_df = df_frequency()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# Récupération de ID du site, Date, Longitude, Latitude #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Filtrage pour récupérer les données
df_download = observation[[
    "id", 
    "date_obs", 
    "localisation_lat",
    "localisation_long"
    ]]

# # # # # # # # # # # 
# Calcul diversité  #
# # # # # # # # # # # 

# Afficher la diversité
count_lichen = table_df.groupby("tree_id")["lichen_id"].count().reset_index()
count_lichen.columns = ["tree_id", "nb_lichen"]
count_lichen = count_lichen.merge(tree_df, left_on="tree_id", right_on="id")
count_lichen = count_lichen[["species_name", "nb_lichen", "observation_id"]]

# Merge et renommer pour un résultat propre
df_download = df_download.merge(count_lichen, left_on="id", right_on="observation_id")
df_download = df_download[[
    "id",
    "date_obs",
    "localisation_lat",
    "localisation_long",
    "nb_lichen",
    ]]
df_download = df_download.rename(columns={"id": "id_site","nb_lichen": "diversite"})

# # # # # # # # # # # # # 
# 3 indices de pollution#
# # # # # # # # # # # # # 

# Degré d'artificialisation
deg_artif = round((frequency_df[frequency_df["poleotolerance"] == "resistant"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
# print(
#     deg_artif[deg_artif.isnull()]
#     )

# print(frequency_df[frequency_df["id"] == 603]) 
deg_artif.columns = ["id", "degres d'artificialisation"]
print(deg_artif)

# Pollution acidé
poll_acid = round((frequency_df[frequency_df["ph"] == "acidophilous"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
# print(poll_acid)
# df_download["pollution acide"] = poll_acid

# Pollution azoté
poll_azo = round((frequency_df[frequency_df["eutrophication"] == "eutrophic"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
# print(poll_azo)
# df_download["pollution azote"] = poll_azo

# print(df_download)