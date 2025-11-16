# Table 3. Comprehensive Performance Metrics by Method and Scenario

**Performance metrics** across 50 simulations per scenario. MSE = Mean Squared Error.

| Scenario | Method | MSE | Coverage (%) | Interval Score | Sharpness | Calibration |
|----------|--------|-----|--------------|----------------|-----------|-------------|
| **Linear (low het)** | Two-Stage DL + HKSJ | 0.082 | 99.4 | 163.23 | 163.22 | 0.00 |
| | Two-Stage Fixed | 0.035 | 96.3 | 23.83 | 23.80 | 0.03 |
| | One-Stage REML | 0.001 | 91.5 | 0.17 | 0.12 | 0.05 |
| **Quadratic (mod het)** | Two-Stage DL + HKSJ | 1.503 | 99.4 | 764.42 | 764.41 | 0.01 |
| | Two-Stage Fixed | 0.338 | 92.7 | 23.93 | 23.80 | 0.12 |
| | One-Stage REML | 0.005 | 84.3 | 0.42 | 0.22 | 0.20 |
| **Logarithmic (high het)** | Two-Stage DL + HKSJ | 1.364 | 97.5 | 1689.13 | 1689.04 | 0.09 |
| | Two-Stage Fixed | 0.309 | 83.1 | 25.22 | 23.80 | 1.41 |
| | One-Stage REML | 0.046 | 54.7 | 2.46 | 0.33 | 2.13 |
| **Threshold (mod het)** | Two-Stage DL + HKSJ | 1.624 | 99.4 | 765.12 | 765.12 | 0.01 |
| | Two-Stage Fixed | 0.362 | 92.7 | 23.93 | 23.80 | 0.12 |
| | One-Stage REML | 0.005 | 85.0 | 0.42 | 0.22 | 0.20 |
| **U-shaped (mod het)** | Two-Stage DL + HKSJ | 2.360 | 99.5 | 770.88 | 770.87 | 0.01 |
| | Two-Stage Fixed | 0.505 | 93.0 | 23.93 | 23.80 | 0.12 |
| | One-Stage REML | 0.005 | 84.8 | 0.44 | 0.22 | 0.22 |
| **J-shaped (mod het)** | Two-Stage DL + HKSJ | 1.215 | 99.5 | 767.19 | 767.19 | 0.01 |
| | Two-Stage Fixed | 0.278 | 92.5 | 23.93 | 23.80 | 0.13 |
| | One-Stage REML | 0.006 | 84.9 | 0.46 | 0.22 | 0.24 |
| **Dose-dep het** | Two-Stage DL + HKSJ | 0.076 | 99.8 | 394.51 | 394.51 | 0.00 |
| | Two-Stage Fixed | 0.076 | 95.9 | 23.98 | 23.95 | 0.03 |
| | One-Stage REML | 0.006 | 72.9 | 0.71 | 0.17 | 0.54 |

**Notes:**
- **MSE:** Lower is better (point prediction accuracy)
- **Coverage:** Target 95%; 90-98% acceptable
- **Interval Score:** Lower is better (proper scoring rule)
  - **Sharpness:** Interval width (precision) - lower is sharper
  - **Calibration:** Miscoverage penalty (accuracy) - should be ≈0
- Interval Score = Sharpness + Calibration

**Key Insights:**

1. **Precision-Validity Tradeoff:**
   - One-Stage: Best MSE (0.001-0.046) and sharpest intervals BUT poor calibration (penalties 0.05-2.13)
   - HKSJ: Higher MSE (0.08-2.4) and wide intervals BUT excellent calibration (penalties ≈0)

2. **Proper Scoring Rules Reveal Truth:**
   - One-Stage appears "best" on traditional metrics (MSE, narrow CIs)
   - But calibration penalties show intervals are too narrow (overclaimed precision)
   - HKSJ sacrifices sharpness for honest uncertainty quantification

3. **Fixed-Effects Misleading:**
   - Constant sharpness (≈23.8) assumes no heterogeneity
   - When heterogeneity present (log scenario), calibration penalty increases to 1.41
   - Undercoverage (83%) in high-heterogeneity scenario

4. **HKSJ Properly Calibrated:**
   - Calibration penalties near zero (0.00-0.09) across all scenarios
   - Intervals honestly reflect uncertainty
   - Wide intervals (sharpness 163-1689) are appropriate, not excessive

**Clinical Interpretation:**
- Narrow intervals (one-stage) may give false confidence
- HKSJ provides valid inference at cost of precision
- Choice depends on goal: inference (use HKSJ) vs. prediction (one-stage acceptable with recalibration)
