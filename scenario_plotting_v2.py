import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

def load_data(filepath='results.csv'):
    """Load results from CSV, handling multilevel indexing appropriately."""
    print(f"Reading from {filepath}...")
    df = pd.read_csv(filepath, index_col=['Scenario', 'Simulation Number', 'Timestep Number', 'Metric'])
    new_order = ['Metric', 'Scenario', 'Simulation Number', 'Timestep Number']
    df = df.reorder_levels(new_order)
    return df

def plot_metrics_to_pdf(df, pdf_path='scenarios_plots_all.pdf'):
    """Iterate through the desired metrics and plot them, saving output to a single PDF."""
    
    smooth_figs = [
        'Renewable Energy capital price', 
        "Average ore extraction cost", 
        "Material price", 
        "Bankruptcy rate", 
        "Total household dividend income", 
        "Electricity price"
    ]
    smooth_window = 10
    fig_size = (6, 4)
    errorbar_format = ("se", 1)
    
    # List of tuples defining all plots: (Metric_Name, Title, Y_Label, Y_Axis_Limits)
    plots_to_make = [
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
        ('Fuel price', 'Fuel Price', 'Fuel Price', None),
        ('Renewable Energy market share', 'Renewable Energy Market Share', 'Renewable Energy Market Share', None),
        ('Material price', 'Material Price', 'Material Price', None),
        ('Material price', 'Material Price (zoomed in)', 'Material Price', 'auto_zoom'),
        ('Average ore extraction cost', 'Average Ore Extraction Cost', 'Average Ore Extraction Cost', None),
        ('Total ore reserves', 'Total Ore Reserves', 'Total Ore Reserves', None),
        ('Material capital productivity', 'Material Capital Productivity', 'Material Capital Productivity', None),
        ('Final good capital productivity', 'Final Good Capital Productivity', 'Final Good Capital Productivity', None),
        ('Renewable Energy capital productivity', 'Renewable Energy Capital Productivity', 'Renewable Energy Capital Productivity', None),
        ('Fossil Fuel Energy capital productivity', 'Fossil Fuel Energy Capital Productivity', 'Fossil Fuel Energy Capital Productivity', None),
    ]

    with PdfPages(pdf_path) as pdf:
        for metric, title, ylabel, ylim in plots_to_make:
            try:
                # Use .copy() to avoid SettingWithCopyWarning
                metric_df = df.loc[[metric]].copy()
            except KeyError:
                print(f"Metric '{metric}' not found in data. Skipping.")
                continue
            
            if metric_df.empty:
                print(f"Metric '{metric}' has no data. Skipping.")
                continue

            if metric in smooth_figs:
                # Group by Scenario and Simulation Number, then apply rolling mean to smooth
                metric_df['Value'] = metric_df.groupby(['Scenario', 'Simulation Number'])['Value'].transform(
                    lambda x: x.rolling(smooth_window, min_periods=1).mean()
                )
            
            plt.figure(figsize=fig_size)
            sns.lineplot(
                x='Timestep Number',
                y='Value',
                data=metric_df,
                hue='Scenario',
                errorbar=errorbar_format
            )
            plt.title(title)
            plt.xlabel('Timestep Number')
            plt.ylabel(ylabel)
            
            # Apply y-axis limits safely depending on the data
            vals = metric_df['Value'].dropna()
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
        print("Generating plots and saving to PDF...")
        plot_metrics_to_pdf(df, 'scenarios_plots_all.pdf')
        print("Done! Saved as scenarios_plots_all.pdf")
    except FileNotFoundError:
        print("results.csv not found. Please ensure the simulation has been run and results are available.")
