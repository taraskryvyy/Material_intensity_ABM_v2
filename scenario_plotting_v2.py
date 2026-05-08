import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from scenarios import scenarios

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

def load_data(filepath='results.csv'):
    """Load results from CSV, handling multilevel indexing appropriately."""
    print(f"Reading from {filepath}...")
    # The file has columns: Metric, Scenario, Timestep Number, mean, std, count, se
    df = pd.read_csv(filepath, index_col=['Scenario', 'Timestep Number', 'Metric'])
    new_order = ['Metric', 'Scenario', 'Timestep Number']
    df = df.reorder_levels(new_order)
    return df

def plot_metrics_to_pdfs(df):
    """Iterate through groups and create a separate PDF for each."""
    
    smooth_figs = [
        'Renewable Energy capital price', 
        "Average ore extraction cost", 
        "Material price", 
        "Bankruptcy rate", 
        "Total household dividend income", 
        "Electricity price",
        'Total GDP (Value Added)',
        'Final good GDP (Value Added)',
        'Material GDP (Value Added)',
        'Renewable Energy GDP (Value Added)',
        'Fossil Fuel Energy GDP (Value Added)',
        'Final good capital GDP (Value Added)',
        'Renewable Energy capital GDP (Value Added)',
        'Fossil Fuel Energy capital GDP (Value Added)',
        'Material capital GDP (Value Added)',
        'Mining GDP (Value Added)',
        # 'Ratio of total ore extraction cost to Total GDP (Value Added)',
        'Material inventory-to-sales ratio',
        'Total material sales (real)',
        'Total material sales (nominal)',
        'Renewable Energy market share'
    ]
    smooth_window = 10
    fig_size = (6, 4)
    errorbar_format = ("se", 1)
    
    # List of tuples defining all plots: (Metric_Name, Title, Y_Label, Y_Axis_Limits)
    plots_to_make = [
        ('Total GDP (Value Added)', 'Total GDP (Value Added)', 'Total GDP (Value Added)', None),
        ('Final good GDP (Value Added)', 'Final Good GDP (Value Added)', 'Final Good GDP (Value Added)', None),
        ('Material GDP (Value Added)', 'Material GDP (Value Added)', 'Material GDP (Value Added)', None),
        ('Renewable Energy GDP (Value Added)', 'Renewable Energy GDP (Value Added)', 'Renewable Energy GDP (Value Added)', None),
        ('Fossil Fuel Energy GDP (Value Added)', 'Fossil Fuel Energy GDP (Value Added)', 'Fossil Fuel Energy GDP (Value Added)', None),
        ('Final good capital GDP (Value Added)', 'Final Good Capital GDP (Value Added)', 'Final Good Capital GDP (Value Added)', None),
        ('Renewable Energy capital GDP (Value Added)', 'Renewable Energy Capital GDP (Value Added)', 'Renewable Energy Capital GDP (Value Added)', None),
        ('Fossil Fuel Energy capital GDP (Value Added)', 'Fossil Fuel Energy Capital GDP (Value Added)', 'Fossil Fuel Energy Capital GDP (Value Added)', None),
        ('Material capital GDP (Value Added)', 'Material Capital GDP (Value Added)', 'Material Capital GDP (Value Added)', None),
        ('Mining GDP (Value Added)', 'Mining GDP (Value Added)', 'Mining GDP (Value Added)', None),
        ('Average material buffer', 'Average Material Buffer', 'Average Material Buffer', None),
        ('Carbon tax', 'Carbon Tax', 'Carbon Tax', None),
        ('Carbon tax growthrate', 'Carbon Tax Growthrate', 'Carbon Tax Growthrate', (0, 0.02)),
        ('Transition risk index', 'Transition Risk Index', 'Transition Risk Index', None),
        ('Renewable Energy capital price', 'Renewable Energy Capital Price', 'Renewable Energy Capital Price', None),
        ('Net Renewable Energy NPV', 'Net Renewable Energy NPV', 'Net Renewable Energy NPV', None),
        ('Net Renewable Energy NPV', 'Net Renewable Energy NPV (zoomed in)', 'Net Renewable Energy NPV', 'auto_zoom'),
        ('Bankruptcy rate', 'Bankruptcy Rate', 'Bankruptcy Rate', None),
        ('NPL ratio', 'NPL Ratio', 'NPL Ratio', None),
        ('Total NPL balance', 'Total NPL balance', 'Total NPL balance', None),
        ('Commercial bank loan-to-deposit-ratio', 'Commercial bank loan-to-deposit-ratio', 'Commercial bank loan-to-deposit-ratio', None),
        ('Cumulative number of bankruptcies', 'Cumulative Number of Bankruptcies', 'Cumulative Number of Bankruptcies', None),
        ('Cumulative number of bankrupt material firms', 'Cumulative Number of Bankrupt Material Firms', 'Cumulative Number of Bankrupt Material Firms', None),
        ('Cumulative number of bankrupt final good firms', 'Cumulative Number of Bankrupt Final Good Firms', 'Cumulative Number of Bankrupt Final Good Firms', None),
        ('Final good output', 'Total Output', 'Total Output', None),
        ('Total consumption budget', 'Total Consumption Budget', 'Total Consumption Budget', None),
        ('Total household dividend income', 'Total Household Dividend Income', 'Total Household Dividend Income', None),
        ('Electricity price', 'Electricity Price', 'Electricity Price', None),
        ('Electricity price', 'Electricity Price (zoomed in)', 'Electricity Price', 'auto_zoom'),
        ('Weighted average sell price of final good', 'Weighted Average Sell Price of Final Good', 'Weighted Average Sell Price of Final Good', None),
        ('Weighted average sell price of final good', 'Weighted Average Sell Price of Final Good (zoomed in)', 'Weighted Average Sell Price of Final Good', 'auto_zoom2'),
        ('Total GDP (Value Added)', 'Total GDP (Value Added)', 'Total GDP (Value Added)', None),
        ('Fuel price', 'Fuel Price', 'Fuel Price', None),
        ('Renewable Energy market share', 'Renewable Energy Market Share', 'Renewable Energy Market Share', None),
        ('Material price', 'Material Price', 'Material Price', None),
        ('Material price', 'Material Price (zoomed in)', 'Material Price', 'auto_zoom'),
        ('Total material inventory', 'Total Material Inventory', 'Total Material Inventory', None),
        ('Material inventory-to-sales ratio', 'Material Inventory-to-Sales Ratio', 'Inventory / Sales Ratio', None),
        ('Material inventory-to-sales ratio', 'Material Inventory-to-Sales Ratio (zoomed in)', 'Inventory / Sales Ratio', 'auto_zoom_2'),
        ('Total material sales (real)', 'Total Material Sales (Real)', 'Total Material Sales', 'auto_zoom'),
        ('Total material sales (nominal)', 'Total Material Sales (Nominal)', 'Total Material Sales', 'auto_zoom'),
        ('Material inventory minus real sales', 'Material Inventory minus Real Sales', 'Inventory minus Sales', None),
        ('Average ore extraction cost', 'Average Ore Extraction Cost', 'Average Ore Extraction Cost', None),
        ('Total ore reserves', 'Total Ore Reserves', 'Total Ore Reserves', None),
        ('Number of active mining sites', 'Number of Active Mining Sites', 'Number of Active Mining Sites', None),
        ('Average reserves per active mining site', 'Average Reserves per Active Mining Site', 'Average Reserves per Active Mining Site', None),
        ('Material capital productivity', 'Material Capital Productivity', 'Material Capital Productivity', None),
        ('Final good capital productivity', 'Final Good Capital Productivity', 'Final Good Capital Productivity', None),
        ('Renewable Energy capital productivity', 'Renewable Energy Capital Productivity', 'Renewable Energy Capital Productivity', None),
        ('Fossil Fuel Energy capital productivity', 'Fossil Fuel Energy Capital Productivity', 'Fossil Fuel Energy Capital Productivity', None),

        ('Final good NPL balance', 'Final good NPL balance', 'NPL balance', None),
        ('Material NPL balance', 'Material NPL balance', 'NPL balance', None),
        ('Renewable Energy NPL balance', 'Renewable Energy NPL balance', 'NPL balance', None),
        ('Fossil Fuel Energy NPL balance', 'Fossil Fuel Energy NPL balance', 'NPL balance', None),
        ('Final good capital NPL balance', 'Final good capital NPL balance', 'NPL balance', None),
        ('Renewable Energy capital NPL balance', 'Renewable Energy capital NPL balance', 'NPL balance', None),
        ('Fossil Fuel Energy capital NPL balance', 'Fossil Fuel Energy capital NPL balance', 'NPL balance', None),
        ('Material capital NPL balance', 'Material capital NPL balance', 'NPL balance', None),

        ('Final good loan-to-deposit-ratio', 'Final good loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Material loan-to-deposit-ratio', 'Material loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Renewable Energy loan-to-deposit-ratio', 'Renewable Energy loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Fossil Fuel Energy loan-to-deposit-ratio', 'Fossil Fuel Energy loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Final good capital loan-to-deposit-ratio', 'Final good capital loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Renewable Energy capital loan-to-deposit-ratio', 'Renewable Energy capital loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Fossil Fuel Energy capital loan-to-deposit-ratio', 'Fossil Fuel Energy capital loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),
        ('Material capital loan-to-deposit-ratio', 'Material capital loan-to-deposit-ratio', 'loan-to-deposit-ratio', None),

        ('Final good NPL ratio', 'Final good NPL ratio', 'NPL ratio', None),
        ('Material NPL ratio', 'Material NPL ratio', 'NPL ratio', None),
        ('Renewable Energy NPL ratio', 'Renewable Energy NPL ratio', 'NPL ratio', None),
        ('Fossil Fuel Energy NPL ratio', 'Fossil Fuel Energy NPL ratio', 'NPL ratio', None),
        ('Final good capital NPL ratio', 'Final good capital NPL ratio', 'NPL ratio', None),
        ('Renewable Energy capital NPL ratio', 'Renewable Energy capital NPL ratio', 'NPL ratio', None),
        ('Fossil Fuel Energy capital NPL ratio', 'Fossil Fuel Energy capital NPL ratio', 'NPL ratio', None),
        ('Material capital NPL ratio', 'Material capital NPL ratio', 'NPL ratio', None),
        
        ('Final good average leverage ratio', 'Final good average leverage ratio', 'Average leverage ratio', None),
        ('Material average leverage ratio', 'Material average leverage ratio', 'Average leverage ratio', None),
        ('Renewable Energy average leverage ratio', 'Renewable Energy average leverage ratio', 'Average leverage ratio', None),
        ('Fossil Fuel Energy average leverage ratio', 'Fossil Fuel Energy average leverage ratio', 'Average leverage ratio', None),
        ('Final good capital average leverage ratio', 'Final good capital average leverage ratio', 'Average leverage ratio', None),
        ('Renewable Energy capital average leverage ratio', 'Renewable Energy capital average leverage ratio', 'Average leverage ratio', None),
        ('Fossil Fuel Energy capital average leverage ratio', 'Fossil Fuel Energy capital average leverage ratio', 'Average leverage ratio', None),
        ('Material capital average leverage ratio', 'Material capital average leverage ratio', 'Average leverage ratio', None),

        ('Material inventory-to-assets ratio', 'Material inventory-to-assets ratio', 'Inventory / Assets', None),
        ('Final good inventory-to-assets ratio', 'Final good inventory-to-assets ratio', 'Inventory / Assets', None),
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
                    # Use .copy() to avoid SettingWithCopyWarning
                    metric_df = group_df.loc[[metric]].copy()
                except KeyError:
                    print(f"Metric '{metric}' not found in data for group '{group_name}'. Skipping.")
                    continue
                
                if metric_df.empty:
                    print(f"Metric '{metric}' has no data for group '{group_name}'. Skipping.")
                    continue

                if metric in smooth_figs:
                    # Smooth the mean and se
                    metric_df['mean'] = metric_df.groupby('Scenario')['mean'].transform(
                        lambda x: x.rolling(smooth_window, min_periods=1).mean()
                    )
                    metric_df['se'] = metric_df.groupby('Scenario')['se'].transform(
                        lambda x: x.rolling(smooth_window, min_periods=1).mean()
                    )
                
                plt.figure(figsize=fig_size)
                
                # Reset index so we can access columns easily
                plot_df = metric_df.reset_index()
                
                scenarios_in_data = plot_df['Scenario'].unique()
                for scenario in scenarios_in_data:
                    scen_df = plot_df[plot_df['Scenario'] == scenario]
                    color = colors.get(scenario, 'blue') if colors else 'blue'
                    
                    x = scen_df['Timestep Number']
                    y = scen_df['mean']
                    y_err = scen_df['se']
                    
                    plt.plot(x, y, label=scenario, color=color)
                    plt.fill_between(x, y - y_err, y + y_err, color=color, alpha=0.2)
                
                plt.title(title)
                plt.xlabel('Timestep Number')
                plt.ylabel(ylabel)
                plt.legend(loc='best', fontsize='small')
                
                # Apply y-axis limits safely depending on the data
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
                print(f"Added '{title}' to PDF.")

if __name__ == '__main__':
    print("Initializing scenario plotting workflow...")
    try:
        df = load_data('results.csv')
        print("Generating plots and saving to PDFs...")
        plot_metrics_to_pdfs(df)
        print("Done! Saved PDFs successfully.")
    except FileNotFoundError:
        print("results.csv not found. Please ensure the simulation has been run and results are available.")
