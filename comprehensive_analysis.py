"""
Comprehensive Analysis Script for Dose-Response Meta-Analysis Methods

This script demonstrates and compares:
1. Restricted cubic splines vs Fractional polynomials
2. One-stage vs Two-stage meta-analysis
3. Performance across different scenarios
4. Heterogeneity assessment

For Advanced Methods Paper
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Import our modules
from dose_response_meta.splines import RestrictedCubicSpline
from dose_response_meta.fractional_polynomials import FractionalPolynomial
from dose_response_meta.one_stage import OneStageDRMA
from dose_response_meta.two_stage import TwoStageDRMA
from dose_response_meta.simulation import DoseResponseSimulator, generate_example_scenarios
from dose_response_meta.visualization import DoseResponsePlotter


class DoseResponseAnalysis:
    """
    Comprehensive analysis framework for comparing dose-response meta-analysis methods
    """

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.plotter = DoseResponsePlotter()
        self.results = {}

    def run_single_analysis(self, data: pd.DataFrame, scenario_name: str):
        """
        Run all methods on a single dataset

        Parameters
        ----------
        data : pd.DataFrame
            Simulated or real dose-response data
        scenario_name : str
            Name of the scenario for saving results
        """
        print(f"\n{'='*70}")
        print(f"Analyzing Scenario: {scenario_name}")
        print(f"{'='*70}")

        doses = data['dose'].values
        log_rr = data['log_rr'].values
        variance = data['variance'].values
        study_id = data['study_id'].values

        # Prepare prediction doses
        dose_pred = np.linspace(doses.min(), doses.max(), 200)

        scenario_results = {
            'data': data,
            'methods': {}
        }

        # ========================================
        # Method 1: Restricted Cubic Splines (pooled)
        # ========================================
        print("\n[1/6] Fitting Restricted Cubic Splines (pooled)...")
        try:
            rcs = RestrictedCubicSpline(n_knots=4)
            rcs.fit(doses, log_rr, variance, study_id)

            rcs_pred, rcs_lower, rcs_upper = rcs.predict(dose_pred, return_ci=True)
            rcs_nonlin = rcs.test_non_linearity()

            scenario_results['methods']['RCS_pooled'] = {
                'model': rcs,
                'predictions': (rcs_pred, rcs_lower, rcs_upper),
                'nonlinearity_test': rcs_nonlin,
                'knots': rcs.knots
            }

            print(f"  ✓ RCS fitted with {rcs.n_knots} knots")
            print(f"  ✓ Non-linearity p-value: {rcs_nonlin['p_value']:.4f}")

        except Exception as e:
            print(f"  ✗ RCS failed: {e}")

        # ========================================
        # Method 2: Fractional Polynomials (pooled)
        # ========================================
        print("\n[2/6] Fitting Fractional Polynomials (pooled)...")
        try:
            fp = FractionalPolynomial(degree=2)
            fp.fit(doses, log_rr, variance, method='aic')

            fp_pred, fp_lower, fp_upper = fp.predict(dose_pred, return_ci=True)
            fp_nonlin = fp.test_non_linearity()
            fp_info = fp.get_model_info()

            scenario_results['methods']['FP2_pooled'] = {
                'model': fp,
                'predictions': (fp_pred, fp_lower, fp_upper),
                'nonlinearity_test': fp_nonlin,
                'best_powers': fp_info['best_powers'],
                'deviance': fp_info['deviance']
            }

            print(f"  ✓ FP2 fitted with powers: {fp_info['best_powers']}")
            print(f"  ✓ Non-linearity p-value: {fp_nonlin['p_value']:.4f}")

        except Exception as e:
            print(f"  ✗ FP2 failed: {e}")

        # ========================================
        # Method 3: One-Stage RCS
        # ========================================
        print("\n[3/6] Fitting One-Stage RCS Meta-Analysis...")
        try:
            # Create basis function for one-stage
            def rcs_basis(d):
                temp_rcs = RestrictedCubicSpline(n_knots=4)
                # Use same knots as pooled RCS
                if 'RCS_pooled' in scenario_results['methods']:
                    temp_rcs.knots = scenario_results['methods']['RCS_pooled']['knots']
                else:
                    temp_rcs.knots = np.percentile(doses, [5, 35, 65, 95])
                return temp_rcs._compute_spline_basis(d, temp_rcs.knots)

            one_stage = OneStageDRMA(method='spline', heterogeneity='iso')
            one_stage.fit(doses, log_rr, variance, study_id, rcs_basis)

            os_pred, os_lower, os_upper = one_stage.predict(dose_pred, return_ci=True)
            os_het = one_stage.get_heterogeneity_stats()

            scenario_results['methods']['OneStage_RCS'] = {
                'model': one_stage,
                'predictions': (os_pred, os_lower, os_upper),
                'heterogeneity': os_het
            }

            print(f"  ✓ One-stage fitted")
            print(f"  ✓ τ² = {os_het['tau2']:.4f}, I² = {os_het['I2']:.1f}%")

        except Exception as e:
            print(f"  ✗ One-stage failed: {e}")

        # ========================================
        # Method 4: Two-Stage RCS (DL)
        # ========================================
        print("\n[4/6] Fitting Two-Stage RCS Meta-Analysis (DL)...")
        try:
            two_stage = TwoStageDRMA(pooling_method='dl')
            two_stage.fit(doses, log_rr, variance, study_id, rcs_basis)

            ts_pred, ts_lower, ts_upper = two_stage.predict(dose_pred, return_ci=True)
            ts_summary = two_stage.get_model_summary()

            scenario_results['methods']['TwoStage_RCS_DL'] = {
                'model': two_stage,
                'predictions': (ts_pred, ts_lower, ts_upper),
                'heterogeneity': {
                    'tau2': ts_summary['tau2'],
                    'I2': ts_summary['I2'],
                    'Q': ts_summary['Q']
                }
            }

            print(f"  ✓ Two-stage (DL) fitted")
            print(f"  ✓ τ² = {ts_summary['tau2']:.4f}, I² = {ts_summary['I2']:.1f}%")

        except Exception as e:
            print(f"  ✗ Two-stage (DL) failed: {e}")

        # ========================================
        # Method 5: Two-Stage RCS (Fixed-effects)
        # ========================================
        print("\n[5/6] Fitting Two-Stage RCS Meta-Analysis (Fixed)...")
        try:
            two_stage_fe = TwoStageDRMA(pooling_method='fixed')
            two_stage_fe.fit(doses, log_rr, variance, study_id, rcs_basis)

            tsfe_pred, tsfe_lower, tsfe_upper = two_stage_fe.predict(dose_pred, return_ci=True)

            scenario_results['methods']['TwoStage_RCS_Fixed'] = {
                'model': two_stage_fe,
                'predictions': (tsfe_pred, tsfe_lower, tsfe_upper)
            }

            print(f"  ✓ Two-stage (Fixed) fitted")

        except Exception as e:
            print(f"  ✗ Two-stage (Fixed) failed: {e}")

        # ========================================
        # Method 6: One-Stage FP
        # ========================================
        print("\n[6/6] Fitting One-Stage FP Meta-Analysis...")
        try:
            # Create FP basis function
            def fp_basis(d):
                temp_fp = FractionalPolynomial(degree=2)
                if 'FP2_pooled' in scenario_results['methods']:
                    temp_fp.best_powers = scenario_results['methods']['FP2_pooled']['best_powers']
                else:
                    temp_fp.best_powers = (1, 2)  # Default
                return temp_fp._create_fp_basis(d, temp_fp.best_powers)

            one_stage_fp = OneStageDRMA(method='fp', heterogeneity='iso')
            one_stage_fp.fit(doses, log_rr, variance, study_id, fp_basis)

            osfp_pred, osfp_lower, osfp_upper = one_stage_fp.predict(dose_pred, return_ci=True)
            osfp_het = one_stage_fp.get_heterogeneity_stats()

            scenario_results['methods']['OneStage_FP'] = {
                'model': one_stage_fp,
                'predictions': (osfp_pred, osfp_lower, osfp_upper),
                'heterogeneity': osfp_het
            }

            print(f"  ✓ One-stage FP fitted")
            print(f"  ✓ τ² = {osfp_het['tau2']:.4f}, I² = {osfp_het['I2']:.1f}%")

        except Exception as e:
            print(f"  ✗ One-stage FP failed: {e}")

        # ========================================
        # Compute Performance Metrics
        # ========================================
        if 'true_log_rr' in data.columns:
            print("\n[Evaluation] Computing performance metrics...")
            scenario_results['performance'] = self._compute_performance_metrics(
                data, dose_pred, scenario_results['methods']
            )

        # ========================================
        # Generate Visualizations
        # ========================================
        print("\n[Visualization] Creating plots...")
        self._create_visualizations(scenario_results, dose_pred, scenario_name)

        # Store results
        self.results[scenario_name] = scenario_results

        print(f"\n✓ Analysis complete for {scenario_name}")
        print(f"{'='*70}\n")

        return scenario_results

    def _compute_performance_metrics(self, data, dose_pred, methods):
        """Compute MSE, bias, coverage for each method"""
        # Interpolate true curve at prediction points
        from scipy.interpolate import interp1d

        true_doses = data['dose'].values
        true_log_rr = data['true_log_rr'].values

        # Get unique true values (average by dose if multiple observations)
        dose_groups = data.groupby('dose')['true_log_rr'].mean()
        interp_func = interp1d(dose_groups.index, dose_groups.values,
                               kind='linear', fill_value='extrapolate')
        true_at_pred = interp_func(dose_pred)

        metrics = []

        for method_name, method_data in methods.items():
            pred, lower, upper = method_data['predictions']

            # MSE
            mse = np.mean((pred - true_at_pred) ** 2)

            # Bias
            bias = np.mean(pred - true_at_pred)

            # Coverage (percentage of true values within CI)
            coverage = np.mean((true_at_pred >= lower) & (true_at_pred <= upper)) * 100

            # CI width
            ci_width = np.mean(upper - lower)

            metrics.append({
                'Method': method_name,
                'MSE': mse,
                'Bias': bias,
                'Coverage': coverage,
                'CI_Width': ci_width
            })

        return pd.DataFrame(metrics)

    def _create_visualizations(self, scenario_results, dose_pred, scenario_name):
        """Create all visualization plots"""
        data = scenario_results['data']
        methods = scenario_results['methods']

        # 1. Method comparison plot
        method_dict = {}
        for name, method_data in methods.items():
            method_dict[name] = method_data['predictions']

        true_curve = None
        if 'true_log_rr' in data.columns:
            from scipy.interpolate import interp1d
            dose_groups = data.groupby('dose')['true_log_rr'].mean()
            interp_func = interp1d(dose_groups.index, dose_groups.values,
                                   kind='linear', fill_value='extrapolate')
            true_curve = interp_func(dose_pred)

        self.plotter.plot_method_comparison(
            dose_pred,
            method_dict,
            true_curve=true_curve,
            title=f"Method Comparison: {scenario_name}",
            save_path=self.output_dir / f"{scenario_name}_comparison.png"
        )

        # 2. Heterogeneity statistics
        het_stats = {}
        for name, method_data in methods.items():
            if 'heterogeneity' in method_data:
                het_stats[name] = method_data['heterogeneity']

        if het_stats:
            self.plotter.plot_heterogeneity_stats(
                het_stats,
                title=f"Heterogeneity Statistics: {scenario_name}",
                save_path=self.output_dir / f"{scenario_name}_heterogeneity.png"
            )

        # 3. Performance metrics (if available)
        if 'performance' in scenario_results:
            self.plotter.plot_performance_metrics(
                scenario_results['performance'],
                title=f"Performance Metrics: {scenario_name}",
                save_path=self.output_dir / f"{scenario_name}_performance.png"
            )

    def generate_summary_table(self):
        """Generate summary table across all scenarios"""
        summary_data = []

        for scenario_name, scenario_results in self.results.items():
            if 'performance' in scenario_results:
                perf = scenario_results['performance']
                for _, row in perf.iterrows():
                    summary_data.append({
                        'Scenario': scenario_name,
                        **row.to_dict()
                    })

        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(self.output_dir / "summary_table.csv", index=False)

            print("\n" + "="*80)
            print("SUMMARY TABLE: Performance Across All Scenarios")
            print("="*80)
            print(summary_df.to_string(index=False))
            print("="*80 + "\n")

            return summary_df
        return None


def main():
    """
    Main analysis script
    """
    print("\n" + "="*80)
    print("DOSE-RESPONSE META-ANALYSIS: COMPREHENSIVE METHODS COMPARISON")
    print("="*80)
    print("\nThis analysis compares:")
    print("  • Restricted Cubic Splines vs Fractional Polynomials")
    print("  • One-Stage vs Two-Stage Meta-Analysis")
    print("  • Different dose-response scenarios")
    print("\n" + "="*80 + "\n")

    # Initialize analysis framework
    analysis = DoseResponseAnalysis(output_dir="results")

    # Generate example scenarios
    print("Generating simulation scenarios...")
    scenarios = generate_example_scenarios()

    # Run analysis for each scenario
    for scenario_name, simulator in scenarios.items():
        print(f"\nSimulating data for: {scenario_name}...")
        data = simulator.simulate()

        # Run comprehensive analysis
        analysis.run_single_analysis(data, scenario_name)

    # Generate summary
    summary = analysis.generate_summary_table()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)
    print(f"\nResults saved to: {analysis.output_dir}")
    print("\nGenerated files:")
    print("  • Comparison plots for each scenario")
    print("  • Heterogeneity statistics")
    print("  • Performance metrics")
    print("  • Summary table (CSV)")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    main()
