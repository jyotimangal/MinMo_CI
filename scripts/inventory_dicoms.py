# Script to inventory DICOM files in the MinMo_CI directory and extract key metadata fields into a CSV file for further analysis
# import packages
import pydicom
from pathlib import Path
import pandas as pd

netapp_dir = Path(r"W:/MinMo_CI/")

# create an empty list to store metadata dictionaries
metadata_list = []
# walk recursively through the root directory for all folders and files
for path in netapp_dir.rglob("*"):
    # check if the path is a file
    if path.is_file():
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            # check if the DICOM file has a Modality field and if it is MR
            if ds.get('Modality') == 'MR':
                print(f"Read MR DICOM file: {path}")
                metadata = {
                    'FilePath': str(path),
                    'PatientID': ds.get('PatientID', 'N/A'),
                    'PatientName': ds.get('PatientName', 'N/A'),
                    'StudyDate': ds.get('StudyDate', 'N/A'),
                    'SeriesDescription': ds.get('SeriesDescription', 'N/A'),
                    'ImageType': ds.get('ImageType', 'N/A'),
                    'PulseSequenceName': ds.get('PulseSequenceName', 'N/A'),
                    'SeriesNumber': ds.get('SeriesNumber', 'N/A'),
                    'SeriesInstanceUID': ds.get('SeriesInstanceUID', 'N/A'),
                    'StudyInstanceUID': ds.get('StudyInstanceUID', 'N/A'),
                    'Modality': ds.get('Modality', 'N/A'),
                    'FieldStrength': ds.get('MagneticFieldStrength', 'N/A'),
                    'Manufacturer': ds.get('Manufacturer', 'N/A')
                }
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")

# create a dataframe from the metadata list and save it to a CSV file
print(f"Total MR DICOM files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
df.to_csv(netapp_dir/"derivatives"/"MinMo_001_to_005_DICOM_Metadata.csv", index=False)