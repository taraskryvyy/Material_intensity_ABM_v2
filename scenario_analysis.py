import pandas as pd
import os
import numpy as np

df = pd.read_csv('results.csv', index_col=['Metric',
                                           'Timestep Number',
                                           'Scenario',
                                           'Simulation Number'])

all_scenarios = df.index.get_level_values('Scenario')
all_metrics = df.index.get_level_values('Metric')

df = df.loc[df.index.get_level_values('Timestep Number') == 199]

# df.to_csv('results_short.csv')

# # compute the mean of each metric for each scenario
mean_df = pd.DataFrame()
for metric in all_metrics.unique():
    temp_df = df.loc[metric].groupby('Scenario').mean()
    temp_df = temp_df.rename(columns={'Value': metric})
    mean_df = pd.concat([mean_df, temp_df], axis=1)

# compute the stdev of each metric for each scenario
serr_df = pd.DataFrame()
for metric in all_metrics.unique():
    temp_df = df.loc[metric].groupby('Scenario').sem()
    temp_df = temp_df.rename(columns={'Value': metric})
    serr_df = pd.concat([serr_df, temp_df], axis=1)

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