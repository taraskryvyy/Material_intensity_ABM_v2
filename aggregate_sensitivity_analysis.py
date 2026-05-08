import pandas as pd
import glob
import os

# Set this to True to compute standard deviation of all final 50 timesteps directly,
# rather than the standard deviation of the time-means.
COMPUTE_STD_OVER_ALL_TIMESTEPS = True

def generate_sensitivity_table():
    results_file = 'sensi_results_full.csv'
    if not os.path.exists(results_file):
        print(f"No {results_file} file found. Please run the simulation first.")
        return
        
    print(f"Reading full simulation runs from {results_file}...")
    
    try:
        df = pd.read_csv(results_file)
        expected_cols = ['Metric', 'Scenario', 'Simulation Number', 'Timestep Number', 'Value']
        if not all(col in df.columns for col in expected_cols):
            print(f"Error: {results_file} does not contain the required columns {expected_cols}.")
            return
    except Exception as e:
        print(f"Error reading {results_file}: {e}")
        return
        
    combined_df = df
    
    # Target metrics
    target_metrics = [
        'Renewable Energy market share',
        'Average ore extraction cost',
        'Cumulative number of bankruptcies',
        'Total NPL balance',
        'Commercial bank loan-to-deposit-ratio'
    ]
    
    filtered_df = combined_df[combined_df['Metric'].isin(target_metrics)]
    if filtered_df.empty:
        print("No target metrics found.")
        return

    # Max timestep per scenario and sim
    max_timesteps = filtered_df.groupby(['Scenario', 'Simulation Number'])['Timestep Number'].max().reset_index()
    max_timesteps = max_timesteps.rename(columns={'Timestep Number': 'MaxTimestep'})
    merged_df = pd.merge(filtered_df, max_timesteps, on=['Scenario', 'Simulation Number'])
    
    # Last 50 timesteps
    last_50_df = merged_df[merged_df['Timestep Number'] > merged_df['MaxTimestep'] - 50].copy()
    
    if COMPUTE_STD_OVER_ALL_TIMESTEPS:
        # Mean and Std across ALL 50 timesteps across all simulations
        scenario_stats = last_50_df.groupby(['Scenario', 'Metric'])['Value'].agg(['mean', 'std']).reset_index()
    else:
        # 1. Mean over time for each individual simulation
        sim_means = last_50_df.groupby(['Scenario', 'Simulation Number', 'Metric'])['Value'].mean().reset_index()
        
        # 2. Mean and Std across simulations
        scenario_stats = sim_means.groupby(['Scenario', 'Metric'])['Value'].agg(['mean', 'std']).reset_index()
    
    table_mean = scenario_stats.pivot(index='Scenario', columns='Metric', values='mean')
    table_std = scenario_stats.pivot(index='Scenario', columns='Metric', values='std')
    
    final_table = pd.DataFrame(index=table_mean.index)
    
    def dynamic_round(val):
        if pd.isna(val):
            return "NaN"
        if val == 0:
            return "0.00"
        decimals = 2
        formatted = f"{val:.{decimals}f}"
        while float(formatted) == 0.0:
            decimals += 1
            formatted = f"{val:.{decimals}f}"
            if decimals > 10:
                break
        return formatted

    for col in target_metrics:
        if col in table_mean.columns:
            mean_str = table_mean[col].apply(dynamic_round)
            std_str = table_std[col].apply(dynamic_round)
            final_table[col] = mean_str + " (" + std_str + ")"
        else:
            final_table[col] = "N/A"
            
    print("\n\n" + "="*80)
    print("SENSITIVITY ANALYSIS RESULTS (Mean and Std Dev of means of last 50 timesteps)")
    print("="*80)
    print(final_table.to_string())
    
    final_table.to_csv('sensitivity_analysis_table.csv')
    print("\nSaved to sensitivity_analysis_table.csv")

if __name__ == "__main__":
    generate_sensitivity_table()
