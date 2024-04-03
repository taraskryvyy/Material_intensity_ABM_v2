from scenarios import generate_scenarios
import random
import os
import sys
import gc
import csv
import json
import subprocess

def rename_file(filename, counter=0):
    new_filename = f"results{counter}.csv"
    if os.path.exists(filename):
        if os.path.exists(new_filename):
            return rename_file(filename, counter+1)
        else:
            os.rename(filename, new_filename)
            print(f"{filename} renamed to {new_filename}")
    else:
        print(f"{filename} does not exist")

# call the function with the initial filename
if True:
    rename_file("results.csv")
print_output = False

random.seed(42)

scenarios = generate_scenarios()
# params = Parameters()

for scenario_name, params in scenarios.items():
      # params
      # attributes = [attr for attr in vars(params) if not attr.startswith('__')]

      print("#####################################################################")
      print("#####################################################################")
      print("#                       START OF SIMULATION                         #")
      print("#####################################################################")
      print("#####################################################################")

      for sim in range(params.nrMonteCarlo['val']):
          # script path /Users/tagger/Documents/GitHub/Material_intensity_ABM/Material_intensity_ABM/simulation.py
          # run the script here with arguments: scenario_name, params and sim
                  # Serialize the Parameters instance to JSON
            params_json = json.dumps(params.to_dict())

            # Construct the command to run the external script
            subprocess_command = [
                  "python",  # or "python3" depending on your system
                  "simulation.py",
                  scenario_name,
                  params_json,
                  str(sim),
            ]

            # Run the subprocess
            try:
                subprocess.run(subprocess_command, check=True)
            except subprocess.CalledProcessError as e:
                print(e.output)