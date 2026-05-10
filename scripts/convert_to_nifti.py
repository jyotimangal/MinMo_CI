# import packages
import pydicom
from pathlib import Path
import subprocess

TARGET_SEQUENCE_NAME = "*tse2d1_17"  # define the target PulseSequenceName to filter DICOM files for conversion
# define the root directory containing the DICOM files
netapp_dir = Path(r"W:/MinMo_CI/")

# make the niftis directory if it doesn't exist
niftis_dir = netapp_dir / "niftis"
niftis_dir.mkdir(exist_ok=True)

processed_folders = set()  # Keep track of processed folders to avoid redundant conversions
# walk recursively through the root directory for all folders and files
for path in netapp_dir.rglob("*"):
    # check if the path is a file
    if path.is_file():
        try:
            # read the DICOM file without loading pixel data to save memory
            ds = pydicom.dcmread(path, stop_before_pixels=True)
            # check if the DICOM file has a Modality field and if it is MR
            if ds.get('Modality') == 'MR' and ds.get('PulseSequenceName') == TARGET_SEQUENCE_NAME:
                # create the same folder structure in the niftis directory as the dicom directory
                series_folder = path.parent
                if series_folder in processed_folders:
                    continue # skip conversion if this folder has already been processed
                processed_folders.add(series_folder)
                niftis_series_folder = niftis_dir / series_folder.relative_to(netapp_dir)
                niftis_series_folder.mkdir(parents=True, exist_ok=True)
                existing_niftis = list(niftis_series_folder.glob("*.nii.gz"))
                if existing_niftis:
                    continue # Skip conversion if NIfTI files already exist in the target folder
                # save the nifti image to the niftis directory with the same name but with a .nii extension
                print(f"Dicom file {path} now being converted to NIfTI format...")
                print(f"Check: path.parent: {path.parent}, niftis_series_folder: {niftis_series_folder}")
                subprocess.run(["dcm2niix", "-o", str(niftis_series_folder), "-z", "y", str(path.parent)], check=True)
                print(f"Converted DICOM file {path} to NIfTI format at {niftis_series_folder}")
        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")
