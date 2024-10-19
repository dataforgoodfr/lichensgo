import pandas as pd
import numpy as np

from Dashboards.constants import SQUARE_COLUMNS, ORIENTATIONS

# Merge table_df with lichen_df, lichen_species_df and observation_df
def merge_tables(table_df, lichen_df, observation_df):

    merged_df = table_df.merge(lichen_df, on='lichen_id', suffixes=('', '_l'), how='left')
    # merged_df = merged_df.merge(lichen_species_df, on='species_id', how='left')
    merged_df = merged_df.merge(observation_df, on='observation_id', how ='left')

    return merged_df

"""
Count the number of lichen (per orientation and total), for each entry in the table_df.
"""
def count_lichen(table_df):

    table_with_nb_lichen_df = table_df.copy()

    # Concatenate all square_columns into a single list per row
    table_with_nb_lichen_df['concatenated_squares'] = table_with_nb_lichen_df[SQUARE_COLUMNS].sum(axis=1)

    # Calculate lichen per orientation
    for orientation in ORIENTATIONS:
        table_with_nb_lichen_df[orientation] = table_with_nb_lichen_df['concatenated_squares'].apply(lambda x, orientation=orientation: x.count(orientation))

    # Calculate total number of lichen by summing over all orientations
    table_with_nb_lichen_df['nb_lichen'] = table_with_nb_lichen_df[ORIENTATIONS].sum(axis=1)

    # Rename the orientations count columns
    table_with_nb_lichen_df.rename(columns={orientation:f'nb_lichen_{orientation}' for orientation in ORIENTATIONS}, inplace=True)

    # Drop concatenated_squares column
    table_with_nb_lichen_df.drop(columns=['concatenated_squares'], inplace=True)

    return table_with_nb_lichen_df


def vdl_value(observation_df, table_with_nb_lichen_df):

    columns = ['observation_id'] + [f'nb_lichen_{orientation}' for orientation in ORIENTATIONS] + ['nb_lichen']
    vdl_df = table_with_nb_lichen_df[columns]

    # Calculate the lichen diversity value (VDL) per observation
    vdl_df = vdl_df.groupby('observation_id').sum() # Sum over all lichen species per observation
    vdl_df['VDL'] = vdl_df['nb_lichen'] / 15 # /5 pour le nombre de carrés par grille, /3 pour le nombre d'arbre par observation
    vdl_df["VDL_cat"] = pd.cut(vdl_df["VDL"], bins=[-1, 4.999, 10, 15, np.inf], labels=["<5", "5-10", "10-15", ">15"])

    observation_with_vdl_df = observation_df.merge(vdl_df, on='observation_id', how='left')
    return observation_with_vdl_df

"""
    Count the number of lichen per lichen ID.
"""
def count_lichen_per_lichen_id(table_with_nb_lichen_df, lichen_df, lichen_species_df):
    # Define the columns to be used for grouping and summing
    columns = ['lichen_id'] + [f'nb_lichen_{orientation}' for orientation in ORIENTATIONS] + ['nb_lichen']

    # Group by 'lichen_id' and sum the counts for each orientation and the total count
    nb_lichen_per_lichen_id_df = table_with_nb_lichen_df[columns].groupby('lichen_id').sum().reset_index()

    # Merge the grouped DataFrame with the lichen DataFrame to add lichen information
    nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df.merge(lichen_df, how='left', on='lichen_id')

    # Merge the result with the lichen species DataFrame to add species information
    nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df.merge(lichen_species_df, how='left', on='species_id', suffixes=['', '_s'])

    # Sort by observation_id and number of lichen in ascending order
    nb_lichen_per_lichen_id_df = nb_lichen_per_lichen_id_df.sort_values(by=['observation_id','nb_lichen'], ascending=True, ignore_index=True)

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
    non_unique_lichen = nb_lichen_per_lichen_id_df.loc[~nb_lichen_per_lichen_id_df['unique'], ['lichen_id', 'observation_id', 'nb_lichen', 'name']]
    # Sort by 'nb_lichen' in descending order to have suffix _1, _2, _3, etc. for the most frequent lichen
    non_unique_lichen = non_unique_lichen.sort_values(by='nb_lichen', ascending=False)

    # Group by 'observation_id' and 'name', and calculate the count for duplicates
    grouped = non_unique_lichen.groupby(['observation_id', 'name']).cumcount()

    # Convert the count to string and create the suffix
    suffix = (grouped + 1).astype(str)

    # Create a new column 'unique_name' by concatenating the original name with the suffix
    non_unique_lichen['unique_name'] = (non_unique_lichen['name'] + " " + suffix)

    # Merge unique names with original df
    merged_df = nb_lichen_per_lichen_id_df.merge(non_unique_lichen[['lichen_id', 'unique_name']], on='lichen_id', how='left')

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
    observation_with_species_count_df = observation_df.merge(count_species_per_observation_df, how='left', on='observation_id')

    # Add a categorical column based on the number of lichen
    observation_with_species_count_df["nb_species_cat"] = pd.cut(
        observation_with_species_count_df["nb_species"],
        bins=[0, 7, 10.5, 15, np.inf],
        labels = ["<7", "7-10", "11-14", ">14"],
        right=False
    )

    return observation_with_species_count_df


# Group by species' type and count them (but only count there presence in the table, not the frequency in each observation)
def count_lichen_per_species(lichen_df, lichen_species_df):

    # Group by species' type and count them
    count_lichen_per_species_df = (
        lichen_df
        .groupby("species_id", as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    # Merge with species names
    count_lichen_per_species_df = count_lichen_per_species_df.merge(lichen_species_df[['species_id', 'name']], on='species_id')

    # Sort based on occurrences in descending order
    count_lichen_per_species_df = count_lichen_per_species_df.sort_values(by='count', ascending=False).reset_index(drop=True)

    return count_lichen_per_species_df

# Group by species' type and observation id and sum the number of lichen, and merge with lichen species ecology
def group_table_by_observation_and_species(merged_table_with_nb_lichen_df, merged_lichen_species_df):

    grouped_table_by_observation_and_species_df = merged_table_with_nb_lichen_df.groupby(['observation_id', 'species_id'])['nb_lichen'].sum().reset_index()

    grouped_table_by_observation_and_species_df = grouped_table_by_observation_and_species_df.merge(merged_lichen_species_df, on='species_id')

    grouped_table_by_observation_and_species_df  = grouped_table_by_observation_and_species_df[['observation_id', 'species_id', 'name', 'nb_lichen', 'pH','eutrophication', 'poleotolerance', 'thallus']]

    return grouped_table_by_observation_and_species_df


# Group lichen by observation and thallus and sum the count of lichen_id (not the number of lichen)
# NB: We count the number of lichen_id and not species as we want to count multiple times the non-unique lichen (other lichen etc)
def group_lichen_by_observation_and_thallus(lichen_df, merged_lichen_species_df):

    merged_lichen_df = lichen_df.merge(merged_lichen_species_df[['species_id', 'thallus']], on='species_id')

    grouped_lichen_by_observation_and_thallus_df = merged_lichen_df.groupby(['observation_id', 'thallus'])['lichen_id'].count().reset_index()

    grouped_lichen_by_observation_and_thallus_df = grouped_lichen_by_observation_and_thallus_df.rename(columns={'lichen_id': 'nb_lichen_id'})

    return grouped_lichen_by_observation_and_thallus_df


# Degree of artificialisation (poleotolerance)
def calc_deg_artif(filtered_lichen_with_ecology_df):

    # Calculate the total number of lichens
    total_nb_lichen = filtered_lichen_with_ecology_df['nb_lichen'].sum()

    # Calculate the number of poleotolerance (resistant) lichens
    poleotolerant_nb_lichen = filtered_lichen_with_ecology_df[(filtered_lichen_with_ecology_df['poleotolerance'] == 'resistant')]['nb_lichen'].sum()

    # Return the ratio in percentage
    return (poleotolerant_nb_lichen / total_nb_lichen) * 100

# Acid pollution calculation
def calc_pollution_acide(filtered_lichen_with_ecology_df):

    # Calculate the total number of lichens
    total_nb_lichen = filtered_lichen_with_ecology_df['nb_lichen'].sum()

    # Calculate the number of acidophilous lichens
    acid_nb_lichen =  filtered_lichen_with_ecology_df[filtered_lichen_with_ecology_df['pH'] == 'acidophilous']['nb_lichen'].sum()

    # Return the ratio in percentage
    return (acid_nb_lichen / total_nb_lichen) * 100


# Azoic pollution calculation
def calc_pollution_azote(filtered_lichen_with_ecology_df):

    # Calculate the total number of lichens
    total_nb_lichen = filtered_lichen_with_ecology_df['nb_lichen'].sum()

    # Calculate the number of eutrophic lichens
    eutrophic_nb_lichen =  filtered_lichen_with_ecology_df[filtered_lichen_with_ecology_df['eutrophication'] == 'eutrophic']['nb_lichen'].sum()

    # Return the ratio in percentage
    return (eutrophic_nb_lichen / total_nb_lichen) * 100
