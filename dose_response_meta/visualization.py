"""
Visualization Tools for Dose-Response Meta-Analysis

Create publication-quality plots for dose-response curves,
heterogeneity assessment, and model comparison.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Optional, List, Tuple
import pandas as pd

# Set publication-quality style
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.3)


class DoseResponsePlotter:
    """
    Create visualizations for dose-response meta-analysis results.

    Parameters
    ----------
    figsize : tuple
        Default figure size (width, height)
    dpi : int
        Resolution for saved figures
    """

    def __init__(self, figsize: Tuple[float, float] = (10, 6), dpi: int = 300):
        self.figsize = figsize
        self.dpi = dpi
        self.colors = sns.color_palette("husl", 8)

    def plot_dose_response_curve(self,
                                 doses: np.ndarray,
                                 predictions: np.ndarray,
                                 lower_ci: Optional[np.ndarray] = None,
                                 upper_ci: Optional[np.ndarray] = None,
                                 observed_doses: Optional[np.ndarray] = None,
                                 observed_rr: Optional[np.ndarray] = None,
                                 observed_se: Optional[np.ndarray] = None,
                                 true_curve: Optional[np.ndarray] = None,
                                 title: str = "Dose-Response Curve",
                                 xlabel: str = "Dose",
                                 ylabel: str = "Relative Risk",
                                 reference_line: bool = True,
                                 log_scale: bool = False,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot dose-response curve with confidence intervals

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for prediction curve
        predictions : np.ndarray
            Predicted relative risks (or log RR)
        lower_ci : Optional[np.ndarray]
            Lower confidence bound
        upper_ci : Optional[np.ndarray]
            Upper confidence bound
        observed_doses : Optional[np.ndarray]
            Observed dose levels from studies
        observed_rr : Optional[np.ndarray]
            Observed relative risks
        observed_se : Optional[np.ndarray]
            Standard errors of observed RRs
        true_curve : Optional[np.ndarray]
            True curve (for simulated data)
        title : str
            Plot title
        xlabel : str
            X-axis label
        ylabel : str
            Y-axis label
        reference_line : bool
            Whether to draw RR=1 reference line
        log_scale : bool
            Whether predictions are on log scale
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plot confidence interval
        if lower_ci is not None and upper_ci is not None:
            if log_scale:
                ax.fill_between(doses, np.exp(lower_ci), np.exp(upper_ci),
                               alpha=0.2, color=self.colors[0], label='95% CI')
            else:
                ax.fill_between(doses, lower_ci, upper_ci,
                               alpha=0.2, color=self.colors[0], label='95% CI')

        # Plot prediction curve
        if log_scale:
            ax.plot(doses, np.exp(predictions), '-', color=self.colors[0],
                   linewidth=2.5, label='Predicted')
        else:
            ax.plot(doses, predictions, '-', color=self.colors[0],
                   linewidth=2.5, label='Predicted')

        # Plot true curve (if available, for simulations)
        if true_curve is not None:
            if log_scale:
                ax.plot(doses, np.exp(true_curve), '--', color='red',
                       linewidth=2, alpha=0.7, label='True curve')
            else:
                ax.plot(doses, true_curve, '--', color='red',
                       linewidth=2, alpha=0.7, label='True curve')

        # Plot observed data points
        if observed_doses is not None and observed_rr is not None:
            if observed_se is not None:
                if log_scale:
                    # Convert log RR to RR for plotting
                    yerr = np.exp(observed_rr) * observed_se
                    ax.errorbar(observed_doses, np.exp(observed_rr), yerr=yerr,
                               fmt='o', color=self.colors[1], markersize=6,
                               alpha=0.6, capsize=4, label='Observed')
                else:
                    ax.errorbar(observed_doses, observed_rr, yerr=observed_se,
                               fmt='o', color=self.colors[1], markersize=6,
                               alpha=0.6, capsize=4, label='Observed')
            else:
                if log_scale:
                    ax.scatter(observed_doses, np.exp(observed_rr),
                             color=self.colors[1], s=60, alpha=0.6, label='Observed')
                else:
                    ax.scatter(observed_doses, observed_rr,
                             color=self.colors[1], s=60, alpha=0.6, label='Observed')

        # Reference line at RR=1
        if reference_line:
            ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5)

        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig

    def plot_study_specific_curves(self,
                                   doses_pred: np.ndarray,
                                   study_data: pd.DataFrame,
                                   study_predictions: dict,
                                   pooled_predictions: np.ndarray,
                                   title: str = "Study-Specific Dose-Response Curves",
                                   save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot individual study curves and pooled estimate

        Parameters
        ----------
        doses_pred : np.ndarray
            Dose levels for prediction
        study_data : pd.DataFrame
            Original study data
        study_predictions : dict
            Dictionary mapping study_id to predicted curves
        pooled_predictions : np.ndarray
            Pooled dose-response curve
        title : str
            Plot title
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)

        # Plot individual study curves (lighter, thinner lines)
        for study_id, preds in study_predictions.items():
            ax.plot(doses_pred, preds, '-', alpha=0.3, linewidth=1,
                   color='gray', label='_nolegend_')

        # Plot observed data points by study
        unique_studies = study_data['study_id'].unique()
        for i, study in enumerate(unique_studies[:5]):  # Limit to first 5 for legend
            study_subset = study_data[study_data['study_id'] == study]
            if i == 0:
                ax.scatter(study_subset['dose'], np.exp(study_subset['log_rr']),
                         alpha=0.5, s=40, label='Study data')
            else:
                ax.scatter(study_subset['dose'], np.exp(study_subset['log_rr']),
                         alpha=0.5, s=40, label='_nolegend_')

        # Plot pooled curve (bold)
        ax.plot(doses_pred, pooled_predictions, '-', color=self.colors[0],
               linewidth=3, label='Pooled estimate', zorder=10)

        ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Dose', fontsize=12, fontweight='bold')
        ax.set_ylabel('Relative Risk', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig

    def plot_method_comparison(self,
                              doses: np.ndarray,
                              method_results: dict,
                              true_curve: Optional[np.ndarray] = None,
                              title: str = "Comparison of Methods",
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Compare multiple methods on the same plot

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        method_results : dict
            Dictionary mapping method names to (predictions, lower_ci, upper_ci)
        true_curve : Optional[np.ndarray]
            True curve (for simulated data)
        title : str
            Plot title
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        fig, ax = plt.subplots(figsize=(12, 7), dpi=self.dpi)

        # Plot true curve first (if available)
        if true_curve is not None:
            ax.plot(doses, np.exp(true_curve), 'k--', linewidth=2.5,
                   label='True curve', zorder=10)

        # Plot each method
        for i, (method_name, (preds, lower, upper)) in enumerate(method_results.items()):
            color = self.colors[i % len(self.colors)]

            # Confidence interval
            ax.fill_between(doses, np.exp(lower), np.exp(upper),
                           alpha=0.15, color=color)

            # Prediction curve
            ax.plot(doses, np.exp(preds), '-', color=color,
                   linewidth=2, label=method_name)

        ax.axhline(y=1, color='gray', linestyle='--', linewidth=1, alpha=0.5)
        ax.set_xlabel('Dose', fontsize=12, fontweight='bold')
        ax.set_ylabel('Relative Risk', fontsize=12, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig

    def plot_heterogeneity_stats(self,
                                 method_stats: dict,
                                 title: str = "Heterogeneity Statistics Across Methods",
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot heterogeneity statistics (I², tau²) across methods

        Parameters
        ----------
        method_stats : dict
            Dictionary mapping method names to statistics dictionaries
        title : str
            Plot title
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=self.dpi)

        methods = list(method_stats.keys())
        I2_values = [method_stats[m].get('I2', 0) for m in methods]
        tau2_values = [method_stats[m].get('tau2', 0) for m in methods]

        # I² plot
        bars1 = ax1.bar(range(len(methods)), I2_values, color=self.colors[:len(methods)])
        ax1.set_xticks(range(len(methods)))
        ax1.set_xticklabels(methods, rotation=45, ha='right')
        ax1.set_ylabel('I² (%)', fontsize=12, fontweight='bold')
        ax1.set_title('Between-Study Heterogeneity (I²)', fontsize=12, fontweight='bold')
        ax1.axhline(y=50, color='orange', linestyle='--', alpha=0.5, label='Moderate (50%)')
        ax1.axhline(y=75, color='red', linestyle='--', alpha=0.5, label='High (75%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3, axis='y')

        # tau² plot
        bars2 = ax2.bar(range(len(methods)), tau2_values, color=self.colors[:len(methods)])
        ax2.set_xticks(range(len(methods)))
        ax2.set_xticklabels(methods, rotation=45, ha='right')
        ax2.set_ylabel('τ²', fontsize=12, fontweight='bold')
        ax2.set_title('Between-Study Variance (τ²)', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')

        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig

    def plot_residuals(self,
                      observed: np.ndarray,
                      fitted: np.ndarray,
                      title: str = "Residual Diagnostics",
                      save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot residual diagnostics

        Parameters
        ----------
        observed : np.ndarray
            Observed values
        fitted : np.ndarray
            Fitted values
        title : str
            Plot title
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        residuals = observed - fitted

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), dpi=self.dpi)

        # Residuals vs fitted
        ax1.scatter(fitted, residuals, alpha=0.6, s=50, color=self.colors[0])
        ax1.axhline(y=0, color='red', linestyle='--', linewidth=2)
        ax1.set_xlabel('Fitted Values', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Residuals', fontsize=12, fontweight='bold')
        ax1.set_title('Residuals vs Fitted', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)

        # Q-Q plot
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=ax2)
        ax2.set_title('Normal Q-Q Plot', fontsize=12, fontweight='bold')
        ax2.grid(True, alpha=0.3)

        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig

    def plot_performance_metrics(self,
                                metrics_df: pd.DataFrame,
                                title: str = "Model Performance Comparison",
                                save_path: Optional[str] = None) -> plt.Figure:
        """
        Plot performance metrics (MSE, bias, coverage) across methods

        Parameters
        ----------
        metrics_df : pd.DataFrame
            DataFrame with columns: method, MSE, bias, coverage, etc.
        title : str
            Plot title
        save_path : Optional[str]
            Path to save figure

        Returns
        -------
        fig : plt.Figure
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10), dpi=self.dpi)

        metrics = ['MSE', 'Bias', 'Coverage', 'CI_Width']
        metric_labels = ['Mean Squared Error', 'Bias', 'Coverage (%)', 'CI Width']

        for idx, (metric, label) in enumerate(zip(metrics, metric_labels)):
            ax = axes[idx // 2, idx % 2]

            if metric in metrics_df.columns:
                bars = ax.bar(range(len(metrics_df)), metrics_df[metric],
                             color=self.colors[:len(metrics_df)])
                ax.set_xticks(range(len(metrics_df)))
                ax.set_xticklabels(metrics_df['Method'], rotation=45, ha='right')
                ax.set_ylabel(label, fontsize=11, fontweight='bold')
                ax.set_title(label, fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')

                # Add reference line for coverage
                if metric == 'Coverage':
                    ax.axhline(y=95, color='red', linestyle='--', alpha=0.5, label='Nominal 95%')
                    ax.legend()

        plt.suptitle(title, fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()

        if save_path:
            fig.savefig(save_path, dpi=self.dpi, bbox_inches='tight')

        return fig
