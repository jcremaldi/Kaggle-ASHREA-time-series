import pandas as pd
import warnings
warnings.filterwarnings("ignore")

index = pd.date_range(start='1/1/2016  12:00:00 AM', end='12/31/2016  11:00:00 PM', freq = 'H')
columns = ['timestamp']

missing = pd.DataFrame(index=index, columns=columns).fillna(0)

raw_data = pd.read_csv(r'../New folder/data/train_short.csv')
raw_data = raw_data[raw_data['meter_reading'] != 0]

def fill_timeseries():
    for building in raw_data.building_id.unique():
        rd_temp_bldg = raw_data[raw_data['building_id'] == building].copy()
        for util in rd_temp_bldg.meter.unique():
            temp_missing = missing.copy()
            util_rd_temp_bldg = rd_temp_bldg[rd_temp_bldg['meter'] == util]
            util_rd_temp_bldg.timestamp = pd.to_datetime(util_rd_temp_bldg.timestamp)
            util_rd_temp_bldg = util_rd_temp_bldg.set_index('timestamp')
            temp_missing = temp_missing.drop(util_rd_temp_bldg.index)
            
            temp_missing['building_id'] = building
            temp_missing['meter'] = util
            temp_missing['meter_reading'] = 0

            temp_raw_data = pd.concat([util_rd_temp_bldg, temp_missing], sort=True)
            temp_raw_data = temp_raw_data.sort_index()
            temp_raw_data = temp_raw_data.drop(columns=['Unnamed: 0','timestamp'])
            temp_raw_data.to_csv('test.csv')
            
            day_conv = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, 'Saturday':6, 'Sunday':7}   
            temp_raw_data['H'] = temp_raw_data.index.hour
            temp_raw_data['D'] = temp_raw_data.index.weekday_name
            temp_raw_data['W'] = temp_raw_data.index.week
            temp_raw_data['M'] = temp_raw_data.index.month
            temp_raw_data['date'] = temp_raw_data.index.date
            temp_raw_data['D'] = temp_raw_data['D'].map(day_conv)
            temp_raw_data = temp_raw_data.fillna(0)
            print(temp_raw_data)
            #print(temp_raw_data.describe(include='all'))

if __name__ == "__main__":
    fill_timeseries()




















