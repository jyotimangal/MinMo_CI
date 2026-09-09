# Script to inventory DICOM files in the MinMo_CI directory and extract key metadata fields into a CSV file for further analysis
import pydicom
from pathlib import Path
import pandas as pd
import re
import sys
import platform

if platform.system() == "Windows":
    netapp_dir = Path(r"W:/MinMo_CI/")
else:
    print("This script is designed to run on Windows. Please adjust the netapp_dir path.")
    exit(1)

TARGET_SEQUENCE_NAME = "*tse2d1_17"
TARGET_SEQUENCE_NAME = None

DEBUG_MODE = False

metadata_list = []

for path in sorted((netapp_dir / "raw").rglob("*")):
    if path.is_file():
        try:
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            if ds.get('Modality') == 'MR' and (TARGET_SEQUENCE_NAME is None or ds.get('PulseSequenceName') == TARGET_SEQUENCE_NAME):
                print(f"Read MR DICOM file: {path}")
                metadata = {
                    'FilePath': str(path),
                    'SubjectID': re.sub(r'Min-Mo-', 'MinMo-', next((p for p in Path(str(path)).parts if re.match(r'Min-?Mo-\d{3}$', p)), 'unknown')),
                    'StudyDate': ds.get('StudyDate', 'N/A'),
                    'ImageType': ds.get('ImageType', 'N/A'),
                    'PulseSequenceName': ds.get('PulseSequenceName', 'N/A'),
                    'SeriesNumber': ds.get('SeriesNumber', 'N/A'),
                    'SeriesInstanceUID': ds.get('SeriesInstanceUID', 'N/A'),
                    'StudyInstanceUID': ds.get('StudyInstanceUID', 'N/A'),
                    'Modality': ds.get('Modality', 'N/A'),
                    'FieldStrength': ds.get('MagneticFieldStrength', 'N/A'),
                    'Manufacturer': ds.get('Manufacturer', 'N/A'),
                    'InstanceNumber': ds.get('InstanceNumber', 'N/A'),
                    'MRAcquisitionType': ds.get('MRAcquisitionType', 'N/A'),
                    'SeriesDescription': ds.get('SeriesDescription', 'N/A'),                }

                # nested extractions — work for both old and new batch
                try:
                    timing = ds[(0x5200, 0x9229)][0][(0x0018, 0x9112)][0]
                    metadata['FlipAngle'] = str(timing[(0x0018, 0x1314)].value)
                    metadata['RepetitionTime'] = str(timing[(0x0018, 0x0080)].value)
                except:
                    metadata['FlipAngle'] = 'N/A'
                    metadata['RepetitionTime'] = 'N/A'

                try:
                    pixel = ds[(0x5200, 0x9230)][0][(0x0028, 0x9110)][0]
                    metadata['SliceThickness'] = str(pixel[(0x0018, 0x0050)].value)
                except:
                    metadata['SliceThickness'] = 'N/A'

                try:
                    echo = ds[(0x5200, 0x9230)][0][(0x0018, 0x9114)][0]
                    metadata['EchoTime'] = str(echo[(0x0018, 0x9082)].value)
                except:
                    metadata['EchoTime'] = 'N/A'

                try:
                    frame_content = ds[(0x5200, 0x9230)][0][(0x0020, 0x9111)][0]
                    metadata['FrameAcquisitionDateTime'] = str(frame_content[(0x0018, 0x9074)].value)
                except:
                    metadata['FrameAcquisitionDateTime'] = 'N/A'

                if DEBUG_MODE:
                    for elem in ds:
                        if elem.keyword and elem.keyword not in metadata:
                            try:
                                metadata[elem.keyword] = str(elem.value)
                            except:
                                metadata[elem.keyword] = 'N/A'

                metadata_list.append(metadata)

        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")

print(f"Total MR DICOM files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
df = df.drop_duplicates(subset=['SeriesInstanceUID'])
suffix = f"_{TARGET_SEQUENCE_NAME.replace('*', '')}" if TARGET_SEQUENCE_NAME else "_all"
df.to_csv(netapp_dir / "derivatives" / f"DICOM_inventory{suffix}.csv", index=False)
print(f"Saved to DICOM_inventory{suffix}.csv with {len(df)} rows and {len(df.columns)} columns")