import pandas as pd
import os
import numpy as np

df1 = pd.read_csv('results.csv', 
                  index_col=['Metric',
                                           'Timestep Number',
                                           'Scenario',
                                           'Simulation Number']
                                           )

df2 = pd.read_csv('results4.csv', 
                  index_col=['Metric',
                                             'Timestep Number',
                                             'Scenario',
                                             'Simulation Number']
                                             )


df2.index = df2.index.set_levels(pd.to_numeric(df2.index.levels[3]), level=3)

df2.index = df2.index.set_levels(df2.index.levels[3] + 80, level=3)

df = pd.concat([df1, df2])

df.to_csv('results02.csv')