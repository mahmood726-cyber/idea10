# Figure Specification for 1000-Word Synthesis Manuscript

## Publication Package Contents

This document specifies the two figures to be included with the 1000-word Synthesis manuscript for immediate publication.

---

## Figure 1: Coverage Probability by Method and Scenario

**File:** `manuscript/figures/Figure_1_Coverage_by_Scenario.pdf` (for print)
**File:** `manuscript/figures/Figure_1_Coverage_by_Scenario.png` (for web)

**Purpose:** Demonstrates the primary finding that HKSJ correction achieves target 95% coverage across all scenarios.

**Description:**
- Comparison of coverage probability across eight dose-response scenarios
- Three methods shown:
  - Two-stage DL + HKSJ (blue) - achieves 96-100% coverage
  - Two-stage Fixed-effects (green) - undercoverage with heterogeneity
  - One-stage REML (red) - severe undercoverage (46-83%)
- Horizontal dashed line at 95% indicates target coverage
- Error bars show 95% confidence intervals from 50 simulations
- X-axis: Eight scenarios (Linear, Quadratic, Logarithmic, Threshold, U-shaped, J-shaped, Complex, Dose-dep het)
- Y-axis: Coverage probability (%)

**Key Message:** HKSJ correction is essential for valid inference in small meta-analyses (k<20 studies).

---

## Figure 2: Decision Framework for Method Selection

**File:** `manuscript/figures/Figure_3_Method_Selection_Flowchart.pdf` (for print)
**File:** `manuscript/figures/Figure_3_Method_Selection_Flowchart.png` (for web)

**Note:** This is labeled as Figure_3 in the files but will be presented as Figure 2 in the 1000-word manuscript.

**Purpose:** Provides practical guidance for researchers on selecting the appropriate dose-response meta-analysis method.

**Description:**
- Flowchart with decision nodes based on:
  1. Number of studies (k < 20 or k ≥ 20)
  2. Analysis goal (inference vs. prediction)
  3. Heterogeneity level (I² < 25% or I² ≥ 25%)
- Four recommendation boxes:
  - **PRIMARY:** Two-stage RCS + DL + HKSJ (for k<20, inference)
  - Two-stage RCS + DL (for k≥20, inference)
  - One-stage RCS + REML (for prediction tasks)
  - Fixed-effects (only when I²<25% and Q-test p>0.10)
- Color-coded by recommendation strength (primary in bold)

**Key Message:** Method selection should be based on study characteristics and analysis objectives, with HKSJ correction as default for small meta-analyses.

---

## Why These Two Figures?

### Figure 1 (Coverage by Scenario)
- **Shows the main empirical finding:** HKSJ achieves target coverage
- **Demonstrates the problem:** Other methods severely undercover
- **Quantifies improvement:** From 63-90% to 96-100% coverage
- **Covers all scenarios:** Validates findings across diverse dose-response shapes

### Figure 2 (Method Selection Flowchart)
- **Practical utility:** Readers can immediately apply guidance
- **Synthesizes recommendations:** Distills 997 words into actionable framework
- **Decision support:** Clear criteria (k, goal, I²) for method selection
- **Primary recommendation clear:** HKSJ for small meta-analyses

### Why Not Other Figures?

- **Figure S1 (Example Curves):** Illustrative but not essential for main findings
- **Figure S2 (Coverage Distribution):** Redundant with Figure 1
- **Figure S3 (MSE vs Coverage):** Important but secondary to coverage message
- **Figure S4 (Interval Score Components):** Technical detail, can be in text

---

## Figure Quality Specifications

### For Print Publication
- **Format:** PDF (vector graphics)
- **Resolution:** Vector (scalable)
- **Color mode:** CMYK or RGB (journal-dependent)
- **Size:** As generated (typically 8" × 6" or journal specification)

### For Online Publication
- **Format:** PNG
- **Resolution:** 300 DPI
- **Color mode:** RGB
- **Size:** High-resolution PNG as generated

---

## Manuscript Structure

The 1000-word synthesis manuscript includes:

1. **Abstract** (250 words)
2. **Introduction** (200 words)
3. **Methods** (250 words)
4. **Results** (200 words)
5. **Discussion** (250 words)
6. **Conclusions** (50 words)
7. **Figure Legends** (integrated)
8. **References** (10 key papers)
9. **Two Figures** (as specified above)

**Total word count:** 997 words (excluding abstract, references, figure legends)

---

## Files for Publication Submission

### Primary Manuscript
- `manuscript/SYNTHESIS_1000_WORD.md` (Markdown source)
- Convert to: DOCX or LaTeX per journal requirements

### Figures
1. `manuscript/figures/Figure_1_Coverage_by_Scenario.pdf`
2. `manuscript/figures/Figure_1_Coverage_by_Scenario.png`
3. `manuscript/figures/Figure_3_Method_Selection_Flowchart.pdf` (submit as Figure 2)
4. `manuscript/figures/Figure_3_Method_Selection_Flowchart.png` (submit as Figure 2)

### Supplementary Files (Optional)
- Full manuscript: `manuscript/MANUSCRIPT_DRAFT.md` (4,500 words)
- Additional figures: Figures S1-S4 for supplementary materials
- Code repository: Link to GitHub with full analysis code

---

## Publication Checklist

- [x] Manuscript text: 1000 words (997 words achieved)
- [x] Figure 1: Coverage by Scenario (exists)
- [x] Figure 2: Method Selection Flowchart (exists as Figure_3)
- [x] Figure legends: Included in manuscript
- [x] References: 10 key papers cited
- [x] Abstract: <250 words
- [ ] Convert to journal format (DOCX/LaTeX)
- [ ] Format figures per journal requirements
- [ ] Submit through journal portal

---

## Recommended Journals

### Tier 1 (High-Impact Methods Journals)
- **Research Synthesis Methods** (Wiley) - Synthesis articles welcomed
- **Statistics in Medicine** - Methodological papers
- **BMC Medical Research Methodology** - Open access

### Tier 2 (Specialized)
- **Journal of Clinical Epidemiology** - Meta-analysis focus
- **Systematic Reviews** (BMC) - Open access
- **Meta-Analysis and Individual Participant Data** (Springer)

### Submission Format
Most journals accept:
- Main text: DOCX or LaTeX
- Figures: PDF (print) + PNG/TIFF (web)
- Supplementary: ZIP with code/data

---

**Document prepared:** November 18, 2025
**Status:** Ready for journal formatting and submission
