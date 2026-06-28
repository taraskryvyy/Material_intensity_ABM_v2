import pandas as pd
import glob
import os

# Aggregation Methods:
# 1 = Academic Standard: Time-mean for each individual simulation, then mean and Standard Error (SE) across simulations.
# 2 = Time-mean for each individual simulation, then mean and Standard Deviation (SD) across simulations.
# 3 = Cross-sectional Pooled Variance: Mean and Variance per timestep across simulations, then pooled Standard Deviation.
# 4 = Pooled All: Mean and Std across ALL 50 final timesteps across all simulations pooled together.
AGGREGATION_METHOD = 1

def generate_sensitivity_table():
    # results_file = 'results_full.csv'
    # results_file = 'sensi_results_full_12052026_0004.csv'
    results_file = 'sensi_results_full_29052026_2240.csv'
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
    
    if AGGREGATION_METHOD == 1 or AGGREGATION_METHOD == 2:
        # 1. Mean over time for each individual simulation
        sim_means = last_50_df.groupby(['Scenario', 'Simulation Number', 'Metric'])['Value'].mean().reset_index()
        
        # 2. Mean and Std across simulations
        scenario_stats = sim_means.groupby(['Scenario', 'Metric'])['Value'].agg(['mean', 'std']).reset_index()
        
        if AGGREGATION_METHOD == 1:
            # =========================================================================
            # CONVERT STANDARD DEVIATION TO STANDARD ERROR (SE = SD / sqrt(N))
            # =========================================================================
            # Standard Deviation (SD) tells us how much the simulations vary from each other
            # (i.e. how volatile the model itself is).
            #
            # Standard Error (SE) tells us how precise our calculated overall average is.
            # Because we ran the simulation N times, we divide the SD by the square root
            # of N. This matches the approach used in previous academic papers to report
            # the confidence/precision of the sensitivity analysis means.
            # =========================================================================
            num_simulations = last_50_df['Simulation Number'].nunique()
            scenario_stats['std'] = scenario_stats['std'] / (num_simulations ** 0.5)

    elif AGGREGATION_METHOD == 3:
        # 1. Mean and Variance per timestep across simulations
        timestep_stats = last_50_df.groupby(['Scenario', 'Metric', 'Timestep Number'])['Value'].agg(['mean', 'var']).reset_index()
        
        # 2. Mean of means and Mean of variances across the 50 timesteps
        scenario_stats = timestep_stats.groupby(['Scenario', 'Metric'])[['mean', 'var']].mean().reset_index()
        
        # 3. Square root of pooled variance to get pooled standard deviation
        scenario_stats['std'] = scenario_stats['var'] ** 0.5

    elif AGGREGATION_METHOD == 4:
        # Mean and Std across ALL 50 timesteps across all simulations
        scenario_stats = last_50_df.groupby(['Scenario', 'Metric'])['Value'].agg(['mean', 'std']).reset_index()
    
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

    ordered_scenarios = [
        # Mining Site Exploration Probability
        'miningSiteExplorationProbability_0.1',
        'miningSiteExplorationProbability_0.25',
        'miningSiteExplorationProbability_0.5',
        'miningSiteExplorationProbability_0.9',
        # Average Ore Extraction Cost of a New Mine
        'oreCostParamOne_0.1',
        'oreCostParamOne_0.3',
        'oreCostParamOne_0.5',
        # Variance in Initial Ore Extraction Cost
        'sigmaOreCostParamOne_0.005',
        'sigmaOreCostParamOne_0.05',
        'sigmaOreCostParamOne_0.03',
        # Speed of Ore Cost Growth as Ore Deposit Gets Depleted
        'oreCostParamTwo_0.1',
        'oreCostParamTwo_0.5',
        'oreCostParamTwo_0.9',
        # Material Productivity of Renewable Energy Capital
        'recMaterialProductivity_0.9',
        'recMaterialProductivity_1.25',
        'recMaterialProductivity_2',
        # Material Productivity of Final Good Capital
        'fgcMaterialProductivity_0.9',
        'fgcMaterialProductivity_1',
        'fgcMaterialProductivity_2',
        # Useful Lifespan of Capital for Renewable Energy Sector
        'reCapitalLifeSpan_15',
        'reCapitalLifeSpan_20',
        'reCapitalLifeSpan_25',
        # Ore Productivity
        'oreProductivity_0.75',
        'oreProductivity_1',
        'oreProductivity_1.25',
        # Average Initial Ore Deposit of a New Mine
        'muOreDeposit_100',
        'muOreDeposit_150',
        'muOreDeposit_200',
        # Variance in Amount of Ore in a New Mine
        'sigmaSqOreDeposit_400',
        'sigmaSqOreDeposit_8000',
        'sigmaSqOreDeposit_16000',
        # Adaptive Expectation of Material Price
        'adaptiveExpectationMaterialPrice_0.1',
        'adaptiveExpectationMaterialPrice_0.5',
        'adaptiveExpectationMaterialPrice_0.9',
        # Logit Competition Parameter When Picking Mining Site
        'logitCompetitionParamMining_0.01',
        'logitCompetitionParamMining_10',
        'logitCompetitionParamMining_50',
        # Fuel Price Drift
        'fuelPriceDrift_0.0003',
        'fuelPriceDrift_0.002',
        'fuelPriceDrift_0.006',
        # Fuel Price Volatility
        'fuelPriceVolatility_0.00000001',
        'fuelPriceVolatility_0.00003',
        'fuelPriceVolatility_0.0009',
        # Loan Interest Rate
        'loanInterestRate_0.00001',
        'loanInterestRate_0.001',
        'loanInterestRate_0.05',
        # Critical value of leverage ratio, under which probability of granting loan falls below 0.5
        'loanParamCritLeverage_0.3',
        'loanParamCritLeverage_0.5',
        'loanParamCritLeverage_0.7',
        # Bank’s lending decision sensitivity to borrower’s leverage ratio
        'loanParamSpeedLeverage_5',
        'loanParamSpeedLeverage_10',
        'loanParamSpeedLeverage_25',
        # Maximum loan to deposit ratio of a bank
        'bnkMaxLoanToDepositRatio_0.5',
        'bnkMaxLoanToDepositRatio_0.9',
        'bnkMaxLoanToDepositRatio_1.2',
        'bnkMaxLoanToDepositRatio_2',
        'bnkMaxLoanToDepositRatio_5',
        'bnkMaxLoanToDepositRatio_500'
    ]

    existing_scenarios = [s for s in ordered_scenarios if s in final_table.index]
    extra_scenarios = [s for s in final_table.index if s not in ordered_scenarios]
    final_table = final_table.reindex(existing_scenarios + extra_scenarios)
            
    print("\n\n" + "="*80)
    if AGGREGATION_METHOD == 1:
        print("SENSITIVITY ANALYSIS RESULTS (Mean and Standard Error)")
    else:
        print("SENSITIVITY ANALYSIS RESULTS (Mean and Standard Deviation)")
    print("="*80)
    print(final_table.to_string())
    
    final_table.to_csv('sensitivity_analysis_table.csv')
    print("\nSaved to sensitivity_analysis_table.csv")

if __name__ == "__main__":
    generate_sensitivity_table()
