import pandas as pd

json_df = pd.read_csv(r"W:/MinMo_CI/derivatives/json_metadata_xnat.csv")
dicom_df = pd.read_csv(r"W:/MinMo_CI/derivatives/dicom_metadata_xnat.csv")

print(f"JSON rows: {len(json_df)}, DICOM rows: {len(dicom_df)}")

# duplicates in JSON on SubjectID + SeriesNumber
dupes_json = json_df[json_df.duplicated(subset=['SubjectID', 'SeriesNumber'], keep=False)]
print(f"\nJSON duplicates: {len(dupes_json)}")
print(dupes_json[['SubjectID', 'SeriesNumber', 'SeriesDescription']].sort_values(['SubjectID', 'SeriesNumber']))

# duplicates in DICOM on SubjectID + SeriesNumber  
dupes_dicom = dicom_df[dicom_df.duplicated(subset=['SubjectID', 'SeriesNumber'], keep=False)]
print(f"\nDICOM duplicates: {len(dupes_dicom)}")
print(dupes_dicom[['SubjectID', 'SeriesNumber', 'SeriesDescription']].sort_values(['SubjectID', 'SeriesNumber']))