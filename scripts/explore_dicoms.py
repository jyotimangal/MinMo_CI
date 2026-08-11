# Script to explore the DICOM files in the MinMo_CI directory on the netapp01data drive.
# import packages
import pydicom
from pathlib import Path

netapp_dir = Path(r"W:/MinMo_CI/")

# walk recursively through the root directory for all folders and files
for path in (netapp_dir / "raw").rglob("*"):
    # check if the path is a file
    if path.is_file():
        # check if the file can be read as a DICOM file
        try:
            # read the DICOM file without loading pixel data to save memory
            ds = pydicom.dcmread(path, stop_before_pixels=True) 
            print(f"Read DICOM file: {path}")
            # print all the metadata fields in the DICOM file if ds.get('modality') is MR (not SR)
            if ds.get('Modality') == 'MR':
                print("Modality is MR, printing ImageType, SeriesDescription, PulseSequenceName, and SeriesNumber:")
                print(f"ImageType: {ds.get('ImageType', 'N/A')}")
                print(f"SeriesDescription: {ds.get('SeriesDescription', 'N/A')}")
                print(f"PulseSequenceName: {ds.get('PulseSequenceName', 'N/A')}")
                print(f"SeriesNumber: {ds.get('SeriesNumber', 'N/A')}")
                print(f"PatientAge: {ds.get('PatientAge', 'N/A')}")
                print(f"PatientBirthDate: {ds.get('PatientBirthDate', 'N/A')}")
            # break after printing the first file to avoid overwhelming output, 
            # remove this break to continue exploring all files
            #break
        except Exception as e:
            print(f"Could not read file {path} as DICOM: {e}")

