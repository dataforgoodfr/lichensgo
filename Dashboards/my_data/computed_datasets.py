import sys
from pathlib import Path
import pandas as pd
import numpy as np
chemin_dossier_parent = Path(__file__).parent.parent
sys.path.append(str(chemin_dossier_parent))
from my_data.datasets import get_environment_data, get_lichen_data, get_lichen_species_data, get_observation_data, get_table_data, get_tree_data, get_tree_species, get_lichen_ecology

square_columns = [f'sq{i}' for i in range(1, 6)]
orientations = ['N', 'E', 'S', 'O']

# Merge table_df with lichen_df, lichen_species_df and observation_df
def merge_tables(table_df, lichen_df, lichen_species_df, observation_df):

    merged_df = table_df.merge(lichen_df, left_on='lichen_id', right_on='id', suffixes=('', '_l'), how='left')
    merged_df = merged_df.merge(lichen_species_df, left_on='species_id', right_on='id', suffixes=('', '_ls'), how='left')
    merged_df = merged_df.merge(observation_df, left_on='observation_id', right_on='id', suffixes=('', '_o'), how ='left')

    return merged_df

"""
Count the number of lichen (per orientation and total), for each entry in the table_df.
"""
def count_lichen(table_df):

    table_with_nb_lichen_df = table_df.copy()

    # Concatenate all square_columns into a single list per row
    table_with_nb_lichen_df['concatenated_squares'] = table_with_nb_lichen_df[square_columns].sum(axis=1)

    # Calculate lichen per orientation
    for orientation in orientations:
        table_with_nb_lichen_df[orientation] = table_with_nb_lichen_df['concatenated_squares'].apply(lambda x: x.count(orientation))

    # Calculate total number of lichen by summing over all orientations
    table_with_nb_lichen_df["nb_lichen"] = table_with_nb_lichen_df[orientations].sum(axis=1)

    # Rename the orientations count columns
    table_with_nb_lichen_df.rename(columns={orientation:f'nb_lichen_{orientation}' for orientation in orientations}, inplace=True)

    # Drop concatenated_squares column
    table_with_nb_lichen_df.drop(columns=['concatenated_squares'], inplace=True)

    return table_with_nb_lichen_df


def vdl_value(observation_df, table_with_nb_lichen_df):

    columns = ['observation_id'] + [f'nb_lichen_{orientation}' for orientation in orientations] + ['nb_lichen']
    vdl_df = table_with_nb_lichen_df[columns]

    # Calculate the lichen diversity value (VDL) per observation
    vdl_df = vdl_df.groupby('observation_id').sum() # Sum over all lichen species per observation
    vdl_df['VDL'] = vdl_df['nb_lichen'] / 15 # /5 pour le nombre de carrés par grille, /3 pour le nombre d'arbre par observation
    vdl_df["VDL_cat"] = pd.cut(vdl_df["VDL"], bins=[-1, 5, 10, 15, np.inf], labels=["<5", "5-10", "10-15", ">15"])

    observation_with_vdl_df = observation_df.merge(vdl_df, left_on='id', right_on='observation_id', how='left')
    return observation_with_vdl_df

"""
    Count the number of lichen per lichen ID.
"""
def count_lichen_per_lichen_id(table_with_nb_lichen_df, lichen_df, lichen_species_df):
     # Define the columns to be used for grouping and summing
    columns = ['lichen_id'] + [f'nb_lichen_{orientation}' for orientation in orientations] + ['nb_lichen']

    # Group by 'lichen_id' and sum the counts for each orientation and the total count
    nb_lichen_per_lichen_id_df = table_with_nb_lichen_df[columns].groupby('lichen_id').sum()

    # Merge the grouped DataFrame with the lichen DataFrame to add lichen information
    nb_lichen_per_lichen_id_df = lichen_df.merge(nb_lichen_per_lichen_id_df, how='left', left_on='id', right_on='lichen_id')

    # Merge the result with the lichen species DataFrame to add species information
    nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df.merge(lichen_species_df, how='left', left_on='species_id', right_on='id', suffixes=['', '_s'])

    # Sort by observation_id and number of lichen in ascending order
    nb_lichen_per_lichen_id_df  = nb_lichen_per_lichen_id_df.sort_values(by=['observation_id','nb_lichen'], ascending=True)

    # Rename the repeated lichen names with a unique name
    nb_lichen_per_lichen_id_df = unique_lichen_name(nb_lichen_per_lichen_id_df)

    return nb_lichen_per_lichen_id_df

"""
Rename repeated lichen names in lichen_species ('Autres lichen ...' etc),
(where unique = False) with a unique name which includes a suffix like
'Autres lichen 1', 'Autres lichen 2', etc.
"""
def unique_lichen_name(nb_lichen_per_lichen_id_df):

    # Filter lichen that are not unique
    non_unique_lichen = nb_lichen_per_lichen_id_df[nb_lichen_per_lichen_id_df['unique'] == False][['id', 'observation_id', 'nb_lichen','name']]

    # Sort by 'nb_lichen' in descending order to have suffix _1, _2, _3, etc. for the most frequent lichen
    non_unique_lichen = non_unique_lichen.sort_values(by='nb_lichen', ascending=False)

    # Group by 'observation_id' and 'name', and calculate the count for duplicates
    grouped = non_unique_lichen.groupby(['observation_id', 'name']).cumcount()

    # Convert the count to string and create the suffix
    suffix = (grouped + 1).astype(str)

    # Create a new column 'unique_name' by concatenating the original name with the suffix
    non_unique_lichen['unique_name'] = (non_unique_lichen['name'] + " " + suffix)

    # Merge unique names with original df
    merged_df = nb_lichen_per_lichen_id_df.merge(non_unique_lichen[['id', 'unique_name']], on='id', how='left')

    # Replace NaN unique names by name
    merged_df['unique_name'] = merged_df['unique_name'].combine_first(merged_df['name'])

    return merged_df

# """
# Count the number of lichen per square in the given table_df.
# """
# def count_lichen_per_square(table_df):

#     table_with_count_per_square_df = table_df.copy()


#     for col in square_columns:
#        table_with_count_per_square_df[f'{col}'] = table_with_count_per_square_df[col].apply(lambda x : len(x))

#     table_with_count_per_square_df['nb_lichen'] = table_with_count_per_square_df[square_columns].sum(axis=1) # Sum over all squares

#     return table_with_count_per_square_df


# def calculate_frequency(column):
#     return column.apply(lambda x: sum(1 for orientation in x if orientation in orientations))

# Count the number of lichen (species) for each observation
def count_species_per_observation(lichen_df, observation_df):
    # Count the number of different lichen (=lines in the df) per observation
    count_species_per_observation_df = lichen_df['observation_id'].value_counts().to_frame().rename(columns={"count":"nb_species"})

    # Merge with observation_df
    observation_with_species_count_df = observation_df.merge(count_species_per_observation_df, how='left', left_on='id', right_on='observation_id')

    # Add a categorical column based on the number of lichen
    observation_with_species_count_df["nb_species_cat"] = pd.cut(observation_with_species_count_df["nb_species"], bins=[-1, 6, 11, 15, np.inf], labels = ["<7", "7-10", "11-14", ">14"])

    return observation_with_species_count_df


# Sum number of lichen per lichen_id
def group_per_lichen_id(table_with_nb_lichen_df):

    columns =[f'nb_lichen_{orientation}' for orientation in orientations] + ['nb_lichen']


    lichen_frequency_df = table_with_nb_lichen_df.groupby(by='lichen_id', as_index=False).agg(
        {
            'name': 'first',
            'N': 'sum',
            'O': 'sum',
            'S': 'sum',
            'E': 'sum',
            'nb_lichen': 'sum'
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
