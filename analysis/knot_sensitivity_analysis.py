"""
Knot Sensitivity Analysis for Restricted Cubic Splines

Tests RCS performance with different numbers of knots (3, 4, 5, 7)
Evaluates impact on:
- Coverage probability
- Mean squared error (MSE)
- Model fit (AIC)
- Calibration and sharpness

For editorial requirement: sensitivity to knot placement
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from dose_response_meta.splines import RestrictedCubicSpline
from dose_response_meta.two_stage import TwoStageDoseResponse
from dose_response_meta.simulation import DoseResponseSimulator
from dose_response_meta.scoring_rules import (
    interval_score,
    decompose_interval_score,
    calibration_metrics,
    sharpness_metrics
)


class KnotSensitivityAnalyzer:
    """
    Analyze RCS performance across different knot configurations

    Tests k ∈ {3, 4, 5, 7} knots across multiple scenarios
    """

    def __init__(self,
                 knot_options: List[int] = [3, 4, 5, 7],
                 n_simulations: int = 100,
                 random_state: int = 42):
        """
        Parameters
        ----------
        knot_options : list of int
            Numbers of knots to test
        n_simulations : int
            Simulations per configuration
        random_state : int
            Random seed
        """
        self.knot_options = knot_options
        self.n_simulations = n_simulations
        self.random_state = random_state
        self.results = []

    def run_analysis(self, scenarios: List[str] = None) -> pd.DataFrame:
        """
        Run knot sensitivity analysis

        Parameters
        ----------
        scenarios : list of str
            Scenario names to test (default: all)

        Returns
        -------
        results_df : pd.DataFrame
            Results with columns:
            - scenario, n_knots, sim_idx, mse, coverage, aic,
              interval_score, sharpness, calibration
        """
        if scenarios is None:
            scenarios = [
                'linear_low_het',
                'quadratic_mod_het',
                'log_high_het',
                'threshold_mod_het',
                'complex_nonlinear'
            ]

        print(f"Running knot sensitivity analysis...")
        print(f"Scenarios: {len(scenarios)}")
        print(f"Knot options: {self.knot_options}")
        print(f"Simulations per config: {self.n_simulations}")
        print(f"Total fits: {len(scenarios) * len(self.knot_options) * self.n_simulations}")
        print()

        for scenario in scenarios:
            print(f"Scenario: {scenario}")

            for n_knots in self.knot_options:
                print(f"  Testing {n_knots} knots...", end=" ")

                for sim_idx in range(self.n_simulations):
                    result = self._run_single_simulation(
                        scenario=scenario,
                        n_knots=n_knots,
                        sim_idx=sim_idx
                    )
                    self.results.append(result)

                print(f"Done ({self.n_simulations} simulations)")

        return pd.DataFrame(self.results)

    def _run_single_simulation(self,
                               scenario: str,
                               n_knots: int,
                               sim_idx: int) -> Dict:
        """Run a single simulation with specified knots"""

        # Generate data
        np.random.seed(self.random_state + sim_idx)
        sim = DoseResponseSimulator(n_studies=15, doses_per_study=4)

        # Get scenario parameters
        scenario_config = self._get_scenario_config(scenario)

        studies = sim.generate_studies(
            true_curve=scenario_config['curve'],
            study_effect=scenario_config['tau2'],
            dose_range=scenario_config['dose_range']
        )

        # Fit RCS with specified knots
        try:
            model = TwoStageDoseResponse(
                model_type='rcs',
                n_knots=n_knots,
                pooling_method='random'
            )

            model.fit(
                doses=[s['doses'] for s in studies],
                log_rr=[s['log_rr'] for s in studies],
                variances=[s['var'] for s in studies]
            )

            # Predictions
            dose_grid = np.linspace(
                scenario_config['dose_range'][0],
                scenario_config['dose_range'][1],
                100
            )

            predictions, ci_lower, ci_upper = model.predict(
                dose_grid,
                alpha=0.05,
                use_hksj=True
            )

            # True values
            y_true = scenario_config['curve'](dose_grid)

            # Metrics
            mse = np.mean((predictions - y_true) ** 2)
            bias = np.mean(predictions - y_true)

            # Coverage
            coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100

            # AIC (approximation)
            n_params = n_knots - 1  # RCS parameters
            rss = np.sum((predictions - y_true) ** 2)
            n = len(dose_grid)
            aic = n * np.log(rss / n) + 2 * n_params

            # Interval score
            scores, mean_is = interval_score(y_true, ci_lower, ci_upper)

            # Decomposition
            decomp = decompose_interval_score(y_true, ci_lower, ci_upper)

            # Calibration metrics
            calib = calibration_metrics(y_true, ci_lower, ci_upper)

            # Sharpness
            sharp = sharpness_metrics(ci_lower, ci_upper)

            return {
                'scenario': scenario,
                'n_knots': n_knots,
                'sim_idx': sim_idx,
                'converged': True,
                'mse': mse,
                'bias': bias,
                'coverage': coverage,
                'aic': aic,
                'interval_score': mean_is,
                'sharpness': decomp['sharpness'],
                'calibration': decomp['calibration'],
                'mean_width': sharp['mean_width'],
                'coverage_error': calib['coverage_error'],
                'well_calibrated': calib['well_calibrated']
            }

        except Exception as e:
            # Record failure
            return {
                'scenario': scenario,
                'n_knots': n_knots,
                'sim_idx': sim_idx,
                'converged': False,
                'mse': np.nan,
                'bias': np.nan,
                'coverage': np.nan,
                'aic': np.nan,
                'interval_score': np.nan,
                'sharpness': np.nan,
                'calibration': np.nan,
                'mean_width': np.nan,
                'coverage_error': np.nan,
                'well_calibrated': False,
                'error_message': str(e)
            }

    def _get_scenario_config(self, scenario: str) -> Dict:
        """Get scenario-specific configuration"""
        configs = {
            'linear_low_het': {
                'curve': lambda x: 0.01 * x,
                'tau2': 0.01,
                'dose_range': (0, 100)
            },
            'quadratic_mod_het': {
                'curve': lambda x: 0.01 * x - 0.0001 * x**2,
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            'log_high_het': {
                'curve': lambda x: 0.3 * np.log(x + 1),
                'tau2': 0.10,
                'dose_range': (0, 100)
            },
            'threshold_mod_het': {
                'curve': lambda x: np.where(x < 50, 0, 0.01 * (x - 50)),
                'tau2': 0.05,
                'dose_range': (0, 100)
            },
            'complex_nonlinear': {
                'curve': lambda x: 0.2 * np.sin(x / 20) + 0.005 * x,
                'tau2': 0.05,
                'dose_range': (0, 100)
            }
        }
        return configs[scenario]

    def create_summary_table(self, results_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create summary table averaging across simulations

        Returns
        -------
        summary : pd.DataFrame
            Mean and SD for each metric by scenario and n_knots
        """
        # Filter successful runs
        results_converged = results_df[results_df['converged']].copy()

        # Group by scenario and n_knots
        grouped = results_converged.groupby(['scenario', 'n_knots'])

        summary = grouped.agg({
            'mse': ['mean', 'std'],
            'bias': ['mean', 'std'],
            'coverage': ['mean', 'std'],
            'aic': ['mean', 'std'],
            'interval_score': ['mean', 'std'],
            'sharpness': ['mean', 'std'],
            'calibration': ['mean', 'std']
        }).round(4)

        # Convergence rate
        conv_rate = results_df.groupby(['scenario', 'n_knots'])['converged'].agg(
            lambda x: 100 * x.sum() / len(x)
        )
        summary[('convergence', 'rate')] = conv_rate

        return summary

    def plot_results(self, results_df: pd.DataFrame, save_dir: str = 'results/knot_sensitivity'):
        """
        Create visualization of knot sensitivity

        Parameters
        ----------
        results_df : pd.DataFrame
            Results from run_analysis()
        save_dir : str
            Directory to save plots
        """
        Path(save_dir).mkdir(parents=True, exist_ok=True)

        results_converged = results_df[results_df['converged']].copy()

        # Set style
        sns.set_style('whitegrid')
        sns.set_palette('colorblind')

        # 1. Coverage by knots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        scenarios = results_converged['scenario'].unique()

        for idx, scenario in enumerate(scenarios):
            if idx >= len(axes):
                break

            ax = axes[idx]
            data = results_converged[results_converged['scenario'] == scenario]

            sns.boxplot(data=data, x='n_knots', y='coverage', ax=ax)
            ax.axhline(95, color='red', linestyle='--', label='Nominal 95%')
            ax.set_title(scenario.replace('_', ' ').title())
            ax.set_xlabel('Number of Knots')
            ax.set_ylabel('Coverage (%)')
            ax.legend()

        plt.tight_layout()
        plt.savefig(f"{save_dir}/coverage_by_knots.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 2. MSE by knots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, scenario in enumerate(scenarios):
            if idx >= len(axes):
                break

            ax = axes[idx]
            data = results_converged[results_converged['scenario'] == scenario]

            sns.boxplot(data=data, x='n_knots', y='mse', ax=ax)
            ax.set_title(scenario.replace('_', ' ').title())
            ax.set_xlabel('Number of Knots')
            ax.set_ylabel('MSE')
            ax.set_yscale('log')

        plt.tight_layout()
        plt.savefig(f"{save_dir}/mse_by_knots.png", dpi=300, bbox_inches='tight')
        plt.close()

        # 3. AIC by knots
        fig, axes = plt.subplots(2, 3, figsize=(15, 10))
        axes = axes.flatten()

        for idx, scenario in enumerate(scenarios):
            if idx >= len(axes):
                break

            ax = axes[idx]
            data = results_converged[results_converged['scenario'] == scenario]

            sns.boxplot(data=data, x='n_knots', y='aic', ax=ax)
            ax.set_title(scenario.replace('_', ' ').title())
            ax.set_xlabel('Number of Knots')
            ax.set_ylabel('AIC')

        plt.tight_layout()
        plt.savefig(f"{save_dir}/aic_by_knots.png", dpi=300, bbox_inches='tight')
        plt.close()

        print(f"Plots saved to {save_dir}/")


def main():
    """Run knot sensitivity analysis"""
    print("="*80)
    print("KNOT SENSITIVITY ANALYSIS")
    print("="*80)
    print()

    analyzer = KnotSensitivityAnalyzer(
        knot_options=[3, 4, 5, 7],
        n_simulations=100,
        random_state=42
    )

    # Run analysis
    results_df = analyzer.run_analysis()

    # Save detailed results
    results_df.to_csv('results/knot_sensitivity_detailed.csv', index=False)
    print("\nDetailed results saved to results/knot_sensitivity_detailed.csv")

    # Create summary table
    summary = analyzer.create_summary_table(results_df)
    summary.to_csv('results/knot_sensitivity_summary.csv')
    print("Summary table saved to results/knot_sensitivity_summary.csv")

    # Print summary
    print("\n" + "="*80)
    print("SUMMARY: Coverage by Knots")
    print("="*80)
    print(summary[('coverage', 'mean')])

    print("\n" + "="*80)
    print("SUMMARY: MSE by Knots")
    print("="*80)
    print(summary[('mse', 'mean')])

    print("\n" + "="*80)
    print("SUMMARY: AIC by Knots (lower is better)")
    print("="*80)
    print(summary[('aic', 'mean')])

    # Create plots
    analyzer.plot_results(results_df)

    print("\n" + "="*80)
    print("KNOT SENSITIVITY ANALYSIS COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()
