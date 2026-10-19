# Author: Jyoti Mangal, Date: 19/10/2026
# QC script for explicit repeat scans - compares metadata between repeat and reference scans and generates a QC csv file with the results.

import pandas as pd
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI")
metadata_df = pd.read_csv(netapp_dir / "derivatives" / "all_metadata_xnat.csv")
explicit_repeat_df = pd.read_csv(netapp_dir / "derivatives" / "explicit_repeat_scans.csv")

qc_rows = []
for _, row in explicit_repeat_df.iterrows():
    ref = metadata_df[
    (metadata_df['SubjectID'] == row['SubjectID']) &
    (metadata_df['SeriesNumber'] == row['Reference_SeriesNumber']) &
    (metadata_df['SeriesDescription'] == row['Reference_SeriesDescription'])]

    if len(ref) == 0:
        continue

    ref = ref.iloc[0]

    desc_repeat = str(row['SeriesDescription']).lower()
    desc_ref = str(ref['SeriesDescription']).lower()
    dur_repeat = row['AcquisitionDuration']
    dur_ref = ref['AcquisitionDuration']
    matrix_repeat = row['AcquisitionMatrixPE']
    matrix_ref = ref['AcquisitionMatrixPE']
    slice_thickness_repeat = row['SliceThickness']
    slice_thickness_ref = ref['SliceThickness']

    qc_rows.append({
        'SubjectID': row['SubjectID'],
        'Reference_SeriesNumber': row['Reference_SeriesNumber'],
        'Reference_SeriesDescription': row['Reference_SeriesDescription'],
        'Repeat_SeriesNumber': row['SeriesNumber'],
        'Repeat_SeriesDescription': row['SeriesDescription'],
        'Reference_AcquisitionDuration': dur_ref,
        'Repeat_AcquisitionDuration': dur_repeat,
        'Reference_AcquisitionMatrixPE': matrix_ref,
        'Repeat_AcquisitionMatrixPE': matrix_repeat,
        'flag_pituitary': any(x in desc_repeat for x in ['pit','tse_2mm','tse 2mm']),
        'flag_spine_neck': any(x in desc_repeat for x in ['c2','c3','c4','c5','c6','c7','stir','spine']),
        'flag_small_fov': matrix_repeat < 150 if pd.notna(matrix_repeat) else False,
        'flag_small_fov_recon': row['ReconMatrixPE'] < 150 if pd.notna(row['ReconMatrixPE']) else False,
        'flag_slice_thickness_change': abs(slice_thickness_repeat - slice_thickness_ref)/ slice_thickness_ref >0.2 if pd.notna(slice_thickness_repeat) and pd.notna(slice_thickness_ref) else False,
        'flag_duration_change': abs(dur_repeat - dur_ref)/ dur_ref >0.2 if pd.notna(dur_repeat) and pd.notna(dur_ref) else False,
        'flag_repeat_longer': dur_repeat > dur_ref if pd.notna(dur_repeat) and pd.notna(dur_ref) else False,
        'Reference_SliceThickness': slice_thickness_ref,
        'Repeat_SliceThickness': slice_thickness_repeat
    })

qc_df = pd.DataFrame(qc_rows)
qc_df.to_csv(netapp_dir / "derivatives" / "comparison_metadata_ExplicitRepeat_Reference.csv", index=False)
print("QC results saved to comparison_metadata_ExplicitRepeat_Reference.csv")
