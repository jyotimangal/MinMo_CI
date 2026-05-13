# script with utility functions: calculate_ngs, resample_source_to_target
import numpy as np
import nibabel as nib
from scipy.ndimage import affine_transform

# Function to resample a source image to the target image space using affine transformation
# order=0 for nearest neighbor interpolation suitable for binary masks as source, order=1 for linear interpolation suitable for continuous data as source
def resample_source_to_target(source_img, target_img, order=0):
    source_data = source_img.get_fdata()
    #target_data = target_img.get_fdata()
    source_affine = source_img.affine
    target_affine = target_img.affine
    transform = np.linalg.inv(source_affine) @ target_affine
    #print(f"transform matrix from source space to target space:\n{transform}")
    print(f"Source image shape: {source_data.shape}, Target image shape: {target_img.shape}")
    resampled_data = affine_transform(
        source_data,
        transform[:3, :3],
        offset=transform[:3, 3],
        output_shape=target_img.shape,
        order=order  
    )
    print(f"Using order {order} for resampling from source space to target space.")
    return resampled_data

""" Function to calculate the mean and standard deviation of the NGS values within the brain mask
It uses finite differences to calculate the per slice gradient matrix in the x and y directions: Gx and Gy
then calculates the absolute values of the gradients: |Gx| and |Gy|
then normalises the absolute gradient values by the total sum of the absolute gradient values across the whole slice (sum(|Gx|) + sum(|Gy|)) 
to get the normalised gradient values nGx and nGy for each voxel in the slice: nGx = |Gx| / (sum(|Gx|) + sum(|Gy|)), nGy = |Gy| / (sum(|Gx|) + sum(|Gy|))
then squares the normalised gradients and sums them to get the NGS value per slice: NGS = sum(nGx^2 + nGy^2)
Finally, it calculates the mean and standard deviation of the NGS values across all slices that contain brain voxels (i.e. where the brain mask is greater than 0) and returns these values.
"""
def calculate_ngs(image_data, brain_mask_data):
    # create an empty list to store the results
    ngs_values = []
    ngs_results = []
    # loop through each slice in the image
    for i in range(image_data.shape[2]):
        mask_data = image_data[:,:,i] * (brain_mask_data[:,:,i] > 0)
        if np.sum(brain_mask_data[:,:,i]) > 0:
            Gx = np.diff(mask_data, axis=0)
            Gy = np.diff(mask_data, axis=1)
            abs_Gx = np.abs(Gx)
            abs_Gy = np.abs(Gy)
            sum_abs_Gx = np.sum(abs_Gx)
            sum_abs_Gy = np.sum(abs_Gy)
            if sum_abs_Gx + sum_abs_Gy > 0:
                nGx = abs_Gx / (sum_abs_Gx + sum_abs_Gy)
                nGy = abs_Gy / (sum_abs_Gx + sum_abs_Gy)
                ngs_slice = np.sum(nGx**2) + np.sum(nGy**2)
                ngs_values.append(ngs_slice)

    mean_ngs = np.mean(ngs_values) if ngs_values else 0
    median_ngs = np.median(ngs_values) if ngs_values else 0
    std_ngs = np.std(ngs_values) if ngs_values else 0
    q25 = np.percentile(ngs_values, 25) if ngs_values else 0
    q75 = np.percentile(ngs_values, 75) if ngs_values else 0
    return mean_ngs, median_ngs, std_ngs, q25, q75



    