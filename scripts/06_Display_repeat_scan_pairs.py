# Author: Jyoti Mangal, Date: 16/10/2026
# Script to display explicit repeat scan pairs in ITK-SNAP for visual inspection on ITKSNAP

import importlib
import utils
from utils import similarity, get_nifti_path, truncate_right, open_in_itksnap
import pandas as pd
from pathlib import Path

mode = 'silent' # or 'silent'

netapp_dir = Path(r"W:/MinMo_CI/")
metadata_df = pd.read_csv(netapp_dir / "derivatives" / "all_metadata_xnat.csv")

if mode == 'explicit':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "explicit_repeat_scans.csv")
elif mode == 'silent':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "potential_silent_repeat_scans.csv")

for _, row in repeat_df.iterrows():
    ref_series = [int(row['Reference_SeriesNumber'])] if pd.notna(row['Reference_SeriesNumber']) else []

    paths = [row['NIfTIPath']] + [get_nifti_path(metadata_df, row['SubjectID'], s) for s in ref_series]
    paths = [p for p in paths if p is not None]

    ref_str = f"S{int(row['Reference_SeriesNumber'])} {row['Reference_SeriesDescription']}" if pd.notna(row['Reference_SeriesNumber']) else "No reference found"
    print(f"SubjectID: {row['SubjectID']}, SeriesNumber: {row['SeriesNumber']}, SeriesDescription: {truncate_right(row['SeriesDescription'], 50)}, Reference: {ref_str}")    
    open_in_itksnap(paths)
    user_input = input("Press Enter to continue to the next pair, or type q to quit: ")
    if user_input.lower() == 'q':
        break
