"""
Generate All Manuscript Figures

Creates publication-ready figures for main text and supplementary materials
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys

sys.path.insert(0, '/home/user/idea10')

# Set publication style
plt.style.use('seaborn-v0_8-paper')
sns.set_context("paper", font_scale=1.2)
sns.set_palette("colorblind")

# Create output directory
output_dir = Path('manuscript/figures')
output_dir.mkdir(parents=True, exist_ok=True)

# Load results
detailed = pd.read_csv('results/detailed_results.csv')
detailed_conv = detailed[detailed['converged']].copy()

print("="*80)
print("GENERATING MANUSCRIPT FIGURES")
print("="*80)

# =============================================================================
# FIGURE 1: Coverage Probability by Scenario and Method (BAR PLOT)
# =============================================================================
print("\nFigure 1: Coverage by Scenario...")

fig, ax = plt.subplots(figsize=(12, 6))

# Prepare data
coverage_data = detailed_conv.groupby(['scenario', 'method'])['coverage'].mean().unstack()

# Reorder scenarios for better presentation
scenario_order = [
    '1_linear_low_het',
    '2_quadratic_mod_het',
    '3_log_high_het',
    '4_threshold_mod_het',
    '5_u_shaped',
    '6_j_shaped',
    '7_quadratic_dose_dep_het'
]

coverage_data = coverage_data.reindex(scenario_order)

# Shorten labels
scenario_labels = {
    '1_linear_low_het': 'Linear\n(Low Het)',
    '2_quadratic_mod_het': 'Quadratic\n(Mod Het)',
    '3_log_high_het': 'Logarithmic\n(High Het)',
    '4_threshold_mod_het': 'Threshold\n(Mod Het)',
    '5_u_shaped': 'U-Shaped\n(Mod Het)',
    '6_j_shaped': 'J-Shaped\n(Mod Het)',
    '7_quadratic_dose_dep_het': 'Dose-Dep\nHet'
}

coverage_data.index = [scenario_labels[s] for s in coverage_data.index]

# Plot
x = np.arange(len(coverage_data))
width = 0.25

bars1 = ax.bar(x - width, coverage_data['TwoStage_RCS_DL_HKSJ'], width,
               label='Two-Stage DL + HKSJ', color='#2E7D32', alpha=0.9)
bars2 = ax.bar(x, coverage_data['TwoStage_RCS_Fixed'], width,
               label='Two-Stage Fixed', color='#F57C00', alpha=0.9)
bars3 = ax.bar(x + width, coverage_data['OneStage_RCS'], width,
               label='One-Stage REML', color='#C62828', alpha=0.9)

# Reference line at 95%
ax.axhline(95, color='black', linestyle='--', linewidth=1.5, label='Target (95%)', zorder=0)

# Acceptable range
ax.axhspan(90, 98, alpha=0.1, color='green', zorder=0)

ax.set_ylabel('Coverage Probability (%)', fontsize=12, fontweight='bold')
ax.set_xlabel('Scenario', fontsize=12, fontweight='bold')
ax.set_title('Coverage Probability by Method and Scenario\n(Target: 95%, Acceptable: 90-98%)',
             fontsize=13, fontweight='bold', pad=15)
ax.set_xticks(x)
ax.set_xticklabels(coverage_data.index, fontsize=10)
ax.legend(loc='lower left', fontsize=10)
ax.set_ylim(40, 105)
ax.grid(axis='y', alpha=0.3, linestyle=':')

# Add value labels on bars
def autolabel(bars, ax):
    for bar in bars:
        height = bar.get_height()
        if height > 50:  # Only label if visible
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=8)

autolabel(bars1, ax)
autolabel(bars2, ax)
autolabel(bars3, ax)

plt.tight_layout()
plt.savefig(output_dir / 'Figure_1_Coverage_by_Scenario.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_1_Coverage_by_Scenario.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_1_Coverage_by_Scenario.png'}")

# =============================================================================
# FIGURE 2: Precision-Validity Tradeoff (SCATTER PLOT)
# =============================================================================
print("\nFigure 2: Precision-Validity Tradeoff...")

fig, ax = plt.subplots(figsize=(10, 8))

# Aggregate by method
method_summary = detailed_conv.groupby('method').agg({
    'sharpness': 'mean',
    'calibration': 'mean',
    'coverage': 'mean'
}).reset_index()

# Colors for methods
colors = {
    'TwoStage_RCS_DL_HKSJ': '#2E7D32',
    'TwoStage_RCS_Fixed': '#F57C00',
    'OneStage_RCS': '#C62828'
}

labels = {
    'TwoStage_RCS_DL_HKSJ': 'Two-Stage DL + HKSJ\n(99% coverage)',
    'TwoStage_RCS_Fixed': 'Two-Stage Fixed\n(92% coverage)',
    'OneStage_RCS': 'One-Stage REML\n(80% coverage)'
}

for _, row in method_summary.iterrows():
    method = row['method']
    ax.scatter(row['sharpness'], row['calibration'],
              s=500, color=colors[method], alpha=0.8,
              edgecolors='black', linewidth=2,
              label=labels[method], zorder=3)

# Ideal point (0, 0) - sharp and calibrated
ax.scatter(0, 0, s=300, marker='*', color='gold',
          edgecolors='black', linewidth=2,
          label='Ideal (Sharp + Calibrated)', zorder=4)

ax.set_xlabel('Sharpness (Interval Width)\nLower = More Precise',
             fontsize=12, fontweight='bold')
ax.set_ylabel('Calibration (Miscoverage Penalty)\nLower = Better Calibrated',
             fontsize=12, fontweight='bold')
ax.set_title('Precision-Validity Tradeoff: Sharpness vs. Calibration\n' +
            'Based on Proper Scoring Rules (Interval Score Decomposition)',
            fontsize=13, fontweight='bold', pad=15)

# Log scale for sharpness
ax.set_xscale('log')
ax.set_yscale('log')

ax.legend(loc='upper left', fontsize=10, framealpha=0.95)
ax.grid(True, alpha=0.3, linestyle=':')

# Add annotations
ax.annotate('Wide but honest\n(Conservative)',
           xy=(method_summary[method_summary['method']=='TwoStage_RCS_DL_HKSJ']['sharpness'].values[0],
               method_summary[method_summary['method']=='TwoStage_RCS_DL_HKSJ']['calibration'].values[0]),
           xytext=(100, 0.001), fontsize=9, style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightgreen', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3'))

ax.annotate('Narrow but poorly calibrated\n(Overconfident)',
           xy=(method_summary[method_summary['method']=='OneStage_RCS']['sharpness'].values[0],
               method_summary[method_summary['method']=='OneStage_RCS']['calibration'].values[0]),
           xytext=(0.5, 1), fontsize=9, style='italic',
           bbox=dict(boxstyle='round,pad=0.3', facecolor='lightcoral', alpha=0.7),
           arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=-0.3'))

plt.tight_layout()
plt.savefig(output_dir / 'Figure_2_Precision_Validity_Tradeoff.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_2_Precision_Validity_Tradeoff.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_2_Precision_Validity_Tradeoff.png'}")

# =============================================================================
# FIGURE 3: Method Selection Flowchart (Text-based for now)
# =============================================================================
print("\nFigure 3: Method Selection Flowchart...")

fig, ax = plt.subplots(figsize=(14, 10))
ax.axis('off')

# Create flowchart using matplotlib patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def add_box(ax, x, y, width, height, text, color='lightblue', fontsize=10):
    box = FancyBboxPatch((x, y), width, height,
                         boxstyle="round,pad=0.1",
                         facecolor=color, edgecolor='black', linewidth=2)
    ax.add_patch(box)
    ax.text(x + width/2, y + height/2, text,
           ha='center', va='center', fontsize=fontsize, fontweight='bold',
           wrap=True)

def add_arrow(ax, x1, y1, x2, y2, label=''):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                           arrowstyle='->', mutation_scale=20,
                           linewidth=2, color='black')
    ax.add_patch(arrow)
    if label:
        mid_x, mid_y = (x1+x2)/2, (y1+y2)/2
        ax.text(mid_x + 0.5, mid_y, label, fontsize=9,
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.9))

# Start
add_box(ax, 5, 9, 4, 0.8, 'START:\nDose-Response Meta-Analysis', 'lightgreen', 11)

# Goal question
add_arrow(ax, 7, 9, 7, 8)
add_box(ax, 5, 7, 4, 0.8, 'Primary Goal?', 'lightyellow', 10)

# Inference path
add_arrow(ax, 5, 7.4, 2, 6.5)
add_box(ax, 0.5, 5.5, 3, 0.8, 'INFERENCE\n(Hypothesis Testing)', 'lightcoral', 10)

# Sample size question
add_arrow(ax, 2, 5.5, 2, 4.5)
add_box(ax, 0.5, 3.5, 3, 0.8, 'k < 20 studies?', 'lightyellow', 10)

# k < 20: HKSJ
add_arrow(ax, 0.5, 3.9, -1, 3)
add_box(ax, -2.5, 2, 3, 0.8, 'Two-Stage DL\n+ HKSJ ✓', 'lightgreen', 11)

# k >= 20: DL
add_arrow(ax, 3.5, 3.9, 5.5, 3)
add_box(ax, 4.5, 2, 3, 0.8, 'Two-Stage DL\n(HKSJ optional)', 'lightblue', 10)

# Prediction path
add_arrow(ax, 9, 7.4, 12, 6.5)
add_box(ax, 10.5, 5.5, 3, 0.8, 'PREDICTION\n(Risk Assessment)', 'lightcoral', 10)

add_arrow(ax, 12, 5.5, 12, 4.5)
add_box(ax, 10.5, 3.5, 3, 0.8, 'One-Stage REML', 'lightblue', 11)

# Heterogeneity check
add_box(ax, 5, 1, 4, 0.8, 'I² < 25% AND\nQ-test p>0.10?', 'lightyellow', 10)

# Fixed-effects option
add_arrow(ax, 5, 1.4, 2, 2)
add_box(ax, 0.5, 0.2, 3, 0.6, 'Fixed-Effects OK', 'lightgreen', 9)

add_arrow(ax, 9, 1.4, 11.5, 2)
add_box(ax, 10.5, 0.2, 3, 0.6, 'Must use Random-Effects', 'lightcoral', 9)

# Title
ax.text(7, 10.2, 'Method Selection Decision Tree for Dose-Response Meta-Analysis',
       ha='center', fontsize=14, fontweight='bold')

ax.set_xlim(-3, 14)
ax.set_ylim(-0.5, 10.5)

plt.tight_layout()
plt.savefig(output_dir / 'Figure_3_Method_Selection_Flowchart.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_3_Method_Selection_Flowchart.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_3_Method_Selection_Flowchart.png'}")

# =============================================================================
# SUPPLEMENTARY FIGURE S1: Example Dose-Response Curves
# =============================================================================
print("\nSupplementary Figure S1: Example Dose-Response Curves...")

from dose_response_meta.simulation import DoseResponseSimulator

fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.flatten()

scenarios_config = {
    'Linear (Low Het)': DoseResponseSimulator.create_linear_curve(0.01),
    'Quadratic (Mod Het)': DoseResponseSimulator.create_quadratic_curve(0.01, -0.0001),
    'Logarithmic (High Het)': DoseResponseSimulator.create_logarithmic_curve(0.3),
    'Threshold (Mod Het)': DoseResponseSimulator.create_threshold_curve(50, 0.01),
    'U-Shaped (Mod Het)': DoseResponseSimulator.create_u_shaped_curve(50, 0.0002),
    'J-Shaped (Mod Het)': DoseResponseSimulator.create_j_shaped_curve(20, 0.01, 0.0002),
    'Dose-Dep Het': DoseResponseSimulator.create_quadratic_curve(0.01, -0.0001),
}

dose_grid = np.linspace(0, 100, 200)

for idx, (name, curve_func) in enumerate(scenarios_config.items()):
    if idx >= len(axes):
        break

    ax = axes[idx]

    # True curve
    y_true = curve_func(dose_grid)
    ax.plot(dose_grid, y_true, 'b-', linewidth=2.5, label='True Curve')

    # Add some example "studies"
    np.random.seed(42 + idx)
    for i in range(5):
        study_doses = np.random.uniform(10, 90, 4)
        study_doses = np.sort(study_doses)
        study_y = curve_func(study_doses) + np.random.normal(0, 0.15, 4)
        ax.scatter(study_doses, study_y, s=50, alpha=0.6, color=f'C{i}')

    ax.set_title(name, fontsize=11, fontweight='bold')
    ax.set_xlabel('Dose', fontsize=10)
    ax.set_ylabel('Log Relative Risk', fontsize=10)
    ax.grid(alpha=0.3, linestyle=':')
    ax.axhline(0, color='gray', linestyle='--', linewidth=1, alpha=0.5)

    if idx == 0:
        ax.legend(fontsize=9)

# Hide extra subplot
if len(scenarios_config) < len(axes):
    axes[-1].axis('off')
    axes[-2].axis('off')

fig.suptitle('Example Dose-Response Curves for Each Scenario',
            fontsize=14, fontweight='bold', y=0.995)

plt.tight_layout()
plt.savefig(output_dir / 'Figure_S1_Example_Curves.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_S1_Example_Curves.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_S1_Example_Curves.png'}")

# =============================================================================
# SUPPLEMENTARY FIGURE S2: Coverage Distribution
# =============================================================================
print("\nSupplementary Figure S2: Coverage Distribution...")

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for idx, method in enumerate(['TwoStage_RCS_DL_HKSJ', 'TwoStage_RCS_Fixed', 'OneStage_RCS']):
    ax = axes[idx]

    method_data = detailed_conv[detailed_conv['method'] == method]

    # Histogram
    ax.hist(method_data['coverage'], bins=20, alpha=0.7,
           color=['#2E7D32', '#F57C00', '#C62828'][idx], edgecolor='black')

    # Target line
    ax.axvline(95, color='black', linestyle='--', linewidth=2, label='Target (95%)')
    ax.axvspan(90, 98, alpha=0.2, color='green', label='Acceptable Range')

    # Mean line
    mean_cov = method_data['coverage'].mean()
    ax.axvline(mean_cov, color='red', linestyle='-', linewidth=2,
              label=f'Mean ({mean_cov:.1f}%)')

    ax.set_xlabel('Coverage Probability (%)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')

    method_names = {
        'TwoStage_RCS_DL_HKSJ': 'Two-Stage DL + HKSJ',
        'TwoStage_RCS_Fixed': 'Two-Stage Fixed',
        'OneStage_RCS': 'One-Stage REML'
    }
    ax.set_title(method_names[method], fontsize=12, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle=':')

fig.suptitle('Distribution of Coverage Probability Across Simulations',
            fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'Figure_S2_Coverage_Distribution.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_S2_Coverage_Distribution.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_S2_Coverage_Distribution.png'}")

# =============================================================================
# SUPPLEMENTARY FIGURE S3: MSE vs Coverage Tradeoff
# =============================================================================
print("\nSupplementary Figure S3: MSE vs Coverage Tradeoff...")

fig, ax = plt.subplots(figsize=(10, 8))

# Aggregate by scenario and method
scenario_summary = detailed_conv.groupby(['scenario', 'method']).agg({
    'mse': 'mean',
    'coverage': 'mean'
}).reset_index()

method_colors = {
    'TwoStage_RCS_DL_HKSJ': '#2E7D32',
    'TwoStage_RCS_Fixed': '#F57C00',
    'OneStage_RCS': '#C62828'
}

method_markers = {
    'TwoStage_RCS_DL_HKSJ': 'o',
    'TwoStage_RCS_Fixed': 's',
    'OneStage_RCS': '^'
}

for method in scenario_summary['method'].unique():
    method_data = scenario_summary[scenario_summary['method'] == method]
    ax.scatter(method_data['mse'], method_data['coverage'],
              s=150, alpha=0.7, color=method_colors[method],
              marker=method_markers[method],
              label=method.replace('_', ' '), edgecolors='black', linewidth=1.5)

# Ideal zone
ax.axhspan(90, 98, alpha=0.1, color='green', zorder=0)
ax.axhline(95, color='black', linestyle='--', linewidth=1.5, label='Target Coverage', zorder=0)

ax.set_xlabel('Mean Squared Error (MSE)\nLower = Better Point Estimates',
             fontsize=12, fontweight='bold')
ax.set_ylabel('Coverage Probability (%)\nTarget: 95%',
             fontsize=12, fontweight='bold')
ax.set_title('MSE vs. Coverage Tradeoff by Method and Scenario',
            fontsize=13, fontweight='bold', pad=15)

ax.set_xscale('log')
ax.legend(loc='lower right', fontsize=10)
ax.grid(True, alpha=0.3, linestyle=':')

# Annotate ideal zone
ax.text(0.001, 96, 'Ideal Zone:\nLow MSE + Valid Coverage',
       fontsize=10, style='italic',
       bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

plt.tight_layout()
plt.savefig(output_dir / 'Figure_S3_MSE_vs_Coverage.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_S3_MSE_vs_Coverage.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_S3_MSE_vs_Coverage.png'}")

# =============================================================================
# SUPPLEMENTARY FIGURE S4: Interval Score Components
# =============================================================================
print("\nSupplementary Figure S4: Interval Score Components...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# S4A: Sharpness by scenario
ax = axes[0, 0]
sharpness_data = detailed_conv.pivot_table(
    values='sharpness', index='scenario', columns='method', aggfunc='mean'
)
sharpness_data.plot(kind='bar', ax=ax, color=['#2E7D32', '#F57C00', '#C62828'])
ax.set_title('A. Sharpness (Interval Width) by Scenario', fontsize=11, fontweight='bold')
ax.set_ylabel('Sharpness', fontsize=10, fontweight='bold')
ax.set_xlabel('')
ax.legend(title='Method', fontsize=8, title_fontsize=9)
ax.set_xticklabels([s[:15] for s in sharpness_data.index], rotation=45, ha='right', fontsize=9)
ax.grid(axis='y', alpha=0.3)

# S4B: Calibration by scenario
ax = axes[0, 1]
calibration_data = detailed_conv.pivot_table(
    values='calibration', index='scenario', columns='method', aggfunc='mean'
)
calibration_data.plot(kind='bar', ax=ax, color=['#2E7D32', '#F57C00', '#C62828'])
ax.set_title('B. Calibration (Miscoverage Penalty) by Scenario', fontsize=11, fontweight='bold')
ax.set_ylabel('Calibration Penalty', fontsize=10, fontweight='bold')
ax.set_xlabel('')
ax.legend(title='Method', fontsize=8, title_fontsize=9)
ax.set_xticklabels([s[:15] for s in calibration_data.index], rotation=45, ha='right', fontsize=9)
ax.axhline(0, color='green', linestyle='--', linewidth=1.5, label='Perfect Calibration')
ax.grid(axis='y', alpha=0.3)

# S4C: Total Interval Score
ax = axes[1, 0]
is_data = detailed_conv.pivot_table(
    values='interval_score', index='scenario', columns='method', aggfunc='mean'
)
is_data.plot(kind='bar', ax=ax, color=['#2E7D32', '#F57C00', '#C62828'])
ax.set_title('C. Total Interval Score by Scenario', fontsize=11, fontweight='bold')
ax.set_ylabel('Interval Score (Lower = Better)', fontsize=10, fontweight='bold')
ax.set_xlabel('Scenario', fontsize=10, fontweight='bold')
ax.legend(title='Method', fontsize=8, title_fontsize=9)
ax.set_xticklabels([s[:15] for s in is_data.index], rotation=45, ha='right', fontsize=9)
ax.set_yscale('log')
ax.grid(axis='y', alpha=0.3)

# S4D: Relationship between sharpness and calibration
ax = axes[1, 1]
for method in detailed_conv['method'].unique():
    method_data = detailed_conv[detailed_conv['method'] == method]
    ax.scatter(method_data['sharpness'], method_data['calibration'],
              s=20, alpha=0.5, color=method_colors[method],
              label=method.replace('_', ' '))

ax.set_xlabel('Sharpness', fontsize=10, fontweight='bold')
ax.set_ylabel('Calibration', fontsize=10, fontweight='bold')
ax.set_title('D. Sharpness vs. Calibration (All Simulations)', fontsize=11, fontweight='bold')
ax.set_xscale('log')
ax.set_yscale('log')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

fig.suptitle('Interval Score Decomposition: Sharpness and Calibration Components',
            fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / 'Figure_S4_Interval_Score_Components.png', dpi=300, bbox_inches='tight')
plt.savefig(output_dir / 'Figure_S4_Interval_Score_Components.pdf', bbox_inches='tight')
plt.close()

print(f"  ✓ Saved: {output_dir / 'Figure_S4_Interval_Score_Components.png'}")

print("\n" + "="*80)
print("FIGURE GENERATION COMPLETE")
print("="*80)
print(f"\nAll figures saved to: {output_dir}")
print("\nMain Figures:")
print("  • Figure 1: Coverage by Scenario (bar plot)")
print("  • Figure 2: Precision-Validity Tradeoff (scatter plot)")
print("  • Figure 3: Method Selection Flowchart")
print("\nSupplementary Figures:")
print("  • Figure S1: Example Dose-Response Curves")
print("  • Figure S2: Coverage Distribution")
print("  • Figure S3: MSE vs Coverage Tradeoff")
print("  • Figure S4: Interval Score Components")
print("\nFormats: PNG (300 DPI) and PDF (vector)")
print("="*80)
