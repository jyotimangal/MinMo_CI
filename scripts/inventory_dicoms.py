# Script to inventory DICOM files in the MinMo_CI directory and extract key metadata fields into a CSV file for further analysis
# import packages
import pydicom
from pathlib import Path
import pandas as pd
import re

netapp_dir = Path(r"W:/MinMo_CI/")
TARGET_SEQUENCE_NAME =  "*tse2d1_17"
TARGET_SEQUENCE_NAME = None
# create an empty list to store metadata dictionaries
metadata_list = []
# walk recursively through the root directory for all folders and files
for path in (netapp_dir / "raw").rglob("*"):
    # check if the path is a file
    if path.is_file():
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            # check if the DICOM file has a Modality field and if it is MR
            if ds.get('Modality') == 'MR' and (TARGET_SEQUENCE_NAME is None or ds.get('PulseSequenceName') == TARGET_SEQUENCE_NAME):
                print(f"Read MR DICOM file: {path}")
                metadata = {
                    'FilePath': str(path),
                    'PatientID': ds.get('PatientID', 'N/A'),
                    'PatientName': ds.get('PatientName', 'N/A'),
                    'SubjectID':  next((p for p in Path(str(path)).parts if re.match(r'Min-?Mo-\d{3}$', p)), 'unknown'), # extract the subject ID from the path if it matches the pattern MinMo-XXX or Min-Mo-XXX, otherwise set to 'unknown'
                    'StudyDate': ds.get('StudyDate', 'N/A'),
                    'ImageType': ds.get('ImageType', 'N/A'),
                    'PulseSequenceName': ds.get('PulseSequenceName', 'N/A'),
                    'SeriesNumber': ds.get('SeriesNumber', 'N/A'),
                    'SeriesInstanceUID': ds.get('SeriesInstanceUID', 'N/A'),
                    'StudyInstanceUID': ds.get('StudyInstanceUID', 'N/A'),
                    'Modality': ds.get('Modality', 'N/A'),
                    'FieldStrength': ds.get('MagneticFieldStrength', 'N/A'),
                    'Manufacturer': ds.get('Manufacturer', 'N/A'),
                    'StudyTime': ds.get('StudyTime', 'N/A'),
                    'InstanceCreationTime': ds.get('InstanceCreationTime', 'N/A'),
                    'InstanceNumber': ds.get('InstanceNumber', 'N/A')
                    }
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")

# create a dataframe from the metadata list and save it to a CSV file
print(f"Total MR DICOM files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
df = df.drop_duplicates(subset=['SeriesInstanceUID'])  # drop duplicates based on SeriesInstanceUID 
suffix = f"_{TARGET_SEQUENCE_NAME.replace('*', '')}" if TARGET_SEQUENCE_NAME else "_all"
df.to_csv(netapp_dir / "derivatives" / f"DICOM_inventory{suffix}.csv", index=False)