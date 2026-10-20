# Author: Jyoti Mangal, date: 19/10/2026
# Script that investigates minmo influence on repeat scans by analying metadata of repeat scan pairs

import pandas as pd
from pathlib import Path

#load the group key and metadata csv files
netapp_dir = Path(r"W:/MinMo_CI")
group_key_df = pd.read_csv(netapp_dir / "derivatives" / "group_key.csv")
explicit_repeat_df = pd.read_csv(netapp_dir / "derivatives" / "comparison_metadata_ExplicitRepeat_Reference.csv")
potential_silent_repeat_df = pd.read_csv(netapp_dir / "derivatives" / "comparison_metadata_SilentRepeat_Reference.csv")

# merge based on SubjectID column
explicit_repeat_df = pd.merge(group_key_df, explicit_repeat_df, on='SubjectID', how='inner')
potential_silent_repeat_df = pd.merge(group_key_df, potential_silent_repeat_df, on='SubjectID', how='inner')

explicit_loosest = explicit_repeat_df[
    (explicit_repeat_df['flag_localiser'] == False) &
    (explicit_repeat_df['flag_fat_sat_crossseq'] == False) &
    (explicit_repeat_df['flag_post_contrast_crossseq'] == False) &
    (explicit_repeat_df['flag_dwi_bvalue'] == False) &
    (explicit_repeat_df['flag_pre_contrast_crossseq'] == False)
]

silent_loosest = potential_silent_repeat_df[
    (potential_silent_repeat_df['flag_localiser'] == False) &
    (potential_silent_repeat_df['flag_fat_sat_crossseq'] == False) &
    (potential_silent_repeat_df['flag_post_contrast_crossseq'] == False) &
    (potential_silent_repeat_df['flag_dwi_bvalue'] == False) &
    (potential_silent_repeat_df['flag_pre_contrast_crossseq'] == False)
]

combined_df = pd.concat([explicit_loosest, silent_loosest], ignore_index=True)
combined_df.to_csv(netapp_dir / "derivatives" / "combined_loosest_repeat_pairs.csv", index=False)
#print(f"Combined: {len(combined_df)} rows, {combined_df['SubjectID'].nunique()} subjects")

combined_df_visual = pd.read_csv(netapp_dir / "derivatives" / "repeat_scan_visual_motion_assessment_combined.csv")
