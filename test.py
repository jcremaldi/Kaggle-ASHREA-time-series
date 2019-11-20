import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


building_id = 1427
meter = 2
raw_data = pd.read_csv(r'../New folder/%s_%s.csv' % (building_id,meter))
raw_data = raw_data.drop(columns = ['building_id','meter'])
raw_data.timestamp = pd.to_datetime(raw_data.timestamp)

# account for xmas in data
xmas_ave = raw_data[raw_data['timestamp'] > '2016-12-19 03:00:00']['meter_reading'].mean()
print(xmas_ave)
raw_data = raw_data[raw_data['timestamp'] < '2016-12-19 03:00:00']

#raw_data = raw_data.set_index('timestamp')
#raw_data_weekly = raw_data.resample('W').mean()
#rolling = raw_data.rolling(window=168)

y_values = raw_data.loc[:, 'meter_reading']
x_values = np.linspace(0,1,len(raw_data.loc[:, 'meter_reading']))
poly_degree = 2
coeffs = np.polyfit(x_values, y_values, poly_degree)
print(coeffs)
poly_eqn = np.poly1d(coeffs)
y_hat = poly_eqn(x_values)

plt.figure(figsize=(12,8))
plt.plot(raw_data.loc[:, 'timestamp'], raw_data.loc[:,'meter_reading'])
plt.plot(raw_data.loc[:, 'timestamp'],y_hat)
plt.ylabel('meter reading')
plt.xlabel('timestamp')
plt.show()