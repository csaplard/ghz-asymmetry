"""
Non-Entangled Control Experiment for GHZ Asymmetry Study
Author: Daniel Csaplár
Description: Generates product states (H on all qubits, no CNOT entanglement)
             to establish baseline asymmetry from readout/gate errors alone.
"""

import os
import csv
import time
import numpy as np
from collections import Counter
from datetime import datetime
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler

# --- Configuration ---
SHOTS = 8192
CAMPAIGN_LOG_FILE = "quantum_campaign_no_entanglement.csv"
REPETITIONS = 5  # 5 runs per configuration

TOPOLOGIES = {
    "A": { # Baseline
        "ghz_indices": [0, 1, 2, 3, 4, 5],
        "local_a_indices": [0, 1, 2],
        "local_b_indices": [3, 4, 5]
    },
    "B": { # Rotation +1
        "ghz_indices": [1, 2, 3, 4, 5, 0],
        "local_a_indices": [1, 2, 3],
        "local_b_indices": [4, 5, 0]
    },
    "C": { # Rotation +2
        "ghz_indices": [2, 3, 4, 5, 0, 1],
        "local_a_indices": [2, 3, 4],
        "local_b_indices": [5, 0, 1]
    },
    "D": { # Interleaved
        "ghz_indices": [0, 1, 2, 3, 4, 5],
        "local_a_indices": [0, 2, 4],
        "local_b_indices": [1, 3, 5]
    }
}

# --- IBM Quantum Credentials ---
# IMPORTANT: Store credentials securely using environment variables or config file
# DO NOT hardcode credentials in production code!

# Option 1: Environment variables (recommended)
TOKEN = os.environ.get("IBM_QUANTUM_TOKEN")
CRN = os.environ.get("IBM_QUANTUM_CRN")

# Option 2: Load from local config file (add ibm_config.json to .gitignore!)
# import json
# with open("ibm_config.json", "r") as f:
#     config = json.load(f)
#     TOKEN = config["token"]
#     CRN = config["crn"]

# Validate credentials are loaded
if not TOKEN or not CRN:
    raise ValueError(
        "IBM Quantum credentials not found! Set environment variables:\n"
        "  export IBM_QUANTUM_TOKEN='your_token_here'\n"
        "  export IBM_QUANTUM_CRN='your_crn_here'\n"
        "Or create ibm_config.json with {\"token\": \"...\", \"crn\": \"...\"}"
    )

def get_backend():
    """Connect to IBM Quantum and select optimal backend."""
    print("Connecting to IBM Quantum...")
    service = None
    
    # Try IBM Cloud first, then IBM Quantum Platform
    try:
        service = QiskitRuntimeService(channel="ibm_cloud", token=TOKEN, instance=CRN)
    except Exception as e:
        print(f"IBM Cloud failed: {e}, trying platform...")
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
        except Exception as e2:
            print(f"All connections failed: {e2}")
            return None, None

    # Preferred backends (in priority order)
    candidates = ["ibm_torino", "ibm_fez", "ibm_sherbrooke", "ibm_brisbane", "ibm_kyoto", "ibm_osaka"]
    backend = None
    
    for name in candidates:
        try:
            b = service.backend(name)
            status = b.status()
            if status.operational and status.pending_jobs < 500:
                backend = b
                print(f"Selected priority backend: {backend.name}")
                break
        except:
            continue
            
    if backend is None:
        print("Priority backends unavailable or busy, selecting least busy...")
        backend = service.least_busy(simulator=False, operational=True)
        
    print(f"Final Backend: {backend.name}")
    return service, backend

def build_circuit(config):
    """
    Build quantum circuit for NON-ENTANGLED control experiment.
    
    Circuit architecture:
    - 9 qubits total: 6 data qubits + 3 ancilla qubits
    - Qubits 0-5: Data qubits (product state |+⟩^⊗6 - NO entanglement)
    - Qubit 6: Global parity ancilla
    - Qubit 7: Local A parity ancilla
    - Qubit 8: Local B parity ancilla
    
    Key difference from GHZ circuit:
    - GHZ: H on qubit 0, then CNOT ladder → maximal entanglement
    - This: H on ALL qubits, NO CNOTs → product state (control)
    """
    qc = QuantumCircuit(9, 9)
    
    ghz_nodes = config["ghz_indices"]
    loc_a_nodes = config["local_a_indices"]
    loc_b_nodes = config["local_b_indices"]

    # --- Prepare product state |+⟩^⊗6 (NO entanglement) ---
    for q in ghz_nodes:
        qc.h(q)

    # --- Global parity measurement ---
    for q in ghz_nodes:
        qc.cx(q, 6)

    # --- Local A parity measurement ---
    for q in loc_a_nodes:
        qc.cx(q, 7)

    # --- Local B parity measurement ---
    for q in loc_b_nodes:
        qc.cx(q, 8)

    # --- Measure all qubits ---
    qc.measure(range(9), range(9))
    return qc

def analyze_results(counts, config):
    """
    Analyze measurement results and calculate stability metrics.
    
    Returns:
    - G: Global stability (parity check correctness)
    - LA: Local A stability
    - LB: Local B stability
    - AI: Asymmetry index |LA - LB|
    - H: Shannon entropy of measurement distribution
    """
    total = sum(counts.values())
    if total == 0: 
        return 0, 0, 0, 0, 0
    
    global_ok = 0
    localA_ok = 0
    localB_ok = 0
    
    ghz_nodes = config["ghz_indices"]
    loc_a_nodes = config["local_a_indices"]
    loc_b_nodes = config["local_b_indices"]

    probs = []
    
    for state, c in counts.items():
        p = c / total
        if p > 0: 
            probs.append(p)
        
        # Handle bitstring format
        if isinstance(state, int):
            bits = format(state, '09b')
        else:
            bits = state.replace(" ", "")
            
        bits_rev = bits[::-1]  # Qiskit bit ordering (LSB first)
        
        # Global parity check
        measured_ghz = [bits_rev[i] for i in ghz_nodes]
        computed_global = measured_ghz.count("1") % 2
        measured_global_ancilla = int(bits_rev[6])
        if measured_global_ancilla == computed_global:
            global_ok += c
            
        # Local A parity check
        measured_locA = [bits_rev[i] for i in loc_a_nodes]
        computed_locA = measured_locA.count("1") % 2
        measured_locA_ancilla = int(bits_rev[7])
        if measured_locA_ancilla == computed_locA:
            localA_ok += c
            
        # Local B parity check
        measured_locB = [bits_rev[i] for i in loc_b_nodes]
        computed_locB = measured_locB.count("1") % 2
        measured_locB_ancilla = int(bits_rev[8])
        if measured_locB_ancilla == computed_locB:
            localB_ok += c
            
    G = global_ok / total
    LA = localA_ok / total
    LB = localB_ok / total
    AI = abs(LA - LB)
    
    # Shannon entropy
    entropy = -sum(pr * np.log2(pr) for pr in probs if pr > 0)
    
    return G, LA, LB, AI, entropy

def main():
    """Main campaign execution."""
    service, backend = get_backend()
    if not backend:
        print("CRITICAL: No backend found.")
        return

    # Initialize CSV log file
    file_exists = os.path.isfile(CAMPAIGN_LOG_FILE)
    if not file_exists:
        with open(CAMPAIGN_LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "backend", "run_label", "job_id", 
                "global_stability (%)", "local_A (%)", "local_B (%)", 
                "asymmetry (%)", "shots"
            ])

    submitted_jobs = []

    print(f"\n--- Starting Control Campaign: {REPETITIONS} runs per config (Total {4*REPETITIONS} jobs) ---")
    sampler = Sampler(mode=backend)

    # 1. JOB SUBMISSION PHASE
    for run_label, config in TOPOLOGIES.items():
        for i in range(1, REPETITIONS + 1):
            print(f"Preparing {run_label} - Run {i}/{REPETITIONS}...")
            qc = build_circuit(config)
            t_qc = transpile(qc, backend, optimization_level=1)
            
            try:
                job = sampler.run([t_qc], shots=SHOTS)
                job_id = job.job_id()
                print(f" -> Submitted! Job ID: {job_id}")
                submitted_jobs.append({
                    "job": job,
                    "job_id": job_id,
                    "run_label": run_label,
                    "config": config,
                    "rep": i
                })
                time.sleep(1)  # Avoid rate limits
            except Exception as e:
                print(f" -> Submission FAILED: {e}")

    print("\n--- All jobs submitted. Waiting for results... ---")

    # 2. RESULT COLLECTION PHASE
    for entry in submitted_jobs:
        job = entry["job"]
        run_label = entry["run_label"]
        job_id = entry["job_id"]
        config = entry["config"]
        
        print(f"Waiting for Job {job_id} ({run_label})...")
        try:
            result = job.result()
            
            # Extract counts from result
            try:
                pub_result = result[0]
                data_bin = pub_result.data
                field_name = [f for f in dir(data_bin) if not f.startswith('_')][0]
                counts = getattr(data_bin, field_name).get_counts()
            except Exception as e:
                print(f"Error extracting counts for {job_id}: {e}")
                continue

            G, LA, LB, AI, H = analyze_results(counts, config)
            
            # Save to CSV
            row = [
                backend.name,
                run_label,
                job_id,
                f"{G*100:.2f}",
                f"{LA*100:.2f}",
                f"{LB*100:.2f}",
                f"{AI*100:.2f}",
                SHOTS
            ]
            
            with open(CAMPAIGN_LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                
            print(f" -> Done. G:{G*100:.1f}% AI:{AI*100:.1f}%")
            
        except Exception as e:
            print(f"Failed to retrieve/process job {job_id}: {e}")

    print("\n✅ Control Campaign Completed.")

if __name__ == "__main__":
    main()
