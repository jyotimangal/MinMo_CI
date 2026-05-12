# MinMo Clinical Investigation:
In this repo, clinical data acquired with and without the MR-MinMo device in a blinded-fashion is explored, investigated and analysed. The aim is to understand the effect of using the device, if any, on the image quality metric such as Normalised gradient squared.

Preliminary investigation of the effect of using the MR-MinMo device in research MR examinations on Siemens 7T was previously done here:

*Reducing motion artefact in high resolution 7T MRI using the Magnetic Resonance Minimal Motion (‘MR-MinMo’) head stabilisation device*, https://doi.org/10.1101/2025.10.10.25337727, Jyoti Mangal, Simon Richardson, Yannick Brackenier, Matthew Gardner, Pierluigi Di Cio,  Chiara Casella, Shaihan Malik, Jo Hajnal, Martina F Callaghan, Fred Dick, David W Carmichael

Now we extend the investigation into clinical exams acquired on the Siemens 3T.

## Folder Structure
Data, raw and processed, is stored on the netapp01data server (mbig/ directory, mounted as W:/ on Windows). 

Root path `W:/MinMo_CI/` is used across all scripts.

- `raw/` — original DICOM files (and the zipped folders), read-only, never modified
- `niftis/` — NIfTI conversions of T2 TSE series (PulseSequenceName 'tse2d1_17') via dcm2niix, mirroring raw/ structure
- `synthseg/` — SynthSeg brain parcellations and resampled images, mirroring niftis/ structure
- `brain_masks/` — binary brain masks derived from SynthSeg parcellations, mirroring niftis/ structure
- `derivatives/` — analysis outputs including DICOM inventory CSV and NGS results CSV

## Scripts

## Running the code

## Dependencies

