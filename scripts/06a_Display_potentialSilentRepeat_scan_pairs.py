# Author: Jyoti Mangal, Date: 19/10/2026
# Script to display potentially silent scan pairs in ITK-SNAP for visual inspection on ITKSNAP

import importlib
from utils import similarity, get_nifti_path, truncate_right, open_in_itksnap
import pandas as pd
import ast
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI/")
metadata_df = pd.read_csv(netapp_dir / "derivatives" / "all_metadata_xnat.csv")
repeat_df = pd.read_csv(netapp_dir / "derivatives" / "potential_silent_repeat_scans.csv")

for _, row in repeat_df.iterrows():
    ref_series = ast.literal_eval(row['potential_silent_repeat_seriesNumbers'])  # Convert string representation of list to actual list
    if ref_series == None:
        print(f"No reference series found for SubjectID: {row['SubjectID']}, SeriesNumber: {row['SeriesNumber']}")
        continue

    paths = [row['NIfTIPath']] + [get_nifti_path(metadata_df, row['SubjectID'], s) for s in ref_series]
    paths = [p for p in paths if p is not None]

    print(f"SubjectID: {row['SubjectID']}, SeriesNumber: {row['SeriesNumber']}, SeriesDescription: {truncate_right(row['SeriesDescription'], 50)}, Potential Silent Repeat Series: {ref_series}")
    open_in_itksnap(paths)
    user_input = input("Press Enter to continue, or type q to quit: ")
    if user_input.lower() == 'q':
        break
