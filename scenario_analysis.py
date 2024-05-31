import pandas as pd
import os
import numpy as np
import scenarios

window = 50
variables = ['Renewable Energy market share',
             'Average ore extraction cost',
             'Cumulative number of bankruptcies',
             'Total NPL balance',
             'Commercial bank loan-to-deposit-ratio']

df = pd.read_csv('results.csv', index_col=['Metric',
                                           'Timestep Number',
                                           'Scenario',
                                           'Simulation Number'])

df = df.loc[df.index.get_level_values('Scenario') != "fuelPriceDrift"]
df = df.loc[df.index.get_level_values('Scenario') == "sigmaOreCostParamOne_0.03"]

# all_scenarios = df.index.get_level_values('Scenario')
# all_metrics = df.index.get_level_values('Metric')
max_timestep = df.index.get_level_values('Timestep Number').max()
max_simulation = df.index.get_level_values('Simulation Number').max()

df = df.loc[df.index.get_level_values('Timestep Number') > max_timestep - window]
df = df.loc[df.index.get_level_values('Metric').isin(variables)]

# len_of_fuel_scen = sum(df.index.get_level_values('Scenario')=="fuelPriceDrift")
# index_new = df.index.get_level_values('Scenario').tolist()
# num = 0
# for i in enumerate(index_new):
#     if i[1] == "fuelPriceDrift":
#         if num < len_of_fuel_scen/2:
#             index_new[i[0]] = "fuelPriceDrift_0.0003"
#         else:
#             index_new[i[0]] = "fuelPriceDrift_0.006"   
#         print(index_new[i[0]])
#         print(i)
#         print(num)
#         num += 1


df = df.groupby(['Metric', 'Scenario', 'Simulation Number']).mean()
df_pivot_mean = df.pivot_table(index='Scenario', columns='Metric', values='Value')
df_pivot_serr = df.pivot_table(index='Scenario', columns='Metric', values='Value', aggfunc=np.std) / np.sqrt(max_simulation)
# df_mean = df.groupby(['Metric', 'Scenario']).mean()
# df_serr = df.groupby(['Metric', 'Scenario']).sem()

# print(df_pivot_mean.head())
# print(df_pivot_serr.head())
# print(df_mean.head())
# print(df_serr.head())

scenarios_order = scenarios.generate_scenarios().keys()
custom_order_mapping = {city: i+1 for i, city in enumerate(scenarios_order)}
custom_order = df_pivot_mean.reset_index()['Scenario'].map(custom_order_mapping)
df_pivot_mean_ordered = df_pivot_mean.sort_index(level=0, key=lambda x: custom_order)#.reset_index()
df_pivot_serr_ordered = df_pivot_serr.sort_index(level=0, key=lambda x: custom_order)#.reset_index()


df_pivot_mean_ordered.to_csv('mean_results.csv')
df_pivot_serr_ordered.to_csv('serr_results.csv')

# print(df_pivot_mean_ordered)
# print(df_pivot_serr_ordered)



# df.to_csv('results_short.csv')

# # compute the mean of each metric for each scenario
# mean_df = pd.DataFrame()
# for metric in all_metrics.unique():
#     temp_df = df.loc[metric].groupby('Scenario').mean()
#     temp_df = temp_df.rename(columns={'Value': metric})
#     mean_df = pd.concat([mean_df, temp_df], axis=1)

# # compute the stdev of each metric for each scenario
# serr_df = pd.DataFrame()
# for metric in all_metrics.unique():
#     temp_df = df.loc[metric].groupby('Scenario').sem()
#     temp_df = temp_df.rename(columns={'Value': metric})
#     serr_df = pd.concat([serr_df, temp_df], axis=1)

# # mean_df to csv
# mean_df.to_csv('mean_results.csv')
# # stdev_df to csv
# stdev_df.to_csv('stdev_results.csv')

# compute the mean of each metric for each scenario
# mean_df = pd.DataFrame()
# for metric in all_metrics.unique():
#     temp_df = df.loc[metric].groupby('Scenario').mean()

#     temp_df = temp_df.rename(columns={'Value': metric})
#     mean_df = pd.concat([mean_df, temp_df], axis=1)

# # compute the stdev of each metric for each scenario
# stdev_df = pd.DataFrame()
# for metric in all_metrics.unique():
#     temp_df = df.loc[metric].groupby('Scenario').std()
#     temp_df = temp_df.rename(columns={'Value': metric})
#     stdev_df = pd.concat([stdev_df, temp_df], axis=1)

# # mean_df to csv
# mean_df.to_csv('mean_results.csv')
# # stdev_df to csv
# stdev_df.to_csv('stdev_results.csv')