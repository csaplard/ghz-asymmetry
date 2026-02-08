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
CAMPAIGN_LOG_FILE = "quantum_campaign_b3.csv"
REPETITIONS = 5  # 5-10 runs requested, setting to 5

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

TOKEN = "cT8474Ek6aCULL-qpYMSOHRMLvA-zM1RlDUc4cYmqlH7"
CRN = "crn:v1:bluemix:public:quantum-computing:us-east:a/035af0b83a3746e7a2e291a5cda4a487:3157ad22-5763-4376-97c4-9aae94d3d930::"

def get_backend():
    print("Connecting to IBM Quantum...")
    service = None
    try:
        service = QiskitRuntimeService(channel="ibm_cloud", token=TOKEN, instance=CRN)
    except Exception as e:
        print(f"IBM Cloud failed: {e}, trying platform...")
        try:
            service = QiskitRuntimeService(channel="ibm_quantum_platform", token=TOKEN)
        except Exception as e2:
            print(f"All connections failed: {e2}")
            return None, None

    # Try specific backends requesting by user (preference order)
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

def classical_control_circuit(topology_map):
    """
    Classical control: NO entanglement.
    Same qubits, same ancilla parity checks.
    """
    qc = QuantumCircuit(8, 8)

    data_qubits = topology_map["data"]
    anc_global = topology_map["anc_global"]
    anc_local = topology_map["anc_local"]

    # Step 1: Prepare classical superposition (no entanglement)
    for q in data_qubits:
        qc.h(q)

    # Step 2: Global parity (same as GHZ version)
    for q in data_qubits:
        qc.cx(q, anc_global)

    # Step 3: Local parity (first half)
    for q in data_qubits[:3]:
        qc.cx(q, anc_local)

    # Step 4: Measurement
    for i in range(8):
        qc.measure(i, i)

    return qc

def get_ordered_data(config):
    ghz = config["ghz_indices"]
    loc_a = config["local_a_indices"]
    # Ensure loc_a is at the start so data_qubits[:3] in the circuit corresponds to LocA
    remaining = [x for x in ghz if x not in loc_a]
    return loc_a + remaining

def analyze_results(counts, data_qubits, anc_global, anc_local):
    total = sum(counts.values())
    if total == 0: return 0, 0, 0

    global_ok = 0
    localA_ok = 0
    
    # We need to map the output bits back to logical meaning.
    # The circuit has 8 qubits, measured 0..7 to 0..7.
    # Qiskit bitstring is reversed: bit 0 is rightmost.
    # Our logical indices:
    # data_qubits: list of 6 integers (part of 0..7 range? No, probably mapped to physical by transpile? 
    # Wait, the circuit uses indices passed in `topology_map`. 
    # We pass virtual 0..5 as data, 6 as global, 7 as local.
    # Logic in circuit: `qc = QuantumCircuit(8, 8)`. Indices 0..7.
    # `data_qubits` passed to function should be integers in 0..7.
    # `anc_global` = 6
    # `anc_local` = 7
    # So `data_qubits` must be [0,1,2,3,4,5] (reordered).
    
    # When analyzing:
    # bits_rev[i] corresponds to measurement of qubit i.
    
    for state, c in counts.items():
        if isinstance(state, int):
            bits = format(state, '08b')
        else:
            bits = state.replace(" ", "")
            # Pad if necessary? Usually standard length.
            
        bits_rev = bits[::-1] # bit 0 is at index 0
        
        # Check Global Parity
        # Sum of '1's in data_qubits vs anc_global
        measured_ghz = [bits_rev[i] for i in data_qubits]
        computed_global = measured_ghz.count("1") % 2
        measured_global_ancilla = int(bits_rev[anc_global])
        
        if measured_global_ancilla == computed_global:
            global_ok += c
            
        # Check Local Parity (first 3 of data_qubits vs anc_local)
        measured_locA = [bits_rev[i] for i in data_qubits[:3]]
        computed_locA = measured_locA.count("1") % 2
        measured_locA_ancilla = int(bits_rev[anc_local])
        
        if measured_locA_ancilla == computed_locA:
            localA_ok += c

    G = global_ok / total
    LA = localA_ok / total
    # Entropy? The user didn't explicitly ask for entropy in the B3 prompt but usually we track it.
    # But for now let's return metrics for CSV.
    
    return G, LA

def main():
    service, backend = get_backend()
    if not backend:
        print("CRITICAL: No backend found.")
        return

    # Initialize CSV if not exists
    file_exists = os.path.isfile(CAMPAIGN_LOG_FILE)
    if not file_exists:
        with open(CAMPAIGN_LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["backend", "run_label", "job_id", "global_stability (%)", "local_A (%)", "local_B (%)", "asymmetry (%)", "shots"])

    submitted_jobs = []

    print(f"\n--- Starting B3 Campaign: {REPETITIONS} runs per config ---")
    sampler = Sampler(mode=backend)

    # We use virtual indices 0..5 for data, 6 for global ancilla, 7 for local ancilla
    # But `data_qubits` needs to be permuted based on the topology logic
    # Wait, `get_ordered_data` returns physical indices from TOPOLOGIES?
    # No, TOPOLOGIES contains integers 0..5. These are virtual indices mapped to the circuit.
    # Yes, `TOPOLOGIES` definitions are just permutations of 0..5.
    # So `get_ordered_data` returns a list of integers from 0..5.
    
    # Standard virtual mapping for our 8-qubit circuit:
    # We will use indices 0..5 for the data qubits, 6 for Global, 7 for Local.
    # `get_ordered_data` gives us the *order* in which to apply `cx`.
    # BUT, `data_qubits` in `classical_control_circuit` are used as arguments to `cx`.
    # `qc.cx(q, anc_local)`
    # If `q` is 0, it means qubit 0.
    # So `get_ordered_data` effectively maps "logical role" to "virtual qubit index".
    # Result: Correct.
    
    ANC_GLOBAL = 6
    ANC_LOCAL = 7

    # 1. SUBMISSION PHASE
    for run_label, config in TOPOLOGIES.items():
        ordered_data = get_ordered_data(config)
        
        topology_map = {
            "data": ordered_data,
            "anc_global": ANC_GLOBAL,
            "anc_local": ANC_LOCAL
        }
        
        for i in range(1, REPETITIONS + 1):
            print(f"Preparing {run_label} - Run {i}/{REPETITIONS}...")
            # Build circuit
            qc = classical_control_circuit(topology_map)
            
            # Transpile
            t_qc = transpile(qc, backend, optimization_level=1)
            
            try:
                job = sampler.run([t_qc], shots=SHOTS)
                job_id = job.job_id()
                print(f" -> Submitted! Job ID: {job_id}")
                submitted_jobs.append({
                    "job": job,
                    "job_id": job_id,
                    "run_label": run_label,
                    "config": config, # Original config for ref if needed
                    "topology_map": topology_map, # Used for analysis
                    "rep": i
                })
                time.sleep(1) 
            except Exception as e:
                print(f" -> Submission FAILED: {e}")

    print("\n--- All jobs submitted. Waiting for results... ---")

    # 2. COLLECTION PHASE
    for entry in submitted_jobs:
        job = entry["job"]
        run_label = entry["run_label"]
        job_id = entry["job_id"]
        topo_map = entry["topology_map"]
        
        print(f"Waiting for Job {job_id} ({run_label})...")
        try:
            result = job.result()
            
            try:
                pub_result = result[0]
                data_bin = pub_result.data
                field_name = [f for f in dir(data_bin) if not f.startswith('_')][0]
                counts = getattr(data_bin, field_name).get_counts()
            except Exception as e:
                print(f"Error extracting counts for {job_id}: {e}")
                continue

            G, LA = analyze_results(counts, topo_map["data"], topo_map["anc_global"], topo_map["anc_local"])
            
            row = [
                backend.name,
                run_label,
                job_id,
                f"{G*100:.2f}",
                f"{LA*100:.2f}",
                "0.00", # Local B N/A
                "0.00", # Asymmetry N/A
                SHOTS
            ]
            
            with open(CAMPAIGN_LOG_FILE, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(row)
                
            print(f" -> Done. G:{G*100:.1f}% LA:{LA*100:.1f}%")
            
        except Exception as e:
            print(f"Failed to retrieve/process job {job_id}: {e}")

    print("\nB3 Campaign Completed.")

if __name__ == "__main__":
    main()
