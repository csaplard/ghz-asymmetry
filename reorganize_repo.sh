#!/bin/bash
# ============================================================
# GHZ-Asymmetry Repository Reorganizer
# ============================================================
# Használat:
#   1. Másold ezt a scriptet a ghz-asymmetry repo mappájába
#   2. Futtasd: bash reorganize_repo.sh
#   3. Ellenőrizd, majd pushold: git push
# ============================================================

set -e

echo "🔧 GHZ-Asymmetry repo átszervezése..."
echo ""

# Ellenőrzés: git repo-ban vagyunk-e?
if [ ! -d ".git" ]; then
    echo "❌ HIBA: Nem git repo-ban vagy!"
    echo "   Futtasd előbb: git clone https://github.com/csaplard/ghz-asymmetry.git"
    echo "   Majd: cd ghz-asymmetry"
    exit 1
fi

# ============================================================
# 1. Mappák létrehozása
# ============================================================
echo "📁 Mappák létrehozása..."
mkdir -p paper
mkdir -p data
mkdir -p code
mkdir -p figures

# ============================================================
# 2. Papír fájlok áthelyezése
# ============================================================
echo "📄 Papír fájlok áthelyezése -> paper/"

if [ -f "arxiv_paper.tex" ]; then
    git mv arxiv_paper.tex paper/
    echo "   ✅ arxiv_paper.tex -> paper/"
fi

if [ -f "arxiv_paper.pdf" ]; then
    git mv arxiv_paper.pdf paper/
    echo "   ✅ arxiv_paper.pdf -> paper/"
fi

if [ -f "fig1_main_results.png" ]; then
    git mv fig1_main_results.png paper/
    echo "   ✅ fig1_main_results.png -> paper/"
fi

if [ -f "fig2_configuration_analysis.png" ]; then
    git mv fig2_configuration_analysis.png paper/
    echo "   ✅ fig2_configuration_analysis.png -> paper/"
fi

# ============================================================
# 3. Adat fájlok áthelyezése
# ============================================================
echo "📊 Adat fájlok áthelyezése -> data/"

if [ -f "quantum_campaign_log.csv" ]; then
    git mv quantum_campaign_log.csv data/
    echo "   ✅ quantum_campaign_log.csv -> data/"
fi

if [ -f "quantum_campaign_no_entanglement.csv" ]; then
    git mv quantum_campaign_no_entanglement.csv data/
    echo "   ✅ quantum_campaign_no_entanglement.csv -> data/"
fi

if [ -f "quantum_campaign_b3.csv" ]; then
    git mv quantum_campaign_b3.csv data/
    echo "   ✅ quantum_campaign_b3.csv -> data/"
fi

# ============================================================
# 4. Data dictionary létrehozása
# ============================================================
echo "📋 data_dictionary.md létrehozása..."

cat > data/data_dictionary.md << 'DATADICT'
# Data Dictionary

## quantum_campaign_log.csv
Main GHZ entanglement experiments (40 runs across 4 configurations).

| Column | Type | Description |
|--------|------|-------------|
| run_id | int | Unique run identifier |
| configuration | str | Circuit configuration (A, B, C, D) |
| shots | int | Number of measurement shots (8192) |
| global_stability | float | P(|000000⟩) + P(|111111⟩) as percentage |
| local_stability_A | float | Subsystem A local stability (%) |
| local_stability_B | float | Subsystem B local stability (%) |
| asymmetry_index | float | |S_local_A - S_local_B| as percentage |
| backend | str | IBM Quantum backend name |
| timestamp | str | Experiment execution time (UTC) |

## quantum_campaign_no_entanglement.csv
Non-entangled control experiments (20 runs). Same columns as above.
Initial state: |0⟩⊗6 (no Hadamard or CNOT gates applied).

## quantum_campaign_b3.csv
Null hypothesis validation (40 runs). Subsystem B measurements disabled
to confirm that asymmetry = 0 when no quantum information is present.
DATADICT

echo "   ✅ data/data_dictionary.md létrehozva"

# ============================================================
# 5. Code placeholder-ek létrehozása
# ============================================================
echo "💻 Code placeholder-ek létrehozása..."

cat > code/README.md << 'CODEREADME'
# Code

Quantum circuit generation and analysis scripts.

## Files

| File | Status | Description |
|------|--------|-------------|
| `quantum_campaign_ghz.py` | 🔜 Coming soon | Main GHZ state generation & measurement |
| `quantum_campaign_control.py` | 🔜 Coming soon | Non-entangled control experiments |
| `quantum_campaign_b3.py` | 🔜 Coming soon | B3 null hypothesis validation |
| `analysis_notebook.ipynb` | 🔜 Coming soon | Data analysis & figure generation |

## Requirements

```
python >= 3.8
qiskit >= 0.45.0
qiskit-ibm-runtime >= 0.15.0
numpy >= 1.21.0
pandas >= 1.3.0
matplotlib >= 3.5.0
seaborn >= 0.11.0
scipy >= 1.7.0
```

## Running Experiments

Requires IBM Quantum credentials. See [IBM Quantum](https://quantum.ibm.com/account).

```bash
pip install -r requirements.txt
python quantum_campaign_ghz.py
```
CODEREADME

echo "   ✅ code/README.md létrehozva"

# ============================================================
# 6. requirements.txt létrehozása
# ============================================================
echo "📦 requirements.txt létrehozása..."

cat > requirements.txt << 'REQS'
qiskit>=0.45.0
qiskit-ibm-runtime>=0.15.0
numpy>=1.21.0
pandas>=1.3.0
matplotlib>=3.5.0
seaborn>=0.11.0
scipy>=1.7.0
jupyter>=1.0.0
REQS

echo "   ✅ requirements.txt létrehozva"

# ============================================================
# 7. CITATION.cff létrehozása
# ============================================================
echo "📖 CITATION.cff létrehozása..."

cat > CITATION.cff << 'CITATION'
cff-version: 1.2.0
message: "If you use this work, please cite it as below."
type: article
title: "Spatially Resolved Decoherence in Multi-Qubit GHZ States: Topological Noise Fingerprinting on IBM Quantum Hardware"
authors:
  - family-names: "Csaplár"
    given-names: "Daniel"
    email: "csaplar.d@gmail.com"
    orcid: "https://orcid.org/0009-0000-7362-7232"
    affiliation: "Independent Researcher"
date-released: 2026-02-08
url: "https://github.com/csaplard/ghz-asymmetry"
repository-code: "https://github.com/csaplard/ghz-asymmetry"
license: MIT
keywords:
  - quantum computing
  - GHZ states
  - decoherence
  - IBM Quantum
  - spatial asymmetry
  - noise characterization
  - NISQ
CITATION

echo "   ✅ CITATION.cff létrehozva"

# ============================================================
# 8. Figures placeholder
# ============================================================
echo "🖼️  figures/ placeholder..."

cat > figures/README.md << 'FIGREADME'
# Figures

Generated figures from analysis notebook.
Publication-quality figures (300 DPI) are in `paper/`.
FIGREADME

echo "   ✅ figures/README.md létrehozva"

# ============================================================
# 9. README frissítése (repo structure szekció)
# ============================================================
echo "📝 README.md ellenőrzése..."
echo "   ⚠️  A README.md-ben a mappastruktúra már helyes."
echo "   ⚠️  DE ellenőrizd, hogy a linkek is frissültek-e:"
echo "      📊 View data -> /data"
echo "      💻 Explore code -> /code"
echo "      📄 Paper -> /paper"

# ============================================================
# 10. Git commit
# ============================================================
echo ""
echo "📦 Változások commitolása..."

git add -A
git commit -m "Reorganize repository: paper/, data/, code/ structure

- Move paper files (tex, pdf, figures) to paper/
- Move experimental data (CSV) to data/
- Add data dictionary (data/data_dictionary.md)
- Add code README with placeholder structure
- Add requirements.txt
- Add CITATION.cff
- Add figures/ placeholder"

echo ""
echo "============================================================"
echo "✅ KÉSZ! A repo átszervezve."
echo ""
echo "Következő lépések:"
echo "  1. Ellenőrizd: git log --oneline"
echo "  2. Ellenőrizd: git status"
echo "  3. Pushold:    git push"
echo ""
echo "⚠️  NE FELEJTSD EL:"
echo "  - A paper/ mappába töltsd fel az ARXIV_READY verziót!"
echo "  - A GitHub Settings-ben javítsd: 'Spatially' (nem 'patially')"
echo "  - Adj hozzá topic-okat: quantum-computing, ghz-state, decoherence"
echo "============================================================"
