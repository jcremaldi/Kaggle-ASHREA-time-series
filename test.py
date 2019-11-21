import pandas as pd
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt

building_id = 7
meter = 1
raw_data = pd.read_csv(r'../New folder/%s_%s.csv' % (building_id,meter))
raw_data = raw_data.drop(columns = ['building_id','meter','Unnamed: 0'])
raw_data.timestamp = pd.to_datetime(raw_data.timestamp)
raw_data = raw_data.set_index('timestamp')

# account for xmas in data
xmas_ave = raw_data[raw_data.index > '2016-12-19 03:00:00']['meter_reading'].mean()
print(xmas_ave)
raw_data = raw_data[raw_data.index < '2016-12-19 03:00:00']
# to do --> remove weekends and holidays to a separate df and just use the average

polyn = 4

raw_data['H'] = raw_data.index.hour
raw_data['D'] = raw_data.index.weekday_name
day_conv = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, 'Saturday':6, 'Sunday':7}
raw_data['D'] = raw_data['D'].map(day_conv)
raw_data['W'] = raw_data.index.week
raw_data['M'] = raw_data.index.month

monthly = raw_data.groupby('M').meter_reading.mean().reset_index()
trendM = np.poly1d(np.polyfit(monthly.M, monthly.meter_reading, polyn))
trendMpoly = np.poly1d(trendM) 

raw_data['mr_m_adj'] = raw_data.meter_reading - trendMpoly(raw_data.M)
weekly = raw_data.groupby('W').mr_m_adj.mean().reset_index()
trendW = np.poly1d(np.polyfit(weekly.W, weekly.mr_m_adj, 1))
trendWpoly = np.poly1d(trendW) 

raw_data['mr_mw_adj'] = raw_data.mr_m_adj - trendWpoly(raw_data.W)

daily = raw_data.groupby('D').mr_mw_adj.mean().reset_index()
trendD = np.poly1d(np.polyfit(daily.index+1, daily.mr_mw_adj, 1))
trendDpoly = np.poly1d(trendD)

raw_data['mr_mwd_adj'] = raw_data.mr_mw_adj - trendDpoly(raw_data.D)
hourly = raw_data.groupby('H').mr_mwd_adj.mean().reset_index()
trendH = np.poly1d(np.polyfit(hourly.H, hourly.mr_mwd_adj, polyn))
trendHpoly = np.poly1d(trendH)

raw_data['mr_mwdh_adj'] = raw_data.mr_mwd_adj - trendHpoly(raw_data.H)

plt.plot(monthly.M, monthly.meter_reading,'.')
plt.plot(monthly.M,trendMpoly(monthly.M))
plt.show()

plt.plot(weekly.W, weekly.mr_m_adj,'.')
plt.plot(weekly.W,trendWpoly(weekly.W))
plt.show()

plt.plot(daily.D, daily.mr_mw_adj,'.')
plt.plot(daily.D,trendDpoly(daily.D))
plt.show()

plt.plot(hourly.H, hourly.mr_mwd_adj,'.')
plt.plot(hourly.H,trendHpoly(hourly.H))
plt.show()




# To do:
# set full hourly yearly index
# fill missing data values
# separate weekend, holiday usage from normal
# get trnds for hourly, daily, weekly, monthly and adjust data
# --> monthly, adjust, weekly, adjust, daily, adjust, hourly, adjust
# store the coef in a dict for each building/meter combo
# maybe use coeff in regression, or use to adjust and back calculate
