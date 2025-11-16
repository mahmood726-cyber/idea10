# Table 2. Coverage Probability by Method and Scenario

**Coverage probability (%)** across 50 simulations per scenario. Values are mean ± SD. Target: 95%.

| Scenario | Two-Stage RCS<br/>DL + HKSJ | Two-Stage RCS<br/>Fixed-Effects | One-Stage RCS<br/>REML |
|----------|--------------------------|----------------------------|---------------------|
| **1. Linear (low heterogeneity)** | 99.4 ± 1.8 | 96.3 ± 4.4 | 91.5 ± 23.1 |
| **2. Quadratic (moderate heterogeneity)** | 99.4 ± 1.6 | 92.7 ± 5.0 | 84.3 ± 33.2 |
| **3. Logarithmic (high heterogeneity)** | 97.5 ± 1.6 | 83.1 ± 2.5 | 54.7 ± 10.7 |
| **4. Threshold (moderate heterogeneity)** | 99.4 ± 1.6 | 92.7 ± 5.0 | 85.0 ± 29.9 |
| **5. U-shaped (moderate heterogeneity)** | 99.5 ± 1.5 | 93.0 ± 5.0 | 84.8 ± 28.8 |
| **6. J-shaped (moderate heterogeneity)** | 99.5 ± 1.5 | 92.5 ± 5.1 | 84.9 ± 27.7 |
| **7. Dose-dependent heterogeneity** | 99.8 ± 0.7 | 95.9 ± 4.1 | 72.9 ± 28.5 |
| **Mean across scenarios** | **99.2** | **92.3** | **79.7** |
| **Range** | 97.5 - 99.8 | 83.1 - 96.3 | 54.7 - 91.5 |

**Notes:**
- Each scenario: k=15 studies, 4 dose levels per study, 50 simulations
- True heterogeneity: Low (τ²=0.01), Moderate (τ²=0.05), High (τ²=0.10)
- HKSJ = Hartung-Knapp-Sidik-Jonkman correction (t-distribution with df = k-p)
- All methods used restricted cubic splines with 4 knots

**Key Findings:**
1. Two-Stage DL + HKSJ achieves target coverage (97-100%) across all scenarios
2. Without HKSJ, fixed-effects undercoverage especially with high heterogeneity (83%)
3. One-stage REML shows severe undercoverage (55-92%), worst in high-heterogeneity scenarios
4. High SD for one-stage reflects variable performance across simulations

**Clinical Interpretation:**
- HKSJ correction critical for valid inference in meta-analyses with k<20 studies
- Fixed-effects inappropriate when I²>25% (leads to 83-93% coverage vs. target 95%)
- One-stage methods may produce overconfident conclusions (CIs too narrow)
