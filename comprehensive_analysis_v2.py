"""
Comprehensive Analysis Script for Dose-Response Meta-Analysis Methods
Version 2.0 - With Convergence Tracking and Proper Scoring Rules

Integrates:
1. All 8 scenarios (including U-shaped, J-shaped, dose-dependent heterogeneity)
2. Convergence tracking for all methods
3. Proper scoring rules (interval score, calibration, sharpness)
4. HKSJ correction for small-sample inference
5. Performance metrics and comprehensive reporting

For Advanced Methods Paper - Post-Revision Version
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import warnings
import time
warnings.filterwarnings('ignore')

# Import our modules
from dose_response_meta.splines import RestrictedCubicSpline
from dose_response_meta.fractional_polynomials import FractionalPolynomial
from dose_response_meta.one_stage import OneStageDoseResponse
from dose_response_meta.two_stage import TwoStageDoseResponse
from dose_response_meta.simulation import DoseResponseSimulator
from dose_response_meta.convergence_tracker import ConvergenceTracker, create_convergence_table
from dose_response_meta.scoring_rules import (
    interval_score,
    decompose_interval_score,
    calibration_metrics,
    sharpness_metrics,
    comprehensive_evaluation
)


class ComprehensiveAnalysis:
    """
    Complete framework for dose-response meta-analysis comparison

    Includes:
    - All 8 scenarios
    - Convergence tracking
    - Proper scoring rules
    - HKSJ correction
    """

    def __init__(self,
                 n_simulations: int = 100,
                 n_studies_per_sim: int = 15,
                 output_dir: str = "results"):
        """
        Parameters
        ----------
        n_simulations : int
            Number of simulations per scenario
        n_studies_per_sim : int
            Studies per meta-analysis
        output_dir : str
            Directory for results
        """
        self.n_simulations = n_simulations
        self.n_studies = n_studies_per_sim
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
                'dose_range': (0, 100),
                'description': 'Linear, low heterogeneity'
            },
            '2_quadratic_mod_het': {
                'curve': lambda x: 0.01 * x - 0.0001 * x**2,
                'tau2': 0.05,
                'dose_range': (0, 100),
                'description': 'Quadratic, moderate heterogeneity'
            },
            '3_log_high_het': {
                'curve': lambda x: 0.3 * np.log(x + 1),
                'tau2': 0.10,
                'dose_range': (0, 100),
                'description': 'Logarithmic, high heterogeneity'
            },
            '4_threshold_mod_het': {
                'curve': lambda x: np.where(x < 50, 0, 0.01 * (x - 50)),
                'tau2': 0.05,
                'dose_range': (0, 100),
                'description': 'Threshold effect at 50'
            },
            '5_complex_nonlinear': {
                'curve': lambda x: 0.2 * np.sin(x / 20) + 0.005 * x,
                'tau2': 0.05,
                'dose_range': (0, 100),
                'description': 'Complex sinusoidal'
            },
            '6_u_shaped': {
                'curve': lambda x: 0.0002 * (x - 50) ** 2,
                'tau2': 0.05,
                'dose_range': (0, 100),
                'description': 'U-shaped (vitamin effect)'
            },
            '7_j_shaped': {
                'curve': self._j_curve,
                'tau2': 0.05,
                'dose_range': (0, 100),
                'description': 'J-shaped (alcohol effect)'
            },
            '8_dose_dep_het': {
                'curve': lambda x: 0.01 * x - 0.0001 * x**2,
                'tau2': 'dose_dependent',  # Special handling
                'dose_range': (0, 100),
                'description': 'Dose-dependent heterogeneity'
            }
        }

    @staticmethod
    def _j_curve(x):
        """J-shaped curve: protective at low, harmful at high"""
        x = np.atleast_1d(x)
        result = np.zeros_like(x, dtype=float)
        threshold = 20
        mask_low = x < threshold
        result[mask_low] = -0.01 * (threshold - x[mask_low])
        mask_high = x >= threshold
        result[mask_high] = 0.0002 * (x[mask_high] - threshold) ** 2
        return result

    def run_complete_analysis(self):
        """
        Run full analysis: all scenarios × all methods × all simulations
        """
        scenarios = self.get_scenarios()

        print("\n" + "="*80)
        print("COMPREHENSIVE DOSE-RESPONSE META-ANALYSIS")
        print("="*80)
        print(f"Scenarios: {len(scenarios)}")
        print(f"Simulations per scenario: {self.n_simulations}")
        print(f"Studies per meta-analysis: {self.n_studies}")
        print(f"Total analyses: {len(scenarios) * self.n_simulations * 6} (6 methods)")
        print("="*80)

        for scenario_name, scenario_config in scenarios.items():
            print(f"\n{'='*80}")
            print(f"SCENARIO: {scenario_name}")
            print(f"Description: {scenario_config['description']}")
            print(f"{'='*80}")

            for sim_idx in range(self.n_simulations):
                if (sim_idx + 1) % 20 == 0:
                    print(f"  Simulation {sim_idx + 1}/{self.n_simulations}...")

                # Generate data
                results = self._run_single_simulation(
                    scenario_name=scenario_name,
                    scenario_config=scenario_config,
                    sim_idx=sim_idx
                )

                self.all_results.extend(results)

            print(f"  ✓ Completed {self.n_simulations} simulations")

        # Save results
        self._save_results()

        # Generate reports
        self._generate_reports()

        print("\n" + "="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

    def _run_single_simulation(self, scenario_name, scenario_config, sim_idx):
        """Run single simulation across all methods"""

        # Generate data
        np.random.seed(42 + sim_idx)
        simulator = DoseResponseSimulator(
            n_studies=self.n_studies,
            doses_per_study=4
        )

        # Handle dose-dependent heterogeneity
        if scenario_config['tau2'] == 'dose_dependent':
            # Generate with dose-dependent tau2
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

        # Prepare data
        doses_list = [s['doses'] for s in studies]
        log_rr_list = [s['log_rr'] for s in studies]
        var_list = [s['var'] for s in studies]

        # Prediction grid
        dose_grid = np.linspace(
            scenario_config['dose_range'][0],
            scenario_config['dose_range'][1],
            100
        )
        y_true = scenario_config['curve'](dose_grid)

        # Results for this simulation
        sim_results = []

        # Method 1: RCS Pooled (no meta-analysis)
        sim_results.append(
            self._fit_rcs_pooled(scenario_name, sim_idx, doses_list, log_rr_list,
                                 var_list, dose_grid, y_true)
        )

        # Method 2: FP2 Pooled (no meta-analysis)
        sim_results.append(
            self._fit_fp2_pooled(scenario_name, sim_idx, doses_list, log_rr_list,
                                var_list, dose_grid, y_true)
        )

        # Method 3: One-Stage RCS
        sim_results.append(
            self._fit_one_stage_rcs(scenario_name, sim_idx, doses_list, log_rr_list,
                                   var_list, dose_grid, y_true)
        )

        # Method 4: Two-Stage RCS DL
        sim_results.append(
            self._fit_two_stage_dl(scenario_name, sim_idx, doses_list, log_rr_list,
                                  var_list, dose_grid, y_true)
        )

        # Method 5: Two-Stage RCS Fixed
        sim_results.append(
            self._fit_two_stage_fixed(scenario_name, sim_idx, doses_list, log_rr_list,
                                     var_list, dose_grid, y_true)
        )

        # Method 6: One-Stage FP
        sim_results.append(
            self._fit_one_stage_fp(scenario_name, sim_idx, doses_list, log_rr_list,
                                  var_list, dose_grid, y_true)
        )

        return sim_results

    def _fit_rcs_pooled(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                        dose_grid, y_true):
        """Fit RCS pooled (not meta-analysis)"""
        method_name = 'RCS_pooled'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            # Flatten data
            all_doses = np.concatenate(doses_list)
            all_log_rr = np.concatenate(log_rr_list)
            all_var = np.concatenate(var_list)

            rcs = RestrictedCubicSpline(n_knots=4)
            rcs.fit(all_doses, all_log_rr, all_var)

            predictions, ci_lower, ci_upper = rcs.predict(dose_grid, return_ci=True)

            # Metrics
            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            self.tracker.record_success(n_params=3)

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

    def _fit_fp2_pooled(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                        dose_grid, y_true):
        """Fit FP2 pooled"""
        method_name = 'FP2_pooled'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            all_doses = np.concatenate(doses_list)
            all_log_rr = np.concatenate(log_rr_list)
            all_var = np.concatenate(var_list)

            fp = FractionalPolynomial(degree=2)
            fp.fit(all_doses, all_log_rr, all_var)

            predictions, ci_lower, ci_upper = fp.predict(dose_grid, return_ci=True)

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            self.tracker.record_success(n_params=2)

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

    def _fit_one_stage_rcs(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                          dose_grid, y_true):
        """Fit one-stage RCS"""
        method_name = 'OneStage_RCS'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            model = OneStageDoseResponse(model_type='rcs', n_knots=4)
            model.fit(doses_list, log_rr_list, var_list)

            predictions, ci_lower, ci_upper = model.predict(dose_grid, alpha=0.05)

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)
            metrics['tau2'] = getattr(model, 'tau2', np.nan)

            self.tracker.record_success(tau2=metrics['tau2'], n_params=3)

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

    def _fit_two_stage_dl(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                         dose_grid, y_true):
        """Fit two-stage DL with HKSJ"""
        method_name = 'TwoStage_RCS_DL'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            model = TwoStageDoseResponse(
                model_type='rcs',
                n_knots=4,
                pooling_method='random'
            )
            model.fit(doses_list, log_rr_list, var_list)

            # HKSJ correction (critical for small samples)
            predictions, ci_lower, ci_upper = model.predict(
                dose_grid,
                alpha=0.05,
                use_hksj=True  # HKSJ correction
            )

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            if hasattr(model, 'heterogeneity_stats'):
                metrics['tau2'] = model.heterogeneity_stats.get('tau2', np.nan)
                metrics['I2'] = model.heterogeneity_stats.get('I2', np.nan)
                metrics['Q'] = model.heterogeneity_stats.get('Q', np.nan)

            self.tracker.record_success(tau2=metrics.get('tau2', np.nan), n_params=3)

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

    def _fit_two_stage_fixed(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                            dose_grid, y_true):
        """Fit two-stage fixed-effects"""
        method_name = 'TwoStage_RCS_Fixed'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            model = TwoStageDoseResponse(
                model_type='rcs',
                n_knots=4,
                pooling_method='fixed'
            )
            model.fit(doses_list, log_rr_list, var_list)

            predictions, ci_lower, ci_upper = model.predict(dose_grid, alpha=0.05)

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)

            self.tracker.record_success(n_params=3)

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

    def _fit_one_stage_fp(self, scenario, sim_idx, doses_list, log_rr_list, var_list,
                         dose_grid, y_true):
        """Fit one-stage FP"""
        method_name = 'OneStage_FP'
        self.tracker.start_fit(method_name, scenario, sim_idx)

        try:
            model = OneStageDoseResponse(model_type='fp', fp_powers=(1, 2))
            model.fit(doses_list, log_rr_list, var_list)

            predictions, ci_lower, ci_upper = model.predict(dose_grid, alpha=0.05)

            metrics = self._compute_metrics(y_true, predictions, ci_lower, ci_upper)
            metrics['tau2'] = getattr(model, 'tau2', np.nan)

            self.tracker.record_success(tau2=metrics['tau2'], n_params=2)

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
        """Compute all metrics using proper scoring rules"""

        # Traditional metrics
        mse = np.mean((predictions - y_true) ** 2)
        bias = np.mean(predictions - y_true)

        # Coverage
        coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100

        # Interval score
        scores, mean_is = interval_score(y_true, ci_lower, ci_upper, alpha=0.05)

        # Decomposition
        decomp = decompose_interval_score(y_true, ci_lower, ci_upper)

        # Calibration
        calib = calibration_metrics(y_true, ci_lower, ci_upper)

        # Sharpness
        sharp = sharpness_metrics(ci_lower, ci_upper)

        return {
            'mse': mse,
            'bias': bias,
            'coverage': coverage,
            'interval_score': mean_is,
            'sharpness': decomp['sharpness'],
            'calibration': decomp['calibration'],
            'coverage_error': calib['coverage_error'],
            'mean_width': sharp['mean_width']
        }

    def _failed_result(self, scenario, method, sim_idx, error_msg):
        """Create result dict for failed fit"""
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

    def _save_results(self):
        """Save all results to CSV"""
        df = pd.DataFrame(self.all_results)
        df.to_csv(self.output_dir / 'detailed_results.csv', index=False)
        print(f"\nDetailed results saved: {self.output_dir / 'detailed_results.csv'}")

        # Save convergence tracking
        self.tracker.save_results(self.output_dir / 'convergence_diagnostics.csv')

    def _generate_reports(self):
        """Generate summary reports and tables"""
        df = pd.DataFrame(self.all_results)

        # Filter converged only
        df_conv = df[df['converged']].copy()

        # Summary by scenario and method
        summary = df_conv.groupby(['scenario', 'method']).agg({
            'mse': ['mean', 'std'],
            'bias': ['mean', 'std'],
            'coverage': ['mean', 'std'],
            'interval_score': ['mean', 'std'],
            'sharpness': ['mean', 'std'],
            'calibration': ['mean', 'std']
        }).round(4)

        summary.to_csv(self.output_dir / 'summary_by_scenario_method.csv')
        print(f"Summary table saved: {self.output_dir / 'summary_by_scenario_method.csv'}")

        # Convergence table
        conv_table = create_convergence_table(
            self.tracker,
            output_file=str(self.output_dir / 'convergence_table.md')
        )

        # Print summary
        print("\n" + "="*80)
        print("COVERAGE SUMMARY (Mean % across simulations)")
        print("="*80)
        coverage_summary = df_conv.pivot_table(
            values='coverage',
            index='scenario',
            columns='method',
            aggfunc='mean'
        ).round(1)
        print(coverage_summary)

        print("\n" + "="*80)
        print("MSE SUMMARY (Mean across simulations)")
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


def main():
    """Run comprehensive analysis"""

    analysis = ComprehensiveAnalysis(
        n_simulations=100,
        n_studies_per_sim=15,
        output_dir='results'
    )

    analysis.run_complete_analysis()

    print("\n" + "="*80)
    print("ALL ANALYSES COMPLETE")
    print("="*80)
    print(f"\nResults saved to: {analysis.output_dir}")
    print("\nGenerated files:")
    print("  • detailed_results.csv - All simulation results")
    print("  • summary_by_scenario_method.csv - Aggregated metrics")
    print("  • convergence_diagnostics.csv - Convergence tracking")
    print("  • convergence_table.md - Publication-ready table")
    print("\n" + "="*80)


if __name__ == '__main__':
    main()
