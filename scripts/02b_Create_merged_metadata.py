#Author: Jyoti Mangal, Date 14/10/2026
#Script to merge the json and dicom metadata csv files and create a final metadata csv file for the MinMo-CI project

#Based on 02a_A_quicklook_at_metadata.py's results and exploration of the metadata (noted on Notion), 
#For the rows/scans in json_metadata_xnat.csv that have SeriesDescription=haste_localiser, only those are retained that have Orientation=axial
#This is to have a homogenous localiser scan entry

import pandas as pd

json_df = pd.read_csv(r"W:/MinMo_CI/derivatives/json_metadata_xnat.csv")
dicom_df = pd.read_csv(r"W:/MinMo_CI/derivatives/dicom_metadata_xnat.csv")

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


#Merge the filtered JSON metadata with the DICOM metadata on SubjectID, SeriesNumber, and SeriesDescription
merged_df = json_filtered_df.merge(dicom_df, on=['SubjectID', 'SeriesNumber', 'SeriesDescription'], how='left')

# Print the number of rows in the merged dataframe
print(f"Merged rows: {len(merged_df)}")

# Save the merged dataframe to a CSV file
merged_df.to_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv", index=False)