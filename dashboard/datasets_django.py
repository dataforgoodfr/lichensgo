import os
import unidecode
import pandas as pd

from dashboard.models import Tree, TreeSpecies, Observation, Lichen, LichenSpecies, Environment, Table

def get_environment_data():
    return pd.DataFrame(Environment.objects.values())

def get_lichen_data():
    return pd.DataFrame(Lichen.objects.values())

def get_lichen_species_data():
    fields = ['id', 'unique', 'name', 'name_en', 'name_fr']  # specify the fields to retrieve the translation
    df = pd.DataFrame(LichenSpecies.objects.values(*fields))
    df = df.dropna()  # Remove rows with NaN values
    df = df[df['name'].astype(str).str.strip().astype(bool)]  # Remove rows where 'name' is empty
    return df

def get_observation_data():
    return pd.DataFrame(Observation.objects.values())

def get_table_data():
    return pd.DataFrame(Table.objects.values())

def get_tree_data():
    return pd.DataFrame(Tree.objects.values())

def get_tree_species():
    return pd.DataFrame(TreeSpecies.objects.values())

def get_lichen_ecology_csv():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    lichen_ecology_csv_path = os.path.join(current_dir, 'data', 'lichen_species_ecology.csv')
    lichen_ecology_df = pd.read_csv(lichen_ecology_csv_path, delimiter=',')

    return lichen_ecology_df

# Function to normalize a string (remove accents, lower case, strip)
def normalize_string(value):
    if isinstance(value, str):
        return unidecode.unidecode(value.strip().lower())
    return value

def merge_lichen_ecology(lichen_species_df, lichen_species_ecology_df):

    # Clean the csv data
    if 'name' not in lichen_species_ecology_df:
        lichen_species_ecology_df.rename(columns={'Taxon': 'name'}, inplace=True)
    if 'species_id' in lichen_species_ecology_df.columns:
        lichen_species_ecology_df.drop(columns=['species_id'], inplace=True)

    # Normalize the names of the species (remove accents, lower case, strip) to match them
    lichen_species_df['normalized_name'] = lichen_species_df['name_fr'].apply(normalize_string)
    lichen_species_ecology_df['normalized_name'] = lichen_species_ecology_df['name'].apply(normalize_string)

    # Merge the df on the normalized names
    merged_lichen_species_df = lichen_species_df.merge(lichen_species_ecology_df, on='normalized_name', how='left', suffixes=('', '_eco'))

    # Check if there are missing species in the ecology data
    missing_data_rows = merged_lichen_species_df['name'][merged_lichen_species_df[lichen_species_ecology_df.columns].isnull().any(axis=1)]

    if not missing_data_rows.empty:
        print('Warning: some species are missing from the ecology data')
        for row in missing_data_rows:
            print(f'Missing: {row}')

    return merged_lichen_species_df

def get_useful_data():
    lichen_df = get_lichen_data()[['id', 'observation_id', 'species_id']]
    lichen_species_df = get_lichen_species_data()[['id', 'unique', 'name', 'name_en', 'name_fr']]
    lichen_species_ecology_df = get_lichen_ecology_csv()
    observation_df = get_observation_data()[['id', 'user_id', 'date_obs', 'localisation_lat', 'localisation_long']]
    table_df = get_table_data()[['id', 'lichen_id', 'sq1', 'sq2', 'sq3', 'sq4', 'sq5']]

    # Rename the id columns for easier merge
    lichen_df.rename(columns={'id': 'lichen_id'}, inplace=True)
    lichen_species_df.rename(columns={'id': 'species_id'}, inplace=True)
    lichen_species_ecology_df.rename(columns={'id': 'species_id'}, inplace=True)
    observation_df.rename(columns={'id': 'observation_id'}, inplace=True)
    table_df.rename(columns={'id': 'table_id'}, inplace=True)

    merged_lichen_species_df = merge_lichen_ecology(lichen_species_df, lichen_species_ecology_df)

    return lichen_df, merged_lichen_species_df, observation_df, table_df
