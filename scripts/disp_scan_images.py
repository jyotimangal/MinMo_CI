# Author: Jyoti Mangal, Date 15/10/2026
# Script to display the scans that have been identified as explicit repeat scans, and open them in ITK-SNAP for visual inspection.

import importlib
import utils
importlib.reload(utils)
from utils import open_in_itksnap, load_json_dicom_merged, truncate_right
import pandas as pd
import platform
from pathlib import Path

if platform.system() == 'Windows':
    netapp_dir = Path(r"W:/MinMo_CI/")
else:
    netapp_dir = Path.home() / "Documents/Postdoc_epilepsy/MinMo_CI"

PRINT_DIFF_COLS = True  # Set to True to print only columns with differences, False to print all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 200)

merged_df = utils.load_json_dicom_merged(netapp_dir, merge_on=['SubjectID', 'SeriesNumber', 'PulseSequenceName'], how='left')

for (group1, group2), group_df in merged_df.groupby(['SubjectID','PulseSequenceName']):
    # display those subjects that have repeat scans for the same pulse sequence 
    # those are the one that have repeat reference in ProtocolName, and subjects 31, 33, 63 has ax_t2_tse, t1_space_sag and ax_t2_tse thave no repeat reference in protocolname
    if not group_df['ProtocolName'].str.contains('RPT|repeat|rpt', case=False, na=False).any() and not (group1 in ['MinMo-031', 'MinMo-033', 'MinMo-063'] and group2 in ['ax_t2_tse', 't1_space_sag']):
        continue
    print(newline := "\n" + "="*80 + "\n")
    print(f"SubjectID: {group1}, PulseSequenceName: {group2}, Number of repeats in PulseSequence per Subject: {len(group_df)}")
    group_df_sorted = group_df.sort_values('SeriesNumber')
    diff_cols = [col for col in group_df_sorted.columns if group_df_sorted[col].nunique() > 1]
    if PRINT_DIFF_COLS:
        print(f"Columns with differences: {diff_cols}")
        print_df = group_df_sorted[diff_cols]
    else:
        print_df = group_df_sorted
    print_df = print_df.map(lambda x: truncate_right(x, 40))
    print(print_df.T.to_string())
    print(newline := "\n" + "="*80 + "\n")
    open_in_itksnap(group_df_sorted['NIfTIPath'].to_list()[::-1])
    user_input= input("Press enter to continue, or type 'q' to exit: ")
    if user_input.lower() == 'q':
        break