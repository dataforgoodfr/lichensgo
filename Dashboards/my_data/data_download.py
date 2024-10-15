import sys
from pathlib import Path
import pandas as pd
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.db_connect import get_session
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology
from my_data.computed_datasets import df_frequency


def get_download_data():
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

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Somme des fréquences sur toutes les espèces sur l'arbre #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    # DEMANDER DES EXPLICATIONS A HUGO DEMAIN

    # # # # # # # # # # # # # 
    # 3 indices de pollution#
    # # # # # # # # # # # # # 

    # Degré d'artificialisation
    deg_artif = round((frequency_df[frequency_df["poleotolerance"] == "resistant"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
    deg_artif = deg_artif.fillna(value=0)
    deg_artif = deg_artif.reset_index()
    df_download = df_download.merge(deg_artif, left_on="id_site", right_on="id", how="left")
    df_download = df_download.drop(columns=["id"])
    df_download = df_download.rename(columns={"freq": "degres d'artificialisation"})

    # Pollution acidé
    poll_acid = round((frequency_df[frequency_df["ph"] == "acidophilous"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
    poll_acid = poll_acid.fillna(value=0)
    poll_acid = poll_acid.reset_index()
    df_download = df_download.merge(poll_acid, left_on="id_site", right_on="id", how="left")
    df_download = df_download.drop(columns=["id"])
    df_download = df_download.rename(columns={"freq": "pollution acide"})

    # Pollution azoté
    poll_azo = round((frequency_df[frequency_df["eutrophication"] == "eutrophic"].groupby("id")["freq"].sum() / frequency_df.groupby("id")["freq"].sum()) * 100, 2)
    poll_azo = poll_azo.fillna(value=0)
    poll_azo = poll_azo.reset_index()
    df_download = df_download.merge(poll_acid, left_on="id_site", right_on="id", how="left")
    df_download = df_download.drop(columns=["id"])
    df_download = df_download.rename(columns={"freq": "pollution azote"})

    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # Retrouver la fréquence de chaque espèce sur un site   #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    merged_lichen = lichen_df.merge(lichen_species_df, left_on="species_id", right_on="id", suffixes=("", "_species"))
    merged_lichen = merged_lichen[["observation_id", "name"]]
    grouped = merged_lichen.groupby(["observation_id", "name"]).size().reset_index(name='count')
    pivoted = grouped.pivot_table(index="observation_id", columns="name", values="count", fill_value=0)
    pivoted = pivoted.reset_index()

    df_download = df_download.merge(pivoted, left_on="id_site", right_on="observation_id")
    df_download = df_download[[
        "id_site", "date_obs", "localisation_lat", 
        "localisation_long", "diversite", "degres d'artificialisation", 
        "pollution acide", "pollution azote", "Amandinea punctata/Lecidella elaeochroma", 
        "Anaptychia ciliaris", "Autre lichen crustacé", "Autre lichen foliacé", 
        "Autre lichen fruticuleux", "Candelaria concolor", "Candelariella sp.", 
        "Diploicia canescens", "Evernia prunastri", "Flavoparmelia caperata/soredians", 
        "Hyperphyscia adglutinata", "Hypogymnia physodes/tubulosa", "Hypotrachyna afrorevoluta/revoluta",
        "Lecanora sp.", "Lichen crustacé à aspect poudreux", "Lichens crustace à lirelles",
        "Melanelixia glabratula/Melanohalea exasperatula", "Melanohalea exasperata", 
        "Parmelia saxatilis", "Parmelia sulcata", "Parmelina tiliacea/pastillifera", 
        "Parmotrema perlatum/reticulatum", "Pertusaria pertusa", "Phaeophyscia orbicularis",
        "Physcia adscendens/tenella", "Physcia aipolia/stellaris", "Physcia leptalea", 
        "Physconia distorta", "Physconia grisea", "Pleurosticta acetabulum", 
        "Polycauliona polycarpa", "Pseudevernia furfuracea", "Punctelia sp.", 
        "Ramalina farinacea", "Ramalina fastigiata", "Ramalina fraxinea", 
        "Usnea sp.", "Xanthoria parietina"
    ]]

    columns_to_sum = [
        "Amandinea punctata/Lecidella elaeochroma", "Anaptychia ciliaris", "Autre lichen crustacé", 
        "Autre lichen foliacé", "Autre lichen fruticuleux", "Candelaria concolor", "Candelariella sp.", 
        "Diploicia canescens", "Evernia prunastri", "Flavoparmelia caperata/soredians", 
        "Hyperphyscia adglutinata", "Hypogymnia physodes/tubulosa", "Hypotrachyna afrorevoluta/revoluta",
        "Lecanora sp.", "Lichen crustacé à aspect poudreux", "Lichens crustace à lirelles",
        "Melanelixia glabratula/Melanohalea exasperatula", "Melanohalea exasperata", 
        "Parmelia saxatilis", "Parmelia sulcata", "Parmelina tiliacea/pastillifera", 
        "Parmotrema perlatum/reticulatum", "Pertusaria pertusa", "Phaeophyscia orbicularis",
        "Physcia adscendens/tenella", "Physcia aipolia/stellaris", "Physcia leptalea", 
        "Physconia distorta", "Physconia grisea", "Pleurosticta acetabulum", 
        "Polycauliona polycarpa", "Pseudevernia furfuracea", "Punctelia sp.", 
        "Ramalina farinacea", "Ramalina fastigiata", "Ramalina fraxinea", 
        "Usnea sp.", "Xanthoria parietina"
    ]

    df_download = df_download.groupby("id_site").agg(
        {col: 'first' for col in df_download.columns if col not in columns_to_sum} | {col: 'sum' for col in columns_to_sum}
    ).reset_index(drop=True)


    return df_download
