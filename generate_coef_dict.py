import pandas as pd
from generate_coef import GenerateCoef

 
raw_data = pd.read_csv(r'../New folder/train.csv')
#raw_data = raw_data[raw_data['meter_reading'] != 0]

# various counts
#print(raw_data.dtypes)
#print(raw_data.groupby('building_id')['meter'].value_counts())

# fill in missing data?
#basis = pd.DataFrame(
#        {'Hours': pd.date_range('2018-01-01', '2019-01-01', freq='1H', closed='left')}
#     )
#basis = basis.set_index('Hours')

coef_dict ={}
def generate_coef_dict(raw_data):
    
    for building in raw_data.building_id.unique():
        rd_temp_bldg = raw_data[raw_data['building_id'] == building].copy()
        for util in rd_temp_bldg.meter.unique():
            rd_temp_bldg_util = rd_temp_bldg[rd_temp_bldg['meter'] == util].copy()
            print(building, util, len(rd_temp_bldg_util))
            
            generate_coef = GenerateCoef(rd_temp_bldg_util, building, util, False)
            coef_dict[building,util,'M'] = generate_coef.monthly_coef
            coef_dict[building,util,'W'] = generate_coef.weekly_coef
            coef_dict[building,util,'D'] = generate_coef.daily_coef
            coef_dict[building,util,'H'] = generate_coef.hourly_coef
            coef_dict[building,util,'OD'] = generate_coef.off_hours_energy
            
    return coef_dict      

print(generate_coef_dict(raw_data))