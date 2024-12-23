import pandas as pd
import numpy as np

from dashboard.constants import SQUARE_COLUMNS, ORIENTATIONS

# from django.utils.translation import get_language
# from django.utils.translation import gettext_lazy as _
# from django.utils import translation

from dashboard.translation import get_lazy_translation as _

# Merge table_df with lichen_df, lichen_species_df and observation_df
def merge_tables(table_df, lichen_df, observation_df):

    merged_df = table_df.merge(lichen_df, on='lichen_id', suffixes=('', '_l'), how='left')
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


def calc_vdl(table_with_nb_lichen_df):

    nb_lichen_df = table_with_nb_lichen_df[['observation_id', 'lichen_id', 'nb_lichen']]

    # Count the average number of lichen per tree (by grouping by observation_id and lichen_id)
    avg_nb_lichen_per_tree = nb_lichen_df.groupby(['observation_id', 'lichen_id']).mean()

    # Sum over all lichen per observation
    vdl_df = avg_nb_lichen_per_tree.groupby('observation_id').sum().reset_index().rename(columns={'nb_lichen': 'VDL'})

    vdl_df['VDL_cat'] = pd.cut(vdl_df['VDL'], bins=[-1, 25, 50, 75, np.inf], labels=['< 25', '25 - 50', '50 - 75', '> 75'])

    return vdl_df

"""
    Count the number of lichen per lichen ID.
"""
def count_lichen_per_lichen_id(table_with_nb_lichen_df, lichen_df, lichen_species_df):
    # Define the columns to be used for grouping and summing
    columns = ['lichen_id'] + [f'nb_lichen_{orientation}' for orientation in ORIENTATIONS] + ['nb_lichen']

    # Group by 'lichen_id' and sum the counts for each orientation and the total count
    nb_lichen_per_lichen_id_df = table_with_nb_lichen_df[columns].groupby('lichen_id').sum().reset_index()

    nb_lichen_per_lichen_id_df['nb_lichen_ratio'] = nb_lichen_per_lichen_id_df['nb_lichen'] / (3 * 5 * 4) # divided by number of trees x number of quadrants x number of orientations

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
    non_unique_lichen['unique_name'] = (non_unique_lichen['name'] + ' ' + suffix)

    # Merge unique names with original df
    merged_df = nb_lichen_per_lichen_id_df.merge(non_unique_lichen[['lichen_id', 'unique_name']], on='lichen_id', how='left')

    # Replace NaN unique names by name
    merged_df['unique_name'] = merged_df['unique_name'].combine_first(merged_df['name'])

    return merged_df


# Count the number of lichen species for each observation
def count_species_per_observation(lichen_df, observation_df):
    # Count the number of different lichen (=lines in the df) per observation
    count_species_per_observation_df = lichen_df['observation_id'].value_counts().to_frame().rename(columns={'count':'nb_species'})

    # Merge with observation_df
    observation_with_species_count_df = observation_df.merge(count_species_per_observation_df, how='left', on='observation_id')

    # Add a categorical column based on the number of lichen
    observation_with_species_count_df['nb_species_cat'] = pd.cut(
        observation_with_species_count_df['nb_species'],
        bins=[0, 7, 10.5, 15, np.inf],
        labels = ['< 7', '7 - 10', '11 - 14', '> 14'],
        right=False
    )

    return observation_with_species_count_df


# Group by species' type and count them (but only count their presence in the table, not the frequency in each observation)
def count_lichen_per_species(lichen_df, lichen_species_df):

    # Group by species' type and count them
    count_lichen_per_species_df = (
        lichen_df
        .groupby('species_id', as_index=False)
        .size()
        .rename(columns={'size': 'count'})
    )

    # Merge with species names
    count_lichen_per_species_df = count_lichen_per_species_df.merge(lichen_species_df[['species_id', 'name']], on='species_id')

    # Sort based on occurrences in descending order
    count_lichen_per_species_df = count_lichen_per_species_df.sort_values(by='count', ascending=False).reset_index(drop=True)

    return count_lichen_per_species_df


# Group and sum nb lichen by observation and thallus and sum the count of lichen_id (not the number of lichen)
def group_lichen_by_observation_and_thallus(merged_table_with_nb_lichen_df, merged_lichen_species_df):

    merged_table_with_species = merged_table_with_nb_lichen_df[['observation_id', 'nb_lichen', 'species_id']].merge(merged_lichen_species_df[['species_id', 'thallus']], on='species_id').drop(columns=['species_id'])
    sum_lichen_by_observation_and_thallus_df = merged_table_with_species.groupby(['observation_id', 'thallus']).sum().reset_index()

    return sum_lichen_by_observation_and_thallus_df


def calc_degrees_pollution(merged_table_with_nb_lichen_df, lichen_df, merged_lichen_species_df):
    nb_lichen_df = merged_table_with_nb_lichen_df[['observation_id', 'lichen_id', 'nb_lichen']].groupby(['observation_id', 'lichen_id']).sum().reset_index()
    nb_lichen_df = nb_lichen_df.merge(lichen_df[['lichen_id', 'species_id']], on='lichen_id', how='left')
    nb_lichen_df = nb_lichen_df.merge(merged_lichen_species_df[['species_id', 'pH', 'eutrophication', 'poleotolerance']], on='species_id', how='left')

    # Calculate the total number of nb_lichen per observation_id
    nb_lichen_per_observation = nb_lichen_df.groupby('observation_id')['nb_lichen'].sum().reset_index()

    #  Calculate the number of resistant lichen per observation_id
    resistant_lichen_per_observation = (
        nb_lichen_df[nb_lichen_df['poleotolerance'] == 'resistant'] # Fitler on resistant lichen
        .groupby('observation_id', as_index=False)['nb_lichen'].sum()  # Group by observation_id without setting it as index
        .rename(columns={'nb_lichen':'nb_lichen_resistant'})
    )

    #  Calculate the number of acid lichen per observation_id
    acid_lichen_per_observation = (
        nb_lichen_df[nb_lichen_df['pH'] == 'acidophilous'] # Fitler on acidophilous lichen
        .groupby('observation_id', as_index=False)['nb_lichen'].sum()  # Group by observation_id without setting it as index
        .rename(columns={'nb_lichen':'nb_lichen_acid'})
    )

    #  Calculate the number of eutrophic lichen per observation_id
    eutrophic_lichen_per_observation = (
        nb_lichen_df[nb_lichen_df['eutrophication'] == 'eutrophic'] # Fitler on eutrophic lichen
        .groupby('observation_id', as_index=False)['nb_lichen'].sum()  # Group by observation_id without setting it as index
        .rename(columns={'nb_lichen':'nb_lichen_eutrophic'})
    )

    # Merge the dataframes
    merged_df = nb_lichen_per_observation.merge(resistant_lichen_per_observation, on='observation_id', how='left')
    merged_df = merged_df.merge(acid_lichen_per_observation, on='observation_id', how='left')
    merged_df = merged_df.merge(eutrophic_lichen_per_observation, on='observation_id', how='left')

    # Fill NaN values with 0 (in case there are observations with no resistant, acid or eutrophic lichen)
    merged_df = merged_df.fillna(0)

    # Calculate the ratio of resistant nb_lichen to total nb_lichen
    merged_df['deg_toxitolerance'] = merged_df['nb_lichen_resistant'] / merged_df['nb_lichen']

    # Calculate the degree of acid pollution
    merged_df['deg_acidity'] = merged_df['nb_lichen_acid'] / merged_df['nb_lichen']

    # Calculate the degree of nitrogen (azote in french) pollution
    merged_df['deg_eutrophication'] = merged_df['nb_lichen_eutrophic'] / merged_df['nb_lichen']

    # Add categorical columns
    for col in ['deg_toxitolerance', 'deg_acidity', 'deg_eutrophication']:
        merged_df[col + '_cat'] = pd.cut(merged_df[col], bins=[-0.1, 0.25, 0.5, 0.75, np.inf], labels=[
                                         '0 - 25%', '25 - 50%', '50 - 75%', '75 - 100%'])

    return merged_df

def count_lichen_per_species_per_observation(lichen_df):

    nb_lichen_per_species_per_observation_df = (
        lichen_df
        .groupby(['observation_id', 'species_id'])
        .size()
        .unstack(fill_value=0)
        )

    return nb_lichen_per_species_per_observation_df

def get_download_df(merged_observation_df, merged_lichen_species_df, nb_lichen_per_species_per_observation_df, lang):

    if lang:
        lang = lang[:2].lower()

    # Mapping of species_id to species_name in the selected language, to replace column with species_id by species_name
    species_name_mapping = merged_lichen_species_df.set_index('species_id')[f'name_{lang}'].to_dict()
    nb_lichen_per_observation_df_translated = nb_lichen_per_species_per_observation_df.rename(columns=species_name_mapping)

    download_df = merged_observation_df.merge(nb_lichen_per_observation_df_translated, on='observation_id')
    download_df.sort_values(by='observation_id', inplace=True)

    download_col = {
        'observation_id': str(_('observation_id')),
        'date_obs_formatted': str(_('date_obs')),
        'localisation_lat': str(_('latitude')),
        'localisation_long': str(_('longitude')),
        'nb_species': str(_('nb_species')),
        'VDL': str(_('VDL')),
        'deg_toxitolerance': str(_('deg_toxitolerance_export')),
        'deg_eutrophication': str(_('deg_eutrophication_export')),
        'deg_acidity': str(_('deg_acidity_export')),
    }

    # Add species names columns in the selected language
    for col in sorted(merged_lichen_species_df[f'name_{lang}'].unique()):
        download_col[col] = col

    # Rename then filter the columns of the DataFrame
    download_df = download_df[download_col.keys()]
    download_df = download_df.rename(columns=download_col)

    return download_df
