"""
Two-Stage Dose-Response Meta-Analysis

Implementation based on:
- Orsini N, et al. Am J Epidemiol. 2012
- Berlin JA, et al. Stat Med. 1993
- DerSimonian R, Laird N. Control Clin Trials. 1986
- Jackson D, et al. Stat Med. 2010 (multivariate pooling)
- White IR. Stata J. 2011 (multivariate meta-regression)

Two-stage approach:
1. Stage 1: Estimate dose-response curves within each study
2. Stage 2: Pool study-specific estimates using multivariate random-effects meta-analysis

IMPORTANT: This implementation assumes ISOTROPIC between-study heterogeneity,
where Psi = tau² * I (proportional to identity matrix). This means all parameters
share the same between-study variance tau², but correlations in random effects
are not modeled. This simplification provides computational tractability and
interpretability while maintaining proper multivariate pooling of point estimates
and within-study correlations.

For unstructured heterogeneity (full Psi matrix), see future extensions.
"""

import numpy as np
from scipy.stats import chi2, norm
from typing import Optional, Tuple, List, Callable
import warnings


class TwoStageDRMA:
    """
    Two-stage dose-response meta-analysis with multivariate pooling.

    Stage 1: Fit dose-response model within each study
    Stage 2: Pool estimates across studies using multivariate random-effects meta-analysis

    This implementation uses MULTIVARIATE pooling (Jackson et al. 2010) which properly
    accounts for correlations between parameters within studies. However, it assumes
    ISOTROPIC between-study heterogeneity: Psi = tau² * I.

    This means:
    - All spline/polynomial coefficients share the same between-study variance (tau²)
    - Correlations in random effects across parameters are not modeled
    - Within-study correlations ARE properly accounted for

    Justification for isotropic assumption:
    - Computational tractability (unstructured Psi requires k*p*(p+1)/2 parameters)
    - Interpretability (single tau² easier to report and understand)
    - Sufficient for most applications (sensitivity analysis recommended)

    Parameters
    ----------
    pooling_method : str
        Method for stage 2 pooling: 'dl' (DerSimonian-Laird), 'reml', or 'fixed'
        Default: 'dl' (recommended)
    reference_dose : float
        Reference dose level (default: 0.0)

    Attributes
    ----------
    tau2 : float
        Between-study variance (estimated if pooling_method='dl')
    pooled_beta : np.ndarray
        Pooled dose-response coefficients
    pooled_vcov : np.ndarray
        Variance-covariance matrix of pooled coefficients
    heterogeneity_stats : dict
        I², H², Q statistics for heterogeneity assessment

    References
    ----------
    Jackson D, White IR, Thompson SG. Stat Med. 2010;29(12):1282-97.
    White IR. Stata J. 2011;11(2):255-270.
    IntHout J, Ioannidis JPA, Borm GF. BMJ. 2014;349:g5219.
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
        Pool estimates using multivariate DerSimonian-Laird random-effects meta-analysis

        Based on Jackson et al. (2010) "Multivariate meta-analysis: Potential and promise"
        and White (2011) "Multivariate random-effects meta-regression"

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
            Between-study variance (isotropic)
        """
        n_studies, n_params = betas.shape

        # Step 1: Fixed-effects pooling to get initial estimate
        # Sum of inverse variance-covariance matrices
        sum_inv_V = np.zeros((n_params, n_params))
        sum_inv_V_beta = np.zeros(n_params)

        for i in range(n_studies):
            try:
                inv_V = np.linalg.inv(vcovs[i] + 1e-8 * np.eye(n_params))
                sum_inv_V += inv_V
                sum_inv_V_beta += inv_V @ betas[i, :]
            except np.linalg.LinAlgError:
                # Skip singular matrices
                continue

        try:
            beta_fixed = np.linalg.solve(sum_inv_V, sum_inv_V_beta)
        except np.linalg.LinAlgError:
            # Fallback to univariate if multivariate fails
            warnings.warn("Multivariate pooling failed, using univariate fallback")
            return self._pool_estimates_dl_univariate(betas, vcovs)

        # Step 2: Compute Q statistic for heterogeneity
        Q = 0.0
        for i in range(n_studies):
            resid = betas[i, :] - beta_fixed
            try:
                inv_V = np.linalg.inv(vcovs[i] + 1e-8 * np.eye(n_params))
                Q += resid.T @ inv_V @ resid
            except np.linalg.LinAlgError:
                continue

        # Step 3: DerSimonian-Laird estimate of tau²
        # For multivariate case with isotropic heterogeneity: Psi = tau² * I
        # Q ~ chi²(df), where df = n_studies * n_params - n_params
        df = n_studies * n_params - n_params

        # Compute constant C for DL estimator
        # C = trace(sum W_i) - trace(sum W_i * inv(sum W_i) * W_i)
        C = 0.0
        for i in range(n_studies):
            try:
                inv_V = np.linalg.inv(vcovs[i] + 1e-8 * np.eye(n_params))
                C += np.trace(inv_V)
            except np.linalg.LinAlgError:
                continue

        # Correction term
        C_correction = 0.0
        for i in range(n_studies):
            try:
                inv_V = np.linalg.inv(vcovs[i] + 1e-8 * np.eye(n_params))
                temp = inv_V @ np.linalg.inv(sum_inv_V) @ inv_V
                C_correction += np.trace(temp)
            except np.linalg.LinAlgError:
                continue

        C = C - C_correction

        # Estimate tau²
        if C > 0:
            tau2 = max(0, (Q - df) / C)
        else:
            tau2 = 0.0

        # Step 4: Random-effects pooling with estimated tau²
        # Total variance: V_i + tau² * I
        sum_inv_V_re = np.zeros((n_params, n_params))
        sum_inv_V_re_beta = np.zeros(n_params)

        Psi = tau2 * np.eye(n_params)  # Isotropic between-study variance

        for i in range(n_studies):
            try:
                V_total = vcovs[i] + Psi
                inv_V_total = np.linalg.inv(V_total)
                sum_inv_V_re += inv_V_total
                sum_inv_V_re_beta += inv_V_total @ betas[i, :]
            except np.linalg.LinAlgError:
                continue

        # Pooled estimate
        try:
            pooled_beta = np.linalg.solve(sum_inv_V_re, sum_inv_V_re_beta)
            pooled_vcov = np.linalg.inv(sum_inv_V_re)
        except np.linalg.LinAlgError:
            # Final fallback
            warnings.warn("Random-effects pooling failed, using fixed-effects")
            pooled_beta = beta_fixed
            pooled_vcov = np.linalg.inv(sum_inv_V)
            tau2 = 0.0

        return pooled_beta, pooled_vcov, tau2

    def _pool_estimates_dl_univariate(self, betas: np.ndarray, vcovs: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Fallback univariate pooling when multivariate pooling fails

        NOTE: This ignores correlation between parameters and should only be used
        as a last resort when multivariate pooling fails.
        """
        n_studies, n_params = betas.shape

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

        # Use average tau²
        tau2 = np.mean(tau2_vec)

        return pooled_beta, pooled_vcov, tau2

    def _pool_estimates_fixed(self, betas: np.ndarray, vcovs: List[np.ndarray]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Pool estimates using multivariate fixed-effects meta-analysis

        Parameters
        ----------
        betas : np.ndarray
            Study-specific estimates (n_studies x n_params)
        vcovs : List[np.ndarray]
            Study-specific variance-covariance matrices

        Returns
        -------
        pooled_beta : np.ndarray
            Pooled coefficients
        pooled_vcov : np.ndarray
            Variance-covariance matrix of pooled estimates
        """
        n_studies, n_params = betas.shape

        # Multivariate fixed-effects: pooled = (sum V_i^-1)^-1 * sum(V_i^-1 * beta_i)
        sum_inv_V = np.zeros((n_params, n_params))
        sum_inv_V_beta = np.zeros(n_params)

        for i in range(n_studies):
            try:
                inv_V = np.linalg.inv(vcovs[i] + 1e-8 * np.eye(n_params))
                sum_inv_V += inv_V
                sum_inv_V_beta += inv_V @ betas[i, :]
            except np.linalg.LinAlgError:
                # Skip singular matrices
                warnings.warn(f"Study {i} has singular covariance matrix, skipping")
                continue

        try:
            pooled_beta = np.linalg.solve(sum_inv_V, sum_inv_V_beta)
            pooled_vcov = np.linalg.inv(sum_inv_V)
        except np.linalg.LinAlgError:
            warnings.warn("Fixed-effects pooling failed, using univariate fallback")
            # Univariate fallback
            pooled_beta = np.zeros(n_params)
            pooled_vcov = np.zeros((n_params, n_params))

            for j in range(n_params):
                theta = betas[:, j]
                sigma2 = np.array([vcov[j, j] for vcov in vcovs])
                w = 1.0 / sigma2
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
                alpha: float = 0.05,
                use_hksj: bool = True) -> Tuple[np.ndarray, ...]:
        """
        Predict pooled dose-response curve with optional HKSJ correction

        Parameters
        ----------
        doses : np.ndarray
            Dose levels for prediction
        return_ci : bool
            Whether to return confidence intervals
        alpha : float
            Significance level
        use_hksj : bool
            Whether to use Hartung-Knapp-Sidik-Jonkman small-sample correction
            (default: True). Recommended for meta-analyses with < 20 studies.

        Returns
        -------
        predictions : np.ndarray
        lower_ci : np.ndarray (if return_ci=True)
        upper_ci : np.ndarray (if return_ci=True)

        References
        ----------
        Hartung J, Knapp G. Stat Med. 2001;20(24):3875-89.
        IntHout J, Ioannidis JP, Borm GF. BMJ. 2014;349:g5219.
        """
        if self.pooled_beta is None:
            raise ValueError("Model must be fitted before prediction")

        doses = np.asarray(doses)
        X = self.basis_function(doses)

        # Point predictions
        predictions = X @ self.pooled_beta

        if not return_ci:
            return predictions

        # Variance of predictions
        pred_var = np.sum((X @ self.pooled_vcov) * X, axis=1)
        pred_se = np.sqrt(pred_var)

        # HKSJ correction for small-sample meta-analyses
        # Based on IntHout et al. (2014) BMJ: "The Hartung-Knapp-Sidik-Jonkman method
        # for random effects meta-analysis is straightforward and considerably
        # outperforms the standard DerSimonian-Laird method"
        if use_hksj and hasattr(self, 'study_estimates'):
            n_studies = len([s for s in self.study_estimates if s['converged']])

            if n_studies < 20:  # HKSJ recommended for < 20 studies
                # Degrees of freedom
                df = n_studies - 1

                # Use t-distribution instead of normal
                from scipy.stats import t as t_dist
                t_crit = t_dist.ppf(1 - alpha/2, df)

                # HKSJ variance correction factor
                # According to IntHout et al. (2014), use Q/df directly
                # This reduces SE when Q < df (low heterogeneity) and increases when Q > df
                if hasattr(self, 'heterogeneity_stats'):
                    Q = self.heterogeneity_stats['Q']
                    Q_df = max(self.heterogeneity_stats['Q_df'], 1)  # Avoid division by zero

                    # HKSJ correction: SE_HKSJ = SE * sqrt(Q / df)
                    hksj_factor = Q / Q_df
                    pred_se_hksj = pred_se * np.sqrt(hksj_factor)
                else:
                    # No heterogeneity stats available, use uncorrected SE
                    pred_se_hksj = pred_se

                lower_ci = predictions - t_crit * pred_se_hksj
                upper_ci = predictions + t_crit * pred_se_hksj
            else:
                # Large sample: use normal distribution
                z = norm.ppf(1 - alpha/2)
                lower_ci = predictions - z * pred_se
                upper_ci = predictions + z * pred_se
        else:
            # No HKSJ correction
            z = norm.ppf(1 - alpha/2)
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
