#!/bin/bash
# #03b_Run_synthseg_xnat.sh 
# Run with command below:
#
# nohup bash /mnt/c/Users/jm19/MinMo_CI/scripts/03b_Run_synthseg_xnat.sh > /mnt/w/MinMo_CI/derivatives/synthseg_log.txt 2>&1 &
# echo $!
#
# Run in wsl after making sure netapp01data/mbig is mounted to /mnt/w
# Run SynthSeg on all NIfTIs in synthseg_input_linux.txt
# Skips files that have already been processed

INPUT_TXT="/mnt/c/Users/jm19/MinMo_CI/synthseg_input_linux.txt"
OUTPUT_TXT="/mnt/c/Users/jm19/MinMo_CI/synthseg_output_linux.txt"
RESAMPLE_DIR="/mnt/w/MinMo_CI/derivatives/synthseg_resampled"
VOL_CSV="/mnt/w/MinMo_CI/derivatives/synthseg_vol.csv"
QC_CSV="/mnt/w/MinMo_CI/derivatives/synthseg_qc.csv"
FAILED_TXT="/mnt/w/MinMo_CI/derivatives/synthseg_failed.txt"
THREADS=2

mkdir -p "$RESAMPLE_DIR"

paste "$INPUT_TXT" "$OUTPUT_TXT" | while IFS=$'\t' read -r input_file output_file; do
    if [ -f "$output_file" ]; then
        echo "Skipping: $input_file"
        continue
    fi
    filename=$(basename "$input_file" .nii.gz)
    subject=$(echo "$input_file" | grep -oP 'MinMo-\d{3}')
    resample_file="$RESAMPLE_DIR/$subject/${filename}_resampled.nii.gz"
    mkdir -p "$RESAMPLE_DIR/$subject"
    echo "Processing: $input_file"
    mri_synthseg --i "$input_file" --o "$output_file" --resample "$resample_file" --robust --cpu --threads $THREADS \
        && echo "Success: $input_file" \
        || echo "$input_file" >> "$FAILED_TXT"
done