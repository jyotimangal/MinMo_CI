# script for analysing NGS results, loading the csv file with the ngs results
# and the csv file with the DICOM metadata, merging them based on the file paths
# and performing some exploratory data analysis to see if there are any relationships between 
# the NGS values and the DICOM metadata fields such as orientation, pulse sequence name, etc.
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI/")
TARGET_SEQUENCE_NAME =  "*tse2d1_17"
# load the NGS results and DICOM metadata csv files
ngs_results_df = pd.read_csv(netapp_dir / "derivatives" / f"MinMo_NGS_Results.csv")
dicom_metadata_df = pd.read_csv(netapp_dir / "derivatives" / f"MinMo_DICOM_{TARGET_SEQUENCE_NAME.replace('*', '')}_Metadata.csv")

# merge the two dataframes based on a common series hash in the file paths
dicom_metadata_df['SeriesHash'] = dicom_metadata_df['FilePath'].apply(lambda x: Path(x).parent.name)
ngs_results_df['SeriesHash'] = ngs_results_df['FilePath'].apply(lambda x: Path(x).parent.name)

# drop the file path column from the dicom metadata dataframe to avoid confusion after merging
dicom_metadata_df = dicom_metadata_df.drop(columns=['FilePath'])

# merge on series hash
merged_df = dicom_metadata_df.merge(ngs_results_df, on='SeriesHash', how='left')
merged_df['QC_flag'] = merged_df['Num_voxels_in_mask_Eroded'] < 1000  # flag if fewer than 1000 brain voxels after erosion

# save the merged dataframe to a new csv file 
merged_csv_file = netapp_dir / "derivatives" / f"MinMo_NGS_DICOM_Merged_{TARGET_SEQUENCE_NAME.replace('*', '')}.csv"
merged_df.to_csv(merged_csv_file, index=False)
print(f"Merged NGS and DICOM metadata saved to {merged_csv_file}")

# limit to axial images that don't contain 'Med_DRS_480' for further analysis
axial_df = merged_df[
    (merged_df['Orientation'] == 'axial') & (~merged_df['FilePath'].str.contains('Med_DRS_480'))
]
# sort the axial dataframe by SeriesNumber and drop duplicates based on PatientID to keep only one scan per patient for the axial analysis
axial_df = axial_df.sort_values('SeriesNumber').drop_duplicates(subset='PatientID', keep='first')

# perform exploratory data analysis
# plot the distribution of mean NGS values for all images
plt.figure(figsize=(10, 6))
sns.histplot(merged_df['Mean_NGS'], bins=31, kde=True)
plt.title('Distribution of Mean NGS Values for Axial Images')
plt.xlabel('Mean NGS')
plt.ylabel('Frequency')
plt.show()