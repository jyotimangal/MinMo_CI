# Author: Jyoti Mangal, Date: 13/10/2026
# Script to convert DICOMs to NIfTI for all subjects in the MinMo_CI/raw_xnat/ directory. Based on Renzo's Harvard Dataverse 00_conv.sh script

#!/bin/bash
# Run from /mnt/w/MinMo_CI/raw_xnat/ in wsl
# Converts DICOMs to NIfTI for all subjects, output goes to <subject>/<session>/nii/

for subject_dir in MinMo-*/; do
    subject_dir=${subject_dir%*/}
    
    for session_dir in $subject_dir/*/; do
        session_dir=${session_dir%*/}
        
        mkdir -p $session_dir/nii
        
        for series_dir in $session_dir/*/; do
            series_dir=${series_dir%*/}
            
            if [ -d "$series_dir/DICOM" ]; then
                cd $series_dir
                echo "Converting: $series_dir"
                dcm2niix -ba y -z y -o ../nii/ -f S%s_%d_e%e ./DICOM/
                cd /mnt/w/MinMo_CI/raw_xnat/
            fi
        done
        
    done
done


# remove _e1 suffix from all nii files in all subject nii folders

for subject_dir in MinMo-*/; do
    for session_dir in $subject_dir/*/; do
        if [ -d "${session_dir}nii" ]; then
            cd ${session_dir}nii
            for file in *.nii.gz ; do mv "$file" "${file//_e1/}" ; done
            for file in *.json ; do mv "$file" "${file//_e1/}" ; done
            cd /mnt/w/MinMo_CI/raw_xnat/
        fi
    done
done   