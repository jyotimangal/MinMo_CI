# Script to inventory DICOM files in the MinMo_CI directory and extract key metadata fields into a CSV file for further analysis
import pydicom
from pathlib import Path
import pandas as pd
import re
import platform
from utils import get_nested_field

if platform.system() == 'Windows':
    netapp_dir = Path(r"W:/MinMo_CI/")
else:
    netapp_dir = Path.home() / "Documents/Postdoc_epilepsy/MinMo_CI"

metadata_list = []

for path in sorted((netapp_dir / "raw_xnat").rglob("*")):
    if path.is_file():
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            print(f"Processing file: {path}")
            subject_id = next((p for p in Path(str(path)).parts if re.match(r'MinMo-\d{3}$', p)), 'unknown')
            series_number = int(path.parent.parent.name) if path.parent.parent.name.isdigit() else ds.get('SeriesNumber')
            if ds.get('Modality') == 'MR':
                metadata = {
                    'SubjectID': subject_id,
                    'SeriesNumber': series_number,
                    'FilePath': str(path),
                    'StudyDate': ds.get('StudyDate'),
                    'ImageType': ds.get('ImageType'),
                    'PulseSequenceName': ds.get('PulseSequenceName'),
                    'SeriesInstanceUID': ds.get('SeriesInstanceUID'),
                    'StudyInstanceUID': ds.get('StudyInstanceUID'),
                    'Modality': ds.get('Modality'),
                    'MagneticFieldStrength': ds.get('MagneticFieldStrength'),
                    'Manufacturer': ds.get('Manufacturer'),
                    'InstanceNumber': ds.get('InstanceNumber'),
                    'MRAcquisitionType': ds.get('MRAcquisitionType'),
                    'SeriesDescription': ds.get('SeriesDescription'),      
                    # nested extractions — work for both old and new batch
                    'RepetitionTime': get_nested_field(ds, (0x5200,0x9229), (0x0018,0x9112), (0x0018,0x0080)),
                    'FlipAngle': get_nested_field(ds, (0x5200,0x9229), (0x0018,0x9112), (0x0018,0x1314)),
                    'SliceThickness': get_nested_field(ds, (0x5200,0x9230), (0x0028,0x9110), (0x0018,0x0050)),
                    'EchoTime': get_nested_field(ds, (0x5200,0x9230), (0x0018,0x9114), (0x0018,0x9082)),
                    'FrameAcquisitionDateTime': get_nested_field(ds, (0x5200,0x9230), (0x0020,0x9111), (0x0018,0x9074))
                }
                metadata_list.append(metadata)

        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")

print(f"Total MR DICOM files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
df = df.drop_duplicates(subset=['SeriesInstanceUID'])
df.to_csv(netapp_dir / "derivatives" / "dicom_metadata_xnat.csv", index=False)
print(f"Saved dicom_metadata_xnat.csv with {len(df)} rows and {len(df.columns)} columns")