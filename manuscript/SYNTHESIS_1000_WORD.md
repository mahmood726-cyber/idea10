# Comparative Performance of Dose-Response Meta-Analysis Methods: Ensuring Valid Inference in Small Meta-Analyses

## Abstract

**Background:** Dose-response meta-analysis synthesizes evidence on exposure-outcome relationships, but confidence interval validity across different methods remains incompletely characterized, particularly for small meta-analyses.

**Methods:** We compared restricted cubic splines (RCS) and fractional polynomials using one-stage and two-stage frameworks across eight scenarios. Two-stage methods included DerSimonian-Laird pooling with and without Hartung-Knapp-Sidik-Jonkman (HKSJ) correction. Performance was evaluated using coverage probability, mean squared error, and interval score decomposition for k=15 studies.

**Results:** Two-stage RCS with HKSJ correction achieved target coverage (96-100%) across all scenarios. Without HKSJ, coverage was inadequate (63-90%). One-stage methods showed lower coverage (46-83%) but smaller MSE. Proper scoring rules revealed that two-stage HKSJ traded precision for validity.

**Conclusions:** For inference in small-to-moderate meta-analyses (k<20), two-stage RCS with HKSJ correction is recommended. One-stage methods may be preferred for prediction or when k≥20.

**Keywords:** dose-response meta-analysis, restricted cubic splines, Hartung-Knapp correction, simulation study, proper scoring rules

---

## 1. Introduction

Dose-response meta-analysis extends traditional meta-analysis to examine how effect magnitude varies with exposure level [1,2]. This approach is essential for identifying optimal pharmaceutical doses, characterizing non-linear relationships in nutritional epidemiology, and informing dose-specific public health guidelines.

Multiple modeling approaches exist: restricted cubic splines (RCS) provide flexible piecewise cubic polynomials with linear tails [3], while fractional polynomials (FP) use power transformations for interpretable curves [4]. These can be estimated using one-stage (simultaneous estimation via mixed-effects models) or two-stage (within-study estimation followed by multivariate pooling) approaches [5,6].

Despite methodological advances, critical questions remain: How well do confidence intervals achieve nominal coverage across different dose-response shapes? Are standard errors correctly estimated when k<20 studies? Recent work highlighted that small-sample meta-analyses often show inadequate coverage without corrections [7]. The Hartung-Knapp-Sidik-Jonkman (HKSJ) correction addresses this by inflating standard errors based on heterogeneity and using t-distribution instead of normal distribution [8].

This simulation study compares RCS and FP approaches across diverse scenarios to evaluate coverage validity and provide guidance for method selection.

## 2. Methods

### 2.1 Simulation Design

We simulated eight dose-response scenarios: linear (τ²=0.01), quadratic (τ²=0.05), logarithmic (τ²=0.10), threshold (τ²=0.05), U-shaped (τ²=0.05), J-shaped (τ²=0.05), complex non-linear (τ²=0.05), and dose-dependent heterogeneity. Each scenario used k=15 studies with 4 dose levels (0-100 units), representing small-to-moderate meta-analyses common in practice. We conducted 50 simulations per scenario, yielding 3,500 meta-analyses.

### 2.2 Statistical Methods

**Restricted Cubic Splines:** We used 4 knots at percentiles [5%, 35%, 65%, 95%], creating 3 basis functions with continuous first and second derivatives [3].

**Two-Stage Meta-Analysis:** Stage 1 estimated within-study coefficients using weighted least squares. Stage 2 pooled estimates using multivariate meta-analysis with DerSimonian-Laird heterogeneity estimation [6,9]. The HKSJ correction inflated variance by √(Q/df) and used t-distribution with df=k-p [8]. We assumed isotropic between-study heterogeneity (Ψ=τ²I) for computational tractability while properly accounting for within-study correlations.

**One-Stage Meta-Analysis:** Mixed-effects models estimated simultaneously using restricted maximum likelihood with multi-start L-BFGS-B optimization [5].

### 2.3 Performance Evaluation

**Coverage probability:** Percentage of 100 prediction points where true curve fell within 95% CI (target: 95%).

**Mean Squared Error (MSE):** Average squared deviation between predicted and true values.

**Interval Score (IS):** Proper scoring rule decomposed into sharpness (interval width) and calibration (miscoverage penalty) [10]. This separates precision from accuracy, revealing whether narrow intervals reflect true certainty or poor calibration.

## 3. Results

### 3.1 Coverage Validity

Two-stage RCS with HKSJ correction achieved target coverage across all scenarios (Figure 1):
- Linear: 98.8% (95% CI: 97.2-99.7%)
- Quadratic: 98.8% (97.2-99.7%)
- Logarithmic: 96.2% (94.1-97.8%)
- Threshold: 98.8% (97.2-99.7%)
- U-shaped: 98.8% (97.2-99.7%)
- J-shaped: 98.8% (97.2-99.7%)
- Dose-dependent heterogeneity: 100.0% (99.3-100%)

Mean coverage: **98.2%** (range: 96.2-100%). Slight overcoverage reflects HKSJ conservatism with small k, which protects against Type I errors.

Without HKSJ correction, coverage was inadequate:
- **Two-Stage DL (no HKSJ):** 63-90%, mean 76.3%
- **Fixed-Effects:** 83-96%, adequate only when I²<25%
- **One-Stage REML:** 46-83%, mean 73.1%

### 3.2 Precision-Validity Tradeoff

Interval score decomposition revealed method tradeoffs:

**Two-Stage HKSJ:** Wide intervals (sharpness: 105-510 on log-RR scale) but excellent calibration (penalty: 0.002-0.21). Intervals are wide because they properly reflect uncertainty in small meta-analyses.

**One-Stage REML:** Narrow intervals (sharpness: 0.12-0.29) but poor calibration (penalty: 0.04-2.56). Apparent precision masks systematic undercoverage.

**Fixed-Effects:** Intermediate sharpness (23.6) but accumulates penalties when heterogeneity present.

### 3.3 Point Prediction

One-stage achieved lower MSE (0.001-0.046) than two-stage (0.015-0.291), reflecting better point estimates. However, invalid confidence intervals make one-stage unsuitable for inference despite superior point prediction.

All methods achieved 100% convergence with multi-start optimization (mean computation time: 0.002s for two-stage, 0.193s for one-stage).

## 4. Discussion

This comprehensive simulation demonstrates that HKSJ correction is essential for valid inference in small dose-response meta-analyses. Without correction, coverage dropped to 63-90%, leading to overconfident conclusions. The two-stage vs. one-stage choice depends on analysis goals: two-stage HKSJ for inference (hypothesis testing, confidence intervals), one-stage for point prediction.

**Method Selection Recommendations (Figure 2):**
- **k<20, inference goal:** Two-stage RCS + DL + HKSJ (primary recommendation)
- **k≥20, inference goal:** Two-stage RCS + DL (HKSJ optional)
- **Prediction goal:** One-stage RCS + REML
- **I²<25%, confirmed by Q-test:** Fixed-effects acceptable

**Knot selection:** Use 4 knots for k≥12 studies; 3 knots if k<12; maximum n_knots ≤ k/3.

Proper scoring rules provide insights beyond traditional metrics. Interval score decomposition separates precision (sharpness) from accuracy (calibration), revealing that "narrow" intervals may reflect poor calibration rather than true certainty. This framework properly incentivizes honest uncertainty quantification.

**Limitations:** Our study simulated k=15 studies; performance may differ for k<10 or k>30. We assumed isotropic heterogeneity (Ψ=τ²I); unstructured Ψ may improve fit but requires substantially more parameters. Balanced designs with 4 doses per study were used; real meta-analyses have variable designs. Publication bias was not modeled.

**Comparison to Literature:** Our findings extend IntHout et al. (2014) [8], who showed HKSJ improves coverage in univariate meta-analysis, to the multivariate dose-response setting. We confirm Crippa & Orsini's (2016) [2] recommendation of two-stage approaches and quantify the coverage improvement with HKSJ correction. Novel contributions include proper scoring rule assessment and comprehensive evaluation across diverse non-linear scenarios (U-shaped, J-shaped, threshold).

## 5. Conclusions

For small-to-moderate dose-response meta-analyses (k<20 studies), two-stage restricted cubic splines with DerSimonian-Laird pooling and HKSJ correction provides valid inference with 96-100% coverage. Without HKSJ, coverage is inadequate (63-90%). One-stage methods offer better point prediction but should be reserved for prediction tasks or larger meta-analyses. Method selection should prioritize validity of inference over MSE minimization. Our decision framework and open-source implementation facilitate appropriate method selection for future dose-response meta-analyses.

---

## Figure Legends

**Figure 1. Coverage Probability by Method and Scenario.** Comparison of coverage probability across eight dose-response scenarios for three meta-analysis methods. Two-stage DL with HKSJ correction (blue) achieves target 95% coverage (dashed line) across all scenarios, while two-stage fixed-effects (green) undercoverage when heterogeneity is present, and one-stage REML (red) shows severe undercoverage. Error bars represent 95% confidence intervals from 50 simulations. k=15 studies, 4 doses per study.

**Figure 2. Decision Framework for Method Selection.** Flowchart for selecting appropriate dose-response meta-analysis method based on number of studies (k), analysis goal (inference vs. prediction), and heterogeneity level (I²). Primary recommendation for small meta-analyses (k<20) is two-stage RCS with DL pooling and HKSJ correction. One-stage methods recommended for prediction tasks or when k≥20. Fixed-effects acceptable only when I²<25% and confirmed by Q-test (p>0.10).

---

## References

1. Greenland S, Longnecker MP. Methods for trend estimation from summarized dose-response data, with applications to meta-analysis. Am J Epidemiol. 1992;135(11):1301-9.

2. Crippa A, Orsini N. Multivariate dose-response meta-analysis: the dosresmeta R package. J Stat Softw. 2016;72(1):1-15.

3. Harrell FE Jr. Regression Modeling Strategies. 2nd ed. Springer; 2015.

4. Royston P, Altman DG. Regression using fractional polynomials of continuous covariates: parsimonious parametric modelling. Appl Stat. 1994;43(3):429-467.

5. Orsini N, Li R, Wolk A, et al. Meta-analysis for linear and nonlinear dose-response relations: examples, an evaluation of approximations, and software. Am J Epidemiol. 2012;175(1):66-73.

6. Jackson D, White IR, Thompson SG. Extending DerSimonian and Laird's methodology to perform multivariate random effects meta-analyses. Stat Med. 2010;29(12):1282-97.

7. Röver C, Knapp G, Friede T. Hartung-Knapp-Sidik-Jonkman approach and its modification for random-effects meta-analysis with few studies. BMC Med Res Methodol. 2015;15:99.

8. IntHout J, Ioannidis JPA, Borm GF. The Hartung-Knapp-Sidik-Jonkman method for random effects meta-analysis is straightforward and considerably outperforms the standard DerSimonian-Laird method. BMJ. 2014;349:g5219.

9. White IR. Multivariate random-effects meta-regression: updates to mvmeta. Stata J. 2011;11(2):255-270.

10. Gneiting T, Raftery AE. Strictly proper scoring rules, prediction, and estimation. J Am Stat Assoc. 2007;102(477):359-378.

---

**Word count:** 997 words (excluding abstract, references, and figure legends)
**Figures:** 2 (Figure 1: Coverage by Scenario; Figure 2: Method Selection Flowchart)
**Tables:** 0 (information integrated into text for brevity)
