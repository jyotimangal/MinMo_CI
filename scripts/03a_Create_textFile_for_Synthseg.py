# Author: Jyoti Mangal, date 14/10/2026
# Script to generate input/output text files for SynthSeg in both Windows and Linux formats

import pandas as pd
from pathlib import Path
import re

metadata_df = pd.read_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv")
nifti_paths = metadata_df['NIfTIPath'].tolist()
netapp_dir = Path(r"W:/MinMo_CI")

# filter to relevant sequences only
exclude_mask = (
    metadata_df['NIfTIPath'].str.contains(r'_ph\.nii', na=False) |
    metadata_df['NIfTIPath'].str.contains('mIP|MIP', na=False) |
    metadata_df['SeriesDescription'].str.contains('localiser|localizer|ge_loc', case=False, na=False) |
    metadata_df['SeriesDescription'].str.contains('Med_DRS', case=False, na=False) |
    metadata_df['SeriesDescription'].str.contains('_Mag$', case=False, na=False) |
    metadata_df['SeriesDescription'].str.contains('MPR', case=False, na=False) |
    metadata_df['SeriesDescription'].str.contains('TRACEW|_ADC', case=False, na=False)
)

nifti_paths = metadata_df[~exclude_mask]['NIfTIPath'].tolist()
print(f"Filtered to {len(nifti_paths)} NIfTIs")

print(metadata_df[~exclude_mask]['SeriesDescription'].value_counts().head(20))

output_paths = []
for path in nifti_paths:
    p = Path(path)
    subject_id = next((part for part in p.parts if re.match(r'MinMo-\d{3}$', part)), 'unknown')
    out_path = netapp_dir / "derivatives" / "synthseg" / subject_id / (p.stem.replace('.nii', '') + '_seg.nii.gz')
    out_path.parent.mkdir(parents=True, exist_ok=True)
    output_paths.append(str(out_path))

# Windows format
with open(r"W:/MinMo_CI/derivatives/synthseg_input.txt", 'w') as f:
    for p in nifti_paths:
        f.write(p + '\n')

with open(r"W:/MinMo_CI/derivatives/synthseg_output.txt", 'w') as f:
    for p in output_paths:
        f.write(p + '\n')

# Linux format (no \r, forward slashes, /mnt/w/ prefix)
with open(r"C:/Users/jm19/MinMo_CI/synthseg_input_linux.txt", 'w', newline='\n') as f:
    for p in nifti_paths:
        f.write(p.replace('W:\\', '/mnt/w/').replace('\\', '/') + '\n')

with open(r"C:/Users/jm19/MinMo_CI/synthseg_output_linux.txt", 'w', newline='\n') as f:
    for p in output_paths:
        f.write(p.replace('W:\\', '/mnt/w/').replace('\\', '/') + '\n')

print(f"Generated {len(nifti_paths)} input paths and {len(output_paths)} output paths")