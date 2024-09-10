import pandas as pd
from sqlalchemy import text
from my_data.db_connect import get_session
from my_data.model import Tree, TreeSpecies, Observation, Lichen, LichenSpecies, Environment, Table, LichenEcology, LichenFrequency

session = get_session()

def get_environment_data():
    data = session.query(Environment).all()
    environment_data = []
    for env in data:
        environment_data.append({
            "id": env.id,
            "name": env.name,
            "name_en": env.name_en,
            "name_fr": env.name_fr
        })
    return pd.DataFrame(environment_data)

def get_lichen_data():
    data = session.query(Lichen).all()
    lichen_data = []
    for lichen in data:
        lichen_data.append({
            "id": lichen.id,
            "species_id": lichen.species_id,
            "picture": lichen.picture,
            "certitude": lichen.certitude,
            "observation_id": lichen.observation_id
        })
    return pd.DataFrame(lichen_data)

def get_lichen_species_data():
    data = session.query(LichenSpecies).all()
    lichen_species_data = []
    for species in data:
        lichen_species_data.append({
            "id": species.id,
            "name": species.name,
            "unique": species.unique,
            "name_en": species.name_en,
            "name_fr": species.name_fr
        })
    return pd.DataFrame(lichen_species_data)

def get_observation_data():
    data = session.query(Observation).all()
    observation_data = []
    for obs in data:
        observation_data.append({
            "id": obs.id,
            "date_obs": obs.date_obs,
            "weather_cond": obs.weather_cond,
            "school_obs": obs.school_obs,
            "localisation_lat": obs.localisation_lat,
            "localisation_long": obs.localisation_long,
            "comment": obs.comment,
            "user_id": obs.user_id,
            "validation": obs.validation,
            "env_type_link_id": obs.env_type_link_id
        })
    return pd.DataFrame(observation_data)

def get_table_data():
    data = session.query(Table).all()
    table_data = []
    for table in data:
        table_data.append({
            "id": table.id,
            "sq1": table.sq1,
            "sq2": table.sq2,
            "sq3": table.sq3,
            "sq4": table.sq4,
            "sq5": table.sq5,
            "lichen_id": table.lichen_id,
            "tree_id": table.tree_id
        })
    return pd.DataFrame(table_data)

def get_tree_data():
    data = session.query(Tree).all()
    tree_data = []
    for tree in data:
        tree_data.append({
            "id": tree.id,
            "species_name": tree.species.name if tree.species else None,
            "circonference": tree.circonference,
            "observation_id": tree.observation_id
        })
    return pd.DataFrame(tree_data)

def get_tree_species():
    data = session.query(TreeSpecies).all()
    tree_species_data = []
    for tree_species in data:
        tree_species_data.append({
            "id": tree_species.id,
            "name": tree_species.name,
            "name_en": tree_species.name_en,
            "name_fr": tree_species.name_fr
        })
    return pd.DataFrame(tree_species_data)

def get_lichen_ecology():
    data = session.query(LichenEcology).all()
    lichen_ecology_data = []
    for lichen_ecology in data:
        lichen_ecology_data.append({
            "id": lichen_ecology.id,
            "taxon": lichen_ecology.taxon,
            "pH": lichen_ecology.pH,
            "aridity": lichen_ecology.aridity,
            "eutrophication": lichen_ecology.eutrophication,
            "poleotolerance": lichen_ecology.poleotolerance,
            "cleaned_taxon": lichen_ecology.cleaned_taxon
        })
    return pd.DataFrame(lichen_ecology_data)

