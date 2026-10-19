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


rows= []
for index, row in non_explicit_df.iterrows():
    subject_id = row['SubjectID']
    pulse_sequence_name = row['PulseSequenceName']
    series_number = row['SeriesNumber']
    series_description = row['SeriesDescription']

    potential_refs = non_explicit_df[
        (non_explicit_df['SubjectID'] == subject_id) &
        (non_explicit_df['SeriesNumber'] < series_number) &
        (non_explicit_df['PulseSequenceName'] == pulse_sequence_name) &
        (non_explicit_df['SeriesDescription'].apply(
                    lambda x: SequenceMatcher(None, str(x).lower(), str(series_description).lower()).ratio() > 0.9))
    ]

    for _, ref_row in potential_refs.iterrows():
            new_row = row.to_dict()
            new_row['Reference_SeriesNumber'] = ref_row['SeriesNumber']
            new_row['Reference_SeriesDescription'] = ref_row['SeriesDescription']
            rows.append(new_row)


silent_repeat_df = pd.DataFrame(rows)
print(f"Identified {len(silent_repeat_df)} potential silent repeat scans.")
# output the potential_silent_repeats_df to a csv file
silent_repeat_df.to_csv(r"W:/MinMo_CI/derivatives/potential_silent_repeat_scans.csv", index=False)