import pandas as pd
import numpy as np
from generate_coef import GenerateCoef
import random 
import numpy as np
import warnings
warnings.filterwarnings("ignore")


creat_short = False
generate_coef = True
data_cbn = False
fill_ts = True

def create_short_raw():
    raw_data = pd.read_csv(r'../New folder/data/train.csv')
    
    raw_data = raw_data[raw_data['building_id'].isin(random.sample(range(0, 1448), 5))]
    raw_data.to_csv(r'../New folder/data/train_short.csv', index=False)
    
def generate_coef_dict(raw_data):
    coef_dict ={}
    data_comb = raw_data[['building_id','meter']].copy().drop_duplicates()    
    
    for building in raw_data.building_id.unique():
        rd_temp_bldg = raw_data[raw_data['building_id'] == building].copy()
        for util in rd_temp_bldg.meter.unique():
            rd_temp_bldg_util = rd_temp_bldg[rd_temp_bldg['meter'] == util].copy()
            print(building, util, len(rd_temp_bldg_util))
            
            
            generate_coef = GenerateCoef(rd_temp_bldg_util, building, util, False)
            
            coef_dict[str(building), str(util), 'M'] = generate_coef.monthly_coef
            coef_dict[str(building), str(util), 'W'] = generate_coef.weekly_coef
            coef_dict[str(building), str(util), 'D'] = generate_coef.daily_coef
            coef_dict[str(building), str(util), 'H'] = generate_coef.hourly_coef
            
            data_comb.loc[((data_comb['building_id'] == building) & \
                           (data_comb['meter'] == util)),'meter_ave'] = generate_coef.ave_meter            
            data_comb.loc[((data_comb['building_id'] == building) & \
                           (data_comb['meter'] == util)),'off_hours_ave'] = generate_coef.off_hours_ave

    return coef_dict, data_comb      
 
def combine_data(raw_data, data_comb):
    building_data = pd.read_csv(r'../New folder/data/building_metadata.csv')
    data_comb = data_comb.merge(building_data, on='building_id', how='left')
    return data_comb

def fill_timeseries(raw_data, coef_dict, data_comb):
    # create a blank date range df and filter out the existing data
    index = pd.date_range(start='1/1/2016', end='12/31/2016', freq = 'H')
    columns = ['timestamp']
    missing = pd.DataFrame(index=index, columns=columns)
    missing.index = pd.to_datetime(missing.index)
    missing['meter_reading'] = 0
    day_conv = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, 'Saturday':6, 'Sunday':7}   
    missing['H'] = missing.index.hour
    missing['M'] = missing.index.month
    missing['W'] = missing.index.week
    missing['D'] = missing.index.weekday_name
    missing['date'] = missing.index.date
    missing['D'] = missing['D'].map(day_conv)
    missing = missing.fillna(0)    
    
    raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
    raw_data = raw_data.set_index('timestamp')       
    
    for building in raw_data.building_id.unique():
        temp_raw = raw_data[raw_data['building_id'] == building].copy()
        for util in temp_raw.meter.unique():
            temp_raw = raw_data[raw_data['meter'] == util].copy()
            
            temp_missing = missing.copy()
            if len(temp_missing) > len(temp_raw):
                temp_missing = temp_missing.drop(temp_raw.index, errors = 'ignore')
    
                # drop the existing data index to find the missing data
                temp_missing = temp_missing.drop(temp_raw.index, errors = 'ignore')
    
                temp_missing['building_id'] = building
                temp_missing['meter'] = util            
                
                # pull out the holidays and weekend, use a simple average for those
                holidays = pd.date_range(start='2016-01-01', end='2016-12-31', freq='D')
                temp_missing.loc[temp_missing.date.astype('str').isin(holidays),'D'] = 99
                off_hours_temp = temp_missing[temp_missing.D.isin([6,7,99])].copy()
                temp_ave_meter = data_comb.loc[((data_comb['building_id'] == building) & (data_comb['meter'] == util)),'off_hours_ave']
                off_hours_temp.loc[:,'meter_reading'] = temp_ave_meter
                temp_missing = temp_missing.drop(off_hours_temp.index)
                
                # cycle through each hour
                for index, row in temp_missing.iterrows():
                    meter_temp = 0
                    # use the coeficcients in reverse order to calculate the missing meter readings
                    for time_unit in ['H','D','W','M']:
                        p = np.poly1d(coef_dict[(str(building),str(util),str(time_unit))])            
                        meter_temp += p(temp_missing.loc[index, time_unit])
    
                    print(time_unit, temp_missing.loc[index, time_unit], meter_temp)
    
                temp_raw_data = pd.concat([temp_raw, temp_missing], sort=True)
                temp_raw_data = temp_raw_data.sort_index()
                temp_raw_data = temp_raw_data.drop(columns=['timestamp'])
                temp_raw_data.to_csv('test.csv')
                
                #print(temp_raw_data.describe(include='all'))

if __name__ == "__main__": 
    
    raw_data = pd.read_csv(r'../New folder/data/train_short.csv')
    raw_data = raw_data[raw_data['meter_reading'] != 0]
    
    if creat_short:
        create_short_raw()
    if generate_coef:
        coef_dict, data_comb  = generate_coef_dict(raw_data)     
    if data_cbn:
        data_comb = combine_data(raw_data, data_comb)
        print(data_comb['meter_ave'],data_comb['off_hours_ave'])
    if fill_ts:
        fill_timeseries(raw_data, coef_dict, data_comb)






















































