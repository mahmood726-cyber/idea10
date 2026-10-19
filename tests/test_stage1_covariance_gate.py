"""Scientific gate: shared-reference contrasts require study-level covariance.

Synthetic inputs only. This test is intentionally expected to FAIL on the
existing implementation and must NOT be marked green or waived. Adapt the API
with a validated covariance route before claiming valid categorical DRMA.
"""
import unittest
import numpy as np
from dose_response_meta.two_stage import TwoStageDRMA


def linear_basis(doses):
    return np.asarray(doses, dtype=float).reshape(-1, 1)


class SharedReferenceStage1Gate(unittest.TestCase):
    def test_stage_one_uses_full_covariance_and_matches_gls(self):
        # Three correlated log risks relative to the same reference category:
        # variance(group)=0.01, variance(reference)=0.09.
        doses = np.array([1., 2., 3.])
        y = np.array([0., .4, .4])
        V = np.full((3, 3), .09) + np.eye(3) * .01
        x = linear_basis(doses)
        Vinv_x = np.linalg.solve(V, x)
        target_var = np.linalg.inv(x.T @ Vinv_x)
        target_beta = np.linalg.solve(x.T @ Vinv_x, x.T @ np.linalg.solve(V, y))

        model = TwoStageDRMA(pooling_method='fixed')
        # Planned corrected interface, not supported by original source.
        got = model._fit_study(doses, y, np.diag(V), linear_basis, covariance=V)
        np.testing.assert_allclose(got['beta'], target_beta, rtol=1e-10, atol=1e-10)
        np.testing.assert_allclose(got['vcov'], target_var, rtol=1e-10, atol=1e-10)

    def test_invalid_covariance_is_rejected(self):
        model = TwoStageDRMA(pooling_method='fixed')
        doses = np.array([1., 2., 3.])
        # Numerically invalid covariance MUST NOT be silently repaired.
        V = np.array([[1., 2., 0.], [2., 1., 0.], [0., 0., 1.]])
        with self.assertRaises(ValueError):
            model._fit_study(doses, np.zeros(3), np.diag(V), linear_basis, covariance=V)


if __name__ == '__main__':
    unittest.main()
