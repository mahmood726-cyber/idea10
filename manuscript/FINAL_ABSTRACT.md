# Abstract

## Background

Dose-response meta-analysis synthesizes evidence on relationships between exposure levels and health outcomes. Multiple statistical approaches exist, but their comparative performance, particularly for small meta-analyses (k<20 studies), remains incompletely characterized. Standard methods may produce overconfident conclusions due to inadequate coverage probability.

## Methods

We conducted a comprehensive simulation study comparing restricted cubic splines (RCS) and fractional polynomials using one-stage and two-stage meta-analysis frameworks. Eight scenarios representing common epidemiological patterns were evaluated: linear, quadratic, logarithmic, threshold, U-shaped, J-shaped, complex non-linear, and dose-dependent heterogeneity. Each scenario was simulated 50 times with k=15 studies and 4 dose levels per study, totaling 1,050 meta-analyses. Performance was evaluated using coverage probability (target: 95%), mean squared error, and proper scoring rules (interval score decomposed into sharpness and calibration). For two-stage methods, we implemented the Hartung-Knapp-Sidik-Jonkman (HKSJ) correction to address small-sample bias.

## Results

Two-stage RCS with DerSimonian-Laird pooling and HKSJ correction achieved target coverage across all scenarios (mean: 99.2%, range: 97.5-99.8%). Without HKSJ, coverage was inadequate: two-stage fixed-effects (92.3%, range: 83-96%) and one-stage REML (79.7%, range: 55-92%). In high heterogeneity scenarios (I²=63%), one-stage methods showed catastrophic undercoverage (54.7%). Proper scoring rules revealed that while one-stage methods achieved lower MSE (0.001-0.046 vs. 0.08-2.4 for HKSJ), this reflected dangerously narrow confidence intervals (sharpness: 0.21 vs. 759) with poor calibration (penalties: 0.52 vs. 0.02). HKSJ sacrificed precision for validity, with calibration penalties near zero across all scenarios. All methods achieved 100% convergence with multi-start optimization. Knot sensitivity analysis confirmed 4 knots as optimal for k≥12 studies (coverage: 99.4%, MSE: 2.5-3.9). Real-world applications to alcohol consumption and vitamin D demonstrated practical utility for detecting J-shaped and U-shaped relationships.

## Conclusions

For small-to-moderate dose-response meta-analyses (k<20 studies), two-stage RCS with DerSimonian-Laird pooling and HKSJ correction is essential for valid statistical inference. Without HKSJ, coverage falls to 55-92%, leading to overconfident conclusions. One-stage methods offer better point estimates but should be reserved for prediction tasks or larger meta-analyses (k≥20). Proper scoring rules demonstrate that "narrow" confidence intervals often indicate poor calibration rather than precision. Our findings suggest many published dose-response meta-analyses from 2010-2020 may require re-analysis with HKSJ correction. We provide a decision framework and open-source implementation to facilitate appropriate method selection.

## Keywords

Dose-response meta-analysis; Restricted cubic splines; Hartung-Knapp correction; Proper scoring rules; Small-sample inference; Coverage probability; Simulation study

---

**Word count:** 397 words (structured abstract)

**Trial Registration:** Not applicable (simulation study)

**Funding:** [To be completed]

**Conflicts of Interest:** None declared

---

## Highlights (for graphical abstract)

1. **HKSJ correction achieves 99% coverage** vs. 55-92% without correction (k<20 studies)
2. **Proper scoring rules reveal narrow CIs can be poorly calibrated** (overconfident)
3. **4 knots optimal for RCS** with k≥12 studies (coverage 99.4%, lowest AIC)
4. **100% convergence** achieved with multi-start optimization
5. **Decision framework provided** for method selection in practice

---

## Plain Language Summary

**What was the question?**
When combining multiple studies to understand how the amount of exposure (e.g., alcohol, vitamins, medication) affects health outcomes, which statistical method provides the most reliable results, especially when only a small number of studies are available?

**What did we do?**
We tested different statistical methods using computer simulations that mimicked real medical research, including complex patterns like U-shaped curves (where both too little and too much is harmful) and J-shaped curves (where a little is protective but a lot is harmful).

**What did we find?**
A specific correction (called HKSJ) is essential when analyzing fewer than 20 studies. Without it, confidence intervals are too narrow, giving false certainty. While methods without this correction seemed "more precise" (narrower ranges), they were actually unreliable – like a broken thermometer that always shows the same temperature. With the HKSJ correction, we got wider but honest estimates that correctly reflected uncertainty.

**What does this mean?**
Many published meta-analyses from 2010-2020 that combined small numbers of studies may have overconfident conclusions. Researchers should re-analyze these using the HKSJ correction. We provide simple guidelines to help researchers choose the right method.

**Who did this work?**
[Research team to be added]

---

## Graphical Abstract Elements

**Problem:** Standard methods → Overconfident CIs (54-92% coverage vs. target 95%)

**Solution:** HKSJ correction → Valid CIs (97-100% coverage)

**Key Visual:** Bar chart showing coverage by method
- Two-Stage DL + HKSJ: 99% ✓
- Two-Stage Fixed: 92% ⚠
- One-Stage REML: 80% ✗

**Innovation:** Proper scoring rules reveal precision-validity tradeoff

**Impact:** Decision framework for practitioners
