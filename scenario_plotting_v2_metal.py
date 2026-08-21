import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from scenarios import scenarios as original_scenarios

# Process all scenarios dynamically to replace 'metal'/'Metal' with 'metal'/'Metal' in names and groups
scenarios = {}
for name, params in original_scenarios.items():
    new_name = name.replace('Metal', 'Metal').replace('metal', 'metal')
    new_params = {}
    for k, v in params.items():
        if k == 'group' and isinstance(v, str):
            new_params[k] = v.replace('Metal', 'Metal').replace('metal', 'metal')
        else:
            new_params[k] = v
    scenarios[new_name] = new_params

def get_scenario_colors(df):
    colors = {}
    for name, params_dict in scenarios.items():
        if isinstance(params_dict, dict) and "color" in params_dict:
            colors[name] = params_dict["color"]
        elif hasattr(params_dict, "color"):
            colors[name] = params_dict.color
            
    default_palette = sns.color_palette()
    all_scenarios = df.index.get_level_values('Scenario').unique()
    
    color_idx = 0
    for scenario in all_scenarios:
        if scenario not in colors:
            colors[scenario] = default_palette[color_idx % len(default_palette)]
            color_idx += 1
            
    return colors

def load_data(filepath='latest_results_agg_scenario_sims.csv'):
    """Load results from CSV, rename them, and handle multilevel indexing."""
    print(f"Reading from {filepath}...")
    df = pd.read_csv(filepath)
    
    # Rename scenarios (replace 'metal' with 'metal')
    df['Scenario'] = df['Scenario'].str.replace('Metal', 'Metal').str.replace('metal', 'metal')
    
    df.set_index(['Scenario', 'Timestep Number', 'Metric'], inplace=True)
    new_order = ['Metric', 'Scenario', 'Timestep Number']
    df = df.reorder_levels(new_order)
    return df

def plot_metrics_to_pdfs(df):
    """Iterate through groups and create a separate PDF for each."""
    
    smooth_figs = [
        'Renewable Energy capital price', 
        "Average ore extraction cost", 
        "Metal price", 
        "Bankruptcy rate", 
        "Total household dividend income", 
        "Electricity price",
        'Total GDP (Value Added)',
        'Final good GDP (Value Added)',
        'Metal GDP (Value Added)',
        'Renewable Energy GDP (Value Added)',
        'Fossil Fuel Energy GDP (Value Added)',
        'Final good capital GDP (Value Added)',
        'Renewable Energy capital GDP (Value Added)',
        'Fossil Fuel Energy capital GDP (Value Added)',
        'Metal capital GDP (Value Added)',
        'Mining GDP (Value Added)',
        # 'Ratio of total ore extraction cost to Total GDP (Value Added)',
        'Metal inventory-to-sales ratio',
        'Total metal sales (real)',
        'Total metal sales (nominal)',
        # 'Renewable Energy market share'
    ]
    smooth_window = 10
    cut_timesteps = 25
    fig_size = (6, 4)
    errorbar_format = ("se", 1)
    
    # List of tuples defining all plots: (Metric_Name, Title, Y_Label, Y_Axis_Limits)
    plots_to_make = [
        ('Renewable Energy capital price', 'Renewable Energy Capital Price', 'Renewable Energy Capital Price', None),
        ('Total NPL balance', 'Total NPL balance', 'Total NPL balance', None),
        ('Commercial bank loan-to-deposit-ratio', 'Commercial bank loan-to-deposit-ratio', 'Commercial bank loan-to-deposit-ratio', None),
        ('Cumulative number of bankruptcies', 'Cumulative Number of Bankruptcies', 'Cumulative Number of Bankruptcies', None),
        ('Cumulative number of bankrupt metal firms', 'Cumulative Number of Bankrupt Metal Firms', 'Cumulative Number of Bankrupt Metal Firms', None),
        ('Cumulative number of bankrupt final good firms', 'Cumulative Number of Bankrupt Final Good Firms', 'Cumulative Number of Bankrupt Final Good Firms', None),
        ('Total household dividend income', 'Total Household Dividend Income', 'Total Household Dividend Income', None),
        ('Fuel price', 'Fuel Price', 'Fuel Price', None),
        ('Renewable Energy market share', 'Renewable Energy Market Share', 'Renewable Energy Market Share', None),
        ('Metal price', 'Metal Price', 'Metal Price', None),
        ('Total metal inventory', 'Total Metal Inventory', 'Total Metal Inventory', None),
        ('Average ore extraction cost', 'Average Ore Extraction Cost', 'Average Ore Extraction Cost', None),
        ('Total ore reserves', 'Total Ore Reserves', 'Total Ore Reserves', None),
        ('Number of active mining sites', 'Number of Active Mining Sites', 'Number of Active Mining Sites', None),
        ('Average reserves per active mining site', 'Average Reserves per Active Mining site', 'Average Reserves per Active Mining Site', None),
        ('Final good NPL balance', 'Final good NPL balance', 'NPL balance', None),
        ('Metal NPL balance', 'Metal NPL balance', 'NPL balance', None),
        ('Renewable Energy NPL balance', 'Renewable Energy NPL balance', 'NPL balance', None),
        ('Fossil Fuel Energy NPL balance', 'Fossil Fuel Energy NPL balance', 'NPL balance', None),
        ('Metal average leverage ratio', 'Metal average leverage ratio', 'Average leverage ratio', None),
        ('Metal inventory-to-assets ratio', 'Metal inventory-to-assets ratio', 'Inventory / Assets', None),
        ('Final good output', 'Total Output', 'Total Output', None),
    ]

    import re
    def sanitize_filename(name):
        return re.sub(r'[\\/*?:"<>|]', "", name).replace(" ", "_").strip("_")
        
    groups = {}
    all_scenarios = df.index.get_level_values('Scenario').unique()
    for s_name in all_scenarios:
        s_group = "Ungrouped"
        if s_name in scenarios:
            params_dict = scenarios[s_name]
            if isinstance(params_dict, dict) and "group" in params_dict:
                s_group = params_dict["group"]
            elif hasattr(params_dict, "group"):
                s_group = params_dict.group
                
        if s_group not in groups:
            groups[s_group] = []
        groups[s_group].append(s_name)
        
    colors = get_scenario_colors(df)
    
    for group_name, group_scenarios in groups.items():
        group_mask = df.index.get_level_values('Scenario').isin(group_scenarios)
        group_df = df[group_mask].copy()
        
        pdf_path = f'scenarios_plots_{sanitize_filename(group_name)}.pdf'
        print(f"Generating PDF for group '{group_name}' -> {pdf_path}")
        
        with PdfPages(pdf_path) as pdf:
            for metric, title, ylabel, ylim in plots_to_make:
                try:
                    metric_df = group_df.loc[[metric]].copy()
                except KeyError:
                    print(f"Metric '{metric}' not found in data for group '{group_name}'. Skipping.")
                    continue
                
                if metric_df.empty:
                    print(f"Metric '{metric}' has no data for group '{group_name}'. Skipping.")
                    continue

                if metric in smooth_figs:
                    metric_df['mean'] = metric_df.groupby('Scenario')['mean'].transform(
                        lambda x: x.rolling(smooth_window, min_periods=1).mean()
                    )
                    metric_df['se'] = metric_df.groupby('Scenario')['se'].transform(
                        lambda x: x.rolling(smooth_window, min_periods=1).mean()
                    )
                
                plt.figure(figsize=fig_size)
                
                plot_df = metric_df.reset_index()
                
                if cut_timesteps > 0:
                    plot_df = plot_df[plot_df['Timestep Number'] >= cut_timesteps]
                
                scenarios_in_data = plot_df['Scenario'].unique()
                for scenario in scenarios_in_data:
                    scen_df = plot_df[plot_df['Scenario'] == scenario]
                    color = colors.get(scenario, 'blue') if colors else 'blue'
                    
                    x = scen_df['Timestep Number']
                    y = scen_df['mean']
                    y_err = scen_df['se']
                    
                    plt.plot(x, y, label=scenario, color=color)
                    plt.fill_between(x, y - y_err, y + y_err, color=color, alpha=0.2)
                
                display_title = title.replace('Metal', 'Metal').replace('metal', 'metal')
                display_ylabel = ylabel.replace('Metal', 'Metal').replace('metal', 'metal')
                plt.title(display_title)
                plt.xlabel('Timestep Number')
                plt.ylabel(display_ylabel)
                plt.legend(loc='best', fontsize='small')
                
                vals = metric_df['mean'].dropna()
                if len(vals) > 0:
                    if ylim == 'auto_zoom':
                        max_y = np.percentile(vals, 99)
                        min_y = np.min(vals)
                        plt.ylim(min_y, max_y)
                    elif ylim == 'auto_zoom2':
                        max_y = np.mean(vals) * 2
                        min_y = np.min(vals)
                        plt.ylim(min_y, max_y)
                    elif ylim is not None:
                        plt.ylim(ylim[0], ylim[1])
                    
                plt.tight_layout()
                pdf.savefig()
                plt.close()
                print(f"Added '{display_title}' to PDF.")

if __name__ == '__main__':
    print("Initializing scenario plotting workflow...")
    try:
        df = load_data('results.csv')#latest_results_agg_scenario_sims.csv')
        print("Generating plots and saving to PDFs...")
        plot_metrics_to_pdfs(df)
        print("Done! Saved PDFs successfully.")
    except FileNotFoundError:
        print("results.csv not found. Please ensure the simulation has been run and results are available.")
