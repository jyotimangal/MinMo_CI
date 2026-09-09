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
    #if len(group_df) == 1: # use this condition to skip groups with only one entry
        #continue
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