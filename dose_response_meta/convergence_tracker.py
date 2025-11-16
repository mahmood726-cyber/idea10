"""
Convergence Tracking for Dose-Response Meta-Analysis Methods

Instruments all estimation methods to track:
- Convergence success/failure rates
- Computation time
- Final objective values
- Optimization diagnostics

For editorial requirement: convergence diagnostics table
"""

import time
import numpy as np
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ConvergenceRecord:
    """Record for a single model fit attempt"""
    method_name: str
    scenario: str
    iteration: int
    converged: bool
    computation_time: float  # seconds
    n_iterations: Optional[int] = None
    final_objective: Optional[float] = None
    exit_message: Optional[str] = None
    tau2_estimate: Optional[float] = None
    n_parameters: Optional[int] = None
    initial_value_index: Optional[int] = None  # For multi-start methods

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for easy DataFrame creation"""
        return {
            'method': self.method_name,
            'scenario': self.scenario,
            'iteration': self.iteration,
            'converged': self.converged,
            'time_sec': self.computation_time,
            'n_iter': self.n_iterations,
            'objective': self.final_objective,
            'tau2': self.tau2_estimate,
            'n_params': self.n_parameters,
            'init_val_idx': self.initial_value_index,
            'message': self.exit_message
        }


class ConvergenceTracker:
    """
    Tracks convergence diagnostics across all methods and scenarios

    Usage:
        tracker = ConvergenceTracker()

        # During estimation:
        tracker.start_fit(method='TwoStage_RCS_DL', scenario='quadratic_mod_het', iteration=1)
        # ... perform estimation ...
        tracker.record_success(tau2=0.05, n_iter=50, objective=-123.4)
        # OR
        tracker.record_failure(message="Did not converge")

        # Generate summary:
        summary = tracker.get_summary()
        tracker.save_results('convergence_diagnostics.csv')
    """

    def __init__(self):
        self.records: List[ConvergenceRecord] = []
        self._current_fit: Optional[Dict[str, Any]] = None
        self._start_time: Optional[float] = None

    def start_fit(self, method: str, scenario: str, iteration: int):
        """Start tracking a new model fit"""
        self._current_fit = {
            'method': method,
            'scenario': scenario,
            'iteration': iteration
        }
        self._start_time = time.time()

    def record_success(self,
                      tau2: Optional[float] = None,
                      n_iter: Optional[int] = None,
                      objective: Optional[float] = None,
                      n_params: Optional[int] = None,
                      init_val_idx: Optional[int] = None):
        """Record successful convergence"""
        if self._current_fit is None:
            raise ValueError("Must call start_fit() before record_success()")

        elapsed = time.time() - self._start_time

        record = ConvergenceRecord(
            method_name=self._current_fit['method'],
            scenario=self._current_fit['scenario'],
            iteration=self._current_fit['iteration'],
            converged=True,
            computation_time=elapsed,
            n_iterations=n_iter,
            final_objective=objective,
            tau2_estimate=tau2,
            n_parameters=n_params,
            initial_value_index=init_val_idx,
            exit_message="Success"
        )

        self.records.append(record)
        self._current_fit = None
        self._start_time = None

    def record_failure(self, message: str = "Failed to converge"):
        """Record convergence failure"""
        if self._current_fit is None:
            raise ValueError("Must call start_fit() before record_failure()")

        elapsed = time.time() - self._start_time

        record = ConvergenceRecord(
            method_name=self._current_fit['method'],
            scenario=self._current_fit['scenario'],
            iteration=self._current_fit['iteration'],
            converged=False,
            computation_time=elapsed,
            exit_message=message
        )

        self.records.append(record)
        self._current_fit = None
        self._start_time = None

    def get_summary(self) -> Dict[str, Any]:
        """
        Generate summary statistics by method and scenario

        Returns
        -------
        summary : dict
            Contains:
            - convergence_rate: % successful by method
            - mean_time: Average computation time by method
            - mean_iterations: Average iterations by method
            - failed_cases: List of all failures
            - by_scenario: Breakdown by scenario
        """
        if not self.records:
            return {}

        # Group by method
        by_method = defaultdict(list)
        for rec in self.records:
            by_method[rec.method_name].append(rec)

        # Convergence rates
        convergence_rates = {}
        mean_times = {}
        mean_iterations = {}

        for method, recs in by_method.items():
            n_total = len(recs)
            n_converged = sum(1 for r in recs if r.converged)
            convergence_rates[method] = 100.0 * n_converged / n_total if n_total > 0 else 0.0

            # Mean time (all attempts)
            mean_times[method] = np.mean([r.computation_time for r in recs])

            # Mean iterations (successful only)
            iters = [r.n_iterations for r in recs if r.converged and r.n_iterations is not None]
            mean_iterations[method] = np.mean(iters) if iters else None

        # Failed cases
        failed_cases = []
        for rec in self.records:
            if not rec.converged:
                failed_cases.append({
                    'method': rec.method_name,
                    'scenario': rec.scenario,
                    'iteration': rec.iteration,
                    'message': rec.exit_message
                })

        # By scenario
        by_scenario = defaultdict(lambda: defaultdict(list))
        for rec in self.records:
            by_scenario[rec.scenario][rec.method_name].append(rec)

        scenario_summary = {}
        for scenario, methods in by_scenario.items():
            scenario_summary[scenario] = {}
            for method, recs in methods.items():
                n_total = len(recs)
                n_converged = sum(1 for r in recs if r.converged)
                scenario_summary[scenario][method] = {
                    'convergence_rate': 100.0 * n_converged / n_total,
                    'mean_time': np.mean([r.computation_time for r in recs]),
                    'n_attempts': n_total
                }

        return {
            'convergence_rate': convergence_rates,
            'mean_time_sec': mean_times,
            'mean_iterations': mean_iterations,
            'n_failures': len(failed_cases),
            'failed_cases': failed_cases,
            'by_scenario': scenario_summary,
            'total_records': len(self.records)
        }

    def save_results(self, filepath: str):
        """Save detailed results to CSV"""
        import pandas as pd

        df = pd.DataFrame([rec.to_dict() for rec in self.records])
        df.to_csv(filepath, index=False)
        print(f"Saved {len(self.records)} convergence records to {filepath}")

    def print_summary(self):
        """Print human-readable summary"""
        summary = self.get_summary()

        if not summary:
            print("No convergence records yet")
            return

        print("\n" + "="*80)
        print("CONVERGENCE DIAGNOSTICS SUMMARY")
        print("="*80)

        print(f"\nTotal model fits: {summary['total_records']}")
        print(f"Total failures: {summary['n_failures']}")

        print("\n" + "-"*80)
        print("CONVERGENCE RATE BY METHOD")
        print("-"*80)
        print(f"{'Method':<25} {'Conv. Rate':>12} {'Mean Time':>12} {'Mean Iter':>12}")
        print("-"*80)

        for method in sorted(summary['convergence_rate'].keys()):
            rate = summary['convergence_rate'][method]
            time_sec = summary['mean_time_sec'][method]
            iters = summary['mean_iterations'][method]
            iter_str = f"{iters:.1f}" if iters is not None else "N/A"
            print(f"{method:<25} {rate:>11.1f}% {time_sec:>11.3f}s {iter_str:>12}")

        if summary['failed_cases']:
            print("\n" + "-"*80)
            print("FAILED CASES")
            print("-"*80)
            for fail in summary['failed_cases'][:10]:  # Show first 10
                print(f"  {fail['method']:<25} {fail['scenario']:<20} iter={fail['iteration']}")
                print(f"    → {fail['message']}")
            if len(summary['failed_cases']) > 10:
                print(f"  ... and {len(summary['failed_cases']) - 10} more")

        print("\n" + "="*80)


def create_convergence_table(tracker: ConvergenceTracker, output_file: Optional[str] = None) -> str:
    """
    Create publication-quality convergence table

    Parameters
    ----------
    tracker : ConvergenceTracker
        Tracker with recorded results
    output_file : str, optional
        If provided, save table to this file

    Returns
    -------
    table : str
        Formatted table for manuscript
    """
    summary = tracker.get_summary()

    if not summary:
        return "No results to tabulate"

    # Create table
    lines = []
    lines.append("Table: Convergence Diagnostics by Method")
    lines.append("")
    lines.append("| Method | Convergence Rate | Mean Time (s) | Mean Iterations |")
    lines.append("|--------|------------------|---------------|-----------------|")

    for method in sorted(summary['convergence_rate'].keys()):
        rate = summary['convergence_rate'][method]
        time_sec = summary['mean_time_sec'][method]
        iters = summary['mean_iterations'][method]

        iter_str = f"{iters:.1f}" if iters is not None else "—"

        lines.append(f"| {method:<20} | {rate:>6.1f}% | {time_sec:>6.3f} | {iter_str:>15} |")

    lines.append("")
    lines.append(f"Total model fits: {summary['total_records']}")
    lines.append(f"Total failures: {summary['n_failures']} ({100*summary['n_failures']/summary['total_records']:.1f}%)")

    table = "\n".join(lines)

    if output_file:
        with open(output_file, 'w') as f:
            f.write(table)
        print(f"Table saved to {output_file}")

    return table
