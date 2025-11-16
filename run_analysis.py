"""
Simplified Comprehensive Analysis using correct API

Runs all scenarios with proper scoring rules and convergence tracking
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.insert(0, '/home/user/idea10')

from dose_response_meta.splines import RestrictedCubicSpline
from dose_response_meta.two_stage import TwoStageDRMA
from dose_response_meta.one_stage import OneStageDRMA
from dose_response_meta.simulation import DoseResponseSimulator
from dose_response_meta.convergence_tracker import ConvergenceTracker
from dose_response_meta.scoring_rules import (
    interval_score,
    decompose_interval_score,
    calibration_metrics
)


def run_comprehensive_analysis(n_simulations=20, output_dir='results'):
    """Run full analysis"""

    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    tracker = ConvergenceTracker()
    all_results = []

    # Define scenarios
    scenarios = {
        '1_linear_low_het': {
            'true_curve': DoseResponseSimulator.create_linear_curve(slope=0.01),
            'between_study_sd': 0.1,
            'dose_dependent_het': False
        },
        '2_quadratic_mod_het': {
            'true_curve': DoseResponseSimulator.create_quadratic_curve(beta1=0.01, beta2=-0.0001),
            'between_study_sd': 0.22,  # sqrt(0.05) for variance
            'dose_dependent_het': False
        },
        '3_log_high_het': {
            'true_curve': DoseResponseSimulator.create_logarithmic_curve(scale=0.3),
            'between_study_sd': 0.316,  # sqrt(0.10)
            'dose_dependent_het': False
        },
        '4_threshold_mod_het': {
            'true_curve': DoseResponseSimulator.create_threshold_curve(threshold=50, slope=0.01),
            'between_study_sd': 0.22,
            'dose_dependent_het': False
        },
        '5_u_shaped': {
            'true_curve': DoseResponseSimulator.create_u_shaped_curve(minimum=50, scale=0.0002),
            'between_study_sd': 0.22,
            'dose_dependent_het': False
        },
        '6_j_shaped': {
            'true_curve': DoseResponseSimulator.create_j_shaped_curve(threshold=20, linear_slope=0.01, quad_coef=0.0002),
            'between_study_sd': 0.22,
            'dose_dependent_het': False
        },
        '7_quadratic_dose_dep_het': {
            'true_curve': DoseResponseSimulator.create_quadratic_curve(beta1=0.01, beta2=-0.0001),
            'between_study_sd': 0.14,  # base SD
            'dose_dependent_het': True,
            'het_dose_slope': 0.015
        },
    }

    print("="*80)
    print("COMPREHENSIVE DOSE-RESPONSE META-ANALYSIS")
    print("="*80)
    print(f"Scenarios: {len(scenarios)}")
    print(f"Simulations per scenario: {n_simulations}")
    print(f"Methods: TwoStage_RCS_DL_HKSJ, TwoStage_RCS_Fixed, OneStage_RCS")
    print("="*80)

    for scenario_name, scenario_config in scenarios.items():
        print(f"\n{'='*80}")
        print(f"SCENARIO: {scenario_name}")
        print(f"{'='*80}")

        for sim_idx in range(n_simulations):
            if (sim_idx + 1) % 5 == 0:
                print(f"  Simulation {sim_idx + 1}/{n_simulations}...")

            # Generate data
            np.random.seed(42 + sim_idx)

            simulator = DoseResponseSimulator(
                n_studies=15,
                n_doses_per_study=4,
                dose_range=(0, 100),
                true_curve=scenario_config['true_curve'],
                between_study_sd=scenario_config['between_study_sd'],
                within_study_sd=0.05,
                dose_dependent_het=scenario_config.get('dose_dependent_het', False),
                het_dose_slope=scenario_config.get('het_dose_slope', 0.001)
            )

            data = simulator.simulate()

            # Extract arrays
            doses = data['dose'].values
            log_rr = data['log_rr'].values
            variance = data['variance'].values
            study_id = data['study_id'].values

            # Prediction grid and true values
            dose_grid = np.linspace(0, 100, 100)
            y_true = scenario_config['true_curve'](dose_grid)

            # Knots for RCS
            knots = np.percentile(doses, [5, 35, 65, 95])

            def rcs_basis(d):
                rcs = RestrictedCubicSpline(n_knots=4, knot_positions=knots)
                return rcs._compute_spline_basis(d, knots)

            # METHOD 1: Two-Stage DL with HKSJ
            method_name = 'TwoStage_RCS_DL_HKSJ'
            tracker.start_fit(method_name, scenario_name, sim_idx)
            try:
                model = TwoStageDRMA(pooling_method='dl')
                model.fit(doses, log_rr, variance, study_id, rcs_basis)

                # Predict
                pred_basis = rcs_basis(dose_grid)
                predictions = pred_basis @ model.pooled_beta
                se = np.sqrt(np.diag(pred_basis @ model.pooled_vcov @ pred_basis.T))

                # HKSJ correction
                if model.heterogeneity_stats and model.heterogeneity_stats.get('Q_df', 0) > 0:
                    Q = model.heterogeneity_stats['Q']
                    Q_df = model.heterogeneity_stats['Q_df']
                    hksj_factor = np.sqrt(Q / Q_df)
                    se_hksj = se * hksj_factor

                    from scipy.stats import t
                    t_crit = t.ppf(0.975, df=Q_df)
                    ci_lower = predictions - t_crit * se_hksj
                    ci_upper = predictions + t_crit * se_hksj
                else:
                    ci_lower = predictions - 1.96 * se
                    ci_upper = predictions + 1.96 * se

                # Metrics
                mse = np.mean((predictions - y_true) ** 2)
                coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100
                _, mean_is = interval_score(y_true, ci_lower, ci_upper)
                decomp = decompose_interval_score(y_true, ci_lower, ci_upper)

                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': True,
                    'mse': mse,
                    'coverage': coverage,
                    'interval_score': mean_is,
                    'sharpness': decomp['sharpness'],
                    'calibration': decomp['calibration'],
                    'tau2': model.heterogeneity_stats.get('tau2', np.nan) if model.heterogeneity_stats else np.nan,
                    'I2': model.heterogeneity_stats.get('I2', np.nan) if model.heterogeneity_stats else np.nan
                })

                tracker.record_success(tau2=model.heterogeneity_stats.get('tau2', np.nan) if model.heterogeneity_stats else np.nan)

            except Exception as e:
                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': False,
                    'mse': np.nan,
                    'coverage': np.nan,
                    'interval_score': np.nan,
                    'sharpness': np.nan,
                    'calibration': np.nan,
                    'tau2': np.nan,
                    'I2': np.nan
                })
                tracker.record_failure(str(e))

            # METHOD 2: Two-Stage Fixed
            method_name = 'TwoStage_RCS_Fixed'
            tracker.start_fit(method_name, scenario_name, sim_idx)
            try:
                model = TwoStageDRMA(pooling_method='fixed')
                model.fit(doses, log_rr, variance, study_id, rcs_basis)

                pred_basis = rcs_basis(dose_grid)
                predictions = pred_basis @ model.pooled_beta
                se = np.sqrt(np.diag(pred_basis @ model.pooled_vcov @ pred_basis.T))
                ci_lower = predictions - 1.96 * se
                ci_upper = predictions + 1.96 * se

                mse = np.mean((predictions - y_true) ** 2)
                coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100
                _, mean_is = interval_score(y_true, ci_lower, ci_upper)
                decomp = decompose_interval_score(y_true, ci_lower, ci_upper)

                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': True,
                    'mse': mse,
                    'coverage': coverage,
                    'interval_score': mean_is,
                    'sharpness': decomp['sharpness'],
                    'calibration': decomp['calibration'],
                    'tau2': 0.0,
                    'I2': 0.0
                })

                tracker.record_success()

            except Exception as e:
                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': False,
                    'mse': np.nan,
                    'coverage': np.nan,
                    'interval_score': np.nan,
                    'sharpness': np.nan,
                    'calibration': np.nan,
                    'tau2': np.nan,
                    'I2': np.nan
                })
                tracker.record_failure(str(e))

            # METHOD 3: One-Stage
            method_name = 'OneStage_RCS'
            tracker.start_fit(method_name, scenario_name, sim_idx)
            try:
                model = OneStageDRMA(method='spline', heterogeneity='iso')
                model.fit(doses, log_rr, variance, study_id, rcs_basis)

                predictions, ci_lower, ci_upper = model.predict(dose_grid, return_ci=True)

                mse = np.mean((predictions - y_true) ** 2)
                coverage = np.mean((y_true >= ci_lower) & (y_true <= ci_upper)) * 100
                _, mean_is = interval_score(y_true, ci_lower, ci_upper)
                decomp = decompose_interval_score(y_true, ci_lower, ci_upper)

                het_stats = model.get_heterogeneity_stats()

                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': True,
                    'mse': mse,
                    'coverage': coverage,
                    'interval_score': mean_is,
                    'sharpness': decomp['sharpness'],
                    'calibration': decomp['calibration'],
                    'tau2': het_stats.get('tau2', np.nan),
                    'I2': het_stats.get('I2', np.nan)
                })

                tracker.record_success(tau2=het_stats.get('tau2', np.nan))

            except Exception as e:
                all_results.append({
                    'scenario': scenario_name,
                    'method': method_name,
                    'sim_idx': sim_idx,
                    'converged': False,
                    'mse': np.nan,
                    'coverage': np.nan,
                    'interval_score': np.nan,
                    'sharpness': np.nan,
                    'calibration': np.nan,
                    'tau2': np.nan,
                    'I2': np.nan
                })
                tracker.record_failure(str(e))

        print(f"  ✓ Completed {n_simulations} simulations")

    # Save results
    df = pd.DataFrame(all_results)
    df.to_csv(output_dir / 'detailed_results.csv', index=False)
    print(f"\n✓ Detailed results: {output_dir / 'detailed_results.csv'}")

    tracker.save_results(output_dir / 'convergence_diagnostics.csv')
    print(f"✓ Convergence diagnostics: {output_dir / 'convergence_diagnostics.csv'}")

    # Summary
    df_conv = df[df['converged']].copy()
    if len(df_conv) > 0:
        summary = df_conv.groupby(['scenario', 'method']).agg({
            'mse': ['mean', 'std'],
            'coverage': ['mean', 'std'],
            'interval_score': ['mean', 'std'],
            'sharpness': ['mean', 'std'],
            'calibration': ['mean', 'std']
        }).round(4)

        summary.to_csv(output_dir / 'summary.csv')
        print(f"✓ Summary table: {output_dir / 'summary.csv'}")

        # Coverage summary
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

        # MSE summary
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

    # Convergence
    print("\n")
    tracker.print_summary()

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE!")
    print("="*80)

    return df


if __name__ == '__main__':
    n_sims = 20 if len(sys.argv) == 1 else int(sys.argv[1])
    print(f"Running with {n_sims} simulations per scenario")
    print(f"Estimated time: {n_sims * 0.5 / 60:.1f} - {n_sims * 1.0 / 60:.1f} minutes\n")

    run_comprehensive_analysis(n_simulations=n_sims, output_dir='results')
