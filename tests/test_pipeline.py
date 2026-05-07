import unittest

from minmo_ci.pipeline import calculate_iqms, compare_blinded_groups


class PipelineMetricsTests(unittest.TestCase):
    def test_normalized_gradient_squared_is_zero_for_uniform_volume(self):
        volume = [
            [[1.0, 1.0], [1.0, 1.0]],
            [[1.0, 1.0], [1.0, 1.0]],
        ]

        metrics = calculate_iqms(volume)

        self.assertEqual(metrics["normalized_gradient_squared"], 0.0)
        self.assertEqual(metrics["std_intensity"], 0.0)

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


if __name__ == "__main__":
    unittest.main()
