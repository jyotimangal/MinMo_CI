# Author: Jyoti Mangal, Date: 19/10/2026
# Script to compare metadata between repeat and reference scans and generate a QC csv file

import pandas as pd
import nibabel as nib
from pathlib import Path

mode = 'explicit'  # or 'silent'

netapp_dir = Path(r"W:/MinMo_CI")
metadata_df = pd.read_csv(netapp_dir / "derivatives" / "all_metadata_xnat.csv")

if mode == 'explicit':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "explicit_repeat_scans.csv")
    output_filename = "comparison_metadata_ExplicitRepeat_Reference.csv"
elif mode == 'silent':
    repeat_df = pd.read_csv(netapp_dir / "derivatives" / "potential_silent_repeat_scans.csv")
    output_filename = "comparison_metadata_SilentRepeat_Reference.csv"

qc_rows = []
for _, row in repeat_df.iterrows():
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

    try:
        nslices_repeat = nib.load(row['NIfTIPath']).shape[2]
    except:
        nslices_repeat = None
    try:
        ref_nifti_path = metadata_df[(metadata_df['SubjectID'] == row['SubjectID']) & (metadata_df['SeriesNumber'] == row['Reference_SeriesNumber'])]['NIfTIPath'].values[0]
        nslices_ref = nib.load(ref_nifti_path).shape[2]
    except:
        nslices_ref = None

    qc_rows.append({
        'SubjectID': row['SubjectID'],
        'flag_explicit_repeat': mode == 'explicit',
        'Reference_SeriesNumber': row['Reference_SeriesNumber'],
        'Reference_SeriesDescription': row['Reference_SeriesDescription'],
        'Repeat_SeriesNumber': row['SeriesNumber'],
        'Repeat_SeriesDescription': row['SeriesDescription'],
        'Reference_AcquisitionDuration': dur_ref,
        'Repeat_AcquisitionDuration': dur_repeat,
        'Reference_AcquisitionMatrixPE': matrix_ref,
        'Repeat_AcquisitionMatrixPE': matrix_repeat,
        'Reference_SliceThickness': slice_thickness_ref,
        'Repeat_SliceThickness': slice_thickness_repeat,
        'Reference_NSlices': nslices_ref,
        'Repeat_NSlices': nslices_repeat,
        'flag_pituitary': any(x in desc_repeat for x in ['pit', 'tse_2mm', 'tse 2mm']),
        'flag_spine_neck': any(x in desc_repeat for x in ['c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'stir', 'spine']),
        'flag_fat_sat': 'fs' in desc_repeat and 'fs' not in desc_ref,
        'flag_dwi_bvalue': any(x in desc_repeat for x in ['b0', 'b1000']),
        'flag_localiser': any(x in desc_repeat for x in ['localiser', 'localizer']),
        'flag_post_contrast': 'post' in desc_repeat and 'post' not in desc_ref,
        'flag_small_fov': matrix_repeat < 150 if pd.notna(matrix_repeat) else False,
        'flag_small_fov_recon': row['ReconMatrixPE'] < 150 if pd.notna(row['ReconMatrixPE']) else False,
        'flag_slice_thickness_change': abs(slice_thickness_repeat - slice_thickness_ref) / slice_thickness_ref > 0.2 if pd.notna(slice_thickness_repeat) and pd.notna(slice_thickness_ref) else False,
        'flag_duration_change': abs(dur_repeat - dur_ref) / dur_ref > 0.2 if pd.notna(dur_repeat) and pd.notna(dur_ref) else False,
        'flag_repeat_longer': dur_repeat > dur_ref if pd.notna(dur_repeat) and pd.notna(dur_ref) else False,
        'flag_protocol_upgrade': matrix_repeat > matrix_ref if pd.notna(matrix_repeat) and pd.notna(matrix_ref) else False,
        'flag_slice_count_change': nslices_repeat != nslices_ref if nslices_repeat and nslices_ref else False,
    })

qc_df = pd.DataFrame(qc_rows)
qc_df.to_csv(netapp_dir / "derivatives" / output_filename, index=False)
print(f"Saved to {output_filename}")