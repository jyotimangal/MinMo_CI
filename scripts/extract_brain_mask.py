# Script to extract the brain mask from the image parcellation file as saved by synthseg
import nibabel as nib
from pathlib import Path

# define the root directory containing the parcellation files
netapp_dir = Path(r"W:/MinMo_CI/")
# define the output directory for the brain masks
brain_masks_dir = netapp_dir / "brain_masks"
# make the brain_masks directory if it doesn't exist
brain_masks_dir.mkdir(exist_ok=True)

# walk recursively through the folder synthseg in root directory for all folders and files
for path in (netapp_dir / "synthseg").rglob("*"):
    if path.is_file() and path.name.endswith("_synthseg.nii.gz"):
        print(f"Found parcellation file: {path}")
        # load the parcellation file and get the data to create a brain mask
        parcellation_img = nib.load(path)
        parcellation_data = parcellation_img.get_fdata()
        brain_mask_data = (parcellation_data > 0).astype(int)
        brain_mask_img = nib.Nifti1Image(brain_mask_data, parcellation_img.affine, parcellation_img.header)
        brain_mask_folder = brain_masks_dir / path.parent.relative_to(netapp_dir / "synthseg")
        brain_mask_folder.mkdir(parents=True, exist_ok=True)
        brain_mask_file = brain_mask_folder / (path.name.replace("_synthseg.nii.gz", "") + "_brain_mask.nii.gz")
        if brain_mask_file.exists():
            print(f"Brain mask already exists, skipping: {brain_mask_file}")
            continue
        nib.save(brain_mask_img, brain_mask_file)
        print(f"Brain mask saved to {brain_mask_file}")
    else:
        print(f"File {path} does not match the expected parcellation file pattern and will be skipped.")
