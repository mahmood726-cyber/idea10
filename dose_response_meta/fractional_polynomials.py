"""
Fractional Polynomial Models for Dose-Response Meta-Analysis

Implementation based on:
- Royston P, Altman DG. Stat Med. 1994
- Royston P, Sauerbrei W. Multivariable Model-building (2008)
- Bagnardi V, et al. Int J Epidemiol. 2017
"""

import numpy as np
from scipy.stats import chi2
from itertools import combinations_with_replacement
from typing import Optional, Tuple, List


class FractionalPolynomial:
    """
    Fractional Polynomial (FP) models for flexible dose-response curves.

    Fractional polynomials extend regular polynomials by allowing non-integer powers
    (e.g., -2, -1, -0.5, 0, 0.5, 1, 2, 3) for more flexible curve shapes.

    Parameters
    ----------
    powers : List[float]
        Powers to use in the model (e.g., [-2, -1, -0.5, 0.5, 1, 2, 3])
    degree : int
        Degree of fractional polynomial (1 or 2, default: 2)
    reference_dose : float
        Reference dose (often 0 or minimum dose)
    shift : float
        Shift parameter to handle zero doses (default: 0.1)
    scale : float
        Scaling factor for doses (default: 1.0)
    """

    # Standard FP power set from Royston & Altman
    STANDARD_POWERS = [-2, -1, -0.5, 0, 0.5, 1, 2, 3]

    def __init__(self,
                 powers: Optional[List[float]] = None,
                 degree: int = 2,
                 reference_dose: float = 0.0,
                 shift: float = 0.1,
                 scale: float = 1.0):

        if powers is None:
            powers = self.STANDARD_POWERS

        self.candidate_powers = sorted(powers)
        self.degree = degree
        self.reference_dose = reference_dose
        self.shift = shift
        self.scale = scale

        self.best_powers = None
        self.coefficients = None
        self.vcov = None
        self.deviance = None
        self.all_models = []

    def _transform_dose(self, dose: np.ndarray, power: float) -> np.ndarray:
        """
        Transform dose using fractional polynomial transformation

        For power p:
        - p != 0: (dose/scale)^p
        - p == 0: log(dose/scale)

        Handles zero doses by adding shift parameter
        """
        dose = np.asarray(dose)

        # Shift doses to avoid log(0) and ensure positivity
        dose_shifted = dose + self.shift

        # Scale
        dose_scaled = dose_shifted / self.scale

        # Transform
        if power == 0:
            return np.log(dose_scaled)
        else:
            return dose_scaled ** power

    def _create_fp_basis(self, doses: np.ndarray, powers: Tuple[float, ...]) -> np.ndarray:
        """
        Create design matrix for fractional polynomial model

        For FP1 (degree 1): X = [1, x^p1]
        For FP2 (degree 2):
            - If p1 != p2: X = [1, x^p1, x^p2]
            - If p1 == p2: X = [1, x^p1, x^p1 * log(x)]
        """
        doses = np.asarray(doses)
        n = len(doses)

        if len(powers) == 1:
            # FP1 model
            basis = np.ones((n, 2))
            basis[:, 1] = self._transform_dose(doses, powers[0])

        elif len(powers) == 2:
            # FP2 model
            basis = np.ones((n, 3))
            basis[:, 1] = self._transform_dose(doses, powers[0])

            if powers[0] == powers[1]:
                # Repeated power: use x^p * log(x)
                x_p = self._transform_dose(doses, powers[0])
                x_0 = self._transform_dose(doses, 0)  # log transform
                basis[:, 2] = x_p * x_0
            else:
                # Different powers
                basis[:, 2] = self._transform_dose(doses, powers[1])

        else:
            raise ValueError(f"Degree must be 1 or 2, got {len(powers)}")

        return basis

    def _fit_single_model(self,
                          doses: np.ndarray,
                          log_rr: np.ndarray,
                          variance: np.ndarray,
                          powers: Tuple[float, ...]) -> dict:
        """
        Fit a single fractional polynomial model with given powers

        Returns
        -------
        model_info : dict
            Dictionary with coefficients, deviance, AIC, etc.
        """
        # Create design matrix
        X = self._create_fp_basis(doses, powers)

        # Weighted least squares
        weights = 1.0 / variance
        W = np.diag(weights)

        # Solve: (X'WX)^-1 X'Wy
        XtWX = X.T @ W @ X
        XtWy = X.T @ W @ log_rr

        # Add small ridge for stability
        ridge = 1e-6 * np.eye(XtWX.shape[0])
        coef = np.linalg.solve(XtWX + ridge, XtWy)

        # Compute deviance (weighted residual sum of squares)
        fitted = X @ coef
        residuals = log_rr - fitted
        deviance = np.sum(weights * residuals ** 2)

        # Compute AIC: AIC = n*log(deviance/n) + 2*k
        n = len(doses)
        k = len(coef)
        aic = n * np.log(deviance / n) + 2 * k

        # Variance-covariance matrix
        vcov = np.linalg.inv(XtWX + ridge)

        return {
            'powers': powers,
            'coefficients': coef,
            'vcov': vcov,
            'deviance': deviance,
            'aic': aic,
            'n_params': k
        }

    def fit(self,
            doses: np.ndarray,
            log_rr: np.ndarray,
            variance: np.ndarray,
            method: str = 'aic') -> 'FractionalPolynomial':
        """
        Fit fractional polynomial model by searching over candidate powers

        Parameters
        ----------
        doses : np.ndarray
            Dose levels
        log_rr : np.ndarray
            Log relative risks
        variance : np.ndarray
            Variances of log_rr
        method : str
            Model selection method: 'aic' or 'deviance' (default: 'aic')

        Returns
        -------
        self : FractionalPolynomial
        """
        doses = np.asarray(doses)
        log_rr = np.asarray(log_rr)
        variance = np.asarray(variance)

        self.fitted_doses = doses
        self.fitted_log_rr = log_rr
        self.fitted_variance = variance

        # Generate all candidate power combinations
        if self.degree == 1:
            candidates = [(p,) for p in self.candidate_powers]
        elif self.degree == 2:
            # Allow repeated powers for FP2
            candidates = list(combinations_with_replacement(self.candidate_powers, 2))
        else:
            raise ValueError("Only degree 1 and 2 are supported")

        # Fit all candidate models
        self.all_models = []
        for powers in candidates:
            model_info = self._fit_single_model(doses, log_rr, variance, powers)
            self.all_models.append(model_info)

        # Select best model
        if method == 'aic':
            best_idx = np.argmin([m['aic'] for m in self.all_models])
        elif method == 'deviance':
            best_idx = np.argmin([m['deviance'] for m in self.all_models])
        else:
            raise ValueError(f"Unknown method: {method}")

        best_model = self.all_models[best_idx]
        self.best_powers = best_model['powers']
        self.coefficients = best_model['coefficients']
        self.vcov = best_model['vcov']
        self.deviance = best_model['deviance']

        return self

    def predict(self,
                doses: np.ndarray,
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
            Significance level for CI

        Returns
        -------
        predictions : np.ndarray
            Predicted log relative risks
        lower_ci : np.ndarray (if return_ci=True)
        upper_ci : np.ndarray (if return_ci=True)
        """
        if self.coefficients is None:
            raise ValueError("Model must be fitted before prediction")

        doses = np.asarray(doses)
        X = self._create_fp_basis(doses, self.best_powers)

        # Point predictions
        predictions = X @ self.coefficients

        if not return_ci:
            return predictions

        # Confidence intervals
        from scipy.stats import norm
        z = norm.ppf(1 - alpha/2)

        # Variance of predictions
        pred_var = np.sum((X @ self.vcov) * X, axis=1)
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

    def test_non_linearity(self) -> dict:
        """
        Test for non-linearity using deviance difference test

        Compares FP model to linear model
        """
        # Fit linear model
        linear_model = self._fit_single_model(
            self.fitted_doses,
            self.fitted_log_rr,
            self.fitted_variance,
            (1,)  # Linear: power = 1
        )

        # Deviance difference test
        dev_diff = linear_model['deviance'] - self.deviance
        df = self.coefficients.shape[0] - 2  # Difference in parameters

        p_value = 1 - chi2.cdf(dev_diff, df)

        return {
            'deviance_difference': dev_diff,
            'df': df,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    def get_model_info(self) -> dict:
        """Return information about the best model"""
        if self.best_powers is None:
            return None

        return {
            'best_powers': self.best_powers,
            'deviance': self.deviance,
            'n_parameters': len(self.coefficients),
            'fp_type': f"FP{self.degree}",
            'n_models_tested': len(self.all_models)
        }

    def compare_models(self, top_n: int = 5) -> List[dict]:
        """
        Compare top N models by AIC

        Returns
        -------
        top_models : List[dict]
            List of top N models with their statistics
        """
        if not self.all_models:
            return []

        # Sort by AIC
        sorted_models = sorted(self.all_models, key=lambda x: x['aic'])

        return [{
            'rank': i + 1,
            'powers': m['powers'],
            'aic': m['aic'],
            'deviance': m['deviance'],
            'delta_aic': m['aic'] - sorted_models[0]['aic']
        } for i, m in enumerate(sorted_models[:top_n])]
