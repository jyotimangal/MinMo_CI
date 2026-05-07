import csv
import math
import os
import tempfile
import unittest

from minmo_ci.pipeline import calculate_iqms, compare_blinded_groups, load_iqm_records_from_csv


class PipelineMetricsTests(unittest.TestCase):
    def test_normalized_gradient_squared_is_zero_for_uniform_volume(self):
        volume = [
            [[1.0, 1.0], [1.0, 1.0]],
            [[1.0, 1.0], [1.0, 1.0]],
        ]

        metrics = calculate_iqms(volume)

        self.assertEqual(metrics["normalized_gradient_squared"], 0.0)
        self.assertEqual(metrics["std_intensity"], 0.0)
        self.assertTrue(math.isinf(metrics["snr"]))

    def test_mask_limits_voxels_used_for_iqm(self):
        volume = [
            [[1.0, 4.0], [1.0, 4.0]],
            [[1.0, 4.0], [1.0, 4.0]],
        ]
        mask = [
            [[True, False], [True, False]],
            [[True, False], [True, False]],
        ]

        metrics = calculate_iqms(volume, mask)

        self.assertAlmostEqual(metrics["mean_intensity"], 1.0)
        self.assertEqual(metrics["normalized_gradient_squared"], 0.0)

    def test_entropy_reflects_intensity_variation(self):
        uniform = [[[2.0, 2.0], [2.0, 2.0]], [[2.0, 2.0], [2.0, 2.0]]]
        varied = [[[0.0, 1.0], [2.0, 3.0]], [[4.0, 5.0], [6.0, 7.0]]]

        uniform_entropy = calculate_iqms(uniform)["entropy"]
        varied_entropy = calculate_iqms(varied)["entropy"]

        self.assertEqual(uniform_entropy, 0.0)
        self.assertGreater(varied_entropy, uniform_entropy)


class BlindedGroupComparisonTests(unittest.TestCase):
    def test_compare_blinded_groups_returns_expected_shape(self):
        records = [
            {"subject": "S1", "group": "A", "normalized_gradient_squared": 0.20},
            {"subject": "S2", "group": "A", "normalized_gradient_squared": 0.19},
            {"subject": "S3", "group": "B", "normalized_gradient_squared": 0.42},
            {"subject": "S4", "group": "B", "normalized_gradient_squared": 0.40},
        ]

        result = compare_blinded_groups(records)

        self.assertEqual(result["group_a"], "A")
        self.assertEqual(result["group_b"], "B")
        self.assertEqual(result["n_group_a"], 2)
        self.assertEqual(result["n_group_b"], 2)
        self.assertLess(result["mean_difference"], 0.0)
        self.assertGreaterEqual(result["p_value"], 0.0)
        self.assertLessEqual(result["p_value"], 1.0)

    def test_compare_blinded_groups_requires_exactly_two_groups(self):
        records = [
            {"group": "A", "normalized_gradient_squared": 0.2},
            {"group": "B", "normalized_gradient_squared": 0.3},
            {"group": "C", "normalized_gradient_squared": 0.4},
        ]
        with self.assertRaises(ValueError):
            compare_blinded_groups(records)

    def test_compare_blinded_groups_checks_metric_key(self):
        with self.assertRaises(KeyError):
            compare_blinded_groups([{"group": "A"}, {"group": "B"}])


class CsvLoadingTests(unittest.TestCase):
    def test_load_iqm_records_from_csv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = os.path.join(temp_dir, "iqm.csv")
            with open(temp_path, "w", newline="", encoding="utf-8") as handle:
                writer = csv.DictWriter(handle, fieldnames=["subject", "group", "normalized_gradient_squared"])
                writer.writeheader()
                writer.writerow({"subject": "S1", "group": "A", "normalized_gradient_squared": "0.21"})
                writer.writerow({"subject": "S2", "group": "B", "normalized_gradient_squared": "0.35"})

            rows = load_iqm_records_from_csv(temp_path)

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["subject"], "S1")
        self.assertEqual(rows[1]["group"], "B")


if __name__ == "__main__":
    unittest.main()
