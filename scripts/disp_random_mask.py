import random
import subprocess
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI/")
itksnap_path = r"C:\Program Files\ITK-SNAP 4.2\bin\ITK-SNAP.exe"
brain_masks_dir = netapp_dir / "brain_masks"

# get all native brain masks
all_masks = list(brain_masks_dir.rglob("*_brain_mask_native.nii.gz"))
print(f"Total native masks: {len(all_masks)}")

# pick a random one
random_mask = random.choice(all_masks)
# find corresponding NIfTI
nifti_path = str(random_mask).replace('brain_masks', 'niftis').replace('_brain_mask_native.nii.gz', '.nii.gz')

print(f"Mask: {random_mask}")
print(f"NIfTI: {nifti_path}")

subprocess.Popen([itksnap_path, '-g', nifti_path, '-s', str(random_mask)])