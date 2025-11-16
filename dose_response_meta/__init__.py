"""
Dose-Response Meta-Analysis Platform

A comprehensive platform for conducting dose-response meta-analyses using:
- Restricted cubic splines
- Fractional polynomial models
- One-stage and two-stage approaches
- Handling heterogeneous dose ranges across studies

Based on methods from Orsini et al. (2012) and Crippa et al. (2019)
"""

__version__ = "1.0.0"
__author__ = "Research Team"

from .splines import RestrictedCubicSpline
from .fractional_polynomials import FractionalPolynomial
from .one_stage import OneStageDRMA
from .two_stage import TwoStageDRMA

__all__ = [
    'RestrictedCubicSpline',
    'FractionalPolynomial',
    'OneStageDRMA',
    'TwoStageDRMA'
]
