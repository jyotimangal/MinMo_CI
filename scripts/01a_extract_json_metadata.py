# Script that traverses the MinMo_CI directory and extracts key metadata fields from JSON files into a CSV file for further analysis
import json
import pandas as pd
from pathlib import Path
import re
import platform
from utils import get_orientation_from_iopField

if platform.system() == 'Windows':
    netapp_dir = Path(r"W:/MinMo_CI/")
else:
    netapp_dir = Path.home() / "Documents/Postdoc_epilepsy/MinMo_CI"
 
# create an empty list to store metadata dictionaries
metadata_list = []

# walk recursively through the root directory for all folders and files
for path in (netapp_dir / "raw_xnat").rglob("*.json"):
    # check if the path is a file
    if path.is_file():
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
                print(f"Processing file: {path}")
                series_match = re.match(r'S(\d+)_', path.stem)
                metadata = {
                        'SubjectID': next((p for p in Path(str(path)).parts if re.match(r'MinMo-\d{3}$', p)), 'unknown'),
                        'NIfTIPath': str(path.with_suffix('.nii.gz')),
                        'SeriesNumber': int(series_match.group(1)) if series_match else None,
                        'Orientation': get_orientation_from_iopField(data.get('ImageOrientationPatientDICOM')),
                        **data
                    }
                metadata_list.append(metadata)
        except Exception as e:
            print(f"Could not read {path} as JSON: {e}")

print(f"Total JSON files found: {len(metadata_list)}")
df = pd.DataFrame(metadata_list)
df.to_csv(netapp_dir / "derivatives" / "JSON_metadata_xnat.csv", index=False)