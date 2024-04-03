import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
# import PyPDF2
import os
import numpy as np

save_figs = True
show_figs = False
merge_figs = False
format = 'pdf'
fig_size = (12, 4)
errorbar_format = ("se", 1)

df = pd.read_csv('results.csv', index_col=['Metric',
                                           'Timestep Number',
                                           'Scenario',
                                           'Simulation Number'])

# df = df.loc[df.index.get_level_values('Timestep Number') > 25]
# df = df.loc[df.index.get_level_values('Simulation Number') == 1]

all_scenarios = df.index.get_level_values('Scenario')
scenario_set = [
    "miningSiteExplorationProbability_0",
    "miningSiteExplorationProbability_0.1",
    "base_miningSiteExplorationProbability_0.5",
    # "miningSiteExplorationProbability_0.01",
    # "miningSiteExplorationProbability_0.5",
    # "miningSiteExplorationProbability_1",

#     # "logitCompetitionParamMining_0.01",
#     # "logitCompetitionParamMining_1",
#     # "logitCompetitionParamMining_10",

#     # "adaptiveExpectationMaterialPrice_0.2",
#     # "adaptiveExpectationMaterialPrice_0.5",
#     # "adaptiveExpectationMaterialPrice_0.8",

#     # "recMaterialProductivity_5",
#     # "recMaterialProductivity_2",
#     # "recMaterialProductivity_1",

#     # "fuelPriceVolatility_0.00000001",
#     # "fuelPriceVolatility_0.00003",
#     # "fuelPriceVolatility_0.0005",

#     # "fuelPriceDrift_0.0002",
#     # "fuelPriceDrift_0.002",
#     # "fuelPriceDrift_0.02",

#     # "oreCostParamOne_0.1",
#     # "oreCostParamOne_0.3",
#     # "oreCostParamOne_0.5",

#     # "sigmaOreCostParamOne 0.001",
#     # "sigmaOreCostParamOne 0.05",
#     # "sigmaOreCostParamOne 0.2",

#     # "oreCostParamTwo_0.1",
#     # "oreCostParamTwo_0.5",
#     # "oreCostParamTwo_0.9",

#     # "muOreDeposit_100",
#     # "muOreDeposit_150",
#     # "muOreDeposit_200",

#     # "sigmaSqOreDeposit_200",
#     # "sigmaSqOreDeposit_400",
#     # "sigmaSqOreDeposit_600",

#     # "oreProductivity_0.5",
#     # "oreProductivity_1",
#     # "oreProductivity_2",
                ]
scenario_filter = [scen in scenario_set for scen in all_scenarios]

# df = df.loc[scenario_filter]

# df = df.loc[df.index.get_level_values('Scenario') == "logitCompetitionParameter_0.01"]

# df = df.loc[df.index.get_level_values('Simulation Number') == 29]

total_NPL_balance_df = df.loc[["Total NPL balance"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=total_NPL_balance_df,#df.loc[["Total NPL balance"]],
                hue='Scenario',
                errorbar=errorbar_format
                )
plt.title('Total NPL balance vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Total NPL balance')
if save_figs:
    plt.savefig('scenario_total_NPL_balance.'+format)
if show_figs:
    plt.show()
plt.close()

commercial_bank_loan_to_deposit_ratio_df = df.loc[["Commercial bank loan-to-deposit-ratio"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
            y='Value',
            data=commercial_bank_loan_to_deposit_ratio_df,#df.loc[["Commercial bank loan-to-deposit-ratio"]],
            hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Commercial bank loan-to-deposit-ratio vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Commercial bank loan-to-deposit-ratio')
if save_figs:
    plt.savefig('scenario_commercial_bank_loan_to_deposit_ratio.'+format)
if show_figs:
    plt.show()
plt.close()

cumulative_number_of_bankruptcies_df = df.loc[["Cumulative number of bankruptcies"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=cumulative_number_of_bankruptcies_df,#df.loc[["Cumulative number of bankruptcies"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Cumulative Number of Bankruptcies vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Cumulative Number of Bankruptcies')
if save_figs:
    plt.savefig('scenario_cumulative_number_of_bankruptcies.'+format)
if show_figs:
    plt.show()
plt.close()

cumulative_number_of_bankrupt_material_firms_df = df.loc[["Cumulative number of bankrupt material firms"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=cumulative_number_of_bankrupt_material_firms_df,#df.loc[["Cumulative number of bankrupt material firms"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Cumulative Number of Bankrupt Material Firms vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Cumulative Number of Bankrupt Material Firms')
if save_figs:
    plt.savefig('scenario_cumulative_number_of_bankrupt_material_firms.'+format)
if show_figs:
    plt.show()
plt.close()

# 'Average age of bankrupt material firms'
# average_age_of_bankrupt_material_firms_df = df.loc[["Average age of bankrupt material firms"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=average_age_of_bankrupt_material_firms_df,#df.loc[["Average age of bankrupt material firms"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Average Age of Bankrupt Material Firms vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Average Age of Bankrupt Material Firms')
# if save_figs:
#     plt.savefig('scenario_average_age_of_bankrupt_material_firms.'+format)
# if show_figs:
#     plt.show()
# plt.close()

'Material inventory of bankrupt material firms'
material_inventory_of_bankrupt_material_firms_df = df.loc[["Material inventory of bankrupt material firms"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=material_inventory_of_bankrupt_material_firms_df,#df.loc[["Material inventory of bankrupt material firms"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Material Inventory of Bankrupt Material Firms vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Material Inventory of Bankrupt Material Firms')
if save_figs:
    plt.savefig('scenario_material_inventory_of_bankrupt_material_firms.'+format)
if show_figs:
    plt.show()
plt.close()

# cumulative_number_of_bankrupt_power_plants_df = df.loc[["Cumulative number of bankrupt power plants"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=cumulative_number_of_bankrupt_power_plants_df,#df.loc[["Cumulative number of bankrupt power plants"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Cumulative Number of Bankrupt Power Plants vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Cumulative Number of Bankrupt Power Plants')
# if save_figs:
#     plt.savefig('scenario_cumulative_number_of_bankrupt_power_plants.'+format)
# if show_figs:
#     plt.show()
# plt.close()

cumulative_number_of_bankrupt_final_good_firms_df = df.loc[["Cumulative number of bankrupt final good firms"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=cumulative_number_of_bankrupt_final_good_firms_df,#df.loc[["Cumulative number of bankrupt final good firms"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Cumulative Number of Bankrupt Final Good Firms vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Cumulative Number of Bankrupt Final Good Firms')
if save_figs:
    plt.savefig('scenario_cumulative_number_of_bankrupt_final_good_firms.'+format)
if show_figs:
    plt.show()
plt.close()

final_output_df = df.loc[["Final good output"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=final_output_df,#df.loc[["Final good output"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Total Output vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Total Output')
if save_figs:
    plt.savefig('scenario_total_output.'+format)
if show_figs:
    plt.show()
plt.close()

total_consumption_budget_df = df.loc[["Total consumption budget"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=total_consumption_budget_df,#df.loc[["Total consumption budget"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Total Consumption Budget vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Total Consumption Budget')
if save_figs:
    plt.savefig('scenario_total_consumption_budget.'+format)
if show_figs:
    plt.show()
plt.close()

total_household_dividend_income_df = df.loc[["Total household dividend income"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=total_household_dividend_income_df,#df.loc[["Total household dividend income"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Total Household Dividend Income vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Total Household Dividend Income')
if save_figs:
    plt.savefig('scenario_total_household_dividend_income.'+format)
if show_figs:
    plt.show()
plt.close()






electricity_price_df = df.loc[["Electricity price"]]
max_ylim = np.percentile(electricity_price_df['Value'], 99)
min_ylim = min(electricity_price_df['Value'])
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=electricity_price_df,#df.loc[["Electricity price"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Electricity Price vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Electricity Price')
if save_figs:
    plt.savefig('scenario_electricity_price.'+format)
if show_figs:
    plt.show()
plt.ylim(min_ylim, max_ylim)  # Set the vertical axis limits
plt.title('Electricity Price vs Timestep Number (zoomed in)')
if save_figs:
    plt.savefig('scenario_electricity_price_zoomed.'+format)
if show_figs:
    plt.show()

plt.close()





weighted_average_sell_price_of_final_good_df = df.loc[["Weighted average sell price of final good"]]
max_ylim = np.mean(weighted_average_sell_price_of_final_good_df['Value']) * 2#np.percentile(weighted_average_sell_price_of_final_good_df['Value'], 99)
min_ylim = min(weighted_average_sell_price_of_final_good_df['Value'])
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=weighted_average_sell_price_of_final_good_df,#df.loc[["Weighted average sell price of final good"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Weighted Average Sell Price of Final Good vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Weighted Average Sell Price of Final Good')
if save_figs:
    plt.savefig('scenario_weighted_average_sell_price_of_final_good.'+format)
if show_figs:
    plt.show()
plt.ylim(min_ylim, max_ylim)  # Set the vertical axis limits
plt.title('Weighted Average Sell Price of Final Good vs Timestep Number (zoomed in)')
if save_figs:
    plt.savefig('scenario_weighted_average_sell_price_of_final_good_zoomed.'+format)
if show_figs:
    plt.show()
plt.close()

# 'Number of renewable energy power plants'
# number_of_renewable_energy_power_plants_df = df.loc[["Number of renewable energy power plants"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=number_of_renewable_energy_power_plants_df,#df.loc[["Number of renewable energy power plants"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Number of Renewable Energy Power Plants vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Number of Renewable Energy Power Plants')
# if save_figs:
#     plt.savefig('scenario_number_of_renewable_energy_power_plants.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# 'Number of fossil fuel energy power plants'
# number_of_fossil_fuel_energy_power_plants_df = df.loc[["Number of fossil fuel energy power plants"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=number_of_fossil_fuel_energy_power_plants_df,#df.loc[["Number of fossil fuel energy power plants"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Number of Fossil Fuel Energy Power Plants vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Number of Fossil Fuel Energy Power Plants')
# if save_figs:
#     plt.savefig('scenario_number_of_fossil_fuel_energy_power_plants.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# 'Fuel price'
# fuel_price_df = df.loc[["Fuel price"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=fuel_price_df,#df.loc[["Fuel price"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Fuel Price vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Fuel Price')
# if save_figs:
#     plt.savefig('scenario_fuel_price.'+format)
# if show_figs:
#     plt.show()
# plt.close()

renewable_energy_market_share_df = df.loc[["Renewable Energy market share"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=renewable_energy_market_share_df,#df.loc[["Renewable energy market share"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Renewable Energy Market Share vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Renewable Energy Market Share')
if save_figs:
    plt.savefig('scenario_renewable_energy_market_share.'+format)
if show_figs:
    plt.show()
plt.close()

electricity_price_df = df.loc[["Electricity price"]]
max_ylim = np.percentile(electricity_price_df['Value'], 99)
min_ylim = min(electricity_price_df['Value'])
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=electricity_price_df,#df.loc[["Electricity price"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Electricity Price vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Electricity Price')
if save_figs:
    plt.savefig('scenario_electricity_price.'+format)
if show_figs:
    plt.show()
plt.ylim(min_ylim, max_ylim)  # Set the vertical axis limits
plt.title('Electricity Price vs Timestep Number (zoomed in)')
if save_figs:
    plt.savefig('scenario_electricity_price_zoomed.'+format)
if show_figs:
    plt.show()

plt.close()

# 'Total energy deficit'
# total_energy_deficit_df = df.loc[["Total energy deficit"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=total_energy_deficit_df,#df.loc[["Total energy deficit"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Energy Deficit vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Energy Deficit')
# if save_figs:
#     plt.savefig('scenario_total_energy_deficit.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# total_supply_of_material_df = df.loc[["Total supply of material"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=total_supply_of_material_df,#df.loc[["Total supply of material"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Supply of Material vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Supply of Material')
# if save_figs:
#     plt.savefig('scenario_total_supply_of_material.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# 'Total demand for material'
# total_demand_for_material_df = df.loc[["Total demand for material"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=total_demand_for_material_df,#df.loc[["Total demand for material"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Demand for Material vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Demand for Material')
# if save_figs:
#     plt.savefig('scenario_total_demand_for_material.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# 'Total material deficit'
# total_material_deficit_df = df.loc[["Total material deficit"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=total_material_deficit_df,#df.loc[["Total material deficit"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Material Deficit vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Material Deficit')
# if save_figs:
#     plt.savefig('scenario_total_material_deficit.'+format)
# if show_figs:
#     plt.show()
# plt.close()

material_price_df = df.loc[["Material price"]]
max_ylim = np.percentile(electricity_price_df['Value'], 99)
min_ylim = min(electricity_price_df['Value'])
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=material_price_df,#df.loc[["Material price"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Material Price vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Material Price')
if save_figs:
    plt.savefig('scenario_material_price.'+format)
if show_figs:
    plt.show()
plt.ylim(min_ylim, max_ylim)  # Set the vertical axis limits
plt.title('Material Price vs Timestep Number (zoomed in)')
if save_figs:
    plt.savefig('scenario_material_price_zoomed.'+format)
if show_figs:
    plt.show()
plt.close()

average_ore_extraction_cost_df = df.loc[["Average ore extraction cost"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=average_ore_extraction_cost_df,#df.loc[["Average ore extraction cost"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Average Ore Extraction Cost vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Average Ore Extraction Cost')
if save_figs:
    plt.savefig('scenario_average_ore_extraction_cost.'+format)
if show_figs:
    plt.show()
plt.close()

'Total ore reserves'
total_ore_reserves_df = df.loc[["Total ore reserves"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number', 
             y='Value', 
             data=total_ore_reserves_df,#df.loc[["Total ore reserves"]],
             hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Total Ore Reserves vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Total Ore Reserves')
if save_figs:
    plt.savefig('scenario_total_ore_reserves.'+format)
if show_figs:
    plt.show()
plt.close()

# 'Number of mining sites'
# number_of_mining_sites_df = df.loc[["Number of mining sites"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number', 
#              y='Value', 
#              data=number_of_mining_sites_df,#df.loc[["Number of mining sites"]],
#              hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Number of Mining Sites vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Number of Mining Sites')
# if save_figs:
#     plt.savefig('scenario_number_of_mining_sites.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# 'Profit of material capital firms'
# profit_of_material_capital_firms_df = df.loc[["Profit of material capital firms"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=profit_of_material_capital_firms_df,#df.loc[["Profit of material capital firms"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Profit of Material Capital Firms vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Profit of Material Capital Firms')
# if save_figs:
#     plt.savefig('scenario_profit_of_material_capital_firms.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# "RnD budget of material capital firms"
# rnd_budget_of_material_capital_firms_df = df.loc[["RnD budget of material capital firms"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=rnd_budget_of_material_capital_firms_df,#df.loc[["RnD budget of material capital firms"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('RnD Budget of Material Capital Firms vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('RnD Budget of Material Capital Firms')
# if save_figs:
#     plt.savefig('scenario_rnd_budget_of_material_capital_firms.'+format)
# if show_figs:
#     plt.show()
# plt.close()

'Material capital productivity'
material_capital_productivity_df = df.loc[["Material capital productivity"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=material_capital_productivity_df,#df.loc[["Material capital productivity"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Material Capital Productivity vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Material Capital Productivity')
if save_figs:
    plt.savefig('scenario_material_capital_productivity.'+format)
if show_figs:
    plt.show()
plt.close()

'Final good capital productivity'
final_good_capital_productivity_df = df.loc[["Final good capital productivity"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=final_good_capital_productivity_df,#df.loc[["Final good capital productivity"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Final Good Capital Productivity vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Final Good Capital Productivity')
if save_figs:
    plt.savefig('scenario_final_good_capital_productivity.'+format)
if show_figs:
    plt.show()
plt.close()

'Renewable Energy capital productivity'
renewable_energy_capital_productivity_df = df.loc[["Renewable Energy capital productivity"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=renewable_energy_capital_productivity_df,#df.loc[["Renewable energy capital productivity"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Renewable Energy Capital Productivity vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Renewable Energy Capital Productivity')
if save_figs:
    plt.savefig('scenario_renewable_energy_capital_productivity.'+format)
if show_figs:
    plt.show()
plt.close()

'Fossil Fuel Energy capital productivity'
fossil_fuel_energy_capital_productivity_df = df.loc[["Fossil Fuel Energy capital productivity"]]
plt.figure(figsize=fig_size)
sns.lineplot(x='Timestep Number',
                y='Value',
                data=fossil_fuel_energy_capital_productivity_df,#df.loc[["Fossil fuel energy capital productivity"]],
                hue='Scenario',
             errorbar=errorbar_format
             )
plt.title('Fossil Fuel Energy Capital Productivity vs Timestep Number')
plt.xlabel('Timestep Number')
plt.ylabel('Fossil Fuel Energy Capital Productivity')
if save_figs:
    plt.savefig('scenario_fossil_fuel_energy_capital_productivity.'+format)
if show_figs:
    plt.show()
plt.close()

# 'Total deposit balance in capital sector'
# total_deposit_balance_in_capital_sector_df = df.loc[["Total deposit balance in capital sector"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=total_deposit_balance_in_capital_sector_df,#df.loc[["Total deposit balance in capital sector"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Deposit Balance in Capital Sector vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Deposit Balance in Capital Sector')
# if save_figs:
#     plt.savefig('scenario_total_deposit_balance_in_capital_sector.'+format)
# if show_figs:
#     plt.show()
# plt.close()

# "Total deposit balance in material capital sector"
# total_deposit_balance_in_material_capital_sector_df = df.loc[["Total deposit balance in material capital sector"]]
# plt.figure(figsize=fig_size)
# sns.lineplot(x='Timestep Number',
#                 y='Value',
#                 data=total_deposit_balance_in_material_capital_sector_df,#df.loc[["Total deposit balance in material capital sector"]],
#                 hue='Scenario',
            #  errorbar=errorbar_format
            #  )
# plt.title('Total Deposit Balance in Material Capital Sector vs Timestep Number')
# plt.xlabel('Timestep Number')
# plt.ylabel('Total Deposit Balance in Material Capital Sector')
# if save_figs:
#     plt.savefig('scenario_total_deposit_balance_in_material_capital_sector.'+format)
# if show_figs:
#     plt.show()
# plt.close()



if merge_figs:
    # List of PDF files to merge
    directory_path = '/Users/tagger/Documents/GitHub/Material_intensity_ABM/Material_intensity_ABM'#'/path/to/your/directory'

    # Get a list of all files in the directory
    all_files = os.listdir(directory_path)

    # Filter files that start with "scenario_" and end with ".pdf"
    # pdf_files = [file for file in all_files if file.startswith("scenario_") and file.endswith(".pdf")]

    pdf_files = [
        "scenario_total_NPL_balance.pdf",
        "scenario_commercial_bank_loan_to_deposit_ratio.pdf",
        "scenario_cumulative_number_of_bankruptcies.pdf",
        "scenario_cumulative_number_of_bankrupt_material_firms.pdf",
        "scenario_average_age_of_bankrupt_material_firms.pdf",
        "scenario_material_inventory_of_bankrupt_material_firms.pdf",
        "scenario_cumulative_number_of_bankrupt_final_good_firms.pdf",
        "scenario_total_output.pdf",
        "scenario_total_consumption_budget.pdf",
        "scenario_total_household_dividend_income.pdf",
        "scenario_weighted_average_sell_price_of_final_good.pdf",
        "scenario_number_of_renewable_energy_power_plants.pdf",
        "scenario_number_of_fossil_fuel_energy_power_plants.pdf",
        "scenario_fuel_price.pdf",
        "scenario_renewable_energy_market_share.pdf",
        "scenario_electricity_price.pdf",
        "scenario_total_energy_deficit.pdf",
        "scenario_total_supply_of_material.pdf",
        "scenario_total_demand_for_material.pdf",
        "scenario_total_material_deficit.pdf",
        "scenario_material_price.pdf",
        "scenario_average_ore_extraction_cost.pdf",
        "scenario_total_ore_reserves.pdf",
        "scenario_number_of_mining_sites.pdf",
        "scenario_profit_of_material_capital_firms.pdf",
        "scenario_rnd_budget_of_material_capital_firms.pdf",
        "scenario_material_capital_productivity.pdf",
        "scenario_final_good_capital_productivity.pdf",
        "scenario_renewable_energy_capital_productivity.pdf",
        "scenario_fossil_fuel_energy_capital_productivity.pdf",
        "scenario_total_deposit_balance_in_capital_sector.pdf",
        "scenario_total_deposit_balance_in_material_capital_sector.pdf"
    ]

    merger = PyPDF2.PdfWriter()

    for pdf in pdf_files:
        merger.append(pdf)

    merger.write("scenarios_plots.pdf")#, "wb")
    merger.close()

    # # Iterate through the list of PDF files
    # for pdf_file in pdf_files:
    #     with open(pdf_file, 'rb') as pdf:
    #         # Create a PDF reader object
    #         pdf_reader = PyPDF2.PdfWriter(pdf)

    #         # Add the single page to the writer
    #         page = pdf_reader.pages
    #         pdf_writer.add_page(page)

    # # Create a new merged PDF file
    # merged_pdf_path = 'scenarios_plots.pdf'
    # with open(merged_pdf_path, 'wb') as merged_pdf:
    #     pdf_writer.write(merged_pdf)

    # print(f'Merged PDF saved at: {merged_pdf_path}')