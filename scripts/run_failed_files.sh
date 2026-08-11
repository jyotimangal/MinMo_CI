#!/bin/bash
NIFTI_DIR="/mnt/w/MinMo_CI/niftis"
SYNTHSEG_DIR="/mnt/w/MinMo_CI/synthseg"

while IFS= read -r nifti_file; do
    relative_path="${nifti_file#/mnt/w/MinMo_CI/niftis/}"
    output_file="/mnt/w/MinMo_CI/synthseg/${relative_path%.nii.gz}_synthseg.nii.gz"
    resampled_file="/mnt/w/MinMo_CI/synthseg/${relative_path%.nii.gz}_resampled.nii.gz"
    mkdir -p "$(dirname "$output_file")"
    if [ -f "$output_file" ]; then
        echo "Skipping - already processed: $nifti_file"
        continue
    fi
    echo "Retrying: $nifti_file"
    mri_synthseg --i "$nifti_file" --resample "$resampled_file" --o "$output_file" --robust --cpu --threads 1
done < /mnt/w/MinMo_CI/derivatives/synthseg_failed.txt