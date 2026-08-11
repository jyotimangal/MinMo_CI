#!/bin/bash
NIFTI_DIR="/mnt/w/MinMo_CI/niftis"
SYNTHSEG_DIR="/mnt/w/MinMo_CI/synthseg"

find "$NIFTI_DIR" -name "*.nii.gz" | while read nifti_file; do
	relative_path="${nifti_file#$NIFTI_DIR/}"
	output_file="$SYNTHSEG_DIR/${relative_path%.nii.gz}_synthseg.nii.gz"
	resampled_file="$SYNTHSEG_DIR/${relative_path%.nii.gz}_resampled.nii.gz"
	output_dir=$(dirname "$output_file")
	mkdir -p "$output_dir"
	if [ -f "$output_file" ]; then
    	echo "Skipping $nifti_file - already processed"
    	continue
	fi	
	echo "Processing: $nifti_file"
	mri_synthseg --i "$nifti_file" --resample "$resampled_file" --o "$output_file" --robust --cpu --threads 1 && echo "Success: $nifti_file" || echo "$nifti_file" >> /mnt/w/MinMo_CI/derivatives/synthseg_failed.txt
done
