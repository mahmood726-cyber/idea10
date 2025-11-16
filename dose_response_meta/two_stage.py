"""
Two-Stage Dose-Response Meta-Analysis

Implementation based on:
- Orsini N, et al. Am J Epidemiol. 2012
- Berlin JA, et al. Stat Med. 1993
- DerSimonian R, Laird N. Control Clin Trials. 1986

Two-stage approach:
1. Stage 1: Estimate dose-response curves within each study
2. Stage 2: Pool study-specific estimates using random-effects meta-analysis
"""

import numpy as np
from scipy.stats import chi2, norm
from typing import Optional, Tuple, List, Callable
import warnings


class TwoStageDRMA:
    """
    Two-stage dose-response meta-analysis.

    Stage 1: Fit dose-response model within each study
    Stage 2: Pool estimates across studies using random-effects meta-analysis

    Parameters
    ----------
    pooling_method : str
        Method for stage 2 pooling: 'dl' (DerSimonian-Laird), 'reml', or 'fixed'
    reference_dose : float
        Reference dose level
    """

    def __init__(self,
                 pooling_method: str = 'dl',
                 reference_dose: float = 0.0):

        self.pooling_method = pooling_method
        self.reference_dose = reference_dose

        self.study_estimates = []
        self.pooled_beta = None
        self.pooled_vcov = None
        self.tau2 = None
        self.heterogeneity_stats = None

    def _fit_study(self,
                   doses: np.ndarray,
                   log_rr: np.ndarray,
                   variance: np.ndarray,
                   basis_function: Callable) -> dict:
        """
        Fit dose-response model for a single study (Stage 1)

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for this study
        log_rr : np.ndarray
            Log relative risks for this study
        variance : np.ndarray
            Variances for this study
        basis_function : Callable
            Function to create basis from doses

        Returns
        -------
        study_result : dict
            Study-specific estimates and variance-covariance matrix
        """
        # Create design matrix
        X = basis_function(doses)

        # Weighted least squares
        weights = 1.0 / variance
        W = np.diag(weights)

        # Solve: (X'WX)^-1 X'Wy
        XtWX = X.T @ W @ X
        XtWy = X.T @ W @ log_rr

        # Add small ridge for stability
        ridge = 1e-6 * np.eye(XtWX.shape[0])

        try:
            beta = np.linalg.solve(XtWX + ridge, XtWy)
            vcov = np.linalg.inv(XtWX + ridge)

            return {
                'beta': beta,
                'vcov': vcov,
                'n_obs': len(doses),
                'converged': True
            }

        except np.linalg.LinAlgError:
            warnings.warn("Failed to fit study - singular matrix")
            return {
                'beta': None,
                'vcov': None,
                'n_obs': len(doses),
                'converged': False
            }

    def _pool_estimates_dl(self, betas: np.ndarray, vcovs: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Pool estimates using DerSimonian-Laird random-effects meta-analysis

        Parameters
        ----------
        betas : np.ndarray
            Study-specific coefficient estimates (n_studies x n_params)
        vcovs : List[np.ndarray]
            Study-specific variance-covariance matrices

        Returns
        -------
        pooled_beta : np.ndarray
            Pooled coefficients
        pooled_vcov : np.ndarray
            Variance-covariance matrix of pooled estimates
        tau2 : float
            Between-study variance
        """
        n_studies, n_params = betas.shape

        # For multivariate case, we'll use a simplified approach
        # Pool each parameter separately using univariate DL method

        pooled_beta = np.zeros(n_params)
        pooled_vcov = np.zeros((n_params, n_params))
        tau2_vec = np.zeros(n_params)

        for j in range(n_params):
            # Extract estimates and variances for parameter j
            theta = betas[:, j]
            sigma2 = np.array([vcov[j, j] for vcov in vcovs])

            # Inverse-variance weights
            w = 1.0 / sigma2

            # Q statistic
            theta_fixed = np.sum(w * theta) / np.sum(w)
            Q = np.sum(w * (theta - theta_fixed) ** 2)

            # DerSimonian-Laird estimate of tau²
            C = np.sum(w) - np.sum(w**2) / np.sum(w)
            tau2 = max(0, (Q - (n_studies - 1)) / C)

            # Random-effects weights
            w_re = 1.0 / (sigma2 + tau2)

            # Pooled estimate
            pooled_beta[j] = np.sum(w_re * theta) / np.sum(w_re)
            pooled_vcov[j, j] = 1.0 / np.sum(w_re)
            tau2_vec[j] = tau2

        # Use average tau² (simplified approach)
        tau2 = np.mean(tau2_vec)

        return pooled_beta, pooled_vcov, tau2

    def _pool_estimates_fixed(self, betas: np.ndarray, vcovs: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Pool estimates using fixed-effects meta-analysis

        Parameters
        ----------
        betas : np.ndarray
            Study-specific estimates
        vcovs : List[np.ndarray]
            Study-specific variance-covariance matrices

        Returns
        -------
        pooled_beta : np.ndarray
        pooled_vcov : np.ndarray
        """
        n_studies, n_params = betas.shape

        pooled_beta = np.zeros(n_params)
        pooled_vcov = np.zeros((n_params, n_params))

        for j in range(n_params):
            theta = betas[:, j]
            sigma2 = np.array([vcov[j, j] for vcov in vcovs])

            # Inverse-variance weights
            w = 1.0 / sigma2

            # Pooled estimate
            pooled_beta[j] = np.sum(w * theta) / np.sum(w)
            pooled_vcov[j, j] = 1.0 / np.sum(w)

        return pooled_beta, pooled_vcov

    def fit(self,
            doses: np.ndarray,
            log_rr: np.ndarray,
            variance: np.ndarray,
            study_id: np.ndarray,
            basis_function: Callable) -> 'TwoStageDRMA':
        """
        Fit two-stage dose-response meta-analysis

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        log_rr : np.ndarray
            Log relative risks
        variance : np.ndarray
            Variances
        study_id : np.ndarray
            Study identifiers
        basis_function : Callable
            Function to create basis functions

        Returns
        -------
        self : TwoStageDRMA
        """
        doses = np.asarray(doses)
        log_rr = np.asarray(log_rr)
        variance = np.asarray(variance)
        study_id = np.asarray(study_id)

        # Stage 1: Fit model within each study
        unique_studies = np.unique(study_id)
        self.study_estimates = []

        for study in unique_studies:
            mask = study_id == study
            study_result = self._fit_study(
                doses[mask],
                log_rr[mask],
                variance[mask],
                basis_function
            )
            study_result['study_id'] = study
            self.study_estimates.append(study_result)

        # Filter out non-converged studies
        converged_studies = [s for s in self.study_estimates if s['converged']]

        if len(converged_studies) < 2:
            raise ValueError("Too few studies converged to pool estimates")

        # Extract estimates
        betas = np.array([s['beta'] for s in converged_studies])
        vcovs = [s['vcov'] for s in converged_studies]

        # Stage 2: Pool estimates
        if self.pooling_method == 'dl':
            self.pooled_beta, self.pooled_vcov, self.tau2 = self._pool_estimates_dl(betas, vcovs)
        elif self.pooling_method == 'fixed':
            self.pooled_beta, self.pooled_vcov = self._pool_estimates_fixed(betas, vcovs)
            self.tau2 = 0.0
        else:
            raise ValueError(f"Unknown pooling method: {self.pooling_method}")

        # Store for predictions
        self.basis_function = basis_function
        self.fitted_doses = doses
        self.fitted_log_rr = log_rr
        self.fitted_variance = variance
        self.study_id = study_id

        # Compute heterogeneity statistics
        self._compute_heterogeneity_stats(betas, vcovs)

        return self

    def _compute_heterogeneity_stats(self, betas: np.ndarray, vcovs: List[np.ndarray]):
        """Compute heterogeneity statistics (Q, I², etc.)"""
        n_studies, n_params = betas.shape

        # Compute Q statistic (simplified: use first parameter)
        theta = betas[:, 0]
        sigma2 = np.array([vcov[0, 0] for vcov in vcovs])

        w = 1.0 / sigma2
        theta_pooled = self.pooled_beta[0]

        Q = np.sum(w * (theta - theta_pooled) ** 2)
        df = n_studies - 1

        # I² statistic
        I2 = max(0, 100 * (Q - df) / Q)

        # H² statistic
        H2 = Q / df

        self.heterogeneity_stats = {
            'Q': Q,
            'Q_df': df,
            'Q_pval': 1 - chi2.cdf(Q, df),
            'I2': I2,
            'H2': H2,
            'tau2': self.tau2,
            'tau': np.sqrt(self.tau2) if self.tau2 > 0 else 0.0
        }

    def predict(self,
                doses: np.ndarray,
                return_ci: bool = False,
                alpha: float = 0.05) -> Tuple[np.ndarray, ...]:
        """
        Predict pooled dose-response curve

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for prediction
        return_ci : bool
            Whether to return confidence intervals
        alpha : float
            Significance level

        Returns
        -------
        predictions : np.ndarray
        lower_ci : np.ndarray (if return_ci=True)
        upper_ci : np.ndarray (if return_ci=True)
        """
        if self.pooled_beta is None:
            raise ValueError("Model must be fitted before prediction")

        doses = np.asarray(doses)
        X = self.basis_function(doses)

        # Point predictions
        predictions = X @ self.pooled_beta

        if not return_ci:
            return predictions

        # Confidence intervals
        z = norm.ppf(1 - alpha/2)

        # Variance of predictions
        pred_var = np.sum((X @ self.pooled_vcov) * X, axis=1)
        pred_se = np.sqrt(pred_var)

        lower_ci = predictions - z * pred_se
        upper_ci = predictions + z * pred_se

        return predictions, lower_ci, upper_ci

    def predict_rr(self,
                   doses: np.ndarray,
                   return_ci: bool = False,
                   alpha: float = 0.05) -> Tuple[np.ndarray, ...]:
        """Predict relative risk (exponential scale)"""
        if return_ci:
            log_rr, log_lower, log_upper = self.predict(doses, return_ci=True, alpha=alpha)
            return np.exp(log_rr), np.exp(log_lower), np.exp(log_upper)
        else:
            log_rr = self.predict(doses, return_ci=False)
            return np.exp(log_rr)

    def get_model_summary(self) -> dict:
        """Return comprehensive model summary"""
        return {
            'method': 'two_stage',
            'pooling_method': self.pooling_method,
            'n_studies': len(self.study_estimates),
            'n_converged': sum(s['converged'] for s in self.study_estimates),
            'n_parameters': len(self.pooled_beta),
            'coefficients': self.pooled_beta,
            'vcov': self.pooled_vcov,
            **self.heterogeneity_stats
        }

    def get_study_estimates(self) -> List[dict]:
        """Return study-specific estimates"""
        return self.study_estimates
