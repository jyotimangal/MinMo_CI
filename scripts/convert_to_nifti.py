# import packages
import pydicom
from pathlib import Path
import subprocess
import shutil

TARGET_SEQUENCE_NAME = "*tse2d1_17"  # define the target PulseSequenceName to filter DICOM files for conversion
TARGET_SEQUENCES = [
    "*tse2d1_17",      
    "*spcir_220ns",    
    "*spcir_210ns",    
    "*spcR_42ns",      
    "*spcR_40ns",      
    "*spcR_50ns",      
    "*swi3d1r",        
]
# define the root directory containing the DICOM files
netapp_dir = Path(r"W:/MinMo_CI/")

# make the niftis directory if it doesn't exist
niftis_dir = netapp_dir / "niftis"
niftis_dir.mkdir(exist_ok=True)
dcm2niix_path = shutil.which("dcm2niix")

processed_folders = set()  # Keep track of processed folders to avoid redundant conversions
# walk recursively through the root directory for all folders and files
for path in (netapp_dir / "raw").rglob("*"):
    # check if the path is a file
    if path.is_file():
        try:
            # read the DICOM file without loading pixel data to save memory
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            # check if the DICOM file has a Modality field and if it is MR
            if ds.get('Modality') == 'MR' and ds.get('PulseSequenceName') in TARGET_SEQUENCES:
                # create the same folder structure in the niftis directory as the dicom directory
                series_folder = path.parent.parent if path.parent.name == "DICOM" else path.parent
                if series_folder in processed_folders:
                    continue # skip conversion if this folder has already been processed
                processed_folders.add(series_folder)
                niftis_series_folder = niftis_dir / series_folder.relative_to(netapp_dir / "raw")
                niftis_series_folder.mkdir(parents=True, exist_ok=True)
                existing_niftis = list(niftis_series_folder.glob("*.nii.gz"))
                if existing_niftis:
                    continue # Skip conversion if NIfTI files already exist in the target folder
                # save the nifti image to the niftis directory with the same name but with a .nii extension
                print(f"Dicom file {path} now being converted to NIfTI format...")
                print(f"Check: path.parent: {path.parent}, niftis_series_folder: {niftis_series_folder}")
                subprocess.run([dcm2niix_path, "-o", str(niftis_series_folder), "-z", "y", str(path.parent)], check=True)
                print(f"Converted DICOM file {path} to NIfTI format at {niftis_series_folder}")
        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")
print(f"Conversion complete. {len(processed_folders)} series converted.")