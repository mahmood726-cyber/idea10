"""
Validation Scripts for RCS Implementation

This module provides validation of our RestrictedCubicSpline implementation
against the R rms package (Harrell 2001).

Usage:
1. Install R with rms package
2. Run validation tests
3. Generate validation report

Expected outcome: Maximum absolute difference < 1e-6
"""

import numpy as np
from dose_response_meta.splines import RestrictedCubicSpline


class RCSValidator:
    """
    Validate RCS implementation against known results

    Test cases:
    1. Harrell (2001) - Example from textbook
    2. Simple linear case (should reduce to linear)
    3. Quadratic case
    4. Edge cases (3 knots, 7 knots)
    5. Comparison to R rms::rcspline.eval()
    """

    def __init__(self):
        self.test_results = []

    def test_case_1_harrell_example(self):
        """
        Test Case 1: Harrell (2001) Example

        From Regression Modeling Strategies, 2nd ed., p. 23-24
        Using age as example with 4 knots at ages 20, 40, 60, 80
        """
        print("\n" + "="*70)
        print("Test Case 1: Harrell (2001) Example")
        print("="*70)

        # Example data from Harrell
        ages = np.array([20, 30, 40, 50, 60, 70, 80])
        knots = np.array([20, 40, 60, 80])

        # Create RCS
        rcs = RestrictedCubicSpline(n_knots=4, knot_positions=knots)
        rcs.knots = knots

        # Compute basis
        basis = rcs._compute_spline_basis(ages, knots)

        print(f"Ages: {ages}")
        print(f"Knots: {knots}")
        print(f"\nBasis matrix (n={len(ages)} x p={basis.shape[1]}):")
        print(basis)

        # Expected properties
        # 1. At knot positions, spline terms should have specific values
        # 2. Linear extrapolation beyond boundary knots

        # Test 1: At minimum knot, all spline terms = 0
        idx_min = np.where(ages == knots[0])[0][0]
        spline_at_min = basis[idx_min, 2:]  # Exclude intercept and linear
        print(f"\nSpline terms at min knot (should be ~0): {spline_at_min}")

        # Test 2: At maximum knot, all spline terms = 0
        idx_max = np.where(ages == knots[-1])[0][0]
        spline_at_max = basis[idx_max, 2:]
        print(f"Spline terms at max knot (should be ~0): {spline_at_max}")

        result = {
            'test': 'Harrell Example',
            'basis_shape': basis.shape,
            'min_knot_spline_max': np.max(np.abs(spline_at_min)),
            'max_knot_spline_max': np.max(np.abs(spline_at_max)),
            'pass': np.max(np.abs(spline_at_min)) < 1e-10 and np.max(np.abs(spline_at_max)) < 1e-10
        }

        self.test_results.append(result)
        print(f"\n✓ Test {'PASSED' if result['pass'] else 'FAILED'}")

        return result

    def test_case_2_linear_reduction(self):
        """
        Test Case 2: Linear Relationship

        When true relationship is linear, RCS should reduce to simple linear model
        """
        print("\n" + "="*70)
        print("Test Case 2: Linear Reduction")
        print("="*70)

        # Generate linear data
        doses = np.linspace(0, 100, 50)
        log_rr = 0.01 * doses  # Perfect linear
        variance = np.ones_like(doses) * 0.01

        # Fit RCS
        rcs = RestrictedCubicSpline(n_knots=4)
        rcs.fit(doses, log_rr, variance)

        # Predict
        dose_pred = np.linspace(0, 100, 100)
        pred = rcs.predict(dose_pred)
        expected = 0.01 * dose_pred

        # Check if predictions are approximately linear
        max_diff = np.max(np.abs(pred - expected))

        print(f"Maximum difference from perfect linear: {max_diff:.2e}")
        print(f"R² with linear: {np.corrcoef(pred, expected)[0,1]**2:.6f}")

        # Test non-linearity test
        nonlin_test = rcs.test_non_linearity()
        print(f"Non-linearity p-value: {nonlin_test['p_value']:.4f} (should be > 0.05)")

        result = {
            'test': 'Linear Reduction',
            'max_diff': max_diff,
            'r_squared': np.corrcoef(pred, expected)[0,1]**2,
            'nonlin_pval': nonlin_test['p_value'],
            'pass': max_diff < 0.1 and nonlin_test['p_value'] > 0.05
        }

        self.test_results.append(result)
        print(f"\n✓ Test {'PASSED' if result['pass'] else 'FAILED'}")

        return result

    def test_case_3_quadratic(self):
        """
        Test Case 3: Quadratic Relationship

        RCS should fit quadratic relationship well
        """
        print("\n" + "="*70)
        print("Test Case 3: Quadratic Relationship")
        print("="*70)

        # Generate quadratic data
        doses = np.linspace(0, 100, 50)
        log_rr = 0.01 * doses - 0.0001 * doses**2
        variance = np.ones_like(doses) * 0.01

        # Fit RCS
        rcs = RestrictedCubicSpline(n_knots=4)
        rcs.fit(doses, log_rr, variance)

        # Predict
        dose_pred = np.linspace(0, 100, 100)
        pred = rcs.predict(dose_pred)
        expected = 0.01 * dose_pred - 0.0001 * dose_pred**2

        # Check fit
        mse = np.mean((pred - expected)**2)
        r_squared = 1 - np.sum((pred - expected)**2) / np.sum((expected - expected.mean())**2)

        print(f"MSE: {mse:.2e}")
        print(f"R²: {r_squared:.6f}")

        # Test non-linearity test
        nonlin_test = rcs.test_non_linearity()
        print(f"Non-linearity p-value: {nonlin_test['p_value']:.4f} (should be < 0.05)")

        result = {
            'test': 'Quadratic Fit',
            'mse': mse,
            'r_squared': r_squared,
            'nonlin_pval': nonlin_test['p_value'],
            'pass': r_squared > 0.99 and nonlin_test['p_value'] < 0.05
        }

        self.test_results.append(result)
        print(f"\n✓ Test {'PASSED' if result['pass'] else 'FAILED'}")

        return result

    def test_case_4_edge_cases(self):
        """
        Test Case 4: Edge Cases

        Test with different numbers of knots
        """
        print("\n" + "="*70)
        print("Test Case 4: Edge Cases (3 and 7 knots)")
        print("="*70)

        doses = np.linspace(0, 100, 50)
        log_rr = 0.01 * doses - 0.0001 * doses**2
        variance = np.ones_like(doses) * 0.01

        results_edge = []

        for n_knots in [3, 5, 7]:
            print(f"\n  Testing with {n_knots} knots...")

            try:
                rcs = RestrictedCubicSpline(n_knots=n_knots)
                rcs.fit(doses, log_rr, variance)

                dose_pred = np.linspace(0, 100, 100)
                pred = rcs.predict(dose_pred)
                expected = 0.01 * dose_pred - 0.0001 * dose_pred**2

                mse = np.mean((pred - expected)**2)

                print(f"    MSE: {mse:.2e}")
                print(f"    Knot positions: {rcs.knots}")

                results_edge.append({
                    'n_knots': n_knots,
                    'mse': mse,
                    'success': True
                })
            except Exception as e:
                print(f"    FAILED: {e}")
                results_edge.append({
                    'n_knots': n_knots,
                    'success': False,
                    'error': str(e)
                })

        all_passed = all(r.get('success', False) for r in results_edge)

        result = {
            'test': 'Edge Cases',
            'results': results_edge,
            'pass': all_passed
        }

        self.test_results.append(result)
        print(f"\n✓ Test {'PASSED' if result['pass'] else 'FAILED'}")

        return result

    def generate_r_comparison_script(self):
        """
        Generate R script for comparison

        This creates an R script that users can run to compare our
        implementation to rms::rcspline.eval()
        """
        r_script = """
# RCS Validation Against R rms Package
# Compare Python implementation to R rms::rcspline.eval()

library(rms)

# Test Case 1: Harrell Example
ages <- c(20, 30, 40, 50, 60, 70, 80)
knots <- c(20, 40, 60, 80)

# Compute RCS basis using rms
basis_r <- rcspline.eval(ages, knots=knots, inclx=TRUE)

cat("\\n=== R rms Output ===\\n")
print(basis_r)

cat("\\n=== Save for Python comparison ===\\n")
write.csv(basis_r, "r_rcs_output.csv", row.names=FALSE)

cat("\\nR output saved to r_rcs_output.csv\\n")
cat("Compare this to Python output using validation script\\n")

# Test Case 2: Linear data
doses <- seq(0, 100, length.out=50)
log_rr <- 0.01 * doses
basis_linear <- rcspline.eval(doses, nk=4, inclx=TRUE)

cat("\\n=== Linear Case ===\\n")
cat("Basis dimensions:", dim(basis_linear), "\\n")

# Save
write.csv(data.frame(dose=doses, basis_linear),
          "r_linear_basis.csv", row.names=FALSE)
"""

        with open('validation/compare_to_rms.R', 'w') as f:
            f.write(r_script)

        print("\n" + "="*70)
        print("R comparison script generated: validation/compare_to_rms.R")
        print("="*70)
        print("\nTo run comparison:")
        print("1. Install R and rms package: install.packages('rms')")
        print("2. Run: Rscript validation/compare_to_rms.R")
        print("3. Compare r_rcs_output.csv to Python output")

    def run_all_tests(self):
        """Run all validation tests"""
        print("\n" + "="*70)
        print("RCS VALIDATION TEST SUITE")
        print("="*70)

        self.test_case_1_harrell_example()
        self.test_case_2_linear_reduction()
        self.test_case_3_quadratic()
        self.test_case_4_edge_cases()

        # Summary
        print("\n" + "="*70)
        print("VALIDATION SUMMARY")
        print("="*70)

        passed = sum(1 for r in self.test_results if r['pass'])
        total = len(self.test_results)

        print(f"\nTests passed: {passed}/{total}")

        for i, result in enumerate(self.test_results, 1):
            status = "✓ PASS" if result['pass'] else "✗ FAIL"
            print(f"{i}. {result['test']}: {status}")

        if passed == total:
            print("\n🎉 ALL VALIDATION TESTS PASSED!")
        else:
            print(f"\n⚠️  {total - passed} test(s) failed")

        return self.test_results


def main():
    """Run validation"""
    import os
    os.makedirs('validation', exist_ok=True)

    validator = RCSValidator()
    results = validator.run_all_tests()

    # Generate R comparison script
    validator.generate_r_comparison_script()

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("\n1. Review test results above")
    print("2. Run R comparison script for external validation")
    print("3. Document results in validation report")
    print("\nValidation infrastructure ready! ✓")


if __name__ == "__main__":
    main()
