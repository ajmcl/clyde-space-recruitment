import geopandas as gpd
import pandas as pd
from pathlib import Path

# Set file paths
base_dir = Path(__file__).parent.parent
volcano_path = base_dir / "data" / "GVP_Volcano_List_Holocene.csv"
eruptions_path = base_dir / "data" / "GVP_Eruption_List.csv"
# volcano_path = "/Users/alexandermclaughlin/Code/clyde-space-recruitment/data/GVP_Volcano_List_Holocene.csv"
# eruptions_path = "/Users/alexandermclaughlin/Code/clyde-space-recruitment/data/GVP_Eruption_List.csv"

# Import volcanoes and eruption data
volc_list = pd.read_csv(volcano_path)
erup_list = pd.read_csv(eruptions_path)

# Initilise data quality report
report_path = base_dir / "outputs" / "eruption_data_quality_report.txt"
# report_path = "/Users/alexandermclaughlin/Code/clyde-space-recruitment/data/eruption_data_quality_report.txt"
with open(report_path, 'w') as report:
    report.write('Data Quality Report for Volcanic Eruption Dataset\n')
    report.write('=================================================\n\n')

## Validation checks on base datasets
def base_data_val_chk():
    '''Validate base datasets for non-integer and duplicate values in Volcano Number and Eruption Number fields'''
    volcnum_int_chk = volc_list['Volcano Number'].map(type) == int
    volcnum_dupl_chk = volc_list['Volcano Number'].duplicated() == True
    erupnum_int_chk = erup_list['Eruption Number'].map(type) == int
    erupnum_dupl_chk = erup_list['Eruption Number'].duplicated() == True
    return volcnum_int_chk, volcnum_dupl_chk, erupnum_int_chk, erupnum_dupl_chk

volcnum_int_chk, volcnum_dupl_chk, erupnum_int_chk, erupnum_dupl_chk = base_data_val_chk()

with open(report_path, 'a') as report:
    report.write('Initial Base Dataset Validation Checks\n')
    report.write('------------------------------\n')
    report.write(f'Non integer Volcano Numbers: {len(volcnum_int_chk) - volcnum_int_chk.value_counts().loc[True]}\n')
    report.write(f'Duplicate Volcano Numbers: {len(volcnum_dupl_chk) - volcnum_dupl_chk.value_counts().loc[False]}\n')
    report.write(f'Non integer Eruption Numbers: {len(erupnum_int_chk) - erupnum_int_chk.value_counts().loc[True]}\n')
    report.write(f'Duplicate Eruption Numbers: {len(erupnum_dupl_chk) - erupnum_dupl_chk.value_counts().loc[False]}\n\n')

# Clean base datasets
erup_list.drop_duplicates(subset='Eruption Number', keep='last', inplace=True)

# Post cleaning validation checks on base datasets

volcnum_int_chk_cln, volcnum_dupl_chk_cln, erupnum_int_chk_cln, erupnum_dupl_chk_cln = base_data_val_chk()

with open(report_path, 'a') as report:
    report.write('Post-Cleaning Base Dataset Validation Checks\n')
    report.write('---------------------------------------------\n')
    report.write(f'Non integer Volcano Numbers: {len(volcnum_int_chk_cln) - volcnum_int_chk_cln.value_counts().loc[True]}\n')
    report.write(f'Duplicate Volcano Numbers: {len(volcnum_dupl_chk_cln) - volcnum_dupl_chk_cln.value_counts().loc[False]}\n')
    report.write(f'Non integer Eruption Numbers: {len(erupnum_int_chk_cln) - erupnum_int_chk_cln.value_counts().loc[True]}\n')
    report.write(f'Duplicate Eruption Numbers: {len(erupnum_dupl_chk_cln) - erupnum_dupl_chk_cln.value_counts().loc[False]}\n\n')

# Merge base datasets
volc_erup = pd.merge(erup_list, volc_list, left_on="Volcano Number", right_on="Volcano Number", how="left")

# Derive dates
volc_erup['Start_Date'] = pd.to_datetime(
    volc_erup[['Start Year', 'Start Month', 'Start Day']].rename(columns={
        'Start Year': 'year',
        'Start Month': 'month',
        'Start Day': 'day'
    }),
    errors='coerce'
)

volc_erup['End_Date'] = pd.to_datetime(
    volc_erup[['End Year', 'End Month', 'End Day']].rename(columns={
        'End Year': 'year',
        'End Month': 'month',
        'End Day': 'day'
    }),
    errors='coerce'
)

# Derive eruption duration
volc_erup['Eruption_Duration_Days'] = (volc_erup['End_Date'] - volc_erup['Start_Date']).dt.days.astype('Int64')

# Initial Validation checks on merged dataset
if volc_erup['Start_Date'].dt.year.describe().loc['max'] == volc_erup['Start Year'].describe().loc['max']:
    start_year_val = 'Pass'
else:
    start_year_val = 'Fail'
if volc_erup['End_Date'].dt.year.describe().loc['max'] == volc_erup['End Year'].describe().loc['max']:
    end_year_val = 'Pass'
else:
    end_year_val = 'Fail'
volc_name_chk = volc_erup['Volcano Name_x'] == volc_erup['Volcano Name_y']
lat_chk = volc_erup['Latitude_x'] == volc_erup['Latitude_y']
lon_chk = volc_erup['Longitude_x'] == volc_erup['Longitude_y']
null_dur = volc_erup['Eruption_Duration_Days'].isna().sum()


with open(report_path, 'a') as report:
    report.write('\n\nInitial Merged Dataset Validation Checks\n')
    report.write('---------------------------------------------\n')
    report.write(f'Start Year check: {start_year_val}\n')
    report.write(f'End Year check: {end_year_val}\n')
    report.write(f'Volcano Name consistency errors: {len(volc_name_chk) - (volc_name_chk == True).value_counts().loc[True]}\n')
    report.write(f'Latitude consistency errors: {len(lat_chk) - (lat_chk == True).value_counts().loc[True]}\n')
    report.write(f'Longitude consistency errors: {len(lon_chk) - (lon_chk == True).value_counts().loc[True]}\n')
    report.write(f'Null eruption duration: {null_dur}\n\n')
    # report.write(f'Start_Date stats: {volc_erup["Start_Date"].dt.year.describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'Start Year stats: {volc_erup["Start Year"].describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'End_Date stats: {volc_erup["End_Date"].dt.year.describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'End Year stats: {volc_erup["End Year"].describe().loc[["min", "max"]].astype(int)}\n')

# Clean merged dataset
# Filter merged dataset to eruptions since 1700 AD to accommodate limitaions of pd.datetime
volc_erup = volc_erup[volc_erup['Start Year'] >= 1700]

# Keep only records with null uncertainty in start and end year
volc_erup = volc_erup.query("`Start Year Uncertainty`.isnull() & `End Year Uncertainty`.isnull()")

# Keep only records that have an erupttion duration value
volc_erup = volc_erup.query("Eruption_Duration_Days.notnull()")

# Convert to geodataframe
eruptions_gdf = gpd.GeoDataFrame(volc_erup, geometry=gpd.points_from_xy(volc_erup['Longitude_x'], volc_erup['Latitude_x']), crs='EPSG:4326')

# Final Validation checks
if eruptions_gdf['Start_Date'].dt.year.describe().loc['max'] == eruptions_gdf['Start Year'].describe().loc['max']:
    start_year_val = 'Pass'
else:
    start_year_val = 'Fail'
if eruptions_gdf['End_Date'].dt.year.describe().loc['max'] == eruptions_gdf['End Year'].describe().loc['max']:
    end_year_val = 'Pass'
else:
    end_year_val = 'Fail'
start_year_uc = (eruptions_gdf['Start Year Uncertainty'] >=1).value_counts().loc[False]
end_year_uc = (eruptions_gdf['End Year Uncertainty'] >= 1).value_counts().loc[False]
volc_name_chk = eruptions_gdf['Volcano Name_x'] == eruptions_gdf['Volcano Name_y']
lat_chk = eruptions_gdf['Latitude_x'] == eruptions_gdf['Latitude_y']
lon_chk = eruptions_gdf['Longitude_x'] == eruptions_gdf['Longitude_y']
null_dur = eruptions_gdf['Eruption_Duration_Days'].isna().sum()

with open(report_path, 'a') as report:
    report.write('Final Merged Dataset Validation Checks\n')
    report.write('---------------------------------------------\n')
    report.write(f'Start Year check: {start_year_val}\n')
    report.write(f'End Year check: {end_year_val}\n')
    report.write(f'Start Year uncertainty > 1: {len(eruptions_gdf["Start Year Uncertainty"]) - start_year_uc}\n')
    report.write(f'End Year uncertainty > 1: {len(eruptions_gdf["End Year Uncertainty"]) - end_year_uc}\n')
    report.write(f'Volcano Name consistency errors: {len(volc_name_chk) - (volc_name_chk == True).value_counts().loc[True]}\n')
    report.write(f'Latitude consistency errors: {len(lat_chk) - (lat_chk == True).value_counts().loc[True]}\n')
    report.write(f'Longitude consistency errors: {len(lon_chk) - (lon_chk == True).value_counts().loc[True]}\n')
    report.write(f'Null eruption duration: {null_dur}\n')
    # report.write(f'Start_Date stats:\n{eruptions_gdf["Start_Date"].dt.year.describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'Start Year stats:\n{eruptions_gdf["Start Year"].describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'End_Date stats:\n{eruptions_gdf["End_Date"].dt.year.describe().loc[["min", "max"]].astype(int)}\n')
    # report.write(f'End Year stats:\n{eruptions_gdf["End Year"].describe().loc[["min", "max"]].astype(int)}\n')

# Select columns for final dataset
cols_to_keep = ['Eruption Number', 'Volcano Number', 'Volcano Name_x', 'Latitude_x', 'Longitude_x', 'Country', 'Volcanic Region', 'Start_Date', 'End_Date', 'Eruption_Duration_Days',  'Primary Volcano Type', 'Activity Evidence', 'Elevation (m)', 'Tectonic Setting', 'geometry']
eruptions_gdf = eruptions_gdf[cols_to_keep].copy()
eruptions_gdf.rename(columns={
    'Volcano Name_x': 'Volcano Name',
    'Latitude_x': 'Latitude',
    'Longitude_x': 'Longitude',
    'Start_Date': 'Start Date',
    'End_Date': 'End Date',
    'Eruption_Duration_Days': 'Eruption Duration Days'
}, inplace=True)


# Generate data quality report


# Export as geojson
export_path = base_dir / "outputs" / "eruptions_cleaned.geojson"
# export_path = "/Users/alexandermclaughlin/Code/clyde-space-recruitment/outputs/eruptions_cleaned.geojson"
eruptions_gdf.to_file(export_path, driver='GeoJSON')

