from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from scenarios import generate_scenarios
import json
import os
import subprocess
import sys
import time


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


def merge_csv_files(source_files, target_file):
    header_written = False
    with open(target_file, "w", encoding="utf-8", newline="") as out_f:
        for source in source_files:
            if not Path(source).exists():
                continue
            with open(source, "r", encoding="utf-8", newline="") as in_f:
                for line_no, line in enumerate(in_f):
                    if line_no == 0:
                        if not header_written:
                            out_f.write(line)
                            header_written = True
                        continue
                    out_f.write(line)


if __name__ == "__main__":
    backup_results_file("results.csv")

    scenarios = generate_scenarios()
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

    if failed:
        print(f"{len(failed)} simulations failed. results.csv will not be merged.")
        sys.exit(1)

    merge_csv_files(output_files, "results.csv")
    print(f"Merged {len(output_files)} files into results.csv")
