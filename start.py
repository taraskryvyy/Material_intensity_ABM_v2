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
    
    if 'Metric' in full_df.columns and 'Value' in full_df.columns:
        if 'Imputed' in full_df.columns:
            # Aggregate by Metric, Scenario, Timestep Number, adding imputed_count
            agg_df = full_df.groupby(['Metric', 'Scenario', 'Timestep Number']).agg(
                mean=('Value', 'mean'),
                std=('Value', 'std'),
                count=('Value', 'count'),
                imputed_count=('Imputed', 'sum')
            ).reset_index()
        else:
            # Aggregate by Metric, Scenario, Timestep Number (backwards compatible)
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
    
    error_log_path = "error_log.csv"
    with open(error_log_path, "w", newline="", encoding="utf-8") as f:
        import csv
        writer = csv.writer(f)
        writer.writerow(["Scenario Name", "Simulation Number", "Timestep", "Error Message"])
        
    import concurrent.futures
    MAX_ATTEMPTS_PER_SCENARIO = 300
    total_attempts = {name: 0 for name in scenarios.keys()}
    future_to_task = {}
    active_futures = set()
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for task in tasks:
            scenario_name = task[0]
            future = executor.submit(run_single_simulation, task)
            future_to_task[future] = task
            active_futures.add(future)
            total_attempts[scenario_name] += 1
            
        while active_futures:
            done, _ = concurrent.futures.wait(active_futures, return_when=concurrent.futures.FIRST_COMPLETED)
            for future in done:
                active_futures.remove(future)
                task = future_to_task.pop(future)
                scenario_name, params_json, sim, output_file, flush_every = task
                
                try:
                    _, _, _, rc, stdout, stderr = future.result()
                except Exception as e:
                    rc = -1
                    stdout = ""
                    stderr = str(e)
                    
                if rc != 0:
                    if output_file.exists():
                        try:
                            output_file.unlink()
                        except Exception as e:
                            print(f"Warning: Could not delete incomplete file {output_file}: {e}")
                            
                    failed.append((scenario_name, sim, rc, stderr))
                    
                    # Extract the last timestep from stdout if available
                    import re
                    last_timestep = "Unknown"
                    matches = re.findall(r"TimeStep: (\d+)", stdout)
                    if matches:
                        last_timestep = matches[-1]
                    
                    print(f"FAILED scenario={scenario_name}, sim={sim}, timestep={last_timestep}, returncode={rc}")
                    if stderr:
                        print(stderr)
                        
                    # Append to error log
                    with open(error_log_path, "a", newline="", encoding="utf-8") as f:
                        import csv
                        writer = csv.writer(f)
                        writer.writerow([scenario_name, sim, last_timestep, stderr.strip()])
                        
                    # Retry logic
                    if total_attempts[scenario_name] < MAX_ATTEMPTS_PER_SCENARIO:
                        print(f"Retrying scenario={scenario_name}, sim={sim} (Total attempts for scenario so far: {total_attempts[scenario_name]})")
                        new_future = executor.submit(run_single_simulation, task)
                        future_to_task[new_future] = task
                        active_futures.add(new_future)
                        total_attempts[scenario_name] += 1
                    else:
                        print(f"ABORTING retries for scenario={scenario_name}, max attempts ({MAX_ATTEMPTS_PER_SCENARIO}) reached.")
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
