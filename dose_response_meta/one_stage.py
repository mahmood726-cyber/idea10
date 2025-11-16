"""
One-Stage Dose-Response Meta-Analysis

Implementation based on:
- Crippa A, Orsini N. Stata J. 2016
- Gasparrini A, et al. Stat Med. 2019
- Discacciati A, et al. Res Synth Methods. 2017

One-stage approach: Simultaneously estimates dose-response curve and between-study
heterogeneity in a single model.
"""

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2, norm
from typing import Optional, Tuple, Callable
import warnings


class OneStageDRMA:
    """
    One-stage dose-response meta-analysis using mixed-effects modeling.

    In one-stage DRMA, all data from all studies are pooled and analyzed
    simultaneously, with random effects accounting for between-study heterogeneity.

    Parameters
    ----------
    method : str
        Dose-response model: 'spline' or 'fp' (default: 'spline')
    heterogeneity : str
        Type of heterogeneity model: 'iso' (isotropic) or 'unstructured'
    Reference_dose : float
        Reference dose level
    """

    def __init__(self,
                 method: str = 'spline',
                 heterogeneity: str = 'iso',
                 reference_dose: float = 0.0):

        self.method = method
        self.heterogeneity = heterogeneity
        self.reference_dose = reference_dose

        self.beta = None  # Fixed effects (dose-response curve parameters)
        self.tau2 = None  # Between-study variance
        self.Psi = None   # Between-study variance-covariance matrix
        self.vcov_beta = None  # Variance-covariance of fixed effects
        self.study_effects = None  # Random effects by study

    def _create_design_matrix(self,
                              doses: np.ndarray,
                              basis_function: Callable) -> np.ndarray:
        """
        Create design matrix using specified basis function

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        basis_function : Callable
            Function to transform doses into basis functions

        Returns
        -------
        X : np.ndarray
            Design matrix
        """
        return basis_function(doses)

    def _reml_objective(self,
                        params: np.ndarray,
                        X: np.ndarray,
                        y: np.ndarray,
                        V_within: np.ndarray,
                        Z: np.ndarray) -> float:
        """
        REML (Restricted Maximum Likelihood) objective function

        Parameters
        ----------
        params : np.ndarray
            Parameters to optimize [beta, tau2_params]
        X : np.ndarray
            Fixed effects design matrix
        y : np.ndarray
            Response vector (log RR)
        V_within : np.ndarray
            Within-study variance-covariance matrix
        Z : np.ndarray
            Random effects design matrix

        Returns
        -------
        neg_reml : float
            Negative REML log-likelihood
        """
        n = len(y)
        p = X.shape[1]

        # Extract parameters
        beta = params[:p]

        # Between-study variance
        if self.heterogeneity == 'iso':
            tau2 = np.exp(params[p])  # Use exp to ensure positivity
            Psi = tau2 * np.eye(Z.shape[1])
        else:
            # Unstructured (would need more complex parameterization)
            tau2 = np.exp(params[p])
            Psi = tau2 * np.eye(Z.shape[1])

        # Total variance: V = V_within + Z * Psi * Z'
        V = V_within + Z @ Psi @ Z.T

        # Add small ridge for numerical stability
        V += 1e-8 * np.eye(n)

        # Residuals
        r = y - X @ beta

        try:
            # Cholesky decomposition for efficient computation
            L = np.linalg.cholesky(V)
            log_det_V = 2 * np.sum(np.log(np.diag(L)))

            # Solve for V^{-1} * r
            V_inv_r = np.linalg.solve(V, r)

            # X' V^{-1} X
            V_inv_X = np.linalg.solve(V, X)
            XtVX = X.T @ V_inv_X
            log_det_XtVX = np.linalg.slogdet(XtVX)[1]

            # REML log-likelihood
            reml = -0.5 * (log_det_V + r.T @ V_inv_r + log_det_XtVX)

            return -reml  # Return negative for minimization

        except np.linalg.LinAlgError:
            # Return large value if matrix is singular
            return 1e10

    def fit(self,
            doses: np.ndarray,
            log_rr: np.ndarray,
            variance: np.ndarray,
            study_id: np.ndarray,
            basis_function: Callable) -> 'OneStageDRMA':
        """
        Fit one-stage dose-response meta-analysis model

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        log_rr : np.ndarray
            Log relative risks
        variance : np.ndarray
            Within-study variances
        study_id : np.ndarray
            Study identifiers
        basis_function : Callable
            Function to create basis functions from doses

        Returns
        -------
        self : OneStageDRMA
        """
        doses = np.asarray(doses)
        log_rr = np.asarray(log_rr)
        variance = np.asarray(variance)
        study_id = np.asarray(study_id)

        # Create design matrix for fixed effects
        X = self._create_design_matrix(doses, basis_function)
        n, p = X.shape

        # Create design matrix for random effects (study indicators)
        unique_studies = np.unique(study_id)
        n_studies = len(unique_studies)

        Z = np.zeros((n, n_studies))
        for i, study in enumerate(unique_studies):
            Z[study_id == study, i] = 1

        # Within-study variance-covariance matrix
        V_within = np.diag(variance)

        # Initial values
        # Start with simple fixed effects estimate
        W = np.diag(1.0 / variance)
        beta_init = np.linalg.solve(X.T @ W @ X + 1e-6 * np.eye(p), X.T @ W @ log_rr)

        # Initial tau2 from residual variance
        residuals = log_rr - X @ beta_init
        tau2_init = max(np.var(residuals) - np.mean(variance), 0.01)

        params_init = np.concatenate([beta_init, [np.log(tau2_init)]])

        # Optimize REML
        result = minimize(
            self._reml_objective,
            params_init,
            args=(X, log_rr, V_within, Z),
            method='BFGS',
            options={'maxiter': 1000}
        )

        if not result.success:
            warnings.warn("REML optimization did not converge")

        # Extract estimates
        self.beta = result.x[:p]

        if self.heterogeneity == 'iso':
            self.tau2 = np.exp(result.x[p])
            self.Psi = self.tau2 * np.eye(n_studies)
        else:
            self.tau2 = np.exp(result.x[p])
            self.Psi = self.tau2 * np.eye(n_studies)

        # Compute variance-covariance matrix of beta
        V = V_within + Z @ self.Psi @ Z.T
        V += 1e-8 * np.eye(n)

        V_inv = np.linalg.inv(V)
        self.vcov_beta = np.linalg.inv(X.T @ V_inv @ X)

        # Store fitted values
        self.fitted_doses = doses
        self.fitted_log_rr = log_rr
        self.fitted_variance = variance
        self.study_id = study_id
        self.basis_function = basis_function

        # Compute study-specific random effects (BLUPs)
        # u = Psi * Z' * V^{-1} * (y - X*beta)
        residuals = log_rr - X @ self.beta
        self.study_effects = self.Psi @ Z.T @ V_inv @ residuals

        return self

    def predict(self,
                doses: np.ndarray,
                return_ci: bool = False,
                alpha: float = 0.05) -> Tuple[np.ndarray, ...]:
        """
        Predict population-average dose-response curve

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for prediction
        return_ci : bool
            Whether to return confidence intervals
        alpha : float
            Significance level for CI

        Returns
        -------
        predictions : np.ndarray
            Predicted log relative risks
        lower_ci : np.ndarray (if return_ci=True)
        upper_ci : np.ndarray (if return_ci=True)
        """
        if self.beta is None:
            raise ValueError("Model must be fitted before prediction")

        doses = np.asarray(doses)
        X = self._create_design_matrix(doses, self.basis_function)

        # Point predictions
        predictions = X @ self.beta

        if not return_ci:
            return predictions

        # Confidence intervals
        z = norm.ppf(1 - alpha/2)

        # Variance of predictions
        pred_var = np.sum((X @ self.vcov_beta) * X, axis=1)
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

    def get_heterogeneity_stats(self) -> dict:
        """
        Compute heterogeneity statistics

        Returns
        -------
        stats : dict
            I², tau², and related statistics
        """
        # Compute Q statistic
        X = self._create_design_matrix(self.fitted_doses, self.basis_function)
        residuals = self.fitted_log_rr - X @ self.beta

        W = np.diag(1.0 / self.fitted_variance)
        Q = residuals.T @ W @ residuals

        # Degrees of freedom
        n_studies = len(np.unique(self.study_id))
        df = len(self.fitted_doses) - X.shape[1]

        # I² statistic
        I2 = max(0, 100 * (Q - df) / Q)

        # H² statistic
        H2 = Q / df

        return {
            'tau2': self.tau2,
            'tau': np.sqrt(self.tau2),
            'I2': I2,
            'H2': H2,
            'Q': Q,
            'Q_df': df,
            'Q_pval': 1 - chi2.cdf(Q, df)
        }

    def get_model_summary(self) -> dict:
        """Return comprehensive model summary"""
        het_stats = self.get_heterogeneity_stats()

        return {
            'method': self.method,
            'n_parameters': len(self.beta),
            'n_studies': len(np.unique(self.study_id)),
            'n_observations': len(self.fitted_doses),
            'coefficients': self.beta,
            'vcov': self.vcov_beta,
            **het_stats
        }
