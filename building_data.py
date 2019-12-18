import numpy as np
import pandas as pd

sid_all = [1,4,5,7 ]
sid_yb = [0,2,3,15]
sid_floors = [8,10]
sid_none = [6,9,11,12,13,14]

raw_data = pd.read_csv('data/building_metadata.csv')
print(raw_data.info(verbose=True),'\n')

raw_data_sid_all = raw_data[raw_data['site_id'].isin(sid_all)]
raw_data_sid_all['year_built'].fillna(raw_data_sid_all['year_built'].mean(), inplace = True) 
raw_data_sid_all['floor_count'].fillna(raw_data_sid_all['floor_count'].mean(), inplace = True)

raw_data_sid_yb = raw_data[raw_data['site_id'].isin(sid_yb)]
raw_data_sid_yb['year_built'].fillna(raw_data_sid_yb['year_built'].mean(), inplace = True)
raw_data_sid_yb['floor_count'] = 0    

raw_data_sid_floors = raw_data[raw_data['site_id'].isin(sid_floors)]
raw_data_sid_floors['year_built'] = 0
raw_data_sid_floors['floor_count'].fillna(raw_data_sid_floors['floor_count'].mean(), inplace = True)

raw_data_sid_none = raw_data[raw_data['site_id'].isin(sid_none)]
raw_data_sid_none['year_built'] = 0
raw_data_sid_none['floor_count'] = 0

raw_data_comb = pd.concat([raw_data_sid_all, raw_data_sid_yb, raw_data_sid_floors, raw_data_sid_none])

print(raw_data_comb.info(verbose=True))
raw_data_comb.to_csv('building_fixed.csv', index = False)




































