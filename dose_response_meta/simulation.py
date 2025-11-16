"""
Data Simulation for Dose-Response Meta-Analysis

Generate synthetic datasets with known dose-response relationships
for testing and comparing different meta-analysis methods.
"""

import numpy as np
from typing import Tuple, Callable, Optional
import pandas as pd


class DoseResponseSimulator:
    """
    Simulate dose-response meta-analysis data with heterogeneity.

    Parameters
    ----------
    n_studies : int
        Number of studies to simulate
    n_doses_per_study : int or tuple
        Number of dose levels per study (fixed or range)
    dose_range : tuple
        Range of doses to simulate (min, max)
    true_curve : Callable
        Function defining true dose-response relationship
    between_study_sd : float
        Between-study standard deviation (heterogeneity)
    within_study_sd : float
        Within-study standard deviation (measurement error)
    random_seed : Optional[int]
        Random seed for reproducibility
    """

    def __init__(self,
                 n_studies: int = 10,
                 n_doses_per_study: int = 5,
                 dose_range: Tuple[float, float] = (0, 100),
                 true_curve: Optional[Callable] = None,
                 between_study_sd: float = 0.1,
                 within_study_sd: float = 0.05,
                 random_seed: Optional[int] = None):

        self.n_studies = n_studies
        self.n_doses_per_study = n_doses_per_study
        self.dose_range = dose_range
        self.between_study_sd = between_study_sd
        self.within_study_sd = within_study_sd
        self.random_seed = random_seed

        if random_seed is not None:
            np.random.seed(random_seed)

        # Default true curve: quadratic dose-response
        if true_curve is None:
            self.true_curve = lambda x: 0.01 * x - 0.0001 * x**2
        else:
            self.true_curve = true_curve

    @staticmethod
    def create_linear_curve(slope: float = 0.01) -> Callable:
        """Create a linear dose-response curve"""
        return lambda x: slope * x

    @staticmethod
    def create_quadratic_curve(beta1: float = 0.01, beta2: float = -0.0001) -> Callable:
        """Create a quadratic dose-response curve"""
        return lambda x: beta1 * x + beta2 * x**2

    @staticmethod
    def create_logarithmic_curve(scale: float = 0.5) -> Callable:
        """Create a logarithmic dose-response curve"""
        return lambda x: scale * np.log(x + 1)

    @staticmethod
    def create_threshold_curve(threshold: float = 50, slope: float = 0.02) -> Callable:
        """Create a threshold dose-response curve"""
        return lambda x: slope * np.maximum(x - threshold, 0)

    @staticmethod
    def create_spline_curve(knots: np.ndarray = np.array([0, 25, 50, 75, 100]),
                           coefficients: np.ndarray = np.array([0, 0.3, 0.8, 1.0, 0.9])) -> Callable:
        """Create a curve based on cubic spline interpolation"""
        from scipy.interpolate import CubicSpline
        cs = CubicSpline(knots, coefficients)
        return lambda x: cs(np.clip(x, knots[0], knots[-1]))

    def simulate_study_doses(self, study_idx: int) -> np.ndarray:
        """
        Simulate dose levels for a single study

        Doses can vary across studies (heterogeneous dose ranges)
        """
        if isinstance(self.n_doses_per_study, tuple):
            n_doses = np.random.randint(self.n_doses_per_study[0],
                                       self.n_doses_per_study[1] + 1)
        else:
            n_doses = self.n_doses_per_study

        # Each study may have different dose range (realistic scenario)
        study_dose_min = self.dose_range[0] + np.random.uniform(0, 0.2 * (self.dose_range[1] - self.dose_range[0]))
        study_dose_max = self.dose_range[1] - np.random.uniform(0, 0.2 * (self.dose_range[1] - self.dose_range[0]))

        # Generate doses (including reference dose = 0)
        if n_doses > 1:
            doses = np.concatenate([[0], np.sort(np.random.uniform(study_dose_min, study_dose_max, n_doses - 1))])
        else:
            doses = np.array([0])

        return doses

    def simulate(self) -> pd.DataFrame:
        """
        Simulate complete dose-response meta-analysis dataset

        Returns
        -------
        data : pd.DataFrame
            Simulated dataset with columns:
            - study_id: Study identifier
            - dose: Dose level
            - log_rr: Log relative risk (observed)
            - se: Standard error
            - variance: Variance
            - true_log_rr: True log relative risk (without error)
            - study_effect: Study-specific random effect
        """
        data_list = []

        for study_idx in range(self.n_studies):
            # Generate doses for this study
            doses = self.simulate_study_doses(study_idx)

            # Study-specific random effect (between-study heterogeneity)
            study_effect = np.random.normal(0, self.between_study_sd)

            # True dose-response for this study
            true_log_rr = self.true_curve(doses) + study_effect

            # Add measurement error (within-study variability)
            # Standard error increases slightly with dose (realistic)
            base_se = self.within_study_sd
            se = base_se * (1 + 0.1 * doses / self.dose_range[1])

            # Observed log RR with error
            observed_log_rr = true_log_rr + np.random.normal(0, se)

            # Create study data
            for i, dose in enumerate(doses):
                data_list.append({
                    'study_id': study_idx,
                    'dose': dose,
                    'log_rr': observed_log_rr[i],
                    'se': se[i],
                    'variance': se[i]**2,
                    'true_log_rr': true_log_rr[i],
                    'study_effect': study_effect
                })

        return pd.DataFrame(data_list)

    def simulate_with_covariates(self,
                                 covariate_effects: dict = None) -> pd.DataFrame:
        """
        Simulate data with study-level covariates

        Parameters
        ----------
        covariate_effects : dict
            Dictionary mapping covariate names to their effects
            Example: {'quality': 0.1, 'year': -0.01}

        Returns
        -------
        data : pd.DataFrame
            Dataset with additional covariate columns
        """
        data = self.simulate()

        if covariate_effects:
            # Add study-level covariates
            for study_idx in range(self.n_studies):
                mask = data['study_id'] == study_idx

                for cov_name, cov_effect in covariate_effects.items():
                    # Generate covariate value
                    cov_value = np.random.normal(0, 1)
                    data.loc[mask, cov_name] = cov_value

                    # Add covariate effect to log_rr
                    data.loc[mask, 'log_rr'] += cov_effect * cov_value

        return data


def generate_example_scenarios() -> dict:
    """
    Generate several example scenarios for testing

    Returns
    -------
    scenarios : dict
        Dictionary of different simulation scenarios
    """
    scenarios = {}

    # Scenario 1: Linear dose-response, low heterogeneity
    scenarios['linear_low_het'] = DoseResponseSimulator(
        n_studies=15,
        n_doses_per_study=5,
        dose_range=(0, 100),
        true_curve=DoseResponseSimulator.create_linear_curve(slope=0.015),
        between_study_sd=0.05,
        within_study_sd=0.08,
        random_seed=42
    )

    # Scenario 2: Quadratic dose-response, moderate heterogeneity
    scenarios['quadratic_mod_het'] = DoseResponseSimulator(
        n_studies=20,
        n_doses_per_study=(4, 7),
        dose_range=(0, 100),
        true_curve=DoseResponseSimulator.create_quadratic_curve(beta1=0.02, beta2=-0.0002),
        between_study_sd=0.15,
        within_study_sd=0.1,
        random_seed=123
    )

    # Scenario 3: Logarithmic dose-response, high heterogeneity
    scenarios['log_high_het'] = DoseResponseSimulator(
        n_studies=12,
        n_doses_per_study=6,
        dose_range=(0, 150),
        true_curve=DoseResponseSimulator.create_logarithmic_curve(scale=0.4),
        between_study_sd=0.25,
        within_study_sd=0.12,
        random_seed=456
    )

    # Scenario 4: Threshold effect, moderate heterogeneity
    scenarios['threshold_mod_het'] = DoseResponseSimulator(
        n_studies=18,
        n_doses_per_study=5,
        dose_range=(0, 120),
        true_curve=DoseResponseSimulator.create_threshold_curve(threshold=60, slope=0.025),
        between_study_sd=0.12,
        within_study_sd=0.09,
        random_seed=789
    )

    # Scenario 5: Complex non-linear (spline-based)
    scenarios['complex_nonlinear'] = DoseResponseSimulator(
        n_studies=25,
        n_doses_per_study=(5, 8),
        dose_range=(0, 100),
        true_curve=DoseResponseSimulator.create_spline_curve(
            knots=np.array([0, 20, 40, 60, 80, 100]),
            coefficients=np.array([0, 0.2, 0.6, 0.8, 0.7, 0.5])
        ),
        between_study_sd=0.18,
        within_study_sd=0.1,
        random_seed=999
    )

    return scenarios
