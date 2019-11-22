import pandas as pd
from generate_coef import GenerateCoef
import random 

def create_short_raw():
    raw_data = pd.read_csv(r'../New folder/data/train.csv')
    
    raw_data = raw_data[raw_data['building_id'].isin(random.sample(range(0, 1448), 5))]
    raw_data.to_csv(r'../New folder/data/train_short.csv')
    
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

raw_data = pd.read_csv(r'../New folder/data/train_short.csv')
#create_short_raw()
coef_dict, data_comb  = generate_coef_dict(raw_data)     
data_comb = combine_data(raw_data, data_comb)
print(data_comb)
#, ['M','W','D','H','OD']


    