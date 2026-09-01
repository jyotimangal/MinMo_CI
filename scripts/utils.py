# script with utility functions: calculate_ngs, resample_source_to_target
from zipfile import Path

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

'Function to filter a dataframe based on a dictionary of filters. The filters can be exact matches or conditions like ''contains'' or ''excludes''.'
def apply_filters_to_df(df, filters):
    result = df.copy()
    for col, cond in filters.items():
        if isinstance(cond, tuple):
            op, val = cond
            if op == 'contains':
                result = result[result[col].str.contains(val, na=False)]
            elif op == 'excludes':
                result = result[~result[col].str.contains(val, na=False)]
        else:
            result = result[result[col] == cond]
    return result


def open_in_itksnap(image_paths):
    import subprocess
    import platform
    import time
    from pathlib import Path
    import os
    netapp_dir = Path(r"W:/MinMo_CI/") if platform.system() == 'Windows' else Path.home() / "Documents/Postdoc_epilepsy/MinMo_CI"
    itksnap_path = r"C:\Program Files\ITK-SNAP 4.2\bin\ITK-SNAP.exe" if platform.system() == 'Windows' else "/Applications/ITK-SNAP.app/Contents/bin/itksnap"
    
    workspace_path = str(netapp_dir / "derivatives" / "temp_workspace.itksnap")
    
    overlay_template = """    <folder key="Layer[{idx:03d}]" >
      <entry key="AbsolutePath" value="{path}" />
      <entry key="Role" value="OverlayRole" />
      <folder key="LayerMetaData" >
        <entry key="Alpha" value="0.5" />
      </folder>
    </folder>"""
    
    main_path = image_paths[0].replace('\\', '/')
    overlays = "\n".join([overlay_template.format(idx=i+1, path=p.replace('\\', '/')) 
                          for i, p in enumerate(image_paths[1:])])
    
    xml = f"""<?xml version="1.0" encoding="UTF-8" ?>
<registry>
  <entry key="Version" value="20230320" />
  <folder key="Layers" >
    <folder key="Layer[000]" >
      <entry key="AbsolutePath" value="{main_path}" />
      <entry key="Role" value="MainRole" />
    </folder>
{overlays}
  </folder>
</registry>"""
    
    with open(workspace_path, 'w') as f:
        f.write(xml)
    # print(f"Workspace written to: {workspace_path}")
    # print(f"Workspace exists: {Path(workspace_path).exists()}")
    # print(f"ITK-SNAP path: {itksnap_path}")
    subprocess.Popen([itksnap_path, '-w', workspace_path], shell=True)
    time.sleep(2)  # Wait for ITK-SNAP to open the workspace

