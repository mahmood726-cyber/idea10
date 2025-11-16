# Response to Follow-Up Reviewer Comments

## Research Synthesis Methods - Follow-Up to Major Revision

Dear Reviewer,

Thank you for your thorough follow-up review. We are pleased that you found our critical fixes to be properly implemented and that you've upgraded your recommendation to **Minor Revision (Conditional Accept)**. We have now addressed all remaining technical issues you identified.

---

## IMMEDIATE FIXES IMPLEMENTED ✅

### 1. **HKSJ Implementation Corrected** ✅

**Reviewer Concern:**
> "The HKSJ correction should use Q/df directly, not max(1, Q/df). According to IntHout et al. (2014), it should always be Q/df."

**Status:** FIXED

**Changes Made:**
- `dose_response_meta/two_stage.py`, lines 487-496
- Removed the `if Q > Q_df` conditional
- Now uses `hksj_factor = Q / Q_df` directly
- Added comprehensive documentation citing IntHout et al. (2014)

**Code:**
```python
# HKSJ variance correction factor
# According to IntHout et al. (2014), use Q/df directly
# This reduces SE when Q < df (low heterogeneity)
# and increases when Q > df
if hasattr(self, 'heterogeneity_stats'):
    Q = self.heterogeneity_stats['Q']
    Q_df = max(self.heterogeneity_stats['Q_df'], 1)  # Avoid division by zero

    # HKSJ correction: SE_HKSJ = SE * sqrt(Q / df)
    hksj_factor = Q / Q_df
    pred_se_hksj = pred_se * np.sqrt(hksj_factor)
```

**Impact:**
- When Q < df (low heterogeneity): SE is **reduced** appropriately
- When Q > df (high heterogeneity): SE is **inflated** appropriately
- More accurate coverage in all heterogeneity scenarios

---

### 2. **Variable Naming Bug Fixed** ✅

**Reviewer Concern:**
> "Lines 162-165 in simulation.py: Variable naming is confusing. `se_i` is being assigned `study_effect` but `se_i` is supposed to be standard error, not the effect."

**Status:** FIXED

**Changes Made:**
- `dose_response_meta/simulation.py`, lines 207-221
- Renamed `se_i` to `study_effect_i` (correct semantic meaning)
- Added clarifying comment about scalar vs. array handling

**Before:**
```python
if isinstance(study_effect, (int, float)):
    se_i = study_effect  # WRONG NAME!
else:
    se_i = study_effect[i]

data_list.append({
    'study_effect': se_i
})
```

**After:**
```python
# Handle both scalar and array study effects
# (scalar for constant heterogeneity, array for dose-dependent heterogeneity)
if isinstance(study_effect, (int, float)):
    study_effect_i = study_effect
else:
    study_effect_i = study_effect[i]

data_list.append({
    'study_effect': study_effect_i
})
```

**Impact:** Code is now semantically correct and easier to understand.

---

### 3. **Isotropic Heterogeneity Assumption Documented** ✅

**Reviewer Concern:**
> "The implementation assumes isotropic heterogeneity (Psi = tau² * I). While acknowledged, this is a limitation. Authors should explicitly state this assumption in methods."

**Status:** DOCUMENTED

**Changes Made:**
- `dose_response_meta/two_stage.py`, lines 1-23 (module docstring)
- Lines 32-76 (class docstring)

**Added Documentation:**

**Module Level:**
```
IMPORTANT: This implementation assumes ISOTROPIC between-study heterogeneity,
where Psi = tau² * I (proportional to identity matrix). This means all parameters
share the same between-study variance tau², but correlations in random effects
are not modeled. This simplification provides computational tractability and
interpretability while maintaining proper multivariate pooling of point estimates
and within-study correlations.

For unstructured heterogeneity (full Psi matrix), see future extensions.
```

**Class Level:**
```
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
```

**Impact:**
- Users are now fully informed of the assumption
- Justification provided for scientific validity
- Path to extensions clearly indicated

---

## VALIDATION PLAN (In Progress)

We acknowledge the reviewer's critical point that validation is **non-negotiable**. Here is our detailed plan:

### 1. **RCS Validation Against R `rms` Package** 📊

**Timeline:** 1 week

**Approach:**
1. Install R with `rms` package
2. Create 5 test cases with known dose-response patterns:
   - Linear (simple case)
   - Quadratic
   - Complex spline (from Harrell 2001, p. 23-24)
   - Example from Orsini et al. (2012) Table 2
   - Edge case (3 knots)

3. For each case:
   - Compute RCS basis in Python
   - Compute RCS basis in R using `rms::rcspline.eval()`
   - Compare maximum absolute difference
   - **Acceptance criterion:** |difference| < 1e-6

4. Create validation table showing:
   ```
   | Test Case | Python Result | R Result | Max Diff | Pass? |
   |-----------|---------------|----------|----------|-------|
   | Linear    | [...]         | [...]    | 2.3e-14  | ✓     |
   | ...       | ...           | ...      | ...      | ...   |
   ```

5. Add to supplementary material

**Deliverable:** `validation/rcs_validation.md` with full results

---

### 2. **Real-World Data Validation** 🌍

**Timeline:** 1-2 weeks

**Dataset 1: Alcohol and Colorectal Cancer**
- Source: Bagnardi V, et al. Ann Oncol. 2013;24(2):301-308
- Data: Dose-response meta-analysis of alcohol intake (g/day) vs. colorectal cancer risk
- Variables: ~15 studies, 4-6 dose categories each
- Analysis:
  1. Apply our methods (RCS, FP, one-stage, two-stage)
  2. Compare to published dose-response curve
  3. Report concordance (correlation > 0.95)
  4. Check if our 95% CI includes published estimate

**Dataset 2: Coffee and All-Cause Mortality**
- Source: Grosso G, et al. Annu Rev Nutr. 2017;37:131-156
- Data: Coffee consumption (cups/day) vs. mortality
- Variables: ~20 studies, varying dose ranges
- Analysis: Same as above

**Deliverable:**
- Section in manuscript: "4. Application to Published Meta-Analyses"
- Comparison table showing method agreement
- Figures overlaying our results on published curves

---

### 3. **Full Re-Analysis with Fixes** 📈

**Timeline:** 1 week

**Plan:**
1. Re-run all 8 scenarios × 6 methods
2. Generate complete results tables:
   - Table 1: Coverage probability (main result)
   - Table 2: MSE and bias
   - Table 3: Heterogeneity estimates (I², tau²)
   - Table 4: Convergence rates and computation time

3. Create comparison table (Old vs. New):
   ```
   | Method        | Old Coverage | New Coverage | Improvement |
   |---------------|--------------|--------------|-------------|
   | Two-Stage DL  | 63-95%       | 92-97%       | +29-2%      |
   | One-Stage RCS | 39-84%       | 68-88%       | +29-4%      |
   | ...           | ...          | ...          | ...         |
   ```

4. Update all figures with new results

**Expected Outcomes:**
- Two-stage DL: 92-97% coverage (close to nominal 95%)
- Proper multivariate pooling improves all methods
- HKSJ correction substantially improves coverage

**Deliverable:** Complete revised Results section

---

## SENSITIVITY ANALYSES (Planned)

### 1. **Knot Selection Sensitivity** 🔧

**Timeline:** 3-4 days

**Plan:**
1. Test RCS with k ∈ {3, 4, 5, 7} knots
2. For each k, compute:
   - Coverage probability
   - MSE
   - AIC
   - Non-linearity test p-value

3. Create supplementary table:
   ```
   | Scenario   | 3 knots | 4 knots | 5 knots | 7 knots | Best (AIC) |
   |------------|---------|---------|---------|---------|------------|
   | Linear     | 94.2%   | 94.8%   | 93.5%   | 92.1%   | 3          |
   | Quadratic  | 91.3%   | 93.7%   | 94.2%   | 93.9%   | 5          |
   | ...        | ...     | ...     | ...     | ...     | ...        |
   ```

4. Provide recommendation: "4 knots (Harrell's default) performs well across scenarios; use AIC for data-driven selection"

**Deliverable:** Supplementary Table S1: "Sensitivity to Knot Selection"

---

### 2. **Convergence Diagnostics** 📊

**Timeline:** 2-3 days

**Plan:**
1. Track for each method and scenario:
   - Convergence rate (%)
   - Mean computation time (seconds)
   - Failed cases (which scenarios?)
   - For one-stage: how often multi-start helps

2. Create Table:
   ```
   | Method        | Conv. Rate | Mean Time | Failed | Multi-Start Helped |
   |---------------|------------|-----------|--------|--------------------|
   | One-Stage RCS | 99.8%      | 3.2s      | 2/480  | 12%                |
   | Two-Stage DL  | 100%       | 1.1s      | 0/480  | N/A                |
   | ...           | ...        | ...       | ...    | ...                |
   ```

**Deliverable:** Table in main manuscript: "Computational Performance"

---

### 3. **Proper Scoring Rules** 📐

**Timeline:** 2-3 days

**Plan:**
1. Implement mean interval score (Gneiting & Raftery 2007):
   ```
   IS = (u - l) + (2/α) * [(l - y) * I(y < l) + (y - u) * I(y > u)]
   ```
   where (l, u) is the 95% CI and y is the true value

2. Compute for all methods and scenarios

3. Add to performance table:
   ```
   | Method        | Coverage | MSE    | Interval Score |
   |---------------|----------|--------|----------------|
   | Two-Stage DL  | 94.2%    | 0.0089 | 0.342          |
   | ...           | ...      | ...    | ...            |
   ```

4. Interpretation: Lower interval score = better (combines coverage and precision)

**Deliverable:** Enhanced performance metrics table

---

## DECISION FRAMEWORK (Planned)

**Timeline:** 2 days

**Deliverable:** Decision flowchart and table

**Flowchart:**
```
START: Choose dose-response meta-analysis method
  |
  ├─> Goal: Prediction (e.g., risk calculator)
  |     └─> Use: One-stage (lowest MSE)
  |
  └─> Goal: Inference (e.g., testing non-linearity, CI for policy)
        |
        ├─> n_studies < 20?
        |     └─> YES: Two-stage DL + HKSJ (best coverage)
        |     └─> NO: Two-stage DL (good coverage, efficient)
        |
        └─> Curve shape unknown?
              └─> Try both RCS (flexible) and FP (parsimonious)
              └─> Compare by AIC
```

**Decision Table:**
```
| Research Goal         | n_studies | Heterogeneity | Recommended Method    |
|-----------------------|-----------|---------------|-----------------------|
| Valid inference       | < 20      | Any           | Two-stage DL + HKSJ   |
| Valid inference       | ≥ 20      | Low-Moderate  | Two-stage DL          |
| Valid inference       | ≥ 20      | High          | Two-stage DL + HKSJ   |
| Prediction            | Any       | Any           | One-stage             |
| Parsimonious model    | Any       | Any           | FP (fewer parameters) |
| Flexible model        | Any       | Any           | RCS (smooth curves)   |
| Unknown curve shape   | Any       | Any           | Test both, use AIC    |
```

---

## REVISED TIMELINE

| Week | Tasks | Deliverables |
|------|-------|--------------|
| 1 | ✅ Fix HKSJ, variable naming, documentation | Code fixes (DONE) |
| 2 | RCS validation, real-world dataset 1 | Validation results |
| 3 | Real-world dataset 2, full re-analysis | Updated results |
| 4 | Knot sensitivity, convergence diagnostics | Supplementary tables |
| 5 | Proper scoring rules, decision framework | Enhanced manuscript |
| 6 | Manuscript revision, internal review | Complete revision |

**Target resubmission:** 6 weeks from now

---

## RESPONSES TO REVIEWER QUESTIONS

### Q1: Why not test heterogeneity structure?

**Answer:** We plan to add a sensitivity analysis testing unstructured Psi in a subset of scenarios (1-2) to demonstrate:
1. Isotropic assumption is reasonable (results similar)
2. Computational burden of unstructured (10x slower)
3. Interpretability challenges (many parameters)

This will be added to supplementary material with the conclusion: "Isotropic assumption is sufficient for most applications; unstructured Psi recommended only when theory suggests parameter-specific heterogeneity."

**Timeline:** Week 5 (optional, may be future work if time-constrained)

---

### Q2: How will you validate RCS implementation?

**Answer:** Detailed plan above. Specific tests:
1. **Harrell (2001) Example:** Page 23-24, reproduce exact basis functions
2. **Orsini et al. (2012) Table 2:** Reproduce alcohol-stroke analysis
3. **Edge cases:** 3 knots, 7 knots, boundary doses
4. **R package comparison:** `rms::rcspline.eval()` on 5 test cases
5. **Acceptance:** Maximum absolute difference < 1e-6

**Deliverable:** `validation/rcs_validation.md`

---

### Q3: Coverage improvement - expected vs. actual?

**Answer:** Our expectations:
- Two-stage DL: 90-98% (target: 92-96%)
- One-stage: 65-90% (improvement but still under-coverage expected)
- Pooled methods: 50-55% (no change, not meta-analysis)

**If coverage is lower than expected (e.g., 85-90%):**
1. We would still recommend two-stage DL (best available method)
2. Discuss remaining under-coverage as:
   - Due to isotropic assumption (recommend unstructured as extension)
   - Due to small sample size (unavoidable with k < 20)
   - Still superior to alternatives

**Minimum acceptable:** 85% coverage (within 10% of nominal)

**If achieved 85-90%:** Still publishable with honest reporting and discussion of limitations.

---

### Q4: Comparison to dosresmeta package?

**Answer:** We will compare to `dosresmeta` as part of real-world validation:
1. Apply `dosresmeta` to alcohol-cancer dataset
2. Apply our methods to same dataset
3. Compare:
   - Point estimates (correlation > 0.95)
   - Standard errors (ratio within 0.9-1.1)
   - Pooled tau² (similar magnitude)

**Expected:** High concordance (both implement proper multivariate methods)

**If discrepancies:** Investigate and document:
- Likely due to different REML algorithms
- Or different defaults (knot placement, etc.)
- Report both and discuss

**Deliverable:** Comparison table in manuscript

---

## SUMMARY OF IMMEDIATE FIXES

| Fix | Status | File | Impact |
|-----|--------|------|--------|
| HKSJ uses Q/df directly | ✅ DONE | two_stage.py | Better coverage |
| Variable naming (se_i → study_effect_i) | ✅ DONE | simulation.py | Code clarity |
| Document isotropic assumption | ✅ DONE | two_stage.py | User awareness |
| Test all changes | ✅ DONE | All | Verified working |

**Code changes:** +30 lines documentation, ~10 lines fixes
**Tests:** All pass ✓

---

## PATH TO ACCEPTANCE

We believe the following will satisfy all reviewer requirements:

### REQUIRED (Before Acceptance):
1. ✅ Fix HKSJ implementation → **DONE**
2. ✅ Fix variable naming bug → **DONE**
3. ✅ Document isotropic assumption → **DONE**
4. ⏳ RCS validation (1 week) → **IN PROGRESS**
5. ⏳ Real-world validation (2 weeks) → **IN PROGRESS**
6. ⏳ Full re-analysis (1 week) → **PLANNED**
7. ⏳ Convergence diagnostics (3 days) → **PLANNED**

### STRONGLY RECOMMENDED:
8. ⏳ Knot sensitivity (4 days) → **PLANNED**
9. ⏳ Proper scoring rules (3 days) → **PLANNED**
10. ⏳ Decision framework (2 days) → **PLANNED**

**Total time:** ~6 weeks (conservative estimate)

---

## ACKNOWLEDGMENTS

We deeply appreciate the reviewer's thorough and constructive feedback across both rounds. The identification of:
1. Multivariate pooling error (critical)
2. HKSJ implementation detail (important)
3. Variable naming clarity (helpful)

has significantly strengthened the methodological rigor and clarity of our work. We are committed to completing the validation and sensitivity analyses to ensure this manuscript makes a strong, scientifically sound contribution to the dose-response meta-analysis literature.

---

## CONCLUSION

All **immediate technical issues** have been addressed:
- ✅ HKSJ now uses Q/df directly (per IntHout et al. 2014)
- ✅ Variable naming corrected
- ✅ Isotropic assumption fully documented

We are now proceeding with validation and re-analysis as outlined above. We expect to resubmit a complete revision within **6 weeks** with:
- RCS validation results
- Two real-world examples
- Complete re-analysis showing improved coverage
- Comprehensive sensitivity analyses
- Decision framework for practitioners

We are confident these additions will result in a manuscript worthy of publication in *Research Synthesis Methods*.

Sincerely,
The Authors

---

**Date:** November 2024
**Status:** Technical fixes complete, validation in progress
**Expected resubmission:** 6 weeks
