import sys
from pathlib import Path
import pandas as pd
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology

square_columns = ['sq1', 'sq2', 'sq3', 'sq4', 'sq5']
orientations = ['N', 'E', 'S', 'O']

# Merge table_df with lichen_df, lichen_species_df and observation_df
def merge_tables(table_df, lichen_df, lichen_species_df, observation_df):

    merged_df = table_df.merge(lichen_df, left_on='lichen_id', right_on='id', suffixes=('', '_l'), how='left')
    merged_df = merged_df.merge(lichen_species_df, left_on='species_id', right_on='id', suffixes=('', '_ls'), how='left')
    merged_df = merged_df.merge(observation_df, left_on='observation_id', right_on='id', suffixes=('', '_o'), how ='left')

    return merged_df

def frequency_table(lichen_df, lichen_species_df, observation_df, table_df):

    # Merge table_df with lichen_df, lichen_species_df and observation_df
    merged_df = merge_tables(table_df, lichen_df, lichen_species_df, observation_df)

    # Concatenate all square_columns into a single list per row
    merged_df['concatenated_squares'] = merged_df[square_columns].sum(axis=1)

    # Calculate frequency per orientation
    for orientation in orientations:
        merged_df[orientation] = merged_df['concatenated_squares'].apply(lambda x: x.count(orientation))

    # Calculate total frequency by summing all orientation frequencies
    merged_df["freq"] = merged_df[orientations].sum(axis=1)

    # Drop concatenated_squares column
    merged_df.drop(columns=['concatenated_squares'], inplace=True)

    return merged_df

# Sum frequency per lichen id
def lichen_frequency(frequency_table_df):

    lichen_frequency_df = frequency_table_df.groupby(by='lichen_id', as_index=False).agg(
        {
            'name': 'first',
            'N': 'sum',
            'O': 'sum',
            'S': 'sum',
            'E': 'sum',
            'freq': 'sum'
        }).sort_values(by='freq', ascending=True, ignore_index=True)

    return lichen_frequency_df


# Group by species' type and count them
def count_lichen_per_species(lichen_df, lichen_species_df):

    # Group by species' type and count them
    count_lichen_per_species_df = (
        lichen_df
        .groupby("species_id", as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    # Merge with species names
    count_lichen_per_species_df = count_lichen_per_species_df.merge(lichen_species_df[['id', 'name']], left_on='species_id', right_on='id').drop(columns='id')

    # Sort based on occurrences in descending order
    count_lichen_per_species_df = count_lichen_per_species_df.sort_values(by='count', ascending=False).reset_index(drop=True)

    return count_lichen_per_species_df

def calculate_frequency(column):
    return column.apply(lambda x: sum(1 for char in x if char in ['E', 'N', 'O', 'S']))

def df_frequency():
    # Load usefull datasets
    lichen_df = get_lichen_data()
    lichen_species_df = get_lichen_species_data()
    observation_df = get_observation_data()
    table_df = get_table_data()
    tree_species_df = get_tree_species()
    ecology_df = get_lichen_ecology()

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

    return grouped_df
