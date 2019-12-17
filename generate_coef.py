import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

class GenerateCoef:
    
    def __init__(self, raw_data, building_id, meter, graph_toggle):
        self.raw_data = raw_data
        self.building_id = building_id
        self.meter = meter
        self.graph_toggle = graph_toggle
        self.data_prep()
        self.separate_off_days()
        self.monthly_coef()
        self.weekly_coef()
        self.daily_coef()
        self.hourly_coef()
        self.ave_meter()

    def data_prep(self):
        day_conv = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, \
                    'Saturday':6, 'Sunday':7}        
        
        self.raw_data.timestamp = pd.to_datetime(self.raw_data.timestamp)
        self.raw_data = self.raw_data.set_index('timestamp')
        
        self.raw_data['H'] = self.raw_data.index.hour
        self.raw_data['D'] = self.raw_data.index.weekday_name
        self.raw_data['W'] = self.raw_data.index.week
        self.raw_data['M'] = self.raw_data.index.month
        self.raw_data['date'] = self.raw_data.index.date
        self.raw_data['D'] = self.raw_data['D'].map(day_conv)
                
    def separate_off_days(self):
        holidays = pd.date_range(start='2016-12-21', end='2016-12-31', freq='D')
        self.raw_data.loc[self.raw_data.date.astype('str').isin(holidays),'D'] = 99
        other_holidays = ['2016-02-29','2016-01-01','2016-05-30','2016-11-24','2016-07-04', \
                          '2016-03-25','2016-01-18','2016-09-05']
        self.raw_data.loc[self.raw_data.date.astype('str').isin(other_holidays),'D'] = 99
        off_hours_data = self.raw_data[self.raw_data.D.isin([6,7,99])]
        self.off_hours_ave = off_hours_data.meter_reading.mean()
        self.raw_data = self.raw_data.drop(off_hours_data.index)
    
    def monthly_coef(self):
        monthly = self.raw_data.groupby('M').meter_reading.mean().reset_index()
        trendM = np.poly1d(np.polyfit(monthly.M, monthly.meter_reading, 6))
        self.monthly_coef = trendM.coef
        self.trendMpoly = np.poly1d(trendM) 

        if self.graph_toggle:
            self.create_graph(self.trendMpoly, monthly, 'M', 'meter_reading')

    def weekly_coef(self):
        self.raw_data['mr_m_adj'] = self.raw_data.meter_reading - self.trendMpoly(self.raw_data.M)
        weekly = self.raw_data.groupby('W').mr_m_adj.mean().reset_index()
        trendW = np.poly1d(np.polyfit(weekly.W, weekly.mr_m_adj, 2))
        self.weekly_coef = trendW.coef
        self.trendWpoly = np.poly1d(trendW) 

        if self.graph_toggle:
            self.create_graph(self.trendWpoly, weekly, 'W', 'mr_m_adj')

    def daily_coef(self):        
        self.raw_data['mr_mw_adj'] = self.raw_data.mr_m_adj - self.trendWpoly(self.raw_data.W)
        daily = self.raw_data.groupby('D').mr_mw_adj.mean().reset_index()
        trendD = np.poly1d(np.polyfit(daily.index+1, daily.mr_mw_adj, 2))
        self.daily_coef = trendD.coef
        self.trendDpoly = np.poly1d(trendD)

        if self.graph_toggle:
            self.create_graph(self.trendDpoly, daily, 'D', 'mr_mw_adj')

    def hourly_coef(self):        
        self.raw_data['mr_mwd_adj'] = self.raw_data.mr_mw_adj - self.trendDpoly(self.raw_data.D)
        hourly = self.raw_data.groupby('H').mr_mwd_adj.mean().reset_index()
        trendH = np.poly1d(np.polyfit(hourly.H, hourly.mr_mwd_adj, 6))
        self.hourly_coef = trendH.coef
        self.trendHpoly = np.poly1d(trendH)
        self.raw_data['mr_mwdh_adj'] = self.raw_data.mr_mwd_adj - self.trendHpoly(self.raw_data.H)

        if self.graph_toggle:
            self.create_graph(self.trendHpoly, hourly, 'H', 'mr_mwd_adj')

    def ave_meter(self):
        self.ave_meter = self.raw_data['mr_mwdh_adj'].mean()
        
    def create_graph(self,trend_poly,df,col,adj_value):
        plt.plot(df[col], df[adj_value],'.')
        plt.plot(df[col],trend_poly(df[col]))
        plt.show()