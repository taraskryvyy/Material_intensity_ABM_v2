from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from scenarios import generate_scenarios
import json
import os
import subprocess
import sys
import time
import pandas as pd
import numpy as np

KEEP_INDIVIDUAL_RUNS = True


def backup_results_file(filename: str) -> None:
    src = Path(filename)
    if not src.exists():
        return
    counter = 0
    while True:
        candidate = Path(f"results{counter}.csv")
        if not candidate.exists():
            src.rename(candidate)
            print(f"{src.name} renamed to {candidate.name}")
            return
        counter += 1


def sanitize_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in name).strip("_")


def run_single_simulation(task):
    scenario_name, params_json, sim, output_file, flush_every = task
    cmd = [
        sys.executable,
        "simulation.py",
        scenario_name,
        params_json,
        str(sim),
        str(output_file),
        str(flush_every),
    ]
    completed = subprocess.run(cmd, capture_output=True, text=True)
    return scenario_name, sim, output_file, completed.returncode, completed.stdout, completed.stderr


def aggregate_csv_files(source_files, target_file):
    dfs = []
    for f in source_files:
        if Path(f).exists():
            df = pd.read_csv(f)
            dfs.append(df)
            
    if not dfs:
        return
        
    full_df = pd.concat(dfs, ignore_index=True)
    
    # Save the full version with all trajectories
    print("Saving full unaggregated results to results_full.csv...")
    full_df.to_csv("results_full.csv", index=False)
    
    # Check if this is the long format output from simulation.py
    # Expected columns: Metric, Scenario, Simulation Number, Timestep Number, Value
    if 'Metric' in full_df.columns and 'Value' in full_df.columns:
        # Aggregate by Metric, Scenario, Timestep Number
        agg_df = full_df.groupby(['Metric', 'Scenario', 'Timestep Number'])['Value'].agg(['mean', 'std', 'count']).reset_index()
        # Calculate standard error (std / sqrt(n))
        agg_df['se'] = agg_df['std'] / np.sqrt(agg_df['count'])
        # Fill NaN standard errors with 0 (e.g. if count is 1)
        agg_df['se'] = agg_df['se'].fillna(0)
        
        agg_df.to_csv(target_file, index=False)
    else:
        # Fallback if the format is different than expected
        full_df.to_csv(target_file, index=False)


if __name__ == "__main__":
    backup_results_file("results.csv")

    scenarios = generate_scenarios()
    
    print("Scheduled Scenarios:")
    for name in scenarios.keys():
        print(f"  - {name}")
    print()
    
    output_dir = Path(f"run_outputs_{time.strftime('%Y%m%d_%H%M%S')}")
    output_dir.mkdir(exist_ok=True)

    # Leave two logical cores free to keep the machine responsive.
    default_workers = max(1, min(6, (os.cpu_count() or 8) - 2))
    max_workers = int(os.getenv("ABM_MAX_WORKERS", default_workers))
    flush_every = int(os.getenv("ABM_FLUSH_EVERY", 25))

    tasks = []
    output_files = []
    for scenario_name, params in scenarios.items():
        params_json = json.dumps(params.to_dict())
        scenario_safe = sanitize_name(scenario_name)
        for sim in range(params.nrMonteCarlo["val"]):
            output_file = output_dir / f"{scenario_safe}_sim_{sim}.csv"
            output_files.append(output_file)
            tasks.append((scenario_name, params_json, sim, output_file, flush_every))

    print(f"Starting {len(tasks)} simulations with {max_workers} workers")
    failed = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_single_simulation, task) for task in tasks]
        for future in as_completed(futures):
            scenario_name, sim, output_file, rc, stdout, stderr = future.result()
            if rc != 0:
                failed.append((scenario_name, sim, rc, stderr))
                print(f"FAILED scenario={scenario_name}, sim={sim}, returncode={rc}")
                if stderr:
                    print(stderr)
            else:
                print(f"Completed scenario={scenario_name}, sim={sim} -> {output_file.name}")

    print("Aggregating output files...")
    aggregate_csv_files(output_files, "results.csv")
    
    if not KEEP_INDIVIDUAL_RUNS:
        print("Cleaning up unaggregated simulation runs...")
        for f in output_files:
            if f.exists():
                f.unlink()
        
    if failed:
        print(f"Finished with {len(failed)} failures.")
        sys.exit(1)
    else:
        print("All simulations completed successfully.")
