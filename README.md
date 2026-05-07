# MinMo_CI

Pipeline utilities to analyse image quality metrics (IQMs) on paediatric clinical MRI scans (T1/T2 multi-slice DICOM) and investigate MR-MinMo head stabilisation effects.

## Implemented workflow components

- **DICOM → NIfTI conversion** (`convert_dicom_to_nifti`)
  - Reads a DICOM series and stacks slices into a 3D volume.
  - Saves NIfTI output (`.nii`/`.nii.gz`).
  - Requires `pydicom`, `numpy`, and `nibabel` in the runtime environment.
- **Brain segmentation/extraction orchestration with SynthSeg** (`run_synthseg`)
  - Executes SynthSeg (`mri_synthseg`) on NIfTI input.
  - Returns segmentation output path and raises clear runtime errors if missing/failing.
- **IQM computation** (`calculate_iqms`)
  - Includes **normalized gradient squared** plus mean intensity, standard deviation, SNR, and entropy.
  - Supports optional binary masks (e.g., SynthSeg-derived brain mask).
- **Blinded-group statistical comparison** (`compare_blinded_groups`)
  - Compares a selected IQM between exactly two blinded groups.
  - Uses a two-sided permutation test and reports effect size summary fields.

## Running tests

```bash
python -m unittest discover -v
```
