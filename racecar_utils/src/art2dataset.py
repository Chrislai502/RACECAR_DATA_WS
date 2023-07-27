import pandas as pd
import pymap3d as pm
import os 

# The initial GPS origin
GPS_ORIGIN_LAT1 = 36.274445823
GPS_ORIGIN_LON1 = -115.012602577
GPS_ORIGIN_ALT1 = 597.7

# The new GPS origin
GPS_ORIGIN_LAT2 = 36.272371177449344    # fill in your new GPS origin here
GPS_ORIGIN_LON2 = -115.01030828834901   # fill in your new GPS origin here
GPS_ORIGIN_ALT2 = 594                   # fill in your new GPS origin here

# Load the CSV file
current_dir = os.getcwd()
filenames = ['iac_lvms_inside.csv', 'iac_lvms_outside.csv']
file_path = os.path.join(current_dir, '..', 'params', filenames[1])
df = pd.read_csv(file_path, header=None, names=['e', 'n', 'u'])  # adjust file name and path if necessary

# Assuming the ENU coordinates are in columns 'e', 'n', 'u' in the df
east = df['e'].values
north = df['n'].values
up = df['u'].values

# Convert from ENU (origin at GPS_ORIGIN1) to Geodetic coordinates
lat, lon, alt = pm.enu2geodetic(east, north, up, GPS_ORIGIN_LAT1, GPS_ORIGIN_LON1, GPS_ORIGIN_ALT1)

# Convert from Geodetic coordinates to ENU (origin at GPS_ORIGIN2)
e_new, n_new, u_new = pm.geodetic2enu(lat, lon, alt, GPS_ORIGIN_LAT2, GPS_ORIGIN_LON2, GPS_ORIGIN_ALT2)

# Create a new dataframe with the transformed coordinates
df_new = pd.DataFrame({
    'e_new': e_new,
    'n_new': n_new,
    'u_new': u_new
})

# Save the new coordinates to a new CSV file
extension = "transformed"
df_new.to_csv(f'iac_lvms_outside_{extension}.csv', index=False, header=False)