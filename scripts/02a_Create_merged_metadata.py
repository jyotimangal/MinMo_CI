#Author: Jyoti Mangal, Date 14/10/2026
#Script to merge the json and dicom metadata csv files and create a final metadata csv file for the MinMo-CI project

#Based on 02a_A_quicklook_at_metadata.py's results and exploration of the metadata (noted on Notion), 
#For the rows/scans in json_metadata_xnat.csv that have SeriesDescription=haste_localiser, only those are retained that have Orientation=axial
#This is to have a homogenous localiser scan entry

import pandas as pd
from utils import drop_common_columns

json_df = pd.read_csv(r"W:/MinMo_CI/derivatives/json_metadata_xnat.csv")
dicom_df = pd.read_csv(r"W:/MinMo_CI/derivatives/dicom_metadata_xnat.csv")
group_key_df = pd.read_csv(r"W:/MinMo_CI/derivatives/group_key.csv")
print(f"JSON rows: {len(json_df)}, DICOM rows: {len(dicom_df)}")

# Filter JSON rows to include the 'coronal' localiser scan for subjects that have both 'axial' and 'coronal' localiser scans, and retain all other rows
# first find all localisers in json_df
localiser_df = json_df[json_df['SeriesDescription'] == 'haste_localiser']
# find subjects that have multiple localisers 
localiser_df_multiple = localiser_df[localiser_df.duplicated(subset=['SubjectID', 'SeriesNumber'], keep=False)]
coronal_multiples = localiser_df_multiple[localiser_df_multiple['Orientation'] == 'coronal']
coronal_multiples_idx = coronal_multiples.index
json_filtered_df = json_df[~json_df.index.isin(coronal_multiples_idx)]
print(f"Filtered JSON rows: {len(json_filtered_df)}")

# convert the FrameAcquisitionDateTime column in dicom_df to datetime format and calculate the time since session start for each scan
dicom_df['FrameAcquisitionDateTime'] = pd.to_datetime(
    dicom_df['FrameAcquisitionDateTime'].dropna().apply(lambda x: str(int(x))),
    format='%Y%m%d%H%M%S',
    errors='coerce'
)
session_start = dicom_df.groupby('SubjectID')['FrameAcquisitionDateTime'].min()
dicom_df['TimeSinceSessionStart'] = dicom_df.apply(
    lambda row: (row['FrameAcquisitionDateTime'] - session_start[row['SubjectID']]).total_seconds() / 60 
    if pd.notna(row['FrameAcquisitionDateTime']) else None, axis=1
)

# build a df after filtering to distinct columns between the two dataframes, excluding the merge keys
dicom_df_distinct_columns = drop_common_columns(dicom_df, json_filtered_df, keep_cols=['SubjectID', 'SeriesNumber', 'SeriesDescription'])

#Merge the filtered JSON metadata with the DICOM metadata on SubjectID, SeriesNumber, and SeriesDescription
merged_df = json_filtered_df.merge(dicom_df_distinct_columns, on=['SubjectID', 'SeriesNumber', 'SeriesDescription'], how='left')
# Print the number of rows in the merged dataframe
print(f"Merged rows: {len(merged_df)}")
print(f"Merged columns: {len(merged_df.columns)} ({len(json_df.columns)} + {len(dicom_df_distinct_columns.columns)} - 3)") # 3 is for the merge keys

# Merge the merged dataframe with the group_key_df to add the MinMo_Group column
merged_df = merged_df.merge(group_key_df, on='SubjectID', how='left')
# Save the merged dataframe to a CSV file
merged_df.to_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv", index=False)