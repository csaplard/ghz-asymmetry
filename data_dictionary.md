# Data Dictionary - CSV File Format

## Overview

This document describes the structure and meaning of the CSV data files in this repository.

---

## File Descriptions

### 1. `quantum_campaign_log.csv`
**Description**: Main experimental data for 6-qubit GHZ entangled states  
**Rows**: 40 (4 configurations × 10 runs each)  
**Purpose**: Primary dataset for measuring spatially-resolved decoherence

### 2. `quantum_campaign_no_entanglement.csv`
**Description**: Control experiment with non-entangled product states  
**Rows**: 20 (fewer runs needed for baseline)  
**Purpose**: Establish baseline asymmetry from classical noise sources

### 3. `quantum_campaign_b3.csv`
**Description**: Null hypothesis validation (subsystem B disabled)  
**Rows**: 40 (4 configurations × 10 runs each)  
**Purpose**: Verify that asymmetry measurements are not statistical artifacts

---

## Column Definitions

### All CSV Files Share the Same Schema:

| Column Name | Data Type | Range | Description |
|-------------|-----------|-------|-------------|
| `backend` | String | - | IBM Quantum hardware backend name (e.g., "ibm_torino") |
| `run_label` | String | A/B/C/D | Circuit configuration identifier |
| `job_id` | String | - | Unique IBM Quantum job identifier for traceability |
| `global_stability (%)` | Float | 0-100 | Percentage of measurements with correct global parity |
| `local_A (%)` | Float | 0-100 | Percentage of measurements with correct subsystem A parity |
| `local_B (%)` | Float | 0-100 | Percentage of measurements with correct subsystem B parity |
| `asymmetry (%)` | Float | 0-100 | Absolute difference: \|local_A - local_B\| |
| `shots` | Integer | 8192 | Number of measurement repetitions per job |

---

## Configuration Labels

| Label | Description | Qubit Mapping | Subsystem A | Subsystem B |
|-------|-------------|---------------|-------------|-------------|
| **A** | Baseline | [0,1,2,3,4,5] | [0,1,2] | [3,4,5] |
| **B** | Rotation +1 | [1,2,3,4,5,0] | [1,2,3] | [4,5,0] |
| **C** | Rotation +2 | [2,3,4,5,0,1] | [2,3,4] | [5,0,1] |
| **D** | Interleaved | [0,1,2,3,4,5] | [0,2,4] | [1,3,5] |

---

## Metric Definitions

### Global Stability
**Formula**: P(|000000⟩) + P(|111111⟩)  
**Interpretation**: Measures how often the 6-qubit GHZ state collapses to the two expected basis states.  
**Range**: 0-100%  
**Higher is better**: Indicates lower overall decoherence

### Local Stability (A or B)
**Formula**: 1 - P(parity_error)  
**Interpretation**: Measures how often the 3-qubit subsystem parity measurement is correct.  
**Range**: 0-100%  
**Higher is better**: Indicates subsystem coherence is preserved

### Asymmetry Index
**Formula**: |Local_A - Local_B|  
**Interpretation**: Quantifies spatial inhomogeneity in decoherence.  
**Range**: 0-100%  
- **0%**: Perfectly symmetric decoherence
- **>0%**: Spatial asymmetry present

**Key Result**: Configuration D shows 1.88× higher asymmetry than Configuration B

---

## Data Quality Notes

### Experimental Parameters
- **Backend**: IBM Torino (127-qubit Eagle r3 processor)
- **Shots per run**: 8,192
- **Repetitions**: 10 per configuration (GHZ), 5 per configuration (control)
- **Total measurements**: ~819,200 quantum circuits executed
- **Optimization level**: 1 (balanced transpilation)

### Known Limitations
1. **Sample size**: n=10 per configuration limits statistical power for subtle effects
2. **Single backend**: Results specific to ibm_torino; cross-device comparison needed
3. **6-qubit scale**: Effects may be more pronounced in larger systems

---

## Statistical Summary

### GHZ States (`quantum_campaign_log.csv`)

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| **Global Stability** | 80.71% | 1.99% | 75.30% | 83.92% |
| **Local A** | 90.09% | 1.97% | 87.45% | 93.64% |
| **Local B** | 89.78% | 2.03% | 87.63% | 93.24% |
| **Asymmetry** | 1.79% | 1.17% | 0.32% | 5.21% |

### Product States (`quantum_campaign_no_entanglement.csv`)

| Metric | Mean | Std Dev | Min | Max |
|--------|------|---------|-----|-----|
| **Global Stability** | 80.93% | 1.65% | 77.90% | 83.67% |
| **Asymmetry** | 1.49% | 1.22% | 0.14% | 4.82% |

### B3 Validation (`quantum_campaign_b3.csv`)

| Metric | Expected | Observed | Status |
|--------|----------|----------|--------|
| **Local B** | 0.00% | 0.00 ± 0.00% | ✅ Validated |
| **Asymmetry** | High | Variable | ✅ Expected (only A measured) |

---

## Data Integrity Verification

All CSV files have been validated against the paper's reported statistics:

```python
import pandas as pd

# Load data
ghz = pd.read_csv('quantum_campaign_log.csv')

# Verify sample size
assert len(ghz) == 40, "Expected 40 GHZ runs"

# Verify mean values (within rounding error)
assert abs(ghz['global_stability (%)'].mean() - 80.71) < 0.01
assert abs(ghz['asymmetry (%)'].mean() - 1.79) < 0.01

print("✅ Data integrity verified!")
```

---

## Usage Examples

### Load and Analyze Data

```python
import pandas as pd
import numpy as np

# Load GHZ data
df = pd.read_csv('data/quantum_campaign_log.csv')

# Calculate configuration-specific statistics
config_stats = df.groupby('run_label').agg({
    'global_stability (%)': ['mean', 'std'],
    'asymmetry (%)': ['mean', 'std']
})

print(config_stats)

# Compare configurations
config_A = df[df['run_label'] == 'A']['asymmetry (%)']
config_D = df[df['run_label'] == 'D']['asymmetry (%)']

print(f"Config D / Config A ratio: {config_D.mean() / config_A.mean():.2f}×")
# Expected output: ~1.09× (D is 2.25% vs A is 2.07%)
```

### Visualize Asymmetry Distribution

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
ghz = pd.read_csv('data/quantum_campaign_log.csv')
control = pd.read_csv('data/quantum_campaign_no_entanglement.csv')

# Plot
plt.figure(figsize=(10, 6))
sns.histplot(ghz['asymmetry (%)'], label='GHZ States', kde=True, alpha=0.6)
sns.histplot(control['asymmetry (%)'], label='Product States', kde=True, alpha=0.6)
plt.xlabel('Local Asymmetry Index (%)')
plt.ylabel('Frequency')
plt.legend()
plt.title('Spatial Asymmetry Distribution')
plt.show()
```

---

## Citation

If you use this data, please cite:

```bibtex
@article{csaplar2026spatially,
  title={Spatially Resolved Decoherence in Multi-Qubit GHZ States: 
         Topological Noise Fingerprinting on IBM Quantum Hardware},
  author={Csapl{\'a}r, Daniel},
  journal={arXiv preprint arXiv:2602.XXXXX},
  year={2026}
}
```

---

## Contact

For questions about the data:
- **Email**: csaplar.d@gmail.com
- **GitHub**: [@csaplard](https://github.com/csaplard)
- **ORCID**: [0009-0000-7362-7232](https://orcid.org/0009-0000-7362-7232)

---

**Last Updated**: February 2026  
**Data Version**: 1.0  
**Status**: Final - Validated against published paper
