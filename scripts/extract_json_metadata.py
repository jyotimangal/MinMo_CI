# Script that traverses the MinMo_CI directory and extracts key metadata fields from JSON files into a CSV file for further analysis
import json
import pandas as pd
from pathlib import Path
import re

netapp_dir = Path(r"W:/MinMo_CI/")
# create an empty list to store metadata dictionaries
TARGET_SEQUENCE_NAME =  "*tse2d1_17"
#TARGET_SEQUENCE_NAME = None
metadata_list = []
# walk recursively through the root directory for all folders and files
for path in (netapp_dir / "niftis").rglob("*.json"):
    # check if the path is a file
    if path.is_file():
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                print(f"Processing file: {path}")
                # extract relevant metadata fields from the JSON data
                metadata = {
                        'SeriesHash': path.parent.name,
                        'MagneticFieldStrength': data.get('MagneticFieldStrength'),
                        'MRAcquisitionType': data.get('MRAcquisitionType'),
                        'PulseSequenceName': data.get('PulseSequenceName'),
                        'SliceThickness': data.get('SliceThickness'),
                        'EchoTime': data.get('EchoTime'),
                        'RepetitionTime': data.get('RepetitionTime'),
                        'FlipAngle': data.get('FlipAngle'),
                        'EchoTrainLength': data.get('EchoTrainLength'),
                        'ParallelReductionFactorInPlane': data.get('ParallelReductionFactorInPlane'),
                        'AcquisitionDuration': data.get('AcquisitionDuration'),
                        'PixelBandwidth': data.get('PixelBandwidth'),
                        'ImageOrientationPatientDICOM': str(data.get('ImageOrientationPatientDICOM')),
                        'BidsGuess': str(data.get('BidsGuess')),
                        'NIfTIPath': str(path.with_suffix('.nii.gz')),

                    }
                if TARGET_SEQUENCE_NAME is None or (metadata['PulseSequenceName'] and re.search(re.escape(TARGET_SEQUENCE_NAME.replace('*', '')), str(metadata['PulseSequenceName']))):
                    metadata_list.append(metadata)
        except Exception as e:
            print(f"Could not read file {path} as JSON: {e}")

# create a datafram from the metadata list and save it to a csv file 
print(f"Total JSON files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
suffix = f"_{TARGET_SEQUENCE_NAME.replace('*', '')}" if TARGET_SEQUENCE_NAME else "_all"
df.to_csv(netapp_dir / "derivatives" / f"JSON_metadata_inventory{suffix}.csv", index=False)