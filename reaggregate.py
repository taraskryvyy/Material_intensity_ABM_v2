import pandas as pd
import numpy as np
import gc

input_file = "results_full_all_sims.csv"
output_file = "results.csv"

print("Loading dataset...")
# Load only needed columns to save memory if needed, but it's fine to load all
df = pd.read_csv(input_file)

print("Aggregating...")
if 'Imputed' in df.columns:
    agg_df = df.groupby(['Metric', 'Scenario', 'Timestep Number']).agg(
        mean=('Value', 'mean'),
        std=('Value', 'std'),
        count=('Value', 'count'),
        imputed_count=('Imputed', 'sum')
    ).reset_index()
else:
    agg_df = df.groupby(['Metric', 'Scenario', 'Timestep Number'])['Value'].agg(['mean', 'std', 'count']).reset_index()
    
agg_df['se'] = agg_df['std'] / np.sqrt(agg_df['count'])
agg_df['se'] = agg_df['se'].fillna(0)

print("Saving aggregated results...")
agg_df.to_csv(output_file, index=False)

print("Done.")
