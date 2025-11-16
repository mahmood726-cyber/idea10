"""
Quick validation test with 20 simulations
"""
import sys
sys.path.insert(0, '/home/user/idea10')

from comprehensive_analysis_v2 import ComprehensiveAnalysis

print("Starting quick validation test (20 simulations)...")
print("This will take approximately 10-15 minutes")
print("="*80)

analysis = ComprehensiveAnalysis(
    n_simulations=20,  # Quick test
    n_studies_per_sim=15,
    output_dir='results/test_run'
)

analysis.run_complete_analysis()

print("\n" + "="*80)
print("QUICK TEST COMPLETE!")
print("Check results/test_run/ for outputs")
print("="*80)
