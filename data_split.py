import pandas as pd

pd.set_option('display.max_colwidth', -1)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 9999)


raw_data = pd.read_csv(r'../New folder/train.csv')
raw_data = raw_data[raw_data['meter_reading'] != 0]

#------------------------------------------------------------------------------
#print(raw_data.dtypes)
#print(raw_data.groupby('building_id')['meter'].value_counts())

# data not missing for all march
#datetime_counts = raw_data['timestamp'].value_counts().sort_index()
#datetime_counts.to_csv('datetime_counts.csv')
#------------------------------------------------------------------------------

building_id = 1427
meter = 2
raw_data = raw_data[(raw_data['building_id'] == building_id) & (raw_data['meter'] == meter)]
raw_data.to_csv('%s_%s.csv' % (building_id,meter))

