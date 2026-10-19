# Author: Jyoti Mangal, date:16/10/2026
# Script that loops through the synthseg output folders and creates a brain mask for each subject using the synthseg output
# and saves it in the derivatives folder.
# The brain mask is created by bindary masking the synthseg output
# The brain mask is then saved as a nifti file in the derivatives folder
# Also save a log file that contains the subject ID and the path to the brain mask for each subject

import nibabel as nib
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI/")
synthseg_output_dir = netapp_dir / "derivatives" / "synthseg"
brain_mask_dir = netapp_dir / "derivatives" / "brain_masks"
brain_mask_log_file = netapp_dir / "derivatives" / "brain_masks" / "brain_mask_log.txt"
brain_mask_dir.mkdir(parents=True, exist_ok=True)

for seg_path in synthseg_output_dir.rglob("**/*_seg.nii.gz"):
    seg_img = nib.load(seg_path)
    seg_data = seg_img.get_fdata()
    mask_data = (seg_data > 0).astype(int)  # Create a binary mask where all non-zero voxels are set to 1

    subject_id = seg_path.parent.name  # Assuming the subject ID is the name of the parent directory
    mask_dir = brain_mask_dir /  subject_id
    mask_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
    mask_path = mask_dir / seg_path.name.replace("_seg.nii.gz", "_brain_mask.nii.gz")

    if mask_path.exists():
        print(f"Brain mask already exists for {subject_id}, skipping...")
        with open(brain_mask_log_file, "a") as log_file:
            log_file.write(f"Brain mask already exists for {subject_id}, skipping...\n")
        continue

    nib.save(nib.Nifti1Image(mask_data, seg_img.affine, seg_img.header), mask_path)
    print(f"Saved brain mask for {subject_id} at {mask_path}")
    with open(brain_mask_log_file, "a") as log_file:
        log_file.write(f"Saved brain mask for {subject_id} at {mask_path}\n")

    