# script that loads the original image and brain mask, resamples it to the original image space,
# and calculates the mean and standard deviation of the NGS values within the brain mask, saving the results to a csv file

import nibabel as nib
import numpy as np
import pandas as pd
from pathlib import Path
from utils import calculate_ngs, resample_source_to_target
from scipy.ndimage import binary_erosion

# define the root directory for the original nifti images and brain masks
netapp_dir = Path(r"W:/MinMo_CI/")
# define the output csv file for the NGS results
output_csv = netapp_dir / "derivatives" / "MinMo_001_to_005_NGS_Results.csv"
# create an empty list to store the results
results_list = []
# walk recursively through the folder synthseg in root directory for all folders and files
for path in (netapp_dir / "niftis").rglob("*"):
    if path.is_file() and path.name.endswith("nii.gz"):
        print(f"Processing image file: {path}")
        # load the original image and the brain mask
        image_img = nib.load(path)
        image_data = image_img.get_fdata()
        brain_mask_dir = netapp_dir / "brain_masks" / path.parent.relative_to(netapp_dir / "niftis")
        brain_mask_file = brain_mask_dir / (path.name.replace(".nii.gz", "") + "_brain_mask_native.nii.gz")
        if brain_mask_file.exists() and False:
            brain_mask_img = nib.load(brain_mask_file)
            brain_mask_data = brain_mask_img.get_fdata()
        else:
            brain_mask_file = brain_mask_dir / (path.name.replace(".nii.gz", "") + "_brain_mask.nii.gz")
            if brain_mask_file.exists():
                brain_mask_img = nib.load(brain_mask_file)
                brain_mask_data = resample_source_to_target(brain_mask_img, image_img, order=0) # order=0 for nearest neighbor interpolation to preserve binary mask values
                # save the resampled brain mask for future use
                resampled_brain_mask_img = nib.Nifti1Image(brain_mask_data, image_img.affine, image_img.header)
                resampled_brain_mask_file = brain_mask_dir / (path.name.replace(".nii.gz", "") + "_brain_mask_native.nii.gz")
                nib.save(resampled_brain_mask_img, resampled_brain_mask_file)
                brain_mask_data_eroded = binary_erosion(brain_mask_data >0, iterations=3).astype(int) # erode the brain mask to avoid edge effects in NGS calculation
                resampled_eroded_brain_mask_file = brain_mask_dir / (path.name.replace(".nii.gz", "") + "_brain_mask_eroded_native.nii.gz")
                nib.save(nib.Nifti1Image(brain_mask_data_eroded, image_img.affine, image_img.header), resampled_eroded_brain_mask_file)
            else:
                print(f"No brain mask found for image {path}, skipping NGS calculation.")
                continue
        
        # calculate the NGS values within the brain mask
        mean_ngs, std_ngs = calculate_ngs(image_data, brain_mask_data)
        mean_ngs_eroded, std_ngs_eroded = calculate_ngs(image_data, brain_mask_data_eroded)

        # append to result list
        results_list.append({
            "FilePath": str(path),
            "Mean_NGS": mean_ngs,
            "Std_NGS": std_ngs,
            "Mean_NGS_Eroded": mean_ngs_eroded,
            "Std_NGS_Eroded": std_ngs_eroded,
            "N_slices": image_data.shape[2],
            "Num_voxels_in_mask": np.sum(brain_mask_data > 0),
            "Num_voxels_in_mask_Eroded": np.sum(brain_mask_data_eroded > 0)
        })
    
# create a dataframe from the results list and save it to a csv file
df = pd.DataFrame(results_list)
df.to_csv(output_csv, index=False)
    

