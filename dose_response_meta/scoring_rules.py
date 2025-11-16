"""
Proper Scoring Rules for Dose-Response Meta-Analysis

Implementation of proper scoring rules for evaluating probabilistic forecasts,
as recommended by Gneiting & Raftery (2007).

References:
- Gneiting T, Raftery AE. J R Stat Soc Series B Stat Methodol. 2007;69(2):243-268.
- Held L, et al. Stat Med. 2014;33(3):378-398.
"""

import numpy as np
from typing import Tuple, Optional


def interval_score(y_true: np.ndarray,
                   lower: np.ndarray,
                   upper: np.ndarray,
                   alpha: float = 0.05) -> Tuple[np.ndarray, float]:
    """
    Compute interval score (Gneiting & Raftery 2007)

    The interval score is a proper scoring rule for interval forecasts that
    combines sharpness (interval width) and calibration (coverage).

    Formula:
    IS = (u - l) + (2/α) * [(l - y) * I(y < l) + (y - u) * I(y > u)]

    Where:
    - (u - l) = interval width (sharpness)
    - Second term = penalty for miscoverage (calibration)
    - α = nominal miscoverage rate (e.g., 0.05 for 95% CI)

    Lower score = better performance

    Parameters
    ----------
    y_true : np.ndarray
        True values
    lower : np.ndarray
        Lower bounds of prediction intervals
    upper : np.ndarray
        Upper bounds of prediction intervals
    alpha : float
        Nominal miscoverage rate (default: 0.05 for 95% CI)

    Returns
    -------
    scores : np.ndarray
        Interval scores for each prediction
    mean_score : float
        Mean interval score

    Examples
    --------
    >>> y_true = np.array([1.0, 2.0, 3.0])
    >>> lower = np.array([0.5, 1.5, 2.0])
    >>> upper = np.array([1.5, 2.5, 4.0])
    >>> scores, mean_score = interval_score(y_true, lower, upper)
    """
    y_true = np.asarray(y_true)
    lower = np.asarray(lower)
    upper = np.asarray(upper)

    # Interval width (sharpness component)
    width = upper - lower

    # Undercoverage penalty (left tail)
    left_penalty = (2.0 / alpha) * np.maximum(0, lower - y_true)

    # Undercoverage penalty (right tail)
    right_penalty = (2.0 / alpha) * np.maximum(0, y_true - upper)

    # Total interval score
    scores = width + left_penalty + right_penalty

    return scores, np.mean(scores)


def weighted_interval_score(y_true: np.ndarray,
                            lower: np.ndarray,
                            upper: np.ndarray,
                            weights: Optional[np.ndarray] = None,
                            alpha: float = 0.05) -> float:
    """
    Weighted interval score

    Useful when observations have different importance or precision

    Parameters
    ----------
    y_true : np.ndarray
        True values
    lower : np.ndarray
        Lower bounds
    upper : np.ndarray
        Upper bounds
    weights : np.ndarray, optional
        Weights for each observation (default: equal weights)
    alpha : float
        Nominal miscoverage rate

    Returns
    -------
    weighted_score : float
        Weighted mean interval score
    """
    scores, _ = interval_score(y_true, lower, upper, alpha)

    if weights is None:
        weights = np.ones_like(scores)

    weights = np.asarray(weights)
    weights = weights / np.sum(weights)  # Normalize

    return np.sum(weights * scores)


def decompose_interval_score(y_true: np.ndarray,
                             lower: np.ndarray,
                             upper: np.ndarray,
                             alpha: float = 0.05) -> dict:
    """
    Decompose interval score into components

    Returns sharpness (width) and calibration (penalties) separately

    Parameters
    ----------
    y_true : np.ndarray
        True values
    lower : np.ndarray
        Lower bounds
    upper : np.ndarray
        Upper bounds
    alpha : float
        Nominal miscoverage rate

    Returns
    -------
    components : dict
        Dictionary with:
        - 'sharpness': Mean interval width
        - 'undercoverage_left': Mean left-tail penalty
        - 'undercoverage_right': Mean right-tail penalty
        - 'calibration': Total calibration penalty
        - 'total_score': Total interval score
        - 'coverage': Empirical coverage rate
    """
    y_true = np.asarray(y_true)
    lower = np.asarray(lower)
    upper = np.asarray(upper)

    # Components
    width = upper - lower
    left_penalty = (2.0 / alpha) * np.maximum(0, lower - y_true)
    right_penalty = (2.0 / alpha) * np.maximum(0, y_true - upper)

    # Coverage
    coverage = np.mean((y_true >= lower) & (y_true <= upper)) * 100

    return {
        'sharpness': np.mean(width),
        'undercoverage_left': np.mean(left_penalty),
        'undercoverage_right': np.mean(right_penalty),
        'calibration': np.mean(left_penalty + right_penalty),
        'total_score': np.mean(width + left_penalty + right_penalty),
        'coverage': coverage,
        'n_obs': len(y_true)
    }


def continuous_ranked_probability_score(y_true: np.ndarray,
                                       predictions: np.ndarray,
                                       lower: np.ndarray,
                                       upper: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Continuous Ranked Probability Score (CRPS) approximation

    Approximates CRPS using prediction interval for normally distributed forecasts

    For normal distribution N(μ, σ²):
    CRPS ≈ σ * [z * (2Φ(z) - 1) + 2φ(z) - 1/√π]

    Where z = (y - μ) / σ

    Parameters
    ----------
    y_true : np.ndarray
        True values
    predictions : np.ndarray
        Point predictions (mean)
    lower : np.ndarray
        Lower CI bounds
    upper : np.ndarray
        Upper CI bounds

    Returns
    -------
    crps_values : np.ndarray
        CRPS for each prediction
    mean_crps : float
        Mean CRPS
    """
    from scipy.stats import norm

    y_true = np.asarray(y_true)
    predictions = np.asarray(predictions)

    # Estimate σ from CI width (assuming normal distribution)
    # For 95% CI: width ≈ 2 * 1.96 * σ
    sigma = (upper - lower) / (2 * 1.96)

    # Standardized residual
    z = (y_true - predictions) / (sigma + 1e-10)

    # CRPS formula for normal distribution
    crps = sigma * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))

    return crps, np.mean(crps)


def log_score(y_true: np.ndarray,
             predictions: np.ndarray,
             lower: np.ndarray,
             upper: np.ndarray) -> Tuple[np.ndarray, float]:
    """
    Logarithmic score (log-likelihood)

    Assumes normal distribution N(μ, σ²)

    Parameters
    ----------
    y_true : np.ndarray
        True values
    predictions : np.ndarray
        Point predictions
    lower : np.ndarray
        Lower CI bounds
    upper : np.ndarray
        Upper CI bounds

    Returns
    -------
    log_scores : np.ndarray
        Logarithmic scores (negative log-likelihood)
    mean_log_score : float
        Mean log score
    """
    from scipy.stats import norm

    # Estimate σ from CI
    sigma = (upper - lower) / (2 * 1.96)

    # Log-likelihood
    log_lik = norm.logpdf(y_true, loc=predictions, scale=sigma)

    # Log score = negative log-likelihood
    log_scores = -log_lik

    return log_scores, np.mean(log_scores)


def calibration_metrics(y_true: np.ndarray,
                       lower: np.ndarray,
                       upper: np.ndarray,
                       alpha: float = 0.05) -> dict:
    """
    Compute calibration metrics

    Parameters
    ----------
    y_true : np.ndarray
        True values
    lower : np.ndarray
        Lower CI bounds
    upper : np.ndarray
        Upper CI bounds
    alpha : float
        Nominal miscoverage rate

    Returns
    -------
    metrics : dict
        Calibration metrics:
        - 'coverage': Empirical coverage rate (%)
        - 'nominal_coverage': Nominal coverage (%)
        - 'coverage_error': Difference from nominal
        - 'undercoverage_left': % below lower bound
        - 'undercoverage_right': % above upper bound
        - 'well_calibrated': Boolean (within ±2% of nominal)
    """
    y_true = np.asarray(y_true)
    lower = np.asarray(lower)
    upper = np.asarray(upper)

    nominal_coverage = (1 - alpha) * 100

    # Empirical coverage
    covered = (y_true >= lower) & (y_true <= upper)
    coverage = np.mean(covered) * 100

    # Undercoverage breakdown
    below_lower = np.mean(y_true < lower) * 100
    above_upper = np.mean(y_true > upper) * 100

    # Coverage error
    coverage_error = coverage - nominal_coverage

    # Well-calibrated if within ±2% of nominal
    well_calibrated = abs(coverage_error) <= 2.0

    return {
        'coverage': coverage,
        'nominal_coverage': nominal_coverage,
        'coverage_error': coverage_error,
        'undercoverage_left': below_lower,
        'undercoverage_right': above_upper,
        'well_calibrated': well_calibrated,
        'n_obs': len(y_true),
        'n_covered': np.sum(covered)
    }


def sharpness_metrics(lower: np.ndarray,
                     upper: np.ndarray) -> dict:
    """
    Compute sharpness (precision) metrics

    Parameters
    ----------
    lower : np.ndarray
        Lower CI bounds
    upper : np.ndarray
        Upper CI bounds

    Returns
    -------
    metrics : dict
        Sharpness metrics:
        - 'mean_width': Mean interval width
        - 'median_width': Median interval width
        - 'min_width': Minimum interval width
        - 'max_width': Maximum interval width
        - 'std_width': SD of interval widths
    """
    width = upper - lower

    return {
        'mean_width': np.mean(width),
        'median_width': np.median(width),
        'min_width': np.min(width),
        'max_width': np.max(width),
        'std_width': np.std(width)
    }


def comprehensive_evaluation(y_true: np.ndarray,
                            predictions: np.ndarray,
                            lower: np.ndarray,
                            upper: np.ndarray,
                            alpha: float = 0.05) -> dict:
    """
    Comprehensive evaluation of prediction intervals

    Combines all metrics into single report

    Parameters
    ----------
    y_true : np.ndarray
        True values
    predictions : np.ndarray
        Point predictions
    lower : np.ndarray
        Lower CI bounds
    upper : np.ndarray
        Upper CI bounds
    alpha : float
        Nominal miscoverage rate

    Returns
    -------
    evaluation : dict
        Comprehensive evaluation with all metrics
    """
    # Interval score
    scores, mean_is = interval_score(y_true, lower, upper, alpha)
    is_decomp = decompose_interval_score(y_true, lower, upper, alpha)

    # Calibration
    calib = calibration_metrics(y_true, lower, upper, alpha)

    # Sharpness
    sharp = sharpness_metrics(lower, upper)

    # Point forecast metrics
    mse = np.mean((y_true - predictions) ** 2)
    mae = np.mean(np.abs(y_true - predictions))
    bias = np.mean(predictions - y_true)

    # CRPS
    crps_vals, mean_crps = continuous_ranked_probability_score(
        y_true, predictions, lower, upper
    )

    return {
        'interval_score': {
            'mean': mean_is,
            'sharpness': is_decomp['sharpness'],
            'calibration': is_decomp['calibration'],
            'decomposition': is_decomp
        },
        'calibration': calib,
        'sharpness': sharp,
        'point_forecast': {
            'mse': mse,
            'mae': mae,
            'bias': bias
        },
        'crps': {
            'mean': mean_crps
        }
    }
