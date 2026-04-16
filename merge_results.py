import os
import glob
from pathlib import Path
import pandas as pd

def find_latest_run_folder():
    """Finds the most recently created run_outputs directory."""
    folders = glob.glob('run_outputs_*')
    if not folders:
        return None
    # Sort folders by name descending (which includes the YYYYMMDD_HHMMSS timestamp)
    folders.sort(reverse=True)
    return Path(folders[0])

def detect_and_merge():
    """Detects failed simulations and merges only the successful ones into results.csv"""
    target_folder = find_latest_run_folder()
    if not target_folder:
        print("No run_outputs_* folders found.")
        return
    
    print(f"Scanning folder: {target_folder.name}")
    csv_files = list(target_folder.glob("*.csv"))
    if not csv_files:
        print("No CSV files found in the folder.")
        return
        
    print(f"Found {len(csv_files)} CSV files. Determining successful runs based on reached timesteps...")
    
    file_max_timesteps = {}
    global_max = -1
    
    # We figure out if a simulation succeeded by determining the max timestep it reached.
    # The true max timestep across all files will be considered the "successful" target line.
    for f in csv_files:
        try:
            # We only read the Timestep Number column to be extremely fast and memory-efficient
            df = pd.read_csv(f, usecols=['Timestep Number'])
            if not df.empty:
                max_t = df['Timestep Number'].max()
                file_max_timesteps[f] = max_t
                if max_t > global_max:
                    global_max = max_t
            else:
                file_max_timesteps[f] = -1
        except Exception as e:
            file_max_timesteps[f] = -1
            
    if global_max == -1:
        print("No valid timestep data found in the files. Exiting.")
        return
        
    successful_files = []
    failed_files = []
    
    for f in csv_files:
        if file_max_timesteps.get(f) == global_max:
            successful_files.append(f)
        else:
            failed_files.append(f)
            
    print(f"\nTarget successful timestep threshold: {global_max}")
    print(f"Detected {len(failed_files)} failed or incomplete simulations.")
    
    for f in failed_files:
        print(f"  --> [FAILED] {f.name} (reached step: {file_max_timesteps.get(f)})")
        
    print(f"\nMerging {len(successful_files)} successful simulations...")
    target_file = "results.csv"
    
    # Backup existing results.csv if it exists
    src = Path(target_file)
    if src.exists():
        counter = 0
        while True:
            candidate = Path(f"results{counter}.csv")
            if not candidate.exists():
                src.rename(candidate)
                print(f"Existing {src.name} was renamed to {candidate.name}")
                break
            counter += 1

    header_written = False
    with open(target_file, "w", encoding="utf-8", newline="") as out_f:
        for source in successful_files:
            with open(source, "r", encoding="utf-8", newline="") as in_f:
                for line_no, line in enumerate(in_f):
                    if line_no == 0:
                        if not header_written:
                            out_f.write(line)
                            header_written = True
                        continue
                    out_f.write(line)
                    
    print(f"\nSuccessfully merged {len(successful_files)} files into {target_file}")

if __name__ == "__main__":
    detect_and_merge()
