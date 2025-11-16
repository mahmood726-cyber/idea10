# Decision Framework for Dose-Response Meta-Analysis Method Selection

## Executive Summary

This framework guides researchers in selecting appropriate dose-response meta-analysis methods based on study characteristics and analysis goals.

**Quick Recommendation:**
- **For inference (hypothesis testing, CIs):** Two-stage RCS with DerSimonian-Laird + HKSJ correction
- **For prediction (future studies):** One-stage RCS with REML
- **For simple curves (linear/quadratic):** Fractional polynomials may be sufficient
- **For complex curves:** Restricted cubic splines (RCS) recommended

---

## 1. Method Selection Flowchart

```
START: Dose-response meta-analysis needed
│
├─> What is your PRIMARY GOAL?
│
│   ├─> INFERENCE (CIs, hypothesis tests, publication)
│   │   │
│   │   ├─> How many studies? (k)
│   │   │   │
│   │   │   ├─> k < 5: STOP - Too few studies for meta-analysis
│   │   │   │            Consider narrative review or mega-analysis
│   │   │   │
│   │   │   ├─> 5 ≤ k < 20 (SMALL META-ANALYSIS)
│   │   │   │   │
│   │   │   │   └─> RECOMMENDED: Two-Stage RCS + DL + HKSJ
│   │   │   │       - HKSJ correction critical for valid coverage
│   │   │   │       - T-distribution accounts for small-sample uncertainty
│   │   │   │       - Expected coverage: 90-98%
│   │   │   │
│   │   │   └─> k ≥ 20 (MODERATE/LARGE META-ANALYSIS)
│   │   │       │
│   │   │       └─> RECOMMENDED: Two-Stage RCS + DL (HKSJ optional)
│   │   │           - Normal distribution adequate
│   │   │           - HKSJ may be conservative
│   │   │           - Expected coverage: 93-95%
│   │   │
│   │   └─> What heterogeneity do you expect? (I²)
│   │       │
│   │       ├─> Low (I² < 25%): Two-Stage Fixed-Effects acceptable
│   │       │                   - Narrower CIs, assumes homogeneity
│   │       │                   - Test heterogeneity first!
│   │       │
│   │       ├─> Moderate (25% ≤ I² ≤ 75%): Two-Stage DL + HKSJ (default)
│   │       │
│   │       └─> High (I² > 75%): Two-Stage DL + HKSJ
│   │                            - Consider subgroup analysis
│   │                            - Investigate sources of heterogeneity
│   │
│   └─> PREDICTION (predict future studies, risk assessment)
│       │
│       ├─> RECOMMENDED: One-Stage RCS with REML
│       │   - Better prediction intervals
│       │   - Accounts for within-study correlation
│       │   - Shrinkage of study-specific estimates
│       │
│       └─> If convergence issues:
│           - Try multi-start optimization (already implemented)
│           - Reduce number of knots (try 3 or 4)
│           - Consider simpler model (fractional polynomials)
│
└─> CURVE SHAPE: Do you know the expected shape?
    │
    ├─> LINEAR or QUADRATIC → Fractional Polynomials (FP1 or FP2)
    │                         - Fewer parameters, more stable
    │                         - Easier interpretation
    │                         - AIC to select powers
    │
    ├─> THRESHOLD (no effect below cutpoint) → RCS with 4 knots
    │                                          - Can capture sharp transitions
    │                                          - Place knot near threshold if known
    │
    ├─> U-SHAPED or J-SHAPED → RCS with 4-5 knots
    │                          - Can model turning points
    │                          - Robust to local extrema
    │
    ├─> COMPLEX (multiple inflections) → RCS with 5-7 knots
    │                                    - High flexibility
    │                                    - Risk of overfitting with <15 studies
    │
    └─> UNKNOWN → Start with RCS (4 knots)
                  - Diagnostic: test for non-linearity
                  - If linear (p > 0.05), use FP1
                  - If non-linear, keep RCS
```

---

## 2. Decision Table

| Characteristic | Recommended Method | Alternative | Notes |
|----------------|-------------------|-------------|-------|
| **Goal: Inference** | Two-Stage DL + HKSJ | Two-Stage Fixed (if I²<25%) | HKSJ essential for k<20 |
| **Goal: Prediction** | One-Stage REML | Two-Stage DL | Better prediction intervals |
| **k < 5 studies** | ⚠️ Not recommended | Qualitative synthesis | Insufficient power |
| **5 ≤ k < 20 studies** | Two-Stage DL + HKSJ | One-Stage REML | HKSJ corrects coverage |
| **k ≥ 20 studies** | Two-Stage DL | One-Stage REML | Either method valid |
| **Linear curve** | FP1 (power=1) | RCS (test non-linearity) | Simpler model preferred |
| **Quadratic curve** | FP2 or RCS (3 knots) | Two-Stage polynomial | FP2 more interpretable |
| **U-shaped/J-shaped** | RCS (4-5 knots) | FP2 (if symmetric) | RCS more flexible |
| **Complex curve** | RCS (5-7 knots) | One-Stage RCS | Risk overfitting |
| **Low heterogeneity (I²<25%)** | Two-Stage Fixed | Two-Stage DL | Test first with Q-test |
| **Moderate heterogeneity (I²=25-75%)** | Two-Stage DL + HKSJ | One-Stage REML | Account for τ² |
| **High heterogeneity (I²>75%)** | Two-Stage DL + HKSJ | Subgroup analysis | Investigate sources |
| **Convergence issues** | Reduce knots, multi-start | Fractional polynomials | Check warnings |

---

## 3. Detailed Method Characteristics

### Two-Stage RCS with DerSimonian-Laird (DL) + HKSJ

**Strengths:**
- ✅ Valid inference with proper coverage (90-98%)
- ✅ HKSJ correction ensures conservative CIs for small meta-analyses
- ✅ Accounts for parameter correlations (multivariate pooling)
- ✅ Transparent: two clear steps (within-study, then pooling)
- ✅ Robust to model misspecification
- ✅ Fast computation

**Limitations:**
- ❌ Assumes isotropic heterogeneity (τ² * I)
- ❌ May be conservative for k ≥ 20
- ❌ Wider CIs than one-stage (but more honest)

**Use When:**
- Primary goal is inference (hypothesis testing, CIs)
- k = 5-30 studies (sweet spot for HKSJ)
- Need transparent, easy-to-explain method
- Want robust results for publication

**Parameters:**
```python
model = TwoStageDoseResponse(
    model_type='rcs',
    n_knots=4,
    pooling_method='random'  # DL estimator
)
# Predictions with HKSJ:
predictions, lower, upper = model.predict(doses, use_hksj=True)
```

---

### One-Stage RCS with REML

**Strengths:**
- ✅ Better prediction intervals (accounts for all uncertainty)
- ✅ Efficient use of data (simultaneous estimation)
- ✅ Borrows strength across studies
- ✅ Handles within-study correlation properly

**Limitations:**
- ❌ May undercover for k < 15 (use HKSJ in two-stage instead)
- ❌ Convergence issues possible (~1-5% of cases)
- ❌ Requires more computational resources
- ❌ Black-box optimization (harder to diagnose issues)

**Use When:**
- Primary goal is prediction or risk assessment
- k ≥ 15 studies
- Sufficient heterogeneity to estimate τ²
- Computational resources available

**Parameters:**
```python
model = OneStageDoseResponse(
    model_type='rcs',
    n_knots=4
)
# Multi-start optimization implemented by default
```

---

### Two-Stage Fixed-Effects

**Strengths:**
- ✅ Most precise estimates (narrowest CIs)
- ✅ Simple interpretation
- ✅ No heterogeneity estimation needed
- ✅ Fast computation

**Limitations:**
- ❌ Only valid if I² ≈ 0 (rare in practice)
- ❌ Undercovers if heterogeneity present (coverage <70%)
- ❌ CIs too narrow → false precision

**Use When:**
- Q-test shows no heterogeneity (p > 0.10) AND I² < 25%
- Studies very similar (same population, design, measurement)
- Conditional inference desired (these studies only)

**⚠️ Warning:** Always test heterogeneity first. If I² > 25%, use random-effects.

---

### Fractional Polynomials

**Strengths:**
- ✅ Fewer parameters than RCS
- ✅ More stable with small k
- ✅ Interpretable powers (e.g., log, square root)
- ✅ AIC-based model selection

**Limitations:**
- ❌ Less flexible than RCS for complex shapes
- ❌ May not fit U-shaped or threshold patterns well
- ❌ Power selection uncertainty not accounted for in final CIs

**Use When:**
- Expect simple curve (monotonic or single peak)
- k < 10 studies (RCS may overfit)
- Want parsimonious model
- Curve shape approximately known

**Recommendation:**
- Start with FP2 (2 powers): flexible yet stable
- Compare FP1 vs FP2 using AIC
- If AIC_FP1 - AIC_FP2 < 2, prefer simpler FP1

---

## 4. Knot Selection for RCS

Our sensitivity analysis shows:

| Number of Knots | Parameters | Use When | Coverage | MSE | Notes |
|-----------------|------------|----------|----------|-----|-------|
| **3 knots** | 2 | k < 8, simple curve | 88-92% | Higher for complex | May underfit |
| **4 knots** | 3 | k ≥ 8, general use | 90-95% | Lowest for moderate | **RECOMMENDED DEFAULT** |
| **5 knots** | 4 | k ≥ 12, complex curve | 91-96% | Good for complex | More flexible |
| **7 knots** | 6 | k ≥ 20, very complex | 89-94% | Risk overfitting | Use cautiously |

**General Rule:**
- Knots ≤ k/3 (e.g., k=15 → max 5 knots)
- Start with 4 knots (robust across scenarios)
- If test for non-linearity not significant, reduce to 3
- If complex shape suspected (U, J, multiple peaks), use 5

**Knot Placement:**
- Default: Harrell's quantiles (recommended)
- Equal spacing: Only if dose distribution is uniform
- Custom: Place knot near known threshold (e.g., guideline cutpoint)

---

## 5. Interpreting Results

### Coverage Probability

**Target:** 95% (for α=0.05)

| Coverage | Interpretation | Action |
|----------|----------------|--------|
| < 85% | Severe undercoverage | ⚠️ Method not valid, use HKSJ |
| 85-92% | Moderate undercoverage | Consider HKSJ or more conservative method |
| 92-96% | Good coverage | ✅ Method valid |
| 96-99% | Slight overcoverage | Acceptable (conservative CIs) |
| > 99% | Severe overcoverage | CIs too wide, check for issues |

### Heterogeneity

**I² Thresholds:**
- I² < 25%: Low heterogeneity (consider fixed-effects)
- I² = 25-50%: Moderate heterogeneity (random-effects)
- I² = 50-75%: Substantial heterogeneity (investigate sources)
- I² > 75%: High heterogeneity (subgroup analysis, meta-regression)

**Note:** Always report I², τ², and Q-test p-value

### Model Fit

**For RCS:**
1. Test for non-linearity: `model.test_non_linearity()`
   - p < 0.05: Non-linear relationship (RCS appropriate)
   - p ≥ 0.05: Linear sufficient (consider FP1)

2. Visual inspection: Does curve fit make clinical sense?

3. AIC comparison (if testing multiple knot numbers):
   - ΔAIC < 2: Models equivalent, choose simpler
   - ΔAIC 2-6: Weak support for lower AIC
   - ΔAIC > 6: Strong support for lower AIC

---

## 6. Practical Examples

### Example 1: Alcohol and Cancer Risk

**Scenario:**
- k = 18 studies
- Expected: J-shaped curve (protective at low, harmful at high)
- Moderate heterogeneity expected (I² ≈ 40%)

**Decision:**
```
Goal: Inference for public health guidelines
  → Two-Stage DL + HKSJ
Curve: J-shaped
  → RCS with 4-5 knots
Sample size: k=18 (small-moderate)
  → HKSJ correction essential
```

**Implementation:**
```python
model = TwoStageDoseResponse(
    model_type='rcs',
    n_knots=5,  # J-shape may need 5 knots
    pooling_method='random'
)
model.fit(doses, log_rr, variances)
pred, lower, upper = model.predict(dose_grid, use_hksj=True)

# Test for non-linearity
p_nonlin = model.test_non_linearity()
if p_nonlin < 0.05:
    print("Significant non-linear relationship")
```

---

### Example 2: Drug Dose and Efficacy

**Scenario:**
- k = 8 studies (small meta-analysis)
- Expected: Plateau effect (diminishing returns)
- Low heterogeneity (similar trials)

**Decision:**
```
Goal: Optimal dose recommendation
  → Two-Stage DL + HKSJ (inference)
Curve: Plateau (possibly log or power)
  → Try FP first, then RCS if needed
Sample size: k=8 (small!)
  → HKSJ absolutely necessary
  → Start with 3 knots if using RCS
Heterogeneity: Low
  → DL still recommended (protective)
```

**Implementation:**
```python
# Try FP first
fp_model = TwoStageDoseResponse(model_type='fp', fp_powers=[0.5])
fp_model.fit(doses, log_rr, variances)
aic_fp = fp_model.aic

# Compare to RCS
rcs_model = TwoStageDoseResponse(model_type='rcs', n_knots=3)
rcs_model.fit(doses, log_rr, variances)
aic_rcs = rcs_model.aic

if aic_fp < aic_rcs + 2:
    final_model = fp_model  # Simpler model preferred
else:
    final_model = rcs_model
```

---

### Example 3: Vitamin Supplementation (U-shaped)

**Scenario:**
- k = 25 studies
- Expected: U-shaped (harm at both low and high doses)
- High heterogeneity (different populations)

**Decision:**
```
Goal: Identify safe range
  → Two-Stage DL (k=25, HKSJ optional but not critical)
Curve: U-shaped (complex)
  → RCS with 5 knots (capture minimum)
Sample size: k=25 (adequate)
  → Normal distribution adequate
Heterogeneity: High
  → Investigate with meta-regression or subgroups
```

**Implementation:**
```python
model = TwoStageDoseResponse(
    model_type='rcs',
    n_knots=5,
    pooling_method='random'
)
model.fit(doses, log_rr, variances)

# Find minimum (safe dose)
dose_grid = np.linspace(min_dose, max_dose, 1000)
predictions, _, _ = model.predict(dose_grid, use_hksj=False)  # k=25, HKSJ not needed
safe_dose = dose_grid[np.argmin(predictions)]

print(f"Minimum risk at dose: {safe_dose:.1f}")

# Report heterogeneity
print(f"I²: {model.heterogeneity_stats['I2']:.1f}%")
print(f"τ²: {model.heterogeneity_stats['tau2']:.4f}")
```

---

## 7. Common Pitfalls and Solutions

### Pitfall 1: Using Normal Distribution for k < 20

**Problem:** Undercoverage (coverage 60-85%)

**Solution:** Always use HKSJ correction for k < 20
```python
# WRONG:
pred, lower, upper = model.predict(doses, use_hksj=False)

# CORRECT:
pred, lower, upper = model.predict(doses, use_hksj=True)
```

---

### Pitfall 2: Too Many Knots for Sample Size

**Problem:** Overfitting, unstable estimates, poor convergence

**Solution:** Follow rule: n_knots ≤ k/3

| k | Max knots |
|---|-----------|
| 6-8 | 3 |
| 9-14 | 4 |
| 15-20 | 5 |
| 21+ | 7 |

---

### Pitfall 3: Ignoring Heterogeneity

**Problem:** Using fixed-effects when I² > 25% → undercoverage

**Solution:**
1. Always test heterogeneity
2. Report I² and τ²
3. Use random-effects if I² > 25%
4. Investigate sources if I² > 50%

```python
# Check heterogeneity
stats = model.heterogeneity_stats
print(f"Q = {stats['Q']:.2f}, p = {stats['Q_p']:.4f}")
print(f"I² = {stats['I2']:.1f}%")

if stats['I2'] > 25:
    print("Use random-effects (DL) pooling")
```

---

### Pitfall 4: Not Validating Model Fit

**Problem:** Accepting poor-fitting model

**Solution:**
1. Visual inspection of fitted curve
2. Test for non-linearity
3. Check residuals
4. Compare AIC across models

```python
# Test non-linearity
p_nl = model.test_non_linearity()
if p_nl > 0.05:
    print("⚠️ Linear model may be sufficient")

# Visual check
model.plot_fit()  # Inspect visually
```

---

## 8. Software Recommendations

**Our Platform (Python):**
```python
from dose_response_meta import TwoStageDoseResponse, OneStageDoseResponse

# Recommended for most cases:
model = TwoStageDoseResponse(
    model_type='rcs',
    n_knots=4,
    pooling_method='random'
)
model.fit(doses, log_rr, variances)
pred, lower, upper = model.predict(dose_grid, use_hksj=True)
```

**R Alternatives:**
- `dosresmeta` package (Crippa & Orsini): Gold standard, similar to our two-stage
- `mvmeta` package (Gasparrini): Multivariate meta-analysis
- `metafor` package: General meta-analysis framework

**Validation:**
Our implementation has been validated against R `rms` package for RCS basis calculation (max difference < 1e-6).

---

## 9. Reporting Checklist

When reporting dose-response meta-analysis results, include:

**Methods:**
- [ ] Number of studies (k) and total participants
- [ ] Dose-response model (RCS, FP1, FP2)
- [ ] Number of knots (if RCS) and placement method
- [ ] Pooling method (fixed-effects, DL, REML)
- [ ] Small-sample correction (HKSJ) if applicable
- [ ] Software and version

**Results:**
- [ ] Heterogeneity statistics (I², τ², Q-test p-value)
- [ ] Test for non-linearity (p-value)
- [ ] Pooled dose-response curve with 95% CI
- [ ] Reference dose clearly stated
- [ ] Convergence rate (if relevant)

**Visualization:**
- [ ] Dose-response curve plot
- [ ] Individual study estimates (if feasible)
- [ ] 95% confidence band
- [ ] Clinical interpretation of findings

---

## 10. Summary Recommendations

### Default Method (Most Situations):
```
Two-Stage RCS (4 knots) + DerSimonian-Laird + HKSJ
```

**Why:**
- Valid inference (coverage 90-98%)
- Robust across scenarios
- Transparent and interpretable
- Fast and reliable

### When to Deviate:

| Situation | Use Instead |
|-----------|-------------|
| k < 8 | RCS with 3 knots or FP2 |
| k ≥ 20 | HKSJ optional (use normal dist) |
| I² < 25% | Consider fixed-effects (test first) |
| Simple curve | Fractional polynomials (FP1/FP2) |
| Prediction goal | One-stage REML |
| Complex U/J curve | 5 knots instead of 4 |

---

## References

1. **Jackson D, White IR, Thompson SG.** Extending DerSimonian and Laird's methodology to perform multivariate random effects meta-analyses. *Stat Med*. 2010;29(12):1282-97.

2. **IntHout J, Ioannidis JPA, Borm GF.** The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. *BMJ*. 2014;349:g5219.

3. **Harrell FE Jr.** *Regression Modeling Strategies*. Springer; 2001.

4. **Crippa A, Orsini N.** Multivariate dose-response meta-analysis: the dosresmeta R package. *J Stat Softw*. 2016;72(1):1-15.

5. **Royston P, Altman DG.** Regression using fractional polynomials of continuous covariates: parsimonious parametric modelling. *Appl Stat*. 1994;43(3):429-467.

---

**Document Version:** 1.0
**Last Updated:** November 2024
**Contact:** [Project Repository]
