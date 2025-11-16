"""
Restricted Cubic Splines for Dose-Response Meta-Analysis

Implementation based on:
- Harrell FE Jr. Regression Modeling Strategies (2001)
- Desquilbet L, Mariotti F. Stat Med. 2010
- Orsini N, et al. Am J Epidemiol. 2012
"""

import numpy as np
from scipy import interpolate
from typing import Optional, Tuple, List


class RestrictedCubicSpline:
    """
    Restricted Cubic Spline (Natural Cubic Spline) implementation for dose-response modeling.

    Restricted cubic splines are piecewise cubic polynomials that are linear beyond
    the boundary knots, providing smooth dose-response curves without edge effects.

    Parameters
    ----------
    n_knots : int
        Number of knots (typically 3, 4, or 5)
    knot_positions : Optional[np.ndarray]
        Custom knot positions. If None, uses Harrell's recommended percentiles
    reference_dose : float
        Reference dose (often 0 or minimum dose)
    """

    def __init__(self, n_knots: int = 4, knot_positions: Optional[np.ndarray] = None,
                 reference_dose: float = 0.0):
        self.n_knots = n_knots
        self.knot_positions = knot_positions
        self.reference_dose = reference_dose
        self.knots = None
        self.spline_basis = None

        # Harrell's recommended percentiles for knot placement
        self.recommended_percentiles = {
            3: [10, 50, 90],
            4: [5, 35, 65, 95],
            5: [5, 27.5, 50, 72.5, 95],
            6: [5, 23, 41, 59, 77, 95],
            7: [2.5, 18.33, 34.17, 50, 65.83, 81.67, 97.5]
        }

    def _get_default_knots(self, doses: np.ndarray) -> np.ndarray:
        """Calculate knot positions using Harrell's recommended percentiles"""
        if self.n_knots not in self.recommended_percentiles:
            raise ValueError(f"Default knots only available for 3-7 knots, got {self.n_knots}")

        percentiles = self.recommended_percentiles[self.n_knots]
        return np.percentile(doses, percentiles)

    def _compute_spline_basis(self, dose: np.ndarray, knots: np.ndarray) -> np.ndarray:
        """
        Compute restricted cubic spline basis functions

        For K knots, generates K-2 basis functions (plus intercept and linear term)
        using the formulation from Harrell (2001)
        """
        dose = np.atleast_1d(dose)
        n = len(dose)
        k = len(knots)

        # Initialize basis matrix: intercept + linear + (k-2) spline terms
        # For k knots, we have k-1 total basis functions
        basis = np.ones((n, k - 1))

        # Linear term
        basis[:, 1] = dose

        # Spline terms (restricted cubic spline transformation)
        # For k knots, we create k-3 spline terms (since we already have intercept and linear)
        # This gives us total k-1 columns: 1 (intercept) + 1 (linear) + (k-3) spline = k-1
        n_spline_terms = k - 3

        if n_spline_terms > 0:
            for j in range(n_spline_terms):
                # Formula from Harrell (2001), Chapter 2
                lambda_j = (knots[-1] - knots[j]) / (knots[-1] - knots[0])

                term1 = np.maximum(dose - knots[j], 0) ** 3
                term2 = lambda_j * np.maximum(dose - knots[-2], 0) ** 3
                term3 = (1 - lambda_j) * np.maximum(dose - knots[-1], 0) ** 3

                basis[:, j + 2] = term1 - term2 - term3

        return basis

    def fit(self, doses: np.ndarray, log_rr: np.ndarray,
            variance: np.ndarray, study_id: Optional[np.ndarray] = None) -> 'RestrictedCubicSpline':
        """
        Fit restricted cubic spline to dose-response data

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        log_rr : np.ndarray
            Log relative risks (or log odds ratios)
        variance : np.ndarray
            Variances of log_rr
        study_id : Optional[np.ndarray]
            Study identifiers for meta-analysis

        Returns
        -------
        self : RestrictedCubicSpline
        """
        doses = np.asarray(doses)
        log_rr = np.asarray(log_rr)
        variance = np.asarray(variance)

        # Determine knot positions
        if self.knot_positions is not None:
            self.knots = np.asarray(self.knot_positions)
        else:
            self.knots = self._get_default_knots(doses)

        # Compute spline basis
        X = self._compute_spline_basis(doses, self.knots)

        # Weighted least squares (inverse variance weighting)
        weights = 1.0 / variance
        W = np.diag(weights)

        # Solve: (X'WX)^-1 X'Wy
        XtWX = X.T @ W @ X
        XtWy = X.T @ W @ log_rr

        # Add small ridge term for numerical stability
        ridge = 1e-6 * np.eye(XtWX.shape[0])
        self.coefficients = np.linalg.solve(XtWX + ridge, XtWy)

        # Store fitted values
        self.fitted_doses = doses
        self.fitted_log_rr = log_rr
        self.fitted_variance = variance

        # Compute variance-covariance matrix of coefficients
        self.vcov = np.linalg.inv(XtWX + ridge)

        return self

    def predict(self, doses: np.ndarray,
                return_ci: bool = False,
                alpha: float = 0.05) -> Tuple[np.ndarray, ...]:
        """
        Predict log relative risk at specified doses

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for prediction
        return_ci : bool
            Whether to return confidence intervals
        alpha : float
            Significance level for CI (default: 0.05 for 95% CI)

        Returns
        -------
        predictions : np.ndarray
            Predicted log relative risks
        lower_ci : np.ndarray (if return_ci=True)
            Lower confidence bound
        upper_ci : np.ndarray (if return_ci=True)
            Upper confidence bound
        """
        if self.coefficients is None:
            raise ValueError("Model must be fitted before prediction")

        doses = np.asarray(doses)
        X = self._compute_spline_basis(doses, self.knots)

        # Point predictions
        predictions = X @ self.coefficients

        if not return_ci:
            return predictions

        # Confidence intervals
        from scipy.stats import norm
        z = norm.ppf(1 - alpha/2)

        # Variance of predictions: Var(X*beta) = X * Vcov * X'
        pred_var = np.sum((X @ self.vcov) * X, axis=1)
        pred_se = np.sqrt(pred_var)

        lower_ci = predictions - z * pred_se
        upper_ci = predictions + z * pred_se

        return predictions, lower_ci, upper_ci

    def predict_rr(self, doses: np.ndarray,
                   return_ci: bool = False,
                   alpha: float = 0.05) -> Tuple[np.ndarray, ...]:
        """
        Predict relative risk (exponential scale) at specified doses

        Returns RR instead of log(RR)
        """
        if return_ci:
            log_rr, log_lower, log_upper = self.predict(doses, return_ci=True, alpha=alpha)
            return np.exp(log_rr), np.exp(log_lower), np.exp(log_upper)
        else:
            log_rr = self.predict(doses, return_ci=False)
            return np.exp(log_rr)

    def test_non_linearity(self) -> dict:
        """
        Test for non-linearity using likelihood ratio test

        Compares the spline model to a linear model

        Returns
        -------
        results : dict
            Dictionary containing chi-square statistic, df, and p-value
        """
        from scipy.stats import chi2

        # Fit linear model
        X_linear = np.column_stack([np.ones_like(self.fitted_doses), self.fitted_doses])
        weights = 1.0 / self.fitted_variance
        W = np.diag(weights)

        XtWX_linear = X_linear.T @ W @ X_linear
        XtWy_linear = X_linear.T @ W @ self.fitted_log_rr
        beta_linear = np.linalg.solve(XtWX_linear, XtWy_linear)

        # Residual sum of squares
        rss_spline = np.sum(weights * (self.fitted_log_rr -
                                       self._compute_spline_basis(self.fitted_doses, self.knots) @ self.coefficients) ** 2)
        rss_linear = np.sum(weights * (self.fitted_log_rr - X_linear @ beta_linear) ** 2)

        # Likelihood ratio test
        df = len(self.coefficients) - 2  # Difference in parameters (spline terms)
        chi_sq = rss_linear - rss_spline
        p_value = 1 - chi2.cdf(chi_sq, df)

        return {
            'chi_square': chi_sq,
            'df': df,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    def get_knot_info(self) -> dict:
        """Return information about knot placement"""
        return {
            'n_knots': self.n_knots,
            'knot_positions': self.knots,
            'n_parameters': len(self.coefficients) if self.coefficients is not None else None
        }
