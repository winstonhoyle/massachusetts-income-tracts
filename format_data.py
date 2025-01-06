import geopandas as gpd
import numpy as np
import pandas as pd

# Function for formatting numbers from tract csv
def format_num(input_val):
    val = str(input_val).replace(',', "")
    try:
        return float(val)
    except ValueError:
        if val == '-' or val == 'N' or val == '(X)':
            return np.nan
        elif val == '250000+':
            return 250000
        else:
            print(val)


# Open income data
income_df = pd.read_csv('data/ACSST5Y2023.S1901_2025-01-06T030207/ACSST5Y2023.S1901-Data.csv')

# Format columns
output_cols = {}
for col in list(income_df.iloc[0])[2:-1]:
    col_split = col.split('!!')
    if col_split[0] == 'Margin of Error':
        continue
    elif col_split[-1] in [
        'Household income in the past 12 months',
        'Family income in the past 12 months',
        'Nonfamily income in the past 12 months',
    ]:
        continue
    else:
        output_cols[
            col
        ] = f'{col_split[-1].strip().lower().replace(" ", "_").replace("$", "")}-{col_split[1].lower().replace("-", "_").replace(" ", "_")}'

# Set labels
income_df.columns = income_df.iloc[0]

# Format file
income_df = income_df.rename(columns=output_cols)
income_df = income_df.drop(0)
income_df = income_df[['Geography', *output_cols.values()]]

# Format columns
for column in output_cols.values():
    income_df[column] = income_df[column].apply(lambda value: format_num(value))

income_df = income_df.rename(columns={'Geography': 'GEOIDFQ'})

# Open Tract file
census_track_gdf = gpd.read_file('data/tl_2023_25_tract/tl_2023_25_tract.shp')
census_track_gdf = census_track_gdf[['geometry', 'GEOIDFQ']]

# Output
census_track_with_income_information = census_track_gdf.merge(
    income_df, on='GEOIDFQ', how='inner'
)
census_track_with_income_information = census_track_with_income_information.to_crs(4326)
census_track_with_income_information.to_file('app/mass.geojson')
