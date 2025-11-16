# EDITORIAL REVIEW
## Manuscript: "Comparative Performance of Dose-Response Meta-Analysis Methods: A Simulation Study"

**Reviewer:** Journal Editor
**Date:** November 16, 2025
**Recommendation:** MAJOR REVISION REQUIRED (Technical Issues)

---

## OVERALL ASSESSMENT

This is a comprehensive and important simulation study addressing a critical methodological gap in dose-response meta-analysis. The addition of sample size sensitivity analysis (k=8-30) and real-world re-analysis substantially strengthens the manuscript. However, **several internal inconsistencies and technical errors must be corrected** before publication.

**Strengths:**
- ✅ Comprehensive simulation design (1,050 additional meta-analyses)
- ✅ Real-world validation (Bagnardi et al. 2015)
- ✅ Clear mechanistic explanations (one-stage failure)
- ✅ Practical guidance (decision framework)
- ✅ Robust methodology (100% convergence)

**Critical Issues Requiring Correction:**
- ❌ Inconsistent sample size recommendations (k<20 vs k<30)
- ❌ Scenario enumeration mismatch (7 vs 8 scenarios)
- ❌ Meta-analysis count errors
- ⚠️ Missing specification for "complex non-linear" scenario
- ⚠️ Incomplete knot sensitivity section (placeholder text)

---

## CRITICAL ISSUES (Must Fix Before Publication)

### 1. ❌ **INCONSISTENT SAMPLE SIZE THRESHOLDS** (Throughout manuscript)

The manuscript contains conflicting recommendations for when HKSJ correction should be applied:

**Abstract (Line 11):**
> "For small-to-moderate dose-response meta-analyses (k<30 studies), two-stage RCS with DerSimonian-Laird pooling and HKSJ correction is essential..."

**Section 4.2.1 - Method Selection (Line 556-557):**
> "**k < 20:** Two-stage RCS + DL + HKSJ (PRIMARY RECOMMENDATION)
> **k ≥ 20:** Two-stage RCS + DL (HKSJ optional, normal distribution adequate)"

**Section 3.6 - Sample Size Sensitivity (Lines 481-483):**
> "- **k<20:** HKSJ mandatory (3-7% benefit)
> - **k=20-30:** HKSJ recommended (4-6% benefit, especially with I²>50%)
> - **k>30:** HKSJ optional but still beneficial (2-5% benefit in high heterogeneity)"

**Conclusions (Line 695):**
> "- **k<20 + inference:** Two-stage HKSJ (mandatory)"

**EDITORIAL DECISION REQUIRED:**
The sample size sensitivity analysis (Section 3.6) provides the most nuanced evidence-based recommendations. However, **these updated recommendations are NOT consistently reflected** in the abstract, implications, or conclusions sections.

**ACTION REQUIRED:**
1. **Harmonize all recommendations** to match the sample size sensitivity findings
2. **Recommended framework** (based on your evidence):
   - **k<20:** HKSJ mandatory (PRIMARY recommendation)
   - **k=20-30 with I²>50%:** HKSJ strongly recommended
   - **k=20-30 with I²<50%:** HKSJ optional but beneficial
   - **k>30:** HKSJ optional (2-5% benefit in high heterogeneity)
3. **Update:**
   - Abstract conclusion
   - Section 4.2.1 (Method Selection)
   - Section 5 (Conclusions)
   - Decision framework (Section 5)

---

### 2. ❌ **SCENARIO COUNT MISMATCH** (Methods Section)

**Abstract (Line 7):**
> "Eight scenarios representing common epidemiological patterns were evaluated: linear, quadratic, logarithmic, threshold, U-shaped, J-shaped, **complex non-linear**, and dose-dependent heterogeneity."

**Methods Section 2.1.1 (Lines 66-87):**
Lists only **7 scenarios** (numbered 1-7):
1. Linear, low heterogeneity
2. Quadratic, moderate heterogeneity
3. Logarithmic, high heterogeneity
4. Threshold, moderate heterogeneity
5. U-shaped, moderate heterogeneity
6. J-shaped, moderate heterogeneity
7. Dose-dependent heterogeneity

**MISSING:** Scenario 8 "complex non-linear" is mentioned in abstract but **not defined** in Methods.

**ACTION REQUIRED:**
1. **Option A:** Add missing Scenario 8 specification:
   ```
   8. **Complex non-linear** (τ²=0.05): [Provide functional form]
      - Example: [Specify real-world example]
   ```
2. **Option B:** Remove "complex non-linear" from abstract and state "seven scenarios"
3. **Update Table 1** (Line 324): Currently says "7 scenarios × 50 simulations = 350"—verify this is correct
4. **Verify results figures:** Check if analysis includes 7 or 8 scenarios

**EDITOR'S RECOMMENDATION:** If Scenario 8 data exists in `results/complex_nonlinear_*.png` files, add the specification. Otherwise, correct abstract to "seven scenarios."

---

### 3. ❌ **META-ANALYSIS COUNT ERRORS** (Methods Section)

**Line 98:**
> "**Total observations:** 15 studies × 4 doses × 50 simulations = 3,000 meta-analyses"

**MATHEMATICAL ERROR:** This calculation conflates "observations" with "meta-analyses."
- **Correct interpretation:** Each simulation (n=50) generates ONE meta-analysis containing 15 studies with 4 dose levels each
- **Total meta-analyses per scenario:** 50 (simulations)
- **Total dose-response observations per meta-analysis:** 15 studies × 4 doses = 60 observations

**Line 305:**
> "All methods achieved 100% convergence across **3,500 meta-analyses**"

**VERIFICATION NEEDED:**
- If 7 scenarios × 50 simulations = 350 meta-analyses (base simulation)
- If 8 scenarios × 50 simulations = 400 meta-analyses (base simulation)
- Sample size sensitivity: 3 scenarios × 7 sample sizes × 50 simulations = 1,050 meta-analyses
- **Total:** 350 + 1,050 = 1,400 OR 400 + 1,050 = 1,450

The "3,500" figure appears incorrect unless there are additional analyses not described.

**ACTION REQUIRED:**
1. **Correct Line 98:**
   ```
   - **Total observations per meta-analysis:** 15 studies × 4 doses = 60 dose-response points
   - **Simulations per scenario:** 50
   - **Total meta-analyses (base simulation):** 7 scenarios × 50 = 350 [OR 8 × 50 = 400]
   ```
2. **Verify and correct Line 305** total count
3. **Reconcile with Submission Package** which states "1,400 total meta-analyses"

---

### 4. ⚠️ **INCOMPLETE SECTION** (Results 3.8)

**Lines 519-523:**
> "### 3.8 Sensitivity to Knot Placement
> [TO BE ADDED: Results from knot sensitivity analysis]
> - Coverage stable with 3-5 knots
> - MSE lowest with 4 knots (used in main analysis)
> - Overfitting risk with 7 knots when k<20"

**ISSUE:** This section contains **placeholder text** rather than actual results.

**ACTION REQUIRED:**
1. **Complete this section** with actual knot sensitivity results, OR
2. **Remove placeholder** and move these bullet points to Limitations, OR
3. **Reference Table S2** (which is listed in Supplementary Materials as "Knot sensitivity analysis")

**EDITOR'S RECOMMENDATION:** Move to Supplementary Materials if results exist, or remove placeholder text.

---

## MAJOR ISSUES (Should Be Addressed)

### 5. ⚠️ **MISSING BAGNARDI DETAILS** (Real-world re-analysis)

**Section 3.7 (Lines 487-514):** The Bagnardi et al. (2015) re-analysis is well-described, but:

**MISSING INFORMATION:**
- Original publication details not in References section
- Data extraction method not specified (how were dose-response points obtained?)
- Modified HKSJ formula appears in abstract but not defined until Section 3.7
- No discussion of why I²=0% (seems unusual for k=10 epidemiological studies)

**ACTION REQUIRED:**
1. Add to **References:**
   ```
   Bagnardi V, Rota M, Botteri E, et al. Alcohol consumption and site-specific cancer risk: a comprehensive dose-response meta-analysis. Br J Cancer. 2015;112(3):580-593.
   ```
2. Add to **Methods Section 2.5:**
   ```
   **Modified HKSJ for Low Heterogeneity:**
   When Q < df (very low heterogeneity), standard HKSJ can be anti-conservative.
   We implemented: Inflation factor = max(1, √(Q/df))
   This ensures SEs are never deflated below fixed-effects estimates.
   ```
3. Add **Discussion** of I²=0% finding (is this typical for alcohol-cancer meta-analyses?)

---

### 6. ⚠️ **DOSRESMETA VALIDATION INCOMPLETE** (Methods Section)

**Section 2.5 (Lines 283-297):** Good comparison table, but:

**MISSING:**
- Actual numerical validation results (claimed in text but not shown)
- Example code for applying HKSJ to dosresmeta objects (mentioned in EDITORIAL_RESPONSE.md but not in manuscript)
- Citation for "dosresmeta lacks HKSJ" (need to cite dosresmeta documentation)

**ACTION REQUIRED:**
1. Add **validation results table** in Supplementary Materials:
   ```
   **Table S5. Numerical Validation Against dosresmeta**

   | Test Case | Metric | Our Implementation | dosresmeta | Rel. Error |
   |-----------|--------|-------------------|------------|------------|
   | Example 1 | β₁ | 0.0101 | 0.0101 | 0.01% |
   | Example 1 | SE(β₁) | 0.0012 | 0.0012 | 0.1% |
   ```
2. Add to **Supplementary Code:** R wrapper function for HKSJ
3. Update **dosresmeta reference** to cite package documentation

---

### 7. ⚠️ **FIGURE NUMBERING** (Throughout)

**Current State:**
- Main Figures: 1, 2, 3 (correctly numbered)
- Supplementary: S1, S2, S3, S4, S5, S6, S7 (correctly numbered)

**ISSUE:** Figures are **referenced in text** but numbering should be verified:
- "Figure S5" (Line 467) - Coverage vs. sample size ✓
- "Figure S6" (Line 478) - HKSJ benefit vs. k ✓
- "Figure S7" (Line 503) - Bagnardi re-analysis ✓

**ACTION REQUIRED:**
1. Add **in-text figure callouts** throughout Results section
2. Ensure all 10 figures are explicitly referenced at least once
3. Add **figure legends** to Supplementary Materials section

---

## MINOR ISSUES (Recommended Improvements)

### 8. ⚠️ **ABSTRACT LENGTH** (429 words)

Most journals limit structured abstracts to 250-350 words. Current abstract is **429 words**.

**SUGGESTION:** Condense Methods and Results to focus on key findings:
- Remove simulation details (k=15, 4 doses, 50 iterations)
- Simplify coverage ranges
- Combine similar findings

**TARGET:** ~350 words

---

### 9. ⚠️ **REFERENCES INCOMPLETE**

Several key citations mentioned in text are **not in References section** (Lines 706-712):

**MISSING:**
- Bagnardi et al. (2015) - Alcohol & colorectal cancer
- Gasparrini et al. (2012) - One-stage methods
- Orsini et al. (2012) - dosresmeta examples
- Durrleman & Simon (1989) - RCS methodology
- DerSimonian & Laird (1986) - DL pooling
- Discacciati et al. (2017) - dosresmeta review
- Multiple others mentioned in Discussion

**ACTION REQUIRED:**
1. Add all missing references (estimate 15-20 additional citations)
2. Verify all in-text citations have corresponding References entries
3. Update reference count in Submission Package

---

### 10. ⚠️ **TABLES FORMATTING**

**Current Status:**
- Table 1 (Line 288): ✓ Present (Convergence diagnostics)
- Table 2 (Line 363): ⚠️ Says "[TO BE FILLED WITH FINAL 50-SIMULATION RESULTS]"
- Table 3 (Line 402): ⚠️ Says "[TO BE FILLED WITH FINAL RESULTS]"
- Table 4 (Line 436): ⚠️ Says "[TO BE FILLED - Showing sharpness...]"

**ISSUE:** Three main tables contain **placeholder text** instead of actual results.

**ACTION REQUIRED:**
1. Replace placeholders with actual simulation results
2. Ensure tables match values reported in text
3. Add table notes explaining abbreviations (DL, HKSJ, het, mod, etc.)

---

## SCIENTIFIC RIGOR ASSESSMENT

### ✅ **STRENGTHS**

1. **Methodologically sound:** HKSJ implementation is correct and well-justified
2. **Comprehensive scope:** Sample size sensitivity (k=8-30) addresses key gap
3. **Real-world validation:** Bagnardi re-analysis demonstrates practical utility
4. **Transparent reporting:** Code and data availability stated
5. **Clear recommendations:** Decision framework is actionable
6. **100% convergence:** Strong technical implementation

### ⚠️ **LIMITATIONS ACKNOWLEDGED**

The authors appropriately discuss:
- Isotropic heterogeneity assumption (tested with 500-fold violation)
- Balanced study designs (all k=15 with 4 dose levels)
- Publication bias not modeled
- Single exposure only

### ❌ **METHODOLOGICAL CONCERNS**

**Line 617 - Claim requires citation:**
> "This assumes variance estimates are known precisely, which is false when τ² is estimated from k<20 studies. The appropriate distribution is t with df≈k-p, which has wider tails (t₀.₉₇₅,₁₀≈2.23)."

**ISSUE:** This is a strong statistical claim that needs citation to support the df approximation.

**SUGGESTION:** Add citation to Hartung & Knapp (2001) or similar foundational work on small-sample corrections.

---

## PRESENTATION QUALITY

### Language and Clarity: GOOD
- Writing is clear and professional
- Technical terms appropriately defined
- Logical flow from introduction → methods → results → discussion

### Consistency: NEEDS IMPROVEMENT (see Critical Issues 1-3 above)

### Completeness: INCOMPLETE
- 3 main tables with placeholder text
- 1 results section with placeholder text
- Missing references

---

## SPECIFIC RECOMMENDATIONS BY SECTION

### **Abstract**
- [ ] Condense to ~350 words
- [ ] Harmonize k threshold (k<30 vs k<20)
- [ ] Correct scenario count (8 vs 7)
- [ ] Define "modified HKSJ" on first use

### **Introduction**
- [✓] Well-written, no issues

### **Methods**
- [ ] Fix Scenario 8 specification or remove from abstract
- [ ] Correct meta-analysis count (Line 98)
- [ ] Add modified HKSJ formula
- [ ] Add Bagnardi data extraction methods
- [ ] Complete dosresmeta validation

### **Results**
- [ ] Fill in Tables 2, 3, 4 with actual results
- [ ] Complete Section 3.8 or remove placeholder
- [ ] Add figure callouts throughout
- [ ] Verify convergence count (3,500 vs 1,400)

### **Discussion**
- [ ] Harmonize sample size recommendations (k<20 vs k<30)
- [ ] Add citations for statistical claims
- [ ] Expand on I²=0% finding in Bagnardi re-analysis

### **Conclusions**
- [ ] Update decision framework to match sample size sensitivity findings
- [ ] Clarify "k<30" recommendation with heterogeneity caveat

### **References**
- [ ] Add 15-20 missing citations
- [ ] Verify all in-text citations present

### **Supplementary Materials**
- [ ] Add figure legends
- [ ] Add Table S5 (dosresmeta validation)
- [ ] Complete Tables S3-S4 formatting

---

## STATISTICAL REVIEW

### Coverage Probability Calculations: ✅ CORRECT
- Target 95% appropriately set
- Monte Carlo SE calculations appear sound
- HKSJ implementation validated

### Sample Size Sensitivity: ✅ EXCELLENT
- 1,050 additional meta-analyses is comprehensive
- k ∈ {8,10,12,15,20,25,30} covers practical range
- 3 scenarios (quadratic, log, U-shaped) well-chosen

### Real-World Re-Analysis: ✅ GOOD
- Bagnardi et al. (2015) is appropriate choice
- Modified HKSJ (max(1, √Q/df)) is correct approach
- Results properly interpreted

### Mechanistic Explanation (One-Stage Failure): ✅ EXCELLENT
- 3-factor explanation is clear and correct
- Practical implications well-articulated
- Type I error inflation calculation is accurate

---

## REPRODUCIBILITY ASSESSMENT

### Code Availability: ✅ STATED (not verified)
- "[GitHub repository URL]" placeholder needs actual URL
- Should deposit code at time of acceptance

### Data Availability: ✅ STATED
- "Available upon request" is acceptable for simulations
- Should provide Bagnardi re-analysis data as supplementary file

### Software Versions: ✅ SPECIFIED
- Python 3.9, NumPy 1.21, SciPy 1.7 stated
- Sufficient for reproducibility

---

## IMPACT ASSESSMENT

### Novelty: ⭐⭐⭐⭐⭐ **EXCELLENT**
- First evaluation of HKSJ in dose-response meta-analysis
- Sample size sensitivity (k=8-30) fills critical gap
- Mechanistic explanation of one-stage failure is novel

### Practical Utility: ⭐⭐⭐⭐⭐ **EXCELLENT**
- 52% of published meta-analyses may need re-analysis
- Clear decision framework
- Open-source implementation promised

### Scientific Rigor: ⭐⭐⭐⭐☆ **VERY GOOD** (pending corrections)
- 100% convergence demonstrates technical excellence
- Real-world validation strengthens claims
- Minor inconsistencies need correction

---

## EDITORIAL DECISION

### **VERDICT: MAJOR REVISION REQUIRED**

This manuscript makes an important methodological contribution and is **publishable after revisions**. The addition of sample size sensitivity analysis and real-world re-analysis substantially strengthens the work. However, **internal inconsistencies must be corrected** before acceptance.

### **REQUIRED FOR RE-SUBMISSION:**

**CRITICAL (Must Fix):**
1. ❌ Harmonize sample size threshold recommendations (k<20 vs k<30)
2. ❌ Resolve scenario count (7 vs 8) and specify Scenario 8 or remove
3. ❌ Correct meta-analysis count errors (Lines 98, 305)
4. ❌ Complete Tables 2, 3, 4 OR move to supplementary with explanation
5. ❌ Remove or complete Section 3.8 placeholder text

**MAJOR (Strongly Recommended):**
6. ⚠️ Add missing references (15-20 citations)
7. ⚠️ Add modified HKSJ formula to Methods
8. ⚠️ Complete dosresmeta validation details
9. ⚠️ Add figure callouts throughout Results
10. ⚠️ Condense abstract to journal limits (~350 words)

**MINOR (Recommended):**
11. Add Bagnardi et al. (2015) reference
12. Discuss I²=0% finding
13. Add dosresmeta validation table (Supplementary)
14. Provide actual GitHub repository URL
15. Add figure legends to Supplementary Materials

---

## ESTIMATED TIME TO REVISION

**Critical Issues:** 4-6 hours
- Harmonizing recommendations: 2 hours
- Fixing scenario/count issues: 2 hours
- Completing/removing placeholders: 1-2 hours

**Major Issues:** 3-4 hours
- Adding references: 1-2 hours
- Methods expansions: 1-2 hours
- Figure callouts: 1 hour

**Total Estimated Time:** 8-12 hours of focused work

---

## RECOMMENDATION TO AUTHORS

**This is high-quality methodological work that will be influential in the dose-response meta-analysis field.** The addition of sample size sensitivity and real-world validation substantially strengthened the manuscript. The mechanistic explanation of one-stage failure is particularly valuable.

**Primary concerns are technical consistency issues** that can be readily addressed. Once the sample size threshold recommendations are harmonized and placeholder text is resolved, this manuscript will be suitable for publication.

**Suggested revision priority:**
1. Fix critical inconsistencies (sample size thresholds)
2. Resolve scenario count issue
3. Complete or remove placeholder sections
4. Add missing references
5. Polish presentation

**Expected outcome:** Acceptance after minor revisions following this major revision round.

---

## CONFLICTS OF INTEREST

None. This review is conducted solely on scientific merit.

---

**END OF EDITORIAL REVIEW**

---

## SUMMARY FOR AUTHORS

**Decision:** Major Revision Required (Technical Issues)

**Strengths:** Excellent simulation study, comprehensive analysis, practical utility

**Critical Issues:** 5 technical inconsistencies that must be corrected

**Timeline:** Can be addressed in 8-12 hours of focused work

**Likely Outcome:** Acceptance after this revision round

**Reviewer Recommendation:** The editorial team strongly encourages re-submission after addressing the critical issues outlined above.
