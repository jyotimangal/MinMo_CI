# Author: Jyoti Mangal, date 14/10/2026
# Script to generate input/output text files for SynthSeg in both Windows and Linux formats

import pandas as pd
from pathlib import Path
import re
from utils import get_derived_without_original

metadata_df = pd.read_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv")
netapp_dir = Path(r"W:/MinMo_CI")

metadata_df = pd.read_csv(r"W:/MinMo_CI/derivatives/all_metadata_xnat.csv")
print(f"Start: {len(metadata_df)} scans across {metadata_df['SubjectID'].nunique()} subjects")

# 1. Exclude DERIVED
original_df = metadata_df[~metadata_df['ImageType'].str.contains('DERIVED', case=False, na=False)]
derived_no_original_df = get_derived_without_original(metadata_df)
df1 = pd.concat([original_df, derived_no_original_df], ignore_index=True)
print(f"After excluding DERIVED with corresponding ORIGINAL: {len(df1)} scans across {df1['SubjectID'].nunique()} subjects")

# 2. Exclude phase images
mask1 = (
    df1['ImageType'].str.contains('PHASE', case=False, na=False) |
    df1['NIfTIPath'].str.contains(r'_ph\.nii', na=False)
)
df2 = df1[~mask1]
print(f"After excluding SWI phase images: {len(df2)} scans across {df2['SubjectID'].nunique()} subjects")

# 3. Exclude spine/neck
mask3 = df2['SeriesDescription'].str.contains(
    'spine|conus|coccyx|C2-C5|C3-C7|upper|lower|_mid|cervical|tse_stir', 
    case=False, na=False)
df3 = df2[~mask3]
print(f"After excluding spine/neck: {len(df3)} scans across {df3['SubjectID'].nunique()} subjects")

# 4. Exclude SWI where Mag exists
swi_mask = df3.apply(
    lambda row: ('_SWI' in row['SeriesDescription'] or 'swi_ge3d_SWI' in row['SeriesDescription']) and
    len(df3[
        (df3['SubjectID'] == row['SubjectID']) &
        (df3['SeriesDescription'].str.contains('_Mag', case=False, na=False))
    ]) > 0, axis=1
)
df4 = df3[~swi_mask]
print(f"After excluding SWI where Mag exists: {len(df4)} scans across {df4['SubjectID'].nunique()} subjects")

# 5. Exclude localisers
mask4 = df4['SeriesDescription'].str.contains('localiser|localizer|ge_loc', case=False, na=False)
df5 = df4[~mask4]
print(f"After excluding localisers: {len(df5)} scans across {df5['SubjectID'].nunique()} subjects")

nifti_paths = df5['NIfTIPath'].tolist()
print(f"Filtered to {len(nifti_paths)} NIfTIs")
print(df5['SeriesDescription'].value_counts().head(20))

output_paths = []
resample_paths = []
qc_paths = []
vol_paths = []

for path in nifti_paths:
    p = Path(path)
    subject_id = next((part for part in p.parts if re.match(r'MinMo-\d{3}$', part)), 'unknown')
    stem = p.stem.replace('.nii', '')
    
    out_path = netapp_dir / "derivatives" / "synthseg" / subject_id / (stem + '_seg.nii.gz')
    resample_path = netapp_dir / "derivatives" / "synthseg_resampled" / subject_id / (stem + '_resampled.nii.gz')
    qc_path = netapp_dir / "derivatives" / "synthseg_qc" / subject_id / (stem + '_qc.csv')
    vol_path = netapp_dir / "derivatives" / "synthseg_vol" / subject_id / (stem + '_vol.csv')
    
    for p_out in [out_path, resample_path, qc_path, vol_path]:
        p_out.parent.mkdir(parents=True, exist_ok=True)
    
    output_paths.append(str(out_path))
    resample_paths.append(str(resample_path))
    qc_paths.append(str(qc_path))
    vol_paths.append(str(vol_path))

# Linux format for bioeng426 (no \r, forward slashes, /mnt/w/ prefix)
with open(r"W:/MinMo_CI/synthseg_input_windows.txt", 'w', newline='\n') as f:
    for p in nifti_paths:
        f.write(p.replace('W:\\', '/mnt/w/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_output_windows.txt", 'w', newline='\n') as f:
    for p in output_paths:
        f.write(p.replace('W:\\', '/mnt/w/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_resample_windows.txt", 'w', newline='\n') as f:
    for p in resample_paths:
        f.write(p.replace('W:\\', '/mnt/w/').replace('\\', '/') + '\n')

# Linux format for bioeng454 (/home/jm19/mnt/mbig/)
with open(r"W:/MinMo_CI/synthseg_input_linux_454.txt", 'w', newline='\n') as f:
    for p in nifti_paths:
        f.write(p.replace('W:\\', '/home/jm19/mnt/mbig/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_output_linux_454.txt", 'w', newline='\n') as f:
    for p in output_paths:
        f.write(p.replace('W:\\', '/home/jm19/mnt/mbig/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_resample_linux_454.txt", 'w', newline='\n') as f:
    for p in resample_paths:
        f.write(p.replace('W:\\', '/home/jm19/mnt/mbig/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_qc_linux_454.txt", 'w', newline='\n') as f:
    for p in qc_paths:
        f.write(p.replace('W:\\', '/home/jm19/mnt/mbig/').replace('\\', '/') + '\n')

with open(r"W:/MinMo_CI/synthseg_vol_linux_454.txt", 'w', newline='\n') as f:
    for p in vol_paths:
        f.write(p.replace('W:\\', '/home/jm19/mnt/mbig/').replace('\\', '/') + '\n')

print(f"Generated {len(nifti_paths)} input paths and {len(output_paths)} output paths and {len(resample_paths)} resample paths for SynthSeg.")