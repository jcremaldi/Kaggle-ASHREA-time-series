import pandas as pd

sid_all = [1,4,5,7 ]
sid_yb = [0,2,3,15]
sid_floors = [8,10]
sid_none = [6,9,11,12,13,14]

raw_data = pd.read_csv('data/weather_train.csv')
print(raw_data.info(verbose=True),'\n')
raw_data = raw_data.drop(columns=['cloud_coverage'])

def missing_weather_fill(df):
    df['air_temperature'].fillna(df['air_temperature'].mean(), inplace = True)
    df['dew_temperature'].fillna(df['dew_temperature'].mean(), inplace = True)
    df['precip_depth_1_hr'].fillna(df['precip_depth_1_hr'].mean(), inplace = True)
    df['sea_level_pressure'].fillna(df['sea_level_pressure'].mean(), inplace = True)
    df['wind_direction'].fillna(df['wind_direction'].mean(), inplace = True)
    df['wind_speed'].fillna(df['wind_speed'].mean(), inplace = True)

    return df

raw_data_sid_all = raw_data[raw_data['site_id'].isin(sid_all)]
raw_data_sid_all = missing_weather_fill(raw_data_sid_all)

raw_data_sid_yb = raw_data[raw_data['site_id'].isin(sid_yb)]
raw_data_sid_yb = missing_weather_fill(raw_data_sid_yb)
 
raw_data_sid_floors = raw_data[raw_data['site_id'].isin(sid_floors)]
raw_data_sid_floors = missing_weather_fill(raw_data_sid_floors)

raw_data_sid_none = raw_data[raw_data['site_id'].isin(sid_none)]
raw_data_sid_none = missing_weather_fill(raw_data_sid_none)

weather_fixed = pd.concat([raw_data_sid_all, raw_data_sid_yb, raw_data_sid_floors, raw_data_sid_none])

print(weather_fixed.info(verbose=True))
raw_data_comb.to_csv('weather_fixed.csv', index = False)






































