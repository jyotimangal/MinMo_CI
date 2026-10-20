import pandas as pd

json_df = pd.read_csv(r"W:/MinMo_CI/derivatives/json_metadata_xnat.csv")
dicom_df = pd.read_csv(r"W:/MinMo_CI/derivatives/dicom_metadata_xnat.csv")
group_key_df = pd.read_csv(r"W:/MinMo_CI/derivatives/group_key.csv")
json_df = json_df.merge(group_key_df, on='SubjectID', how='left')
dicom_df = dicom_df.merge(group_key_df, on='SubjectID', how='left')
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

# duplicates in JSON on SubjectID + SeriesNumber
dupes_json = json_df[json_df.duplicated(subset=['SubjectID', 'SeriesNumber'], keep=False)]
# duplicates in DICOM on SubjectID + SeriesNumber  
dupes_dicom = dicom_df[dicom_df.duplicated(subset=['SubjectID', 'SeriesNumber'], keep=False)]

# print the number of rows in each dataframe
print(f"JSON rows: {len(json_df)}, DICOM rows: {len(dicom_df)}")
# print the duplicates with relevant columns
print(f"\nJSON duplicates: {len(dupes_json)}")
print(dupes_json[['MinMo_Group', 'SubjectID', 'SeriesNumber', 'SeriesDescription','Orientation','ImageType']].sort_values(['SubjectID', 'SeriesNumber']))
# print the duplicates with relevant columns
print(f"\nDICOM duplicates: {len(dupes_dicom)}")
print(dupes_dicom[['MinMo_Group', 'SubjectID', 'SeriesNumber', 'SeriesDescription','ImageType','FrameAcquisitionDateTime','TimeSinceSessionStart']].sort_values(['SubjectID', 'SeriesNumber']))