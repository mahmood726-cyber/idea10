# RESEARCH SYNTHESIS METHODS - EDITORIAL REVIEW
## Manuscript: "Comparative Performance of Dose-Response Meta-Analysis Methods: A Simulation Study"

**Journal:** Research Synthesis Methods
**Manuscript ID:** RSM-2025-XXXX
**Date:** November 16, 2025
**Handling Editor:** [Editor Name]
**Recommendation:** **MAJOR REVISION** (Conditional Accept Pending Technical Clarifications)

---

## OVERALL ASSESSMENT

This is a **methodologically rigorous and timely** simulation study addressing a critical gap in dose-response meta-analysis methodology. The application of HKSJ correction to multivariate dose-response settings represents an important methodological contribution. The comprehensive sample size sensitivity analysis (k=8-30) and real-world validation strengthen the practical utility. However, **several technical clarifications and methodological concerns must be addressed** before acceptance.

**Rating:** ⭐⭐⭐⭐☆ (4/5) - Very Good, pending revisions

**Suitability for RSM:** ✅ Excellent fit (meta-analysis methodology, simulation study, practical guidance)

---

## DECISION SUMMARY

### **ACCEPT** subject to satisfactory responses to:
1. **Critical Issue:** Scenario 7 specification incomplete
2. **Major Issue:** Within-study correlation structure not fully specified
3. **Major Issue:** FP implementation unclear (methods vs. results disconnect)
4. **Methodological Concern:** Isotropic heterogeneity assumption may be too restrictive
5. **Transparency Issue:** Simulation parameters incomplete for reproducibility

### **STRENGTHS (Why this deserves publication in RSM):**
- ✅ Novel application of HKSJ to multivariate dose-response meta-analysis
- ✅ Comprehensive simulation design (1,450 meta-analyses)
- ✅ Sample size sensitivity analysis addresses practical questions (k=8-30)
- ✅ Real-world validation (Bagnardi et al. 2015 re-analysis)
- ✅ Proper scoring rules (rarely used in meta-analysis simulations)
- ✅ Modified HKSJ prevents anti-conservatism
- ✅ Clear, actionable decision framework

### **CONCERNS (Must address before acceptance):**
- ⚠️ Scenario 7 functional form not specified
- ⚠️ Within-study correlation reconstruction method unclear
- ⚠️ FP methods described but results not reported
- ⚠️ Isotropic heterogeneity assumption potentially too restrictive
- ⚠️ Missing simulation details for full reproducibility
- ⚠️ No sensitivity to correlation misspecification

---

## DETAILED METHODOLOGICAL REVIEW

### **SECTION 1: SIMULATION DESIGN**

#### ✅ **STRENGTHS**

**1. Scenario Selection (Lines 66-92):** Excellent coverage of realistic dose-response patterns
- Linear through complex non-linear ✓
- Dose-dependent heterogeneity (Scenario 8) is particularly valuable ✓
- Practical examples aid interpretation ✓

**2. Sample Size Sensitivity (Section 3.6):** Outstanding contribution
- k ∈ {8, 10, 12, 15, 20, 25, 30} covers practical range ✓
- 1,050 additional meta-analyses is comprehensive ✓
- Addresses key question: "When does HKSJ benefit diminish?" ✓

**3. Number of Simulations (n=50):** Adequate for coverage estimation
- Monte Carlo SE ≈ 3% for 95% coverage probability ✓
- Acceptable for comparative study ✓

#### ❌ **CRITICAL ISSUE 1: Scenario 7 Specification Incomplete**

**Line 86-87:**
> "**Complex non-linear, moderate heterogeneity** (τ²=0.05): Combination of cubic and exponential terms"

**Problem:** No functional form provided. This is insufficient for reproducibility.

**What's needed:**
```
Scenario 7: f(x) = β₀ + β₁x + β₂x² + β₃x³ + β₄exp(-x/25)
```
Or similar explicit specification.

**Impact:** **Cannot reproduce this scenario** without functional form.

**Required Action:** Provide explicit functional form in Methods or move to Supplementary if not central.

---

#### ⚠️ **MAJOR ISSUE 1: Within-Study Correlation Structure**

**Lines 98-105:** Data generation details are good, but **critical information missing:**

**What's specified:**
- k=15 studies ✓
- 4 dose levels per study ✓
- Dose range 0-100 ✓
- Between-study heterogeneity ✓
- Within-study error ✓

**What's MISSING:**
1. **How are within-study correlations generated?**
   - Are the 4 dose observations per study correlated?
   - What correlation structure? (compound symmetry, AR(1), unstructured?)
   - What magnitude of correlation?

2. **Greenland-Longnecker covariance reconstruction:**
   - Methods section mentions "covariance reconstruction" (line 285)
   - But simulation doesn't explain if/how this is used
   - Need clarification: Are you simulating from known correlations or reconstructing them?

**Why this matters for RSM readers:**
- Within-study correlation is **critical** in dose-response meta-analysis
- Misspecification can affect coverage probability
- Readers need to understand what you're simulating

**Required Action:**
Add to Section 2.1.2:
```
Within-study correlation structure:
- Observations within study i were generated with correlation ρ=0.X
- Covariance structure: [specify: compound symmetry, AR(1), etc.]
- In two-stage analysis, correlations were reconstructed using
  Greenland-Longnecker method [1] assuming [specify assumptions]
```

---

#### ⚠️ **MAJOR ISSUE 2: Fractional Polynomials Results Missing**

**Methods (Lines 132-143):** FP2 models described in detail
- Power selection from {-2, -1, -0.5, 0, 0.5, 1, 2, 3} ✓
- AIC-based selection ✓
- Clear description ✓

**Results:** **FP results completely absent**
- Tables 2-4: Only show RCS results
- No FP vs. RCS comparison
- Abstract mentions "fractional polynomials" but no FP results reported

**Possible explanations:**
1. FP convergence issues? (Should report this)
2. FP results identical to RCS? (Should state this)
3. FP analysis planned but not completed? (Should remove from abstract/methods)

**Impact:** Methods-Results disconnect confuses readers

**Required Action:**
1. **Option A:** Report FP results in Supplementary Materials
2. **Option B:** Remove FP from abstract/methods if not analyzed
3. **Option C:** Add brief statement: "FP results were similar to RCS (see Supplementary Table SX)"

**Recommendation:** At minimum, report FP coverage in Supplementary Materials for completeness

---

### **SECTION 2: STATISTICAL METHODOLOGY**

#### ✅ **STRENGTHS**

**1. HKSJ Implementation (Lines 180-197):** Excellent technical detail
- Variance inflation formula correct ✓
- t-distribution with df=k-p specified ✓
- Modified HKSJ (max(1, √Q/df)) prevents anti-conservatism ✓
- **This is novel and valuable** ✓

**2. HKSJ for Predictions (Lines 201-211):** Outstanding clarification
- Mathematical justification clear ✓
- Addresses potential reviewer concern proactively ✓
- Empirical validation (97.5-99.8% coverage) strengthens argument ✓

**3. Isotropic Heterogeneity (Line 199):** Transparent assumption
- Ψ = τ²I clearly stated ✓
- Computational tractability rationale ✓
- Tested robustness (Scenario 8 with 500-fold variation) ✓

#### ⚠️ **METHODOLOGICAL CONCERN: Isotropic Heterogeneity May Be Too Restrictive**

**Current Approach (Line 199):**
> "We assume isotropic between-study heterogeneity (Ψ = τ²I)"

**Testing (Section 4.5, Lines 641-654):**
- Scenario 8 tests **anisotropic heterogeneity** (τ² varies by dose)
- HKSJ robust: 99.5% coverage despite 500-fold variation ✓

**Concern for RSM readers:**

While Scenario 8 tests τ²(dose), the **isotropic assumption applies to covariance structure**:
```
Ψ = τ²I  (isotropic - all parameters have same variance)
```

vs.

```
Ψ = diag(τ₁², τ₂², ..., τₚ²)  (anisotropic variance)
```

or

```
Ψ = unstructured (different variances + correlations)
```

**Question:** Does the isotropic assumption (equal variance for all spline coefficients) hold in practice?
- β₁ (linear term) may have different between-study variability than β₃ (cubic term)
- This is conceptually different from dose-dependent heterogeneity

**Impact:** May affect coverage if spline coefficients have heterogeneous variances

**Suggested Addition:**
```
Sensitivity Analysis: Anisotropic Between-Study Variance

We tested sensitivity to Ψ = τ²I by simulating scenarios where:
- Linear coefficient: τ₁² = 0.01
- Cubic coefficient: τ₃² = 0.10 (10× larger)

Results: HKSJ maintained 97.2% coverage vs. 99.5% under isotropic assumption.
Conclusion: Isotropic assumption appears robust for inference.
```

**Required Action:** Add brief discussion or supplementary analysis testing anisotropic **parameter** variance (not just dose-dependent heterogeneity)

---

#### 🔬 **TECHNICAL QUESTION: DerSimonian-Laird in Multivariate Setting**

**Lines 166-172:** DL τ² estimation

**Standard DL (univariate):**
```
τ² = (Q - (k-1)) / C
```

**Your implementation (multivariate):**
```
Q = Σ (β̂ᵢ - β̂_FE)' Vᵢ⁻¹ (β̂ᵢ - β̂_FE)
τ² = max(0, (Q - df) / C)
```

**Question:** How is df calculated in multivariate setting?
- df = k - p (total parameters)?
- df = k - 1 (studies minus 1)?
- df accounts for multivariate structure?

**Also:** What is C in multivariate setting?
- Line 172: `C = tr(Σ Wᵢ) - tr(Σ WᵢW⁻¹Wᵢ)`
- This needs clearer explanation or citation to Jackson et al. [6]

**Suggestion:** Add explicit formula or clearer reference:
```
DL estimation followed Jackson et al. [6, eq. 7] for multivariate meta-analysis:
- Q-statistic accounts for within-study correlations via V̂ᵢ
- df = k-1 (between-study degrees of freedom)
- C calculated as tr(Σ Wᵢ) - tr(Σ WᵢW⁻¹Wᵢ) where W = Σ Vᵢ⁻¹
```

---

### **SECTION 3: RESULTS EVALUATION**

#### ✅ **EXCELLENT FEATURES**

**1. Proper Scoring Rules (Section 3.4, Lines 425-466):** Rarely seen in meta-analysis!
- Interval score decomposition into sharpness + calibration ✓
- Demonstrates one-stage methods have poor calibration despite low MSE ✓
- **This is a major strength of the paper** ✓

**2. Sample Size Sensitivity (Section 3.6):** Outstanding
- Clear table showing coverage by k ✓
- Demonstrates HKSJ benefit persists to k=30 ✓
- Practical utility excellent ✓

**3. Real-World Validation (Section 3.7):** Strong empirical support
- Bagnardi et al. (2015) re-analysis ✓
- Modified HKSJ application ✓
- Modest widening (1.15×) with I²=0% demonstrates principle ✓

#### ⚠️ **CONCERN: Coverage "Overcoverage" Interpretation**

**Lines 304-316, 336-348:** HKSJ achieves 98-100% coverage

**Results state:**
> "Slight overcoverage (98% vs. 95%) is conservative but acceptable"

**For RSM:**
This is **correct** but needs **statistical nuance**:

1. **Monte Carlo SE:** With n=50 simulations, SE ≈ 3%
   - 98% coverage has 95% CI: [92%, 100%]
   - Includes nominal 95%
   - **Not statistically significantly different from 95%**

2. **T-distribution expectation:** HKSJ uses t-distribution
   - With df=k-p and k=15, p=3: df=12
   - t-distribution should produce **slight** overcoverage with true normal data
   - This is **expected behavior**, not a bug

**Suggestion:** Add statistical interpretation:
```
The observed 98% coverage (vs. nominal 95%) is:
(a) Within Monte Carlo error (95% CI: 92-100%)
(b) Consistent with t-distribution behavior (df=12)
(c) Preferable to undercoverage for inference
```

---

### **SECTION 4: REPRODUCIBILITY ASSESSMENT**

#### ✅ **GOOD:**
- Clear scenario specifications (mostly) ✓
- Sample sizes stated ✓
- Number of simulations stated ✓
- Software versions (Python 3.9, NumPy 1.21, SciPy 1.7) ✓
- Code availability statement ✓

#### ❌ **MISSING for Full Reproducibility:**

1. **Random seeds:** Not mentioned
   - Need for exact reproduction

2. **Dose allocation within studies:**
   - Are doses random? Fixed percentiles? Uniform?
   - Critical for spline knot placement

3. **Knot placement algorithm:**
   - Line 106: "knots at percentiles [5%, 35%, 65%, 95%]"
   - Percentiles of what? Overall dose range? Study-specific data?

4. **Optimization details:**
   - One-stage: "Multi-start L-BFGS-B with 5 initial values" (Line 206)
   - What are the 5 initial values?
   - Convergence tolerance?

5. **Modified HKSJ implementation:**
   - When is Q < df in practice?
   - How often was the modification triggered?
   - Should report in Results

**Required Action:** Add to Supplementary Materials:
```
Reproducibility Checklist:
- Random seed: 12345
- Dose allocation: [specify]
- Knot placement: [specify]
- Optimization: [full details]
- Modified HKSJ: Triggered in X% of simulations
```

---

### **SECTION 5: PRESENTATION QUALITY**

#### ✅ **EXCELLENT:**
- Abstract: Concise (229 words) ✓
- Figures: Well-referenced (S5, S6, S7) ✓
- Tables: Complete and clear ✓
- Decision framework: Practical and actionable ✓
- Writing: Clear technical prose ✓

#### ⚠️ **MINOR ISSUES:**

**1. Table 4 (Lines 443-466):** "Representative Scenarios" only
- Shows 2 scenarios (Linear, Logarithmic)
- What about the other 6 scenarios?
- **Suggestion:** Move full table to Supplementary, keep representative in main text

**2. Scenario ordering inconsistency:**
- Tables show 1-8
- Text sometimes refers by name (Linear, Quadratic)
- **Suggestion:** Always use "Scenario X (name)" for clarity

**3. Reference formatting:**
- Some citations missing page numbers
- Check journal requirements for RSM

---

## SPECIFIC TECHNICAL QUESTIONS

### **Q1: Why is one-stage coverage SO low (54.7%)?**

Lines 609-633 provide excellent explanation, but **one concern:**

**You attribute to 3 factors:**
1. τ² underestimation (10-30%)
2. Wrong critical values (z vs. t)
3. Imprecise correlations

**Question:** Have you decomposed the contribution of each?
- Run one-stage with **true** τ²: Does coverage improve?
- Run one-stage with **t-distribution**: Does coverage improve?

**This would strengthen the mechanistic explanation**

**Suggestion:** Add supplementary analysis:
```
Decomposition of One-Stage Undercoverage:

Scenario 3 (Logarithmic, I²=63%, one-stage coverage 46%):
1. True τ² known: Coverage 68% (Δ=22%)
2. + t-distribution: Coverage 82% (Δ=14%)
3. + known correlations: Coverage 94% (Δ=12%)

Conclusion: All three factors contribute approximately equally.
```

---

### **Q2: Isotropic assumption vs. dose-dependent heterogeneity**

**Scenario 8 tests:** τ²(dose) varies by dose (anisotropic over dose)

**But** you still assume: Ψ = τ²I (isotropic over parameters)

**Clarify:** Are these conceptually different?
- Dose-dependent heterogeneity: Between-study variance changes with dose
- Parameter heterogeneity: Linear vs. cubic coefficients have different τ²

**Suggestion:** Distinguish clearly or state assumption more precisely:
```
We assume:
1. Isotropic parameter variance: Var(β₁ᵢ) = Var(β₂ᵢ) = ... = τ²
2. But allow: τ² may vary by dose (Scenario 8 tests this)
```

---

### **Q3: Modified HKSJ - How often used?**

**Lines 189-197:** Modified HKSJ prevents anti-conservatism when Q < df

**Questions:**
1. In simulation: How often was Q < df?
2. In Bagnardi re-analysis: Was modification triggered? (I²=0%, so likely yes)
3. What happens to coverage if you DON'T use modification?

**Suggestion:** Report in Results:
```
Modified HKSJ (max(1, √Q/df)) was triggered in:
- Linear scenario: 12% of simulations
- High heterogeneity: 0% of simulations
- Bagnardi re-analysis: Yes (Q=7.2 < df=8)

Without modification: Coverage dropped to 93.2% (anticonservative)
With modification: Coverage maintained at 98.8%
```

---

## NOVEL CONTRIBUTIONS (Why RSM Should Publish)

### **1. HKSJ in Multivariate Dose-Response** ⭐⭐⭐⭐⭐
- **First comprehensive evaluation** of HKSJ in this setting
- Addresses known gap in dosresmeta package
- Practical utility: 52% of published meta-analyses may need re-analysis

### **2. Modified HKSJ** ⭐⭐⭐⭐☆
- max(1, √Q/df) prevents anti-conservatism
- Novel solution to known problem
- Validated in real-world application

### **3. Sample Size Sensitivity (k=8-30)** ⭐⭐⭐⭐⭐
- Answers practical question: "When can I stop using HKSJ?"
- Finding: Benefit persists even at k=30
- Challenges conventional k=20 threshold

### **4. Proper Scoring Rules in Meta-Analysis** ⭐⭐⭐⭐☆
- Rarely used in meta-analysis simulations
- Demonstrates precision-validity tradeoff elegantly
- Shows one-stage methods have poor calibration

### **5. Mechanistic Explanation of One-Stage Failure** ⭐⭐⭐⭐☆
- Three-factor decomposition valuable
- 54.7% coverage is alarming and well-explained
- Practical implications clear (52% of meta-analyses at risk)

---

## COMPARISON TO EXISTING LITERATURE

### **Advances Over Crippa & Orsini (2016):**
- ✅ HKSJ correction (not in dosresmeta)
- ✅ Coverage evaluation (not in original paper)
- ✅ Sample size sensitivity
- ✅ Proper scoring rules

### **Advances Over IntHout et al. (2014):**
- ✅ Extends HKSJ to multivariate dose-response
- ✅ Modified HKSJ for Q < df
- ✅ Demonstrates benefit persists at k=30

### **Advances Over Jackson et al. (2010):**
- ✅ Application to dose-response (not just multivariate MA)
- ✅ Small-sample corrections
- ✅ Comprehensive simulation evaluation

**Conclusion:** Sufficient novelty for RSM publication ✓

---

## PRACTICAL UTILITY FOR META-ANALYSTS

### **Decision Framework (Section 5):** ⭐⭐⭐⭐⭐

**Strengths:**
- Clear, actionable recommendations ✓
- Evidence-based thresholds ✓
- Accounts for heterogeneity ✓

**Example:**
```
k<20 + inference → HKSJ mandatory (3-7% benefit)
k=20-30 + I²>50% → HKSJ recommended (4-6% benefit)
```

**This alone justifies publication** - meta-analysts will use this

### **dosresmeta R Package Comparison (Lines 283-304):** Valuable

**Key finding:** dosresmeta lacks HKSJ correction

**Provides:**
- Algorithm correspondence table ✓
- Validation results ✓
- R function for applying HKSJ (mentioned, should be in Supplementary) ✓

**Suggestion:** Provide R code in Supplementary Materials for immediate application

---

## REQUIRED REVISIONS (Must Address)

### **CRITICAL (Must fix before acceptance):**

1. **Specify Scenario 7 functional form** (Lines 86-87)
   - Cannot reproduce without this
   - Provide explicit formula

2. **Clarify within-study correlation structure** (Section 2.1.2)
   - How generated in simulation?
   - How reconstructed in analysis?
   - Correlation magnitude?

3. **Address FP results absence** (Methods describe, Results omit)
   - Report FP results OR
   - Remove FP from abstract/methods OR
   - State why excluded

### **MAJOR (Strongly recommended):**

4. **Add anisotropic parameter variance sensitivity**
   - Test Ψ = diag(τ₁², ..., τₚ²) with unequal variances
   - Distinguish from dose-dependent heterogeneity

5. **Enhance reproducibility documentation**
   - Random seeds
   - Dose allocation algorithm
   - Knot placement details
   - Complete optimization settings

6. **Report modified HKSJ usage statistics**
   - How often Q < df?
   - Impact on coverage with/without modification

7. **Decompose one-stage undercoverage**
   - Contribution of each factor (τ² bias, wrong dist, correlation)
   - Strengthens mechanistic explanation

### **MINOR (Recommended):**

8. **Clarify DL multivariate formula**
   - df calculation
   - C formula with reference

9. **Statistical interpretation of overcoverage**
   - Monte Carlo SE
   - T-distribution expectation

10. **Full Table 4 in Supplementary**
    - All 8 scenarios, not just 2

---

## SUGGESTED ADDITIONS (Enhance Impact)

### **1. R Package or Code Repository:**
- Implement HKSJ-corrected dose-response MA in R
- Wrapper for dosresmeta objects
- Would increase citations significantly

### **2. Supplementary Tutorial:**
- Worked example with code
- Step-by-step HKSJ application
- Interpretation guidance

### **3. Extended Real-World Validation:**
- Re-analyze 2-3 more published meta-analyses
- Show range of HKSJ impact
- Strengthen generalizability

---

## RECOMMENDATION TO AUTHORS

This manuscript makes **important methodological contributions** that warrant publication in Research Synthesis Methods. The HKSJ application to dose-response meta-analysis fills a significant gap, and the comprehensive simulation study provides strong evidence for practice change.

**Primary strengths:**
1. Novel and needed methodological contribution
2. Rigorous simulation design
3. Real-world validation
4. Actionable decision framework
5. High practical utility

**Primary concerns:**
1. Scenario 7 not specified (reproducibility issue)
2. Within-study correlation unclear
3. FP results missing (methods-results disconnect)
4. Some technical details need clarification

**Expected outcome:** **ACCEPT** after addressing critical and major issues

**Revision timeline:** 4-6 weeks recommended

**Impact potential:** **High** - will influence dose-response meta-analysis practice

---

## EDITORIAL DECISION

**MAJOR REVISION REQUIRED**

**Rationale:**
- Excellent methodological contribution
- Strong evidence and practical utility
- Technical issues can be readily addressed
- Missing details affect reproducibility

**Next Steps:**
1. Address 3 critical issues (Scenario 7, correlations, FP)
2. Address 4 major issues (anisotropic variance, reproducibility, modified HKSJ stats, decomposition)
3. Consider 2 minor issues (DL formula, overcoverage interpretation)
4. Re-submit with point-by-point response letter

**Anticipated final decision:** **ACCEPT** after satisfactory revision

---

## CONFLICTS OF INTEREST

None. Review conducted solely on scientific merit.

---

**END OF RESEARCH SYNTHESIS METHODS EDITORIAL REVIEW**

---

**Summary for Authors:**

Decision: **Major Revision** (likely Accept after revision)
Priority: Address 3 critical + 4 major issues
Timeline: 4-6 weeks for revision
Expected outcome: **Acceptance**

This is publishable, high-quality work that RSM readers will find valuable. The revisions will strengthen reproducibility and clarify technical details.
