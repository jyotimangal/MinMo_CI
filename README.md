# MinMo Clinical Investigation:
In this repo, clinical data acquired with and without the MR-MinMo device in a blinded-fashion is explored, investigated and analysed. The aim is to understand the effect of using the device, if any, on the image quality metric such as Normalised gradient squared.

Preliminary investigation of the effect of using the MR-MinMo device in research MR examinations on Siemens 7T was previously done here:

*Reducing motion artefact in high resolution 7T MRI using the Magnetic Resonance Minimal Motion (‘MR-MinMo’) head stabilisation device*, https://doi.org/10.1101/2025.10.10.25337727, Jyoti Mangal, Simon Richardson, Yannick Brackenier, Matthew Gardner, Pierluigi Di Cio,  Chiara Casella, Shaihan Malik, Jo Hajnal, Martina F Callaghan, Fred Dick, David W Carmichael

Now we extend the investigation into clinical exams acquired on the Siemens 3T.

## Folder Structure
Data, raw and processed, is stored on the netapp01data server (mbig/ directory, mounted as W:/ on Windows). 

Root path `W:\MinMo_CI\` is used across all scripts.

- `raw\` — original DICOM files (and the zipped folders), read-only, never modified
- `niftis\` — NIfTI conversions of T2 TSE series (PulseSequenceName 'tse2d1_17') via dcm2niix, mirroring raw/ structure
- `synthseg\` — SynthSeg brain parcellations and resampled images, mirroring niftis/ structure
- `brain_masks\` — binary brain masks derived from SynthSeg parcellations, mirroring niftis/ structure
- `derivatives\` — analysis outputs including DICOM inventory CSV and NGS results CSV

## Scripts
Different scripts perform different functions. Exploratory scripts:
- `explore_dicoms.py` prints key metadata fields from all dicom files within the root directory W:/MinMo_CI/raw/
- `inventory_dicoms.py` saves a csv file with key metadata fields from all dicom files within the root directory W:/MinMo_CI/raw/ om `derivatives\`
- `convert_to_nifti.py` walks the raw folder and converts the dicom files whose metadata field for sequence name matches TARGET_SEQUENCE_NAME and saves them in `niftis\`
- `run_synthseg.sh` is a bash script that runs mri-synthseg on nifti files to save the resampled parcellation file if it doesn't exist in `synthseg\`
- `extract_brain_mask.py` extracts whole brain mask from the parcellation files and saves in `brain_masks\`
- `calculate_ngs.py` calculates the normalised gradient squared for the multi slice 2D images after masking the nifti images with the native space brain mask (saved `brain_masks\*brain_mask_native.nii.gz`). Scripts saves the key values such as mean ngs across slices, std ngs across slices etc. in csv file in `derivatives\`
- `analyse_ngs.ipynb` is a jupyter notebook that does basic analyses (scatterplot, errorplot) from the data linking metadata fields with ngs results. To do so, it merges the metadata csv with ngs csv and saves the merged dataframe as a csv in `derivatives\`.

## Running the code
Currently the code is simple and split up into different scripts. Use python for .py scripts and bash for run_synthseg.sh. 
### Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate it: `.\.venv\Scripts\activate` (Windows) or `source .venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. For SynthSeg, WSL with FreeSurfer is required (see FreeSurfer installation docs). Mount the data drive in WSL with `sudo mount -t drvfs W: /mnt/w` before running `run_synthseg.sh`

Future updates may involve the usage of flags for optional parameters for mri_synthseg as well as TARGET_SEQUENCE_NAME, FileName, FilePath and/or other metadata fields. Watch this space.

