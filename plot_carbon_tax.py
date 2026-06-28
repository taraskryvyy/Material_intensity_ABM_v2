import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def load_data(filepath='results.csv'):
    print(f"Reading from {filepath}...")
    df = pd.read_csv(filepath)
    if 'Metric' in df.columns and 'Scenario' in df.columns and 'Timestep Number' in df.columns:
        df.set_index(['Metric', 'Scenario', 'Timestep Number'], inplace=True)
    return df

def generate_carbon_tax_plot():
    df = load_data('latest_results_agg_scenario_sims.csv')
    
    # Target metric
    metric = 'Carbon tax'
    
    # Target scenarios and their new names
    scenario_mapping = {
        "High tax / high expectations": "High tax",
        "Low tax / high expectations": "Low tax",
        "Baseline (no tax policy)": "Baseline (no tax policy)"
    }
    
    # Filter the dataframe for the specific metric
    try:
        metric_df = df.loc[[metric]].copy()
    except KeyError:
        print(f"Metric '{metric}' not found in data.")
        return

    # Filter for the scenarios we want
    plot_df = metric_df.reset_index()
    
    cut_timesteps = 25
    if cut_timesteps > 0:
        plot_df = plot_df[plot_df['Timestep Number'] >= cut_timesteps]
        
    plot_df = plot_df[plot_df['Scenario'].isin(scenario_mapping.keys())].copy()
    
    # Rename the scenarios
    plot_df['Scenario'] = plot_df['Scenario'].map(scenario_mapping)
    
    # Define colors
    colors = {
        "High tax": "red",
        "Low tax": "blue",
        "Baseline (no tax policy)": "gray"
    }

    pdf_path = 'carbon_tax_plot.pdf'
    print(f"Generating PDF -> {pdf_path}")
    
    with PdfPages(pdf_path) as pdf:
        plt.figure(figsize=(6, 4))
        
        scenarios_in_data = plot_df['Scenario'].unique()
        for scenario in scenarios_in_data:
            scen_df = plot_df[plot_df['Scenario'] == scenario]
            color = colors.get(scenario, 'black')
            
            x = scen_df['Timestep Number']
            y = scen_df['mean']
            
            plt.plot(x, y, label=scenario, color=color)
            if 'se' in scen_df.columns and not scen_df['se'].isnull().all():
                y_err = scen_df['se']
                plt.fill_between(x, y - y_err, y + y_err, color=color, alpha=0.2)
        
        plt.title('Carbon tax')
        plt.xlabel('Timestep Number')
        plt.ylabel('Carbon tax')
        plt.legend(loc='best', fontsize='small')
        
        plt.tight_layout()
        pdf.savefig()
        plt.close()
        print("Added 'Carbon tax' to PDF.")

if __name__ == '__main__':
    generate_carbon_tax_plot()
