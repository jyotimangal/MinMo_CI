"""Utilities for MinMo clinical MRI processing and IQM analysis."""

from __future__ import annotations

import csv
import math
import random
import statistics
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

ENTROPY_BIN_COUNT = 32
DEFAULT_PERMUTATIONS = 10_000
DEFAULT_RANDOM_SEED = 42


def _optional_import(module_name: str) -> Any:
    try:
        return __import__(module_name)
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            f"{module_name} is required for this operation. Install it in the runtime environment."
        ) from exc


def convert_dicom_to_nifti(dicom_dir: str | Path, output_nifti: str | Path) -> str:
    """Convert a multi-slice DICOM series into NIfTI.

    This function expects `pydicom` and `nibabel` to be available in the environment.
    """

    pydicom = _optional_import("pydicom")
    nibabel = _optional_import("nibabel")

    dicom_dir = Path(dicom_dir)
    output_nifti = Path(output_nifti)

    if not dicom_dir.is_dir():
        raise FileNotFoundError(f"DICOM directory not found: {dicom_dir}")

    dicom_files = sorted(p for p in dicom_dir.iterdir() if p.is_file())
    if not dicom_files:
        raise ValueError(f"No DICOM files found in: {dicom_dir}")

    slices: List[Tuple[int, object]] = []
    for file_path in dicom_files:
        ds = pydicom.dcmread(str(file_path), force=True)
        if not hasattr(ds, "PixelData"):
            continue
        instance_number = int(getattr(ds, "InstanceNumber", len(slices)))
        slices.append((instance_number, ds.pixel_array))

    if not slices:
        raise ValueError(f"No readable DICOM image slices found in: {dicom_dir}")

    slices.sort(key=lambda item: item[0])
    np = _optional_import("numpy")
    volume = np.stack([pixel for _, pixel in slices], axis=-1)
    affine = np.eye(4)

    output_nifti.parent.mkdir(parents=True, exist_ok=True)
    nii = nibabel.Nifti1Image(volume, affine)
    nibabel.save(nii, str(output_nifti))
    return str(output_nifti)


def run_synthseg(input_nifti: str | Path, output_segmentation: str | Path, synthseg_bin: str = "mri_synthseg") -> str:
    """Run SynthSeg for brain segmentation from MRI NIfTI."""

    input_nifti = Path(input_nifti)
    output_segmentation = Path(output_segmentation)

    if not input_nifti.exists():
        raise FileNotFoundError(f"Input NIfTI not found: {input_nifti}")

    output_segmentation.parent.mkdir(parents=True, exist_ok=True)

    command = [synthseg_bin, "--i", str(input_nifti), "--o", str(output_segmentation)]
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except FileNotFoundError as exc:
        raise RuntimeError(
            f"SynthSeg executable '{synthseg_bin}' was not found. "
            "Install FreeSurfer/SynthSeg and ensure the command-line tool is on PATH."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(
            "SynthSeg failed with a non-zero exit code. "
            f"stderr: {exc.stderr.strip()}"
        ) from exc

    return str(output_segmentation)


def _validate_3d(volume: Sequence[Sequence[Sequence[float]]]) -> Tuple[int, int, int]:
    if not volume or not volume[0] or not volume[0][0]:
        raise ValueError("Volume must be a non-empty 3D array.")

    z = len(volume)
    y = len(volume[0])
    x = len(volume[0][0])
    for plane in volume:
        if len(plane) != y:
            raise ValueError("Volume has inconsistent Y dimension.")
        for row in plane:
            if len(row) != x:
                raise ValueError("Volume has inconsistent X dimension.")
    return z, y, x


def _iter_voxels(volume: Sequence[Sequence[Sequence[float]]], mask: Sequence[Sequence[Sequence[bool]]] | None) -> Iterable[Tuple[int, int, int, float]]:
    z_dim, y_dim, x_dim = _validate_3d(volume)
    if mask is not None:
        _validate_3d(mask)  # type: ignore[arg-type]

    for z in range(z_dim):
        for y in range(y_dim):
            for x in range(x_dim):
                if mask is not None and not bool(mask[z][y][x]):
                    continue
                yield z, y, x, float(volume[z][y][x])


def _normalized_gradient_squared(
    volume: Sequence[Sequence[Sequence[float]]],
    mask: Sequence[Sequence[Sequence[bool]]] | None = None,
) -> float:
    z_dim, y_dim, x_dim = _validate_3d(volume)

    grad_sq_sum = 0.0
    intensity_sq_sum = 0.0

    for z, y, x, value in _iter_voxels(volume, mask):
        dx = 0.0
        dy = 0.0
        dz = 0.0

        if x + 1 < x_dim and (mask is None or bool(mask[z][y][x + 1])):
            dx = float(volume[z][y][x + 1]) - value
        if y + 1 < y_dim and (mask is None or bool(mask[z][y + 1][x])):
            dy = float(volume[z][y + 1][x]) - value
        if z + 1 < z_dim and (mask is None or bool(mask[z + 1][y][x])):
            dz = float(volume[z + 1][y][x]) - value

        grad_sq_sum += dx * dx + dy * dy + dz * dz
        intensity_sq_sum += value * value

    if intensity_sq_sum == 0.0:
        return 0.0
    return grad_sq_sum / intensity_sq_sum


def calculate_iqms(
    volume: Sequence[Sequence[Sequence[float]]],
    mask: Sequence[Sequence[Sequence[bool]]] | None = None,
) -> Dict[str, float]:
    """Calculate image-quality metrics for a 3D MRI volume."""

    values = [value for _, _, _, value in _iter_voxels(volume, mask)]
    if not values:
        raise ValueError("No voxels selected for IQM calculation.")

    mean_val = statistics.fmean(values)
    std_val = statistics.pstdev(values) if len(values) > 1 else 0.0
    snr = (mean_val / std_val) if std_val > 0 else float("inf")

    # Histogram-based entropy using fixed-size bins.
    min_val, max_val = min(values), max(values)
    if min_val == max_val:
        entropy = 0.0
    else:
        bins = [0] * ENTROPY_BIN_COUNT
        width = (max_val - min_val) / ENTROPY_BIN_COUNT
        for value in values:
            index = int((value - min_val) / width)
            if index == ENTROPY_BIN_COUNT:
                index = ENTROPY_BIN_COUNT - 1
            bins[index] += 1
        total = float(len(values))
        entropy = -sum((count / total) * math.log2(count / total) for count in bins if count)

    return {
        "normalized_gradient_squared": _normalized_gradient_squared(volume, mask),
        "mean_intensity": mean_val,
        "std_intensity": std_val,
        "snr": snr,
        "entropy": entropy,
    }


def _two_sided_permutation_p_value(
    group_a: List[float],
    group_b: List[float],
    permutations: int = DEFAULT_PERMUTATIONS,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> float:
    """Return two-sided permutation-test p-value for mean differences.

    A fixed default seed keeps outputs reproducible for CI/tests while still
    allowing callers to override the seed when needed.

    Parameters
    ----------
    group_a, group_b:
        Metric values from each blinded cohort.
    permutations:
        Number of random label permutations.
    random_seed:
        Seed for deterministic permutation sampling.
    """

    observed = abs(statistics.fmean(group_a) - statistics.fmean(group_b))
    joined = group_a + group_b
    a_size = len(group_a)
    rng = random.Random(random_seed)

    exceed_count = 0
    for _ in range(permutations):
        permuted = list(joined)
        rng.shuffle(permuted)
        perm_a = permuted[:a_size]
        perm_b = permuted[a_size:]
        if abs(statistics.fmean(perm_a) - statistics.fmean(perm_b)) >= observed:
            exceed_count += 1

    return (exceed_count + 1) / (permutations + 1)


def compare_blinded_groups(
    records: Sequence[Dict[str, Any]],
    metric_name: str = "normalized_gradient_squared",
    group_name: str = "group",
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> Dict[str, Any]:
    """Compare one IQM between two blinded groups using a permutation test."""

    grouped: Dict[str, List[float]] = {}
    for record in records:
        if group_name not in record:
            raise KeyError(f"Missing '{group_name}' in record: {record}")
        if metric_name not in record:
            raise KeyError(f"Missing '{metric_name}' in record: {record}")

        group = str(record[group_name])
        grouped.setdefault(group, []).append(float(record[metric_name]))

    if len(grouped) != 2:
        raise ValueError("Exactly two blinded groups are required for comparison.")

    group_labels = sorted(grouped)
    group_a = grouped[group_labels[0]]
    group_b = grouped[group_labels[1]]

    if not group_a or not group_b:
        raise ValueError("Both groups must contain at least one subject.")

    mean_a = statistics.fmean(group_a)
    mean_b = statistics.fmean(group_b)

    return {
        "group_a": group_labels[0],
        "group_b": group_labels[1],
        "n_group_a": len(group_a),
        "n_group_b": len(group_b),
        "mean_group_a": mean_a,
        "mean_group_b": mean_b,
        "mean_difference": mean_a - mean_b,
        "p_value": _two_sided_permutation_p_value(group_a, group_b, random_seed=random_seed),
    }


def load_iqm_records_from_csv(csv_path: str | Path) -> List[Dict[str, Any]]:
    """Load per-subject IQM records from CSV for blinded-group statistics."""

    csv_path = Path(csv_path)
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))
