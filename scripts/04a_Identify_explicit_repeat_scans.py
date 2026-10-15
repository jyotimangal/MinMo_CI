#Author Jyoti Mangal, Date 14/10/2026
# Script to do some repeat scan identification from metadata extracted from json and dicom files (merged)

from difflib import SequenceMatcher
import re
import pandas as pd

metadata_df = pd.read_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv")

# Explicit repeat scan identification
SeriesDescriptionStrings = metadata_df['SeriesDescription'].str
listOfUniqueSeriesDescriptions = SeriesDescriptionStrings.lower().unique()
explicit_repeat_df = metadata_df[SeriesDescriptionStrings.contains('rpt|repeat', case=False, na=False)].sort_values(by=['SubjectID', 'SeriesNumber'])

# load group_key.csv and merge with explicit_repeat_df on SubjectID to get the group information
group_key_df = pd.read_csv(r"W:/MinMo_CI/derivatives/group_key.csv")
explicit_repeat_df = explicit_repeat_df.merge(group_key_df, on='SubjectID', how='left').reset_index(drop=True)

# Check the initial (earlier scan) from the metadata_df for each explicit repeat scan, for each subject and pulse sequence
# mark it as reference scan and add a column to explicit_repeat_df to indicate which scan is the reference scan for each subject and pulse sequence
explicit_repeat_df['potential_ref_SeriesNumbers'] = None
explicit_repeat_df['potential_ref_count'] = None
explicit_repeat_df['is_cross_sequence_repeat'] = False

# loop through each entry in explicit_repeat_df and find the reference scan for that subject and pulse sequence in metadata_df
for index, row in explicit_repeat_df.iterrows():
    subject_id = row['SubjectID']
    pulse_sequence_name = row['PulseSequenceName']
    series_number = row['SeriesNumber']
    orientation = row['Orientation']
    series_description = row['SeriesDescription']
    pulse_sequence_name_prefix = str(pulse_sequence_name)[1:4]  # get the first 3 characters of the pulse sequence name, e.g. 'ax_t2_tse' -> 'ax_'
    base_series_description = re.sub(r'[_\s]*(rpt|repeat)[_\s]*', ' ', series_description, flags=re.IGNORECASE).lower().strip()  # remove 'rpt' or 'repeat' from series description and convert to lower case
    # list how many scans exist for this subject, this pulsesequence with series number less than the current series number
    ref_scans = metadata_df[(metadata_df['SubjectID'] == subject_id) & 
                             (metadata_df['PulseSequenceName'] == pulse_sequence_name) & 
                             (metadata_df['SeriesNumber'] < series_number) &
                             (metadata_df['Orientation'] == orientation) &
                             (metadata_df['SeriesDescription'].apply(lambda x: SequenceMatcher(None, str(x).lower(), base_series_description).ratio() > 0.9)) &
                             (~metadata_df['SeriesDescription'].str.contains('rpt|repeat', case=False, na=False))].sort_values(by='SeriesNumber', ascending=False)
    # check if there are any scans for this subject with the same orientation and pulse sequence name prefix, but different pulse sequence name (cross-sequence repeat)
    cross_ref_scans =  metadata_df[(metadata_df['SubjectID'] == subject_id) &
                             (metadata_df['SeriesNumber'] < series_number) &
                             (metadata_df['Orientation'] == orientation) &
                             (metadata_df['PulseSequenceName'].str[1:4] == pulse_sequence_name_prefix) &
                             (~metadata_df['SeriesDescription'].str.contains('rpt|repeat', case=False, na=False))]
    # further filter by similarity if possible
    high_sim = cross_ref_scans[cross_ref_scans['SeriesDescription'].apply(lambda x: SequenceMatcher(None, str(x).lower(), base_series_description).ratio() > 0.9)]
    cross_ref_scans = high_sim if len(high_sim) > 0 else cross_ref_scans
    if len(ref_scans) > 0:
        # list all the series numbers of potential ref scans and note in an array
        explicit_repeat_df.at[index, 'potential_ref_SeriesNumbers'] = ref_scans['SeriesNumber'].tolist()
    elif len(cross_ref_scans) > 0:
        explicit_repeat_df.at[index, 'is_cross_sequence_repeat'] = True
        explicit_repeat_df.at[index, 'potential_ref_SeriesNumbers'] = cross_ref_scans['SeriesNumber'].tolist()
    else:
        explicit_repeat_df.at[index, 'potential_ref_SeriesNumbers'] = None

    explicit_repeat_df.at[index, 'potential_ref_count'] = len(explicit_repeat_df.at[index, 'potential_ref_SeriesNumbers']) if explicit_repeat_df.at[index, 'potential_ref_SeriesNumbers'] is not None else 0
    print(f"SubjectID: {subject_id}, PulseSequenceName: {pulse_sequence_name}, SeriesNumber: {series_number}, Number of potential reference scans: {explicit_repeat_df.at[index, 'potential_ref_count']}")
    
print(f"Explicit repeat scans identified: {len(explicit_repeat_df)}")

print(f"Total explicit repeats: {len(explicit_repeat_df)}")
print(f"With MinMo: {len(explicit_repeat_df[explicit_repeat_df['MinMo_Group'] == 'With MinMo'])}")
print(f"Without MinMo: {len(explicit_repeat_df[explicit_repeat_df['MinMo_Group'] == 'Without MinMo'])}")
print(f"\nSubjects with repeats - With MinMo: {explicit_repeat_df[explicit_repeat_df['MinMo_Group'] == 'With MinMo']['SubjectID'].nunique()}")
print(f"Subjects with repeats - Without MinMo: {explicit_repeat_df[explicit_repeat_df['MinMo_Group'] == 'Without MinMo']['SubjectID'].nunique()}")
print(f"\nTotal subjects - With MinMo: {metadata_df[metadata_df['MinMo_Group'] == 'With MinMo']['SubjectID'].nunique()}")
print(f"Total subjects - Without MinMo: {metadata_df[metadata_df['MinMo_Group'] == 'Without MinMo']['SubjectID'].nunique()}")

