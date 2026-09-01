import importlib
import utils
importlib.reload(utils)
from utils import open_in_itksnap
import pandas as pd
import platform
from pathlib import Path

if platform.system() == 'Windows':
    netapp_dir = Path(r"W:/MinMo_CI/")
else:
    netapp_dir = Path.home() / "Documents/Postdoc_epilepsy/MinMo_CI"

merged_df = pd.read_csv(netapp_dir / "derivatives" / "NGS_json_merged_all.csv")

for (group1, group2), group_df in merged_df.groupby(['SubjectID','PulseSequenceName']):
    print(newline := "\n" + "="*80 + "\n")
    print(f"SubjectID: {group1}, PulseSequenceName: {group2}, Number of repeats in PulseSequence per Subject: {len(group_df)}")
    group_df_sorted = group_df.sort_values('SeriesNumber')
    print(group_df_sorted[['FilePath', 'SeriesNumber', 'EchoTime', 'RepetitionTime', 'FlipAngle','Orientation','BidsGuess','MagneticFieldStrength']])
    open_in_itksnap(group_df.sort_values('SeriesNumber')['FilePath'].to_list())
    print(newline := "\n" + "="*80 + "\n")
    user_input= input("Press enter to continue, or type 'q' to exit: ")
    if user_input.lower() == 'q':
        break