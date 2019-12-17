import pandas as pd
import numpy as np
from generate_coef import GenerateCoef
import random 


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
            
            data_comb.loc[((data_comb['building_id'] == building) & 
                           (data_comb['meter'] == util)),'meter_ave'] = generate_coef.ave_meter            
            data_comb.loc[((data_comb['building_id'] == building) & \
                           (data_comb['meter'] == util)),'off_hours_ave'] = generate_coef.off_hours_ave

    return coef_dict, data_comb      

def combine_data(raw_data, data_comb):
    building_data = pd.read_csv(r'../New folder/data/building_metadata.csv')
    data_comb = data_comb.merge(building_data, on='building_id', how='left')
    return data_comb

def date_breakdown(df):
    day_conv = {'Monday':1, 'Tuesday':2, 'Wednesday':3, 'Thursday':4, 'Friday':5, \
                'Saturday':6, 'Sunday':7}   
    df['H'] = df.index.hour
    df['M'] = df.index.month
    df['W'] = df.index.week
    df['D'] = df.index.weekday_name
    df['date'] = df.index.date
    df['D'] = df['D'].map(day_conv)
    df = df.fillna(0)        
    
    return df

def fill_timeseries(raw_data, coef_dict, data_comb):
    # create a blank date range df and filter out the existing data
    index = pd.date_range(start='1/1/2016', end='12/31/2016', freq = 'H')
    columns = ['timestamp']
    missing = pd.DataFrame(index=index, columns=columns)
    missing.index = pd.to_datetime(missing.index)
    missing['meter_reading'] = 0
    missing = date_breakdown(missing)
    
    corrected_data = pd.DataFrame()
    
    raw_data['timestamp'] = pd.to_datetime(raw_data['timestamp'])
    raw_data = raw_data.set_index('timestamp')
    raw_data = date_breakdown(raw_data)
    
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
                holidays = pd.date_range(start='2016-12-21', end='2016-12-31', freq='D')
                temp_missing.loc[temp_missing.date.astype('str').isin(holidays),'D'] = 99
                #2016 was a leap year day
                other_holidays = ['2016-02-29','2016-01-01','2016-05-30','2016-11-24',\
                                  '2016-07-04','2016-03-25','2016-01-18','2016-09-05']
                temp_missing.loc[temp_missing.date.astype('str').isin(other_holidays),'D'] = 99

                off_hours_temp = temp_missing[temp_missing.D.isin([6,7,99])].copy()
                temp_ave_meter = data_comb.loc[((data_comb['building_id'] == building) & \
                                                (data_comb['meter'] == util)),'off_hours_ave']
                # *** first df to add
                off_hours_temp.loc[:,'meter_reading'] = temp_ave_meter
                temp_missing = temp_missing.drop(off_hours_temp.index)
                
                # cycle through each hour
                for index, row in temp_missing.iterrows():
                    meter_temp = 0
                    # use the coeficcients in reverse order to calculate the missing meter readings
                    for time_unit in ['M','W','D','H']:
                        p = np.poly1d(coef_dict[(str(building),str(util),str(time_unit))])            
                        meter_temp = meter_temp + p(temp_missing.loc[index, time_unit])
                        # (-) meter readings dont occur, so eliminate the possibility
                        if meter_temp < 0:
                            meter_temp = 0
                    temp_missing.loc[index,'meter_reading'] = meter_temp
                    #print(time_unit, index, p(temp_missing.loc[index, time_unit]), temp_save, meter_temp)    
                
                temp_missing = pd.concat([temp_missing, off_hours_temp], sort=True)
            temp_raw = pd.concat([temp_raw, temp_missing], sort=True)
            temp_raw = temp_raw.sort_index()
        corrected_data = pd.concat([corrected_data,temp_raw])
        corrected_data = corrected_data.dropna(subset=['meter'])
        corrected_data = corrected_data.drop(columns=['timestamp'])
        corrected_data = corrected_data.sort_values(by=['building_id','meter'])
        corrected_data.to_csv('test.csv', index = False)
                
if __name__ == "__main__": 
    
    raw_data = pd.read_csv(r'../New folder/data/train_short.csv')
    # assumption: '0' readings are mistakes and should be omitted
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






















































