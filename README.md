# Spatially Resolved Decoherence in Multi-Qubit GHZ States

[![arXiv](https://img.shields.io/badge/arXiv-2602.XXXXX-b31b1b.svg)](https://arxiv.org/abs/2602.XXXXX)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.XXXX-blue.svg)](https://doi.org/10.5281/zenodo.18625124)

**Experimental investigation of spatially inhomogeneous decoherence in 6-qubit GHZ states on IBM Quantum hardware**

📄 [Read the paper](https://arxiv.org/abs/2602.XXXXX) | 📊 [View data](data/) | 💻 [Explore code](code/)

---

## 🎯 Overview

This repository contains the complete research dataset, analysis code, and manuscript for our study on **spatially resolved decoherence** in multi-qubit entangled states. We demonstrate that quantum decoherence exhibits measurable spatial asymmetry that varies by **1.88×** across different circuit configurations on IBM Quantum hardware.

### Key Findings

- **Spatial Asymmetry**: Multi-qubit entanglement does not decohere uniformly—different subsystems degrade at different rates
- **Hardware Fingerprints**: Asymmetry patterns are configuration-dependent and reveal hardware-specific noise signatures
- **Entanglement Enhancement**: GHZ states show 1.20× higher asymmetry than non-entangled controls
- **Configuration Sensitivity**: Asymmetry ranges from 1.20% (Config B) to 2.25% (Config D)

---

## 📁 Repository Structure

```
ghz-asymmetry/
├── paper/
│   ├── arxiv_paper.tex           # LaTeX manuscript
│   ├── arxiv_paper.pdf           # Compiled PDF
│   ├── fig1_main_results.png     # Figure 1 (300 DPI)
│   └── fig2_configuration_analysis.png  # Figure 2 (300 DPI)
├── data/
│   ├── quantum_campaign_log.csv          # Main GHZ experiments (40 runs)
│   ├── quantum_campaign_no_entanglement.csv  # Control experiments (20 runs)
│   ├── quantum_campaign_b3.csv           # Null hypothesis validation (40 runs)
│   └── data_dictionary.md                # Data format documentation
├── code/
│   ├── quantum_campaign_ghz.py           # Main GHZ state generation (TO ADD)
│   ├── quantum_campaign_control.py       # Non-entangled control experiments
│   ├── quantum_campaign_b3.py            # B3 null hypothesis validation
│   └── analysis_notebook.ipynb           # Data analysis and visualization
├── figures/
│   └── (Generated figures from analysis)
├── LICENSE.md                            # CC BY 4.0
├── README.md                             # This file
└── CITATION.cff                          # Citation metadata
```

---

## 🔬 Experimental Design

### Quantum Circuit Architecture

We construct 6-qubit GHZ states using the Hadamard-CNOT ladder:

```
|ψ₀⟩ = |000000⟩
|ψ₁⟩ = H₀|ψ₀⟩ = (|0⟩ + |1⟩)/√2 ⊗ |00000⟩
|ψ_GHZ⟩ = CNOT₀₁ · CNOT₁₂ · CNOT₂₃ · CNOT₃₄ · CNOT₄₅ |ψ₁⟩
```

### Subsystem Partitioning

- **Subsystem A**: Qubits {0, 1, 2}
- **Subsystem B**: Qubits {3, 4, 5}
- **Measurement**: Ancilla-assisted 3-qubit parity for each subsystem

### Configurations Tested

| Config | Description | Qubit Mapping | Key Feature |
|--------|-------------|---------------|-------------|
| **A** | Baseline | [0,1,2,3,4,5] | Standard linear chain |
| **B** | Rotation +1 | [1,2,3,4,5,0] | Shifted by 1 position |
| **C** | Rotation +2 | [2,3,4,5,0,1] | Shifted by 2 positions |
| **D** | Interleaved | [0,2,4] & [1,3,5] | Non-contiguous subsystems |

---

## 📊 Key Results

### Statistical Summary

| Metric | GHZ States | Product States | Ratio |
|--------|------------|----------------|-------|
| **Global Stability** | 80.71 ± 1.99% | 80.93 ± 1.65% | 0.997 |
| **Local Asymmetry** | 1.79 ± 1.17% | 1.49 ± 1.22% | 1.20× |
| **Local A Stability** | 90.09 ± 1.97% | 89.64 ± 2.09% | 1.005 |
| **Local B Stability** | 89.78 ± 2.03% | 90.66 ± 1.84% | 0.990 |

### Configuration Sensitivity

| Configuration | Asymmetry (%) | Std Dev (%) |
|---------------|---------------|-------------|
| **A (Baseline)** | 2.07 | ± 0.74 |
| **B (Rot +1)** | 1.20 | ± 0.66 |
| **C (Rot +2)** | 1.63 | ± 1.59 |
| **D (Interleaved)** | 2.25 | ± 1.30 |

**Configuration D exhibits 1.88× higher asymmetry than Configuration B**

---

## 🛠️ Reproducibility

### Requirements

```bash
# Python environment
python >= 3.8
qiskit >= 0.45.0
qiskit-ibm-runtime >= 0.15.0
numpy >= 1.21.0
pandas >= 1.3.0
matplotlib >= 3.5.0
seaborn >= 0.11.0
scipy >= 1.7.0
```

### Installation

```bash
# Clone repository
git clone https://github.com/csaplard/ghz-asymmetry.git
cd ghz-asymmetry

# Install dependencies
pip install -r requirements.txt

# Set up IBM Quantum credentials
# (See https://quantum.ibm.com/account)
```

### Running Experiments

```bash
# Main GHZ experiments (requires IBM Quantum access)
python code/quantum_campaign_ghz.py

# Control experiments (non-entangled)
python code/quantum_campaign_control.py

# B3 null hypothesis validation
python code/quantum_campaign_b3.py
```

### Data Analysis

```bash
# Launch Jupyter notebook for analysis
jupyter notebook code/analysis_notebook.ipynb
```

---

## 📈 Hardware Specifications

- **Backend**: IBM Quantum `ibm_torino` (127-qubit Eagle r3 processor)
- **Shots per run**: 8,192
- **Total runs**: 100 (40 GHZ + 20 control + 40 B3)
- **Total measurements**: ~819,200 quantum circuit executions
- **Optimization level**: 1 (balanced compilation)

---

## 📖 Citation

If you use this work, please cite:

```bibtex
@article{csaplar2026spatially,
  title={Spatially Resolved Decoherence in Multi-Qubit GHZ States: 
         Topological Noise Fingerprinting on IBM Quantum Hardware},
  author={Csaplár, Daniel},
  journal={arXiv preprint arXiv:2602.XXXXX},
  year={2026},
  url={https://arxiv.org/abs/2602.XXXXX}
}
```

### BibTeX (APA Style)
```bibtex
Csaplár, D. (2026). Spatially resolved decoherence in multi-qubit GHZ states: 
    Topological noise fingerprinting on IBM quantum hardware. 
    arXiv preprint arXiv:2602.XXXXX.
```

---

## 👤 Author

**Daniel Csaplár**  
Independent Researcher  
Kazincbarcika, Hungary

- 📧 Email: csaplar.d@gmail.com
- 🔗 ORCID: [0009-0000-7362-7232](https://orcid.org/0009-0000-7362-7232)
- 💼 GitHub: [@csaplard](https://github.com/csaplard)

---

## 🙏 Acknowledgments

This work was performed using IBM Quantum resources. We thank:

- **IBM Quantum** for providing open access to quantum hardware
- **Qiskit development team** for the open-source quantum computing framework
- **The quantum computing community** for discussions and feedback

---

## 📄 License

This work is licensed under a [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

- **Paper**: CC BY 4.0
- **Data**: CC BY 4.0  
- **Code**: MIT License

You are free to:
- **Share** — copy and redistribute the material
- **Adapt** — remix, transform, and build upon the material

Under the following terms:
- **Attribution** — You must give appropriate credit

---

## 🔗 Links

- [arXiv Preprint](https://arxiv.org/abs/2602.XXXXX) (UPDATE after submission)
- [IBM Quantum Experience](https://quantum.ibm.com/)
- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Author's ORCID](https://orcid.org/0009-0000-7362-7232)

---

## 📊 Repository Statistics

![GitHub stars](https://img.shields.io/github/stars/csaplard/ghz-asymmetry?style=social)
![GitHub forks](https://img.shields.io/github/forks/csaplard/ghz-asymmetry?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/csaplard/ghz-asymmetry?style=social)

---

**Last Updated**: February 2026  
**Repository Status**: ✅ Active | 📝 Paper Under Review
