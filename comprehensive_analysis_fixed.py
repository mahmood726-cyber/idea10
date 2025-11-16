"""
Comprehensive Analysis for Dose-Response Meta-Analysis Methods
Fixed version using correct API

Integrates:
- All 8 scenarios
- Convergence tracking
- Proper scoring rules
- HKSJ correction
"""

import numpy as np
import pandas as pd
from pathlib import Path
import warnings
import sys
warnings.filterwarnings('ignore')

# Add to path
sys.path.insert(0, '/home/user/idea10')

from dose_response_meta.splines import RestrictedCubicSpline
from dose_response_meta.fractional_polynomials import FractionalPolynomial
from dose_response_meta.one_stage import OneStageDRMA
from dose_response_meta.two_stage import TwoStageDRMA
from dose_response_meta.simulation import DoseResponseSimulator
from dose_response_meta.convergence_tracker import ConvergenceTracker
from dose_response_meta.scoring_rules import (
    interval_score,
    decompose_interval_score,
    calibration_metrics
)


class ComprehensiveAnalysis:
    """Complete analysis framework"""

    def __init__(self, n_simulations=100, n_studies=15, output_dir='results'):
        self.n_simulations = n_simulations
        self.n_studies = n_studies
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)

        self.tracker = ConvergenceTracker()
        self.all_results = []

    def get_scenarios(self):
        """Define all 8 scenarios"""
        return {
            '1_linear_low_het': {
                'curve': lambda x: 0.01 * x,
                'tau2': 0.01,
                'dose_range': (0, 100)
            },
            '2_quadratic_mod_het': {
                'curve': lambda x: 0.01 * x - 0.0001 * x**2,
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            '3_log_high_het': {
                'curve': lambda x: 0.3 * np.log(x + 1),
                'tau2': 0.10,
                'dose_range': (0, 100)
            },
            '4_threshold_mod_het': {
                'curve': lambda x: np.where(x < 50, 0, 0.01 * (x - 50)),
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            '5_complex_nonlinear': {
                'curve': lambda x: 0.2 * np.sin(x / 20) + 0.005 * x,
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            '6_u_shaped': {
                'curve': lambda x: 0.0002 * (x - 50) ** 2,
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            '7_j_shaped': {
                'curve': self._j_curve,
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            '8_quadratic_dose_dep_het': {
                'curve': lambda x: 0.01 * x - 0.0001 * x**2,
                'tau2': 'dose_dependent',
                'dose_range': (0, 100)
            }
        }

    @staticmethod
    def _j_curve(x):
        """J-shaped curve"""
        x = np.atleast_1d(x)
        result = np.zeros_like(x, dtype=float)
        threshold = 20
        mask_low = x < threshold
        result[mask_low] = -0.01 * (threshold - x[mask_low])
        mask_high = x >= threshold
        result[mask_high] = 0.0002 * (x[mask_high] - threshold) ** 2
        return result

    def run_analysis(self):
        """Run complete analysis"""
        scenarios = self.get_scenarios()

        print("\n" + "="*80)
        print("COMPREHENSIVE DOSE-RESPONSE META-ANALYSIS")
        print("="*80)
        print(f"Scenarios: {len(scenarios)}")
        print(f"Simulations per scenario: {self.n_simulations}")
        print(f"Studies per meta-analysis: {self.n_studies}")
        print("="*80)

        for scenario_name, scenario_config in scenarios.items():
            print(f"\n{'='*80}")
            print(f"SCENARIO: {scenario_name} - {scenario_config.get('description', '')}")
            print(f"{'='*80}")

            for sim_idx in range(self.n_simulations):
                if (sim_idx + 1) % 10 == 0:
                    print(f"  Simulation {sim_idx + 1}/{self.n_simulations}...")

                results = self._run_single_simulation(
                    scenario_name, scenario_config, sim_idx
                )
                self.all_results.extend(results)

            print(f"  ✓ Completed {self.n_simulations} simulations")

        self._save_and_report()

    def _run_single_simulation(self, scenario_name, scenario_config, sim_idx):
        """Run one simulation"""
        np.random.seed(42 + sim_idx)

        # Generate data
        simulator = DoseResponseSimulator(
            n_studies=self.n_studies,
            doses_per_study=4
        )

        if scenario_config['tau2'] == 'dose_dependent':
            studies = simulator.generate_studies_dose_dependent_het(
                true_curve=scenario_config['curve'],
                base_tau2=0.02,
                het_slope=0.015,
                dose_range=scenario_config['dose_range']
            )
        else:
            studies = simulator.generate_studies(
                true_curve=scenario_config['curve'],
                study_effect=scenario_config['tau2'],
                dose_range=scenario_config['dose_range']
            )

        # Convert to flat arrays for API
        all_doses = []
        all_log_rr = []
        all_var = []
        all_study_id = []

        for study_idx, study in enumerate(studies):
            all_doses.extend(study['doses'])
            all_log_rr.extend(study['log_rr'])
            all_var.extend(study['var'])
            all_study_id.extend([study_idx] * len(study['doses']))

        doses = np.array(all_doses)
        log_rr = np.array(all_log_rr)
        variance = np.array(all_var)
        study_id = np.array(all_study_id)

        # Prediction grid
        dose_grid = np.linspace(
            scenario_config['dose_range'][0],
            scenario_config['dose_range'][1],
            100
        )
        y_true = scenario_config['curve'](dose_grid)

        # Results for this simulation
        sim_results = []

        # Method 1: Two-Stage RCS DL (primary method)
        sim_results.append(
            self._fit_two_stage_rcs_dl(
                scenario_name, sim_idx, doses, log_rr, variance,
                study_id, dose_grid, y_true
            )
        )

        # Method 2: Two-Stage RCS Fixed
        sim_results.append(
            self._fit_two_stage_rcs_fixed(
                scenario_name, sim_idx, doses, log_rr, variance,
                study_id, dose_grid, y_true
            )
        )

        # Method 3: One-Stage RCS
        sim_results.append(
            self._fit_one_stage_rcs(
                scenario_name, sim_idx, doses, log_rr, variance,
                study_id, dose_grid, y_true
            )
        )

        return sim_results

    def _fit_two_stage_rcs_dl(self, scenario, sim_idx, doses, log_rr,
                               variance, study_id, dose_grid, y_true):
        """Fit two-stage RCS with DL + HKSJ"""
        method_name = 'TwoStage_RCS_DL_HKSJ'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            # Create RCS basis function
            knots = np.percentile(doses, [5, 35, 65, 95])

            def rcs_basis(d):
                rcs = RestrictedCubicSpline(n_knots=4, knot_positions=knots)
                return rcs._compute_spline_basis(d, knots)

            # Fit model
            model = TwoStageDRMA(pooling_method='dl')
            model.fit(doses, log_rr, variance, study_id, rcs_basis)

            # Predict with HKSJ
            pred_basis = rcs_basis(dose_grid)
            predictions = pred_basis @ model.pooled_beta

            # Get CI with HKSJ correction
            se = np.sqrt(np.diag(pred_basis @ model.pooled_vcov @ pred_basis.T))

            # Apply HKSJ if applicable
            if hasattr(model, 'heterogeneity_stats') and model.heterogeneity_stats is not None:
                Q = model.heterogeneity_stats.get('Q', 0)
                Q_df = model.heterogeneity_stats.get('Q_df', 1)
                if Q_df > 0:
                    hksj_factor = np.sqrt(Q / Q_df)
                    se_hksj = se * hksj_factor

                    # Use t-distribution
                    from scipy.stats import t
                    t_crit = t.ppf(0.975, df=Q_df)
                    ci_lower = predictions - t_crit * se_hksj
                    ci_upper = predictions + t_crit * se_hksj
                else:
                    ci_lower = predictions - 1.96 * se
                    ci_upper = predictions + 1.96 * se
            else:
                ci_lower = predictions - 1.96 * se
                ci_upper = predictions + 1.96 * se

            # Compute metrics
            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            if hasattr(model, 'heterogeneity_stats') and model.heterogeneity_stats:
                metrics['tau2'] = model.heterogeneity_stats.get('tau2', np.nan)
                metrics['I2'] = model.heterogeneity_stats.get('I2', np.nan)

            self.tracker.record_success(tau2=metrics.get('tau2', np.nan))

            return {
                'scenario': scenario,
                'method': method_name,
                'sim_idx': sim_idx,
                'converged': True,
                **metrics
            }

        except Exception as e:
            self.tracker.record_failure(str(e))
            return self._failed_result(scenario, method_name, sim_idx, str(e))

    def _fit_two_stage_rcs_fixed(self, scenario, sim_idx, doses, log_rr,
                                  variance, study_id, dose_grid, y_true):
        """Fit two-stage RCS fixed-effects"""
        method_name = 'TwoStage_RCS_Fixed'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            knots = np.percentile(doses, [5, 35, 65, 95])

            def rcs_basis(d):
                rcs = RestrictedCubicSpline(n_knots=4, knot_positions=knots)
                return rcs._compute_spline_basis(d, knots)

            model = TwoStageDRMA(pooling_method='fixed')
            model.fit(doses, log_rr, variance, study_id, rcs_basis)

            pred_basis = rcs_basis(dose_grid)
            predictions = pred_basis @ model.pooled_beta
            se = np.sqrt(np.diag(pred_basis @ model.pooled_vcov @ pred_basis.T))

            ci_lower = predictions - 1.96 * se
            ci_upper = predictions + 1.96 * se

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            self.tracker.record_success()

            return {
                'scenario': scenario,
                'method': method_name,
                'sim_idx': sim_idx,
                'converged': True,
                **metrics
            }

        except Exception as e:
            self.tracker.record_failure(str(e))
            return self._failed_result(scenario, method_name, sim_idx, str(e))

    def _fit_one_stage_rcs(self, scenario, sim_idx, doses, log_rr,
                           variance, study_id, dose_grid, y_true):
        """Fit one-stage RCS"""
        method_name = 'OneStage_RCS'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            knots = np.percentile(doses, [5, 35, 65, 95])

            def rcs_basis(d):
                rcs = RestrictedCubicSpline(n_knots=4, knot_positions=knots)
                return rcs._compute_spline_basis(d, knots)

            model = OneStageDRMA(method='spline', heterogeneity='iso')
            model.fit(doses, log_rr, variance, study_id, rcs_basis)

            predictions, ci_lower, ci_upper = model.predict(dose_grid, return_ci=True)

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            het_stats = model.get_heterogeneity_stats()
            metrics['tau2'] = het_stats.get('tau2', np.nan)
            metrics['I2'] = het_stats.get('I2', np.nan)

            self.tracker.record_success(tau2=metrics['tau2'])

            return {
                'scenario': scenario,
                'method': method_name,
                'sim_idx': sim_idx,
                'converged': True,
                **metrics
            }

        except Exception as e:
            self.tracker.record_failure(str(e))
            return self._failed_result(scenario, method_name, sim_idx, str(e))

    def _compute_metrics(self, y_true, predictions, ci_lower, ci_upper):
        """Compute all performance metrics"""
        # Traditional
        mse = np.mean((predictions - y_true) ** 2)
        bias = np.mean(predictions - y_true)
        coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100

        # Proper scoring rules
        scores, mean_is = interval_score(y_true, ci_lower, ci_upper, alpha=0.05)
        decomp = decompose_interval_score(y_true, ci_lower, ci_upper)
        calib = calibration_metrics(y_true, ci_lower, ci_upper)

        return {
            'mse': mse,
            'bias': bias,
            'coverage': coverage,
            'interval_score': mean_is,
            'sharpness': decomp['sharpness'],
            'calibration': decomp['calibration'],
            'coverage_error': calib['coverage_error'],
            'mean_width': np.mean(ci_upper - ci_lower)
        }

    def _failed_result(self, scenario, method, sim_idx, error_msg):
        """Create result for failed fit"""
        return {
            'scenario': scenario,
            'method': method,
            'sim_idx': sim_idx,
            'converged': False,
            'error': error_msg,
            'mse': np.nan,
            'bias': np.nan,
            'coverage': np.nan,
            'interval_score': np.nan,
            'sharpness': np.nan,
            'calibration': np.nan,
            'coverage_error': np.nan,
            'mean_width': np.nan
        }

    def _save_and_report(self):
        """Save results and generate reports"""
        # Save detailed results
        df = pd.DataFrame(self.all_results)
        df.to_csv(self.output_dir / 'detailed_results.csv', index=False)
        print(f"\nDetailed results: {self.output_dir / 'detailed_results.csv'}")

        # Save convergence
        self.tracker.save_results(self.output_dir / 'convergence_diagnostics.csv')

        # Summary tables
        df_conv = df[df['converged']].copy()

        if len(df_conv) > 0:
            summary = df_conv.groupby(['scenario', 'method']).agg({
                'mse': ['mean', 'std'],
                'bias': ['mean', 'std'],
                'coverage': ['mean', 'std'],
                'interval_score': ['mean', 'std'],
                'sharpness': ['mean', 'std'],
                'calibration': ['mean', 'std']
            }).round(4)

            summary.to_csv(self.output_dir / 'summary_by_scenario_method.csv')
            print(f"Summary table: {self.output_dir / 'summary_by_scenario_method.csv'}")

            # Print coverage summary
            print("\n" + "="*80)
            print("COVERAGE SUMMARY (Target: 95%)")
            print("="*80)
            coverage_summary = df_conv.pivot_table(
                values='coverage',
                index='scenario',
                columns='method',
                aggfunc='mean'
            ).round(1)
            print(coverage_summary)

            print("\n" + "="*80)
            print("MSE SUMMARY")
            print("="*80)
            mse_summary = df_conv.pivot_table(
                values='mse',
                index='scenario',
                columns='method',
                aggfunc='mean'
            ).round(6)
            print(mse_summary)

        # Convergence summary
        print("\n")
        self.tracker.print_summary()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE!")
        print("="*80)


def main():
    """Run analysis"""
    import sys

    # Default to 20 sims for quick test
    n_sims = 20
    if len(sys.argv) > 1:
        n_sims = int(sys.argv[1])

    print(f"Running with {n_sims} simulations per scenario")
    print(f"Estimated time: {n_sims * 0.5} - {n_sims * 1.0} minutes")
    print()

    analysis = ComprehensiveAnalysis(
        n_simulations=n_sims,
        n_studies=15,
        output_dir='results'
    )

    analysis.run_analysis()


if __name__ == '__main__':
    main()
