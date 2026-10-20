# Author: Jyoti Mangal, Date: 16/10/2026
# Script to display explicit repeat scan pairs in ITK-SNAP for visual inspection on ITKSNAP

import importlib
import utils
from utils import similarity, get_nifti_path, truncate_right, open_in_itksnap
import pandas as pd
from pathlib import Path

mode = 'combined' # or 'silent'

netapp_dir = Path(r"W:/MinMo_CI/")
metadata_df = pd.read_csv(netapp_dir / "derivatives" / "all_metadata_xnat.csv")

if mode == 'explicit':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "explicit_repeat_scans.csv")
elif mode == 'silent':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "potential_silent_repeat_scans.csv")
elif mode == 'combined':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "combined_loosest_repeat_pairs.csv")

repeat_df['visual_motion_assessment'] = None

for idx, row in repeat_df.iterrows():
    ref_series = [int(row['Reference_SeriesNumber'])] if pd.notna(row['Reference_SeriesNumber']) else []

    if mode == 'combined':
        paths = [row['Repeat_NIfTIPath'], row['Reference_NIfTIPath']]
    else:
        paths = [row['NIfTIPath']] + [get_nifti_path(metadata_df, row['SubjectID'], s) for s in ref_series]

    paths = [p for p in paths if pd.notna(p)]

    series_num = row.get('Repeat_SeriesNumber') or row.get('SeriesNumber')
    series_desc = row.get('Repeat_SeriesDescription') or row.get('SeriesDescription')
    ref_num = row.get('Reference_SeriesNumber')
    ref_desc = row.get('Reference_SeriesDescription')
    ref_str = f"S{int(ref_num)} {ref_desc}" if pd.notna(ref_num) else "No reference found"
    print(f"SubjectID: {row['SubjectID']} | Group: {row.get('MinMo_Group', 'N/A')} | "
      f"Repeat: S{series_num} {series_desc} | Reference: {ref_str}")
    print("Opening in ITK-SNAP")
    open_in_itksnap(paths)
    user_input = input("Press Enter/y (motion reduced), n (motion worse), ? (unclear), q to quit: ").strip().lower()
    if user_input == 'q':
        break
    assessment = user_input if user_input in ['y', 'n', '?'] else 'y'
    repeat_df.at[idx, 'visual_motion_assessment'] = assessment

repeat_df.to_csv(netapp_dir / "derivatives" / f"repeat_scan_visual_motion_assessment_{mode}.csv", index=False)
