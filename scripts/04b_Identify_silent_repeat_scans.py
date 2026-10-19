# Author: Jyoti Mangal, date 16/10/2026
# Script to identify silent repeat scans in the metadata dataframe. 
# The script looks for scans with the same subject ID, orientation, and similar series description (ignoring 'rpt' or 'repeat' in the series description). 
# It also checks for scans with the same pulse sequence name prefix (first 3 characters of the pulse sequence name) to identify potential repeat scans. 

import pandas as pd
import re
from difflib import SequenceMatcher

metadata_df = pd.read_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv")

# first exclude explicit repeats from the metadata dataframe
non_explicit_df = metadata_df[~metadata_df['SeriesDescription'].str.contains('rpt|repeat', case=False, na=False) &
                              metadata_df['ImageType'].str.contains('ORIGINAL', case=False, na=False)].copy()
non_explicit_df['potential_silent_repeat_seriesNumbers'] = None
non_explicit_df['potential_silent_repeat_count'] = None

for index, row in non_explicit_df.iterrows():
    subject_id = row['SubjectID']
    pulse_sequence_name = row['PulseSequenceName']
    series_number = row['SeriesNumber']
    series_description = row['SeriesDescription']

    # pre-flter to same subject and pulse prefix before applying SequenceMatcher for efficiency
    potential_silent_repeats = non_explicit_df[
        (non_explicit_df['SubjectID'] == subject_id) &
        (non_explicit_df['SeriesNumber'] != series_number) &
        (non_explicit_df['PulseSequenceName'] == pulse_sequence_name)
    ]

    matches = potential_silent_repeats[potential_silent_repeats['SeriesDescription'].apply(
        lambda x: SequenceMatcher(None, str(x).lower(), str(series_description).lower()).ratio() > 0.9
    )]['SeriesNumber'].tolist() if len(potential_silent_repeats) > 0 else []

    non_explicit_df.at[index, 'potential_silent_repeat_seriesNumbers'] = matches
    non_explicit_df.at[index, 'potential_silent_repeat_count'] = len(matches)

potential_silent_repeats_df = non_explicit_df[non_explicit_df['potential_silent_repeat_count'] > 0].copy()
print(f"Identified {len(potential_silent_repeats_df)} potential silent repeat scans.")
# output the potential_silent_repeats_df to a csv file
potential_silent_repeats_df.to_csv(r"W:/MinMo_CI/derivatives/potential_silent_repeat_scans.csv", index=False)