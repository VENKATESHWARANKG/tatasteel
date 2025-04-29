# %%
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler
import os
from datetime import datetime

# %%
# Read file 
df = pd.read_excel('Data/raw_data_1903_fy25_merged.xlsx')
df_visual = df.copy()
df['new_market_potential'] = df['new_market_potential'].fillna(df['market_potential'])

# df_display = df.copy() #For display only
# df = df.fillna(0)
# df_ones = df.copy()
# df_ones = df_ones.replace(0, 1)


# %%
sales_columns = ['Dealer_Code'] + [col for col in df.columns if "sales" in col]
#ov_columns = ['Dealer_Code'] + [col for col in df.columns if "Counter" in col]
#sales_columns = ['Dealer_Code'] + [col for col in df.columns if "sales" in col]
#incentive_columns = ['Dealer_Code'] + [col for col in df.columns if "Incentive" in col and 'ton' not in col]
#incentive_per_ton_columns = ['Dealer_Code'] + [col for col in df.columns if "Incentive_per_ton" in col]
cs_columns = ['Dealer_Code'] + [col for col in df.columns if "CS" in col]
#monsoon_columns = ['Dealer_Code'] + [col for col in df.columns if "Monsoon" in col]
target_columns = ['Dealer_Code'] + [col for col in df.columns if "Target" in col]
other_colums = ['Dealer_Code','dealer_district','dealer_taluka','population','taluka_population','market_potential', 'new_market_potential']
df_oth = df[['Dealer_Code','Dealer_Name','dealer_district','dealer_taluka','dealer_type',
'population','taluka_population','market_potential', 'new_market_potential']]
oth_display = ['Dealer_Code'] #To add the the display column in the end

# Splitting into two DataFrames
df_retail_sales = df[sales_columns]
df_ts_sales = df[sales_columns]
#df_incentive = df[incentive_columns]
#df_incentive_per_ton = df[incentive_per_ton_columns]
#df_closing_stock = df[cs_columns]
#df_monsoon = df[monsoon_columns]
#df_ov_sales = df[ov_columns]
df_target = df[target_columns]
df_others = df[other_colums]



#df_retail_sales.head(600)

#Replacing the 2425 columns with the new values
df_retail_sales = df_retail_sales[['Dealer_Code', 'Apr_2223_sales', 'May_2223_sales', 'Jun_2223_sales',
       'Jul_2223_sales', 'Aug_2223_sales', 'Sep_2223_sales', 'Oct_2223_sales',
       'Nov_2223_sales', 'Dec_2223_sales', 'Jan_2223_sales', 'Feb_2223_sales',
       'Mar_2223_sales', 'Apr_2324_sales', 'May_2324_sales', 'Jun_2324_sales',
       'Jul_2324_sales', 'Aug_2324_sales', 'Sep_2324_sales', 'Oct_2324_sales',
       'Nov_2324_sales', 'Dec_2324_sales', 'Jan_2324_sales', 'Feb_2324_sales',
       'Mar_2324_sales',
        #'Apr_2425_sales', 'May_2425_sales', 'Jun_2425_sales',
       #'Jul_2425_sales', 'Aug_2425_sales', 'Sep_2425_sales', 'Oct_2425_sales',
       #'Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales', 'Feb_2425_sales',
       #'Mar_2425_sales',
       'Apr_2425_sales_new', 'May_2425_sales_new',
       'Jun_2425_sales_new', 'Jul_2425_sales_new', 'Aug_2425_sales_new',
       'Sep_2425_sales_new', 'Oct_2425_sales_new', 'Nov_2425_sales_new',
       'Dec_2425_sales_new', 'Jan_2425_sales_new', 'Feb_2425_sales_new',
       'Mar_2425_sales_new']].copy()

# Remove "_new" suffix from all column names that end with it
df_retail_sales.columns = [col.replace('_new', '') if col.endswith('_new') else col for col in df_retail_sales.columns]
df_retail_sales.columns

df_target = df_target[['Dealer_Code', 'Apr_2223_Target', 'May_2223_Target', 'Jun_2223_Target',
       'Jul_2223_Target', 'Aug_2223_Target', 'Sep_2223_Target',
       'Oct_2223_Target', 'Nov_2223_Target', 'Dec_2223_Target',
       'Jan_2223_Target', 'Feb_2223_Target', 'Mar_2223_Target',
       'Apr_2324_Target', 'May_2324_Target', 'Jun_2324_Target',
       'Jul_2324_Target', 'Aug_2324_Target', 'Sep_2324_Target',
       'Oct_2324_Target', 'Nov_2324_Target', 'Dec_2324_Target',
       'Jan_2324_Target', 'Feb_2324_Target', 'Mar_2324_Target',
       #'Apr_2425_Target', 'May_2425_Target', 'Jun_2425_Target',
       #'Jul_2425_Target', 'Aug_2425_Target', 'Sep_2425_Target',
       'Apr_2425_Target_new', 'May_2425_Target_new', 'Jun_2425_Target_new',
       'Jul_2425_Target_new', 'Aug_2425_Target_new', 'Sep_2425_Target_new',
       'Oct_2425_Target_new', 'Nov_2425_Target_new', 'Dec_2425_Target_new',
       'Jan_2425_Target_new', 'Feb_2425_Target_new', 'Mar_2425_Target_new']].copy()

# Remove "_new" suffix from all column names that end with it
df_target.columns = [col.replace('_new', '') if col.endswith('_new') else col for col in df_target.columns]
df_target.columns

#For display
df_display = df_retail_sales.copy()
df_display = df_display.merge(df_target, on = "Dealer_Code", how = 'left')

# %%
# Identify active dealers and total months of data 
# 2022-2023,
# 2023-24
# 24-25


def calculate_active_months(df):
    sales_columns = [col for col in df.columns if "sales" in col]
    
    
    def first_nonzero_month(rows):
        for col in sales_columns:
            if rows[col].sum() > 0:
                return col  # Returning the first month with a non-zero value
        return None
    
    def last_nonzero_month(rows):
        for col in reversed(sales_columns):
            if rows[col].sum() > 0:
                return col  # Returning the last month with a non-zero value
        return None
    
    def active_months_duration(rows):
        first_month = first_nonzero_month(rows)
        last_month = last_nonzero_month(rows)
        if first_month and last_month:
            return sales_columns.index(last_month) - sales_columns.index(first_month) + 1
        return 0
    
    grouped_df = df.groupby('Dealer_Code').apply(
        lambda x: pd.Series({
            'First_Active_Month': first_nonzero_month(x),
            'Last_Active_Month': last_nonzero_month(x),
            'Total_Active_Months': active_months_duration(x)
        })
    ).reset_index()

    return grouped_df
    
df_retail_sales = df_retail_sales.fillna(0)
result_df = calculate_active_months(df_retail_sales)
last_months = ['Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']

# Filter out dealers that do not have a non-zero value in Jan, Feb, or Mar 2324
grouped_df_filtered = result_df[result_df['Last_Active_Month'].isin(last_months)]
    
# Join the result with the original dataframe based on Dealer_Code
df_merged = df_retail_sales.merge(grouped_df_filtered[['Dealer_Code', 'Total_Active_Months']], on='Dealer_Code', how='left')

#Dropping inactive dealers
df_merged_dropped = df_merged.dropna(subset=['Total_Active_Months']).copy()

#Editing the display to include only the active dealers
df_display = df_display[df_display['Dealer_Code'].isin(df_merged_dropped['Dealer_Code'])]

# df_merged.head(600)

# For deseasonalize 
# df_des = df_merged
# df_des = df_des.merge(df_others, on='Dealer_Code', how='left')

# district_wise_dealers = df_des[['Dealer_Code','Total_Active_Months', 'dealer_district']].drop_duplicates()
# filtered_dealers = district_wise_dealers[district_wise_dealers['Total_Active_Months'] >= 6]

# filtered_dealers = filtered_dealers[['Dealer_Code', 'dealer_district']].drop_duplicates()
# df_des = pd.merge(df_des, filtered_dealers, on=['Dealer_Code', 'dealer_district'], how='inner')
# df_des.head()

# %%
df_original_reshaped = df_merged
df_original_reshaped = df_original_reshaped.merge(df_others, on='Dealer_Code', how='left')
df_original_reshaped.head()

# %%
def convert_fy_to_price(col_name):
    try:
        # Keep 'Dealer_Code' unchanged
        if col_name == "Dealer_Code":
            return col_name

        # Extract month and fiscal year
        parts = col_name.split("_")
        month = parts[0]  # Extract month abbreviation
        fy_start = int("20" + parts[1][:2])  # Extract fiscal start year

        # Determine the actual year
        actual_year = fy_start if month in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] else fy_start + 1

        return f"{month}-{str(actual_year)[-2:]}"  # Convert to "Aug-22" format
    except:
        return col_name  # Return original if conversion fails

# Apply the function to rename columns
# df_retail_sales.rename(columns={col: convert_fy_to_price(col) for col in df_retail_sales.columns}, inplace=True)
# df_ts_sales.rename(columns={col: convert_fy_to_price(col) for col in df_ts_sales.columns}, inplace=True)
# df_incentive.rename(columns={col: convert_fy_to_price(col) for col in df_incentive.columns}, inplace=True) 
# df_incentive_per_ton.rename(columns={col: convert_fy_to_price(col) for col in df_incentive_per_ton.columns}, inplace=True) 
# df_closing_stock.rename(columns={col: convert_fy_to_price(col) for col in df_closing_stock.columns}, inplace=True)
# df_monsoon.rename(columns={col: convert_fy_to_price(col) for col in df_monsoon.columns}, inplace=True) 
# df_ov_sales.rename(columns={col: convert_fy_to_price(col) for col in df_ov_sales.columns}, inplace=True) 

# df_des.rename(columns={col: convert_fy_to_price(col) for col in df_des.columns}, inplace=True)
df_original_reshaped.rename(columns={col: convert_fy_to_price(col) for col in df_original_reshaped.columns}, inplace=True)

# %%
# reshape the dataset
month_year_cols = [col for col in df_original_reshaped.columns if '-' in col] 

df_original_reshaped = df_original_reshaped.melt(id_vars=['Dealer_Code', 'Total_Active_Months', 'dealer_district', 
                             'dealer_taluka', 'population', 'taluka_population'], 
                    value_vars=month_year_cols, var_name='Month-Year', value_name='Value')

df_original_reshaped['Date'] = pd.to_datetime(df_original_reshaped['Month-Year'], format='%b-%y') + pd.offsets.MonthBegin(0)

df_original_reshaped.set_index('Date', inplace=True)

# For deseasonalization
# # reshape the dataset
# month_year_cols = [col for col in df_des.columns if '-' in col] 

# df_melted = df_des.melt(id_vars=['Dealer_Code', 'Total_Active_Months', 'dealer_district', 
#                              'dealer_taluka', 'population', 'taluka_population'], 
#                     value_vars=month_year_cols, var_name='Month-Year', value_name='Value')

# df_melted['Date'] = pd.to_datetime(df_melted['Month-Year'], format='%b-%y') + pd.offsets.MonthBegin(0)

# df_melted.set_index('Date', inplace=True)

# %%
df_original_reshaped.head()

# %%
# Function to detect outliers using IQR and replace with rolling 6-month average at the row level
def detect_outliers_replace_with_avg(df, columns, window=6):
    for index, row in df.iterrows():
        row_values = row[columns]
        Q1 = row_values.quantile(0.25)
        Q3 = row_values.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 2 * IQR
        upper_bound = Q3 + 2 * IQR
        
        # Identify outliers
        outliers = (row_values < lower_bound) | (row_values > upper_bound)
        
        # Compute rolling 6-month average for the row
        rolling_avg = row_values.rolling(window=min(window, len(row_values)), min_periods =1).mean()
        
        # Replace outliers with rolling 6-month average
        row_values[outliers] = rolling_avg[outliers]
        df.loc[index, columns] = row_values
    return df

# %%
sales_columns_2223 = [col for col in df_retail_sales.columns if "sales" in col and '2223' in col]
sales_columns_2324 = [col for col in df_retail_sales.columns if "sales" in col and '2324' in col]
sales_columns_2425 = [col for col in df_retail_sales.columns if "sales" in col and '2425' in col]
print(sales_columns_2425)

# %%
df_merged_1 = detect_outliers_replace_with_avg(df_merged, sales_columns_2223)
df_merged_1 = detect_outliers_replace_with_avg(df_merged_1, sales_columns_2324)
df_merged_1 = detect_outliers_replace_with_avg(df_merged_1, sales_columns_2425)
#df_merged_1 = df_merged_1.replace(0, 1)
df_merged_1.head()

# %%
#df_merged_1.head()
#df_merged_1[df_merged_1['Dealer_Code'] == 'SIPA086']

# %%
# def calculate_district_seasonality(district_df, model_type='additive'):
#     """Calculate monthly seasonal indices for a district"""
    
   
#     # Perform decomposition
#     decomposition = seasonal_decompose(
#         district_df['Value'], 
#         model=model_type, 
#         period=12
#     )
    
#     # Extract seasonal component (first 12 months)
#     seasonal_component = decomposition.seasonal[:12]
    
#     # Convert to dictionary {month: index}
#     return {month: seasonal_component.iloc[i] 
#             for i, month in enumerate(range(1,13))}

# df_melted['Value'] = df_melted['Value'].replace(0, 0.01)
# district_seasonality = {}
# df_district_groupby = df_melted.groupby(['dealer_district','Date'], as_index=False)['Value'].sum()
# for district in df_district_groupby['dealer_district'].unique():
#     district_data = df_district_groupby[df_district_groupby['dealer_district'] == district]
#     district_seasonality[district] = calculate_district_seasonality(
#         district_data, 
#         model_type='multiplicative'  # Choose based on your data
#     )

# dealer_seasonality = {}
# df_dealer_groupby = df_melted.groupby(['Dealer_Code','Date'], as_index=False)['Value'].sum()

# # for dealer in df_dealer_groupby['Dealer_Code'].unique():
# #     dealer_data = df_dealer_groupby[df_dealer_groupby['Dealer_Code'] == dealer]
# #     dealer_seasonality[dealer] = calculate_district_seasonality(
# #         dealer_data, 
# #         model_type='multiplicative'  # Choose based on your data
# #     )
    

# %%
# def deseasonalize(row):
#     """Apply district-level seasonal adjustment to dealer data"""
#     district = row['dealer_district']
#     dealer = row['Dealer_Code']
    
#     month = row.name.month  # Assuming datetime index
#     if row['Dealer_Code'] in dealer_seasonality.keys():
#         seasonal_index = dealer_seasonality[dealer][month]
#     elif row['dealer_district'] in district_seasonality.keys():
#         seasonal_index = district_seasonality[district][month]
#     else:
#         seasonal_index = 1
    
#     # Choose additive or multiplicative adjustment
#     #return row['Value'] - seasonal_index  # Additive model
#     return row['Value'] / seasonal_index  # Multiplicative model

# # Apply to all dealer data
# df_original_reshaped['deseasonalized_sales'] = df_original_reshaped.apply(deseasonalize, axis=1)

# %%
#calculate CMGR

df_fy = df_original_reshaped[(df_original_reshaped.index >= '2023-04-01') & (df_original_reshaped.index <= '2025-01-31')]

def calculate_cmgr(start_value, end_value, months):
    if pd.isna(start_value) or pd.isna(end_value) or start_value == 0:
        return np.nan  # Handle zero or missing starting values safely
    return ((end_value / start_value) ** (1 / months)) - 1


# Create a new DataFrame containing only 'Dealer_Code'
df_cmgr = df_fy[['Dealer_Code']].drop_duplicates().reset_index(drop=True)


# # comment Calculate CMGR for 3-month periods
# cmgr_last_3m_1_des = df_fy.groupby('Dealer_Code')['deseasonalized_sales'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-06-01'], x.loc['2024-09-01'], 3)
# )

# cmgr_last_3m_2_des = df_fy.groupby('Dealer_Code')['deseasonalized_sales'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-03-01'], x.loc['2024-06-01'], 3)
# )

# # Calculate CMGR for 6-month periods
# cmgr_last_6m_1_des = df_fy.groupby('Dealer_Code')['deseasonalized_sales'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-03-01'], x.loc['2024-09-01'], 6)
# )

# cmgr_last_6m_2_des = df_fy.groupby('Dealer_Code')['deseasonalized_sales'].apply(
#     lambda x: calculate_cmgr(x.loc['2023-10-01'], x.loc['2024-03-01'], 6)
# )

# # Actual Values 

# # Calculate CMGR for 3-month periods
# cmgr_last_3m_1 = df_fy.groupby('Dealer_Code')['Value'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-06-01'], x.loc['2024-09-01'], 3)
# )

# cmgr_last_3m_2 = df_fy.groupby('Dealer_Code')['Value'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-03-01'], x.loc['2024-06-01'], 3)
# )

# # Calculate CMGR for 6-month periods
# cmgr_last_6m_1 = df_fy.groupby('Dealer_Code')['Value'].apply(
#     lambda x: calculate_cmgr(x.loc['2024-03-01'], x.loc['2024-09-01'], 6)
# )

# cmgr_last_6m_2 = df_fy.groupby('Dealer_Code')['Value'].apply(
#     lambda x: calculate_cmgr(x.loc['2023-10-01'], x.loc['2024-03-01'], 6)
# )



# # %%
# df_3m_1_des = pd.DataFrame({'Dealer_Code': cmgr_last_3m_1_des.index, 'CMGR_3m_1_des': cmgr_last_3m_1_des.values})
# df_3m_2_des = pd.DataFrame({'Dealer_Code': cmgr_last_3m_2_des.index, 'CMGR_3m_2_des': cmgr_last_3m_2_des.values})
# df_6m_1_des = pd.DataFrame({'Dealer_Code': cmgr_last_6m_1_des.index, 'CMGR_6m_1_des': cmgr_last_6m_1_des.values})
# df_6m_2_des = pd.DataFrame({'Dealer_Code': cmgr_last_6m_2_des.index, 'CMGR_6m_2_des': cmgr_last_6m_2_des.values})

# df_3m_1 = pd.DataFrame({'Dealer_Code': cmgr_last_3m_1.index, 'CMGR_3m_1': cmgr_last_3m_1.values})
# df_3m_2 = pd.DataFrame({'Dealer_Code': cmgr_last_3m_2.index, 'CMGR_3m_2': cmgr_last_3m_2.values})
# df_6m_1 = pd.DataFrame({'Dealer_Code': cmgr_last_6m_1.index, 'CMGR_6m_1': cmgr_last_6m_1.values})
# df_6m_2 = pd.DataFrame({'Dealer_Code': cmgr_last_6m_2.index, 'CMGR_6m_2': cmgr_last_6m_2.values})

# # %%
# df_cmgr = df_cmgr.merge(df_3m_1_des,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_3m_2_des,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_6m_1_des,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_6m_2_des,on = 'Dealer_Code', how = 'left')

# df_cmgr = df_cmgr.merge(df_3m_1,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_3m_2,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_6m_1,on = 'Dealer_Code', how = 'left')
# df_cmgr = df_cmgr.merge(df_6m_2,on = 'Dealer_Code', how = 'left')

df_cmgr = df_cmgr.merge(df_merged_1, on = 'Dealer_Code', how = 'left')

# # %%
df_cmgr = df_cmgr.merge(df_target,on='Dealer_Code',how = 'left')

#df_cmgr.head()

# %%
df_cmgr = df_cmgr[['Dealer_Code',
                    # 'CMGR_3m_1_des','CMGR_3m_2_des','CMGR_6m_1_des','CMGR_6m_2_des',
                    # 'CMGR_3m_1','CMGR_3m_2',
                    
                   # 'Jan_2324_sales',
                   'Feb_2324_sales', 'Mar_2324_sales',
                    'Apr_2425_sales','May_2425_sales','Jun_2425_sales', 
                    'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
                   'Oct_2425_sales', 'Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales',
                   

                     
                   # 'Jan_2324_Target',
                   'Feb_2324_Target', 'Mar_2324_Target',
                    'Apr_2425_Target','May_2425_Target','Jun_2425_Target', 
                    'Jul_2425_Target', 'Aug_2425_Target','Sep_2425_Target',
                  'Oct_2425_Target', 'Nov_2425_Target', 'Dec_2425_Target','Jan_2425_Target']]
#
#  %%
# venkate added for target month count 01:10 AM

sales_cols = ['Aug_2425_sales','Sep_2425_sales', 'Oct_2425_sales', 'Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']
target_cols = [col.replace('sales', 'Target') for col in sales_cols]

sales_cols_1y = ['Feb_2324_sales', 'Mar_2324_sales',
                    'Apr_2425_sales','May_2425_sales','Jun_2425_sales', 
                    'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
                   'Oct_2425_sales', 'Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']

target_cols_1y = [col.replace('sales', 'Target') for col in sales_cols_1y]

#One year sales and targets for display
df_display_sales_targets = df_display[oth_display + sales_cols_1y + target_cols_1y]
# Convert sales and target columns to nearest integer
df_display_sales_targets[sales_cols_1y + target_cols_1y] = df_display_sales_targets[sales_cols_1y + target_cols_1y].round().astype('Int64')



# Compare saless with targets
achievement = (df_cmgr[sales_cols].values >= df_cmgr[target_cols].values).astype(int)

# Count the months where target was achieved
df_cmgr['Achieved_Months_2425'] = achievement.sum(axis=1)

# Display result
print(df_cmgr[['Dealer_Code', 'Achieved_Months_2425']])


# %%
#df_cmgr.head()

# %%
# venkate added for target month count 01:23 AM
conditions = [
    (df_cmgr['Achieved_Months_2425'] == 0),
    (df_cmgr['Achieved_Months_2425'].between(1, 2)),
    (df_cmgr['Achieved_Months_2425'].between(3, 4)),
    (df_cmgr['Achieved_Months_2425'].between(5, 6))
]

labels = ['0', '1_2', '3_4', '5_6']

# Assign the output column based on conditions
df_cmgr['Achieved_Category'] = pd.cut(df_cmgr['Achieved_Months_2425'], 
                                 bins=[-1, 0, 2, 4, 6], 
                                 labels=labels, 
                                 right=True)

df_cmgr.head()


# %%
sales_cols = [col for col in df_cmgr.columns if 'sales' in col]

# Compute rolling average (6-months) for each dealer across months
rolling_avg_df = df_cmgr[sales_cols].rolling(window=6, axis=1).mean()

# Add the last available rolling average as a new column
df_cmgr['Rolling_Avg_6M'] = rolling_avg_df.iloc[:, -1]  # Last available value for each dealer

# Display Result
print(df_cmgr[['Dealer_Code', 'Rolling_Avg_6M']])

df_pattern = df_cmgr


# %%
df_pattern.head()

# %%
# Set Current Month Target using the correct column
df_cmgr['Current_Month_Target'] = df_cmgr['Jan_2425_Target']

# %%
# Identify last 3 months for averaging
last_6_months = ['Aug_2425_sales', 'Sep_2425_sales', 'Oct_2425_sales', 'Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']

# %%
# Compute Last 3-Month Average
df_cmgr['Last_3_Month_Avg'] = df_cmgr[last_6_months].apply(lambda x: x[x >= 10].tail(3).mean(), axis=1)

# %%
# df_cmgr[df_cmgr['Dealer_Code'] == 'SIPT299']

# %%
#df_cmgr[['Jul_2425_sales', 'May_2425_sales', 'Jun_2425_sales','Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales', 'Last_3_Month_Avg']].to_csv('Data/test_1903.csv')

# %%
#df_cmgr[['Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales', 'Last_3_Month_Avg']]


# %%
# Define percentage increase based on flag and value ranges
def apply_percentage_increase(current_target, avg, flag):
    if flag == '5_6':
        if avg < 20:
            return avg * 1.3  # 30% increase
        elif 20 <= avg <= 30:
            return avg * 1.3  # 30% increase
        elif 30 < avg <= 50:
            return avg * 1.2  # 20% increase
        elif 50 < avg <= 100:
            return avg * 1.15  # 15% increase
        elif 100 < avg <= 200:
            return avg * 1.10  # 10% increase
        elif 200 < avg <= 400:
            return avg * 1.05  # 5% increase
        elif avg > 400:
            return avg * 1.05  # 5% increase
    elif flag == '3_4':
        if 0 <= avg <= 30:
            return avg * 1.2  # 20% increase
        elif 30 < avg <= 50:
            return avg * 1.15  # 15% increase
        elif 50 < avg <= 100:
            return avg * 1.10  # 10% increase
        elif 100 < avg <= 200:
            return avg * 1.05  # 5% increase
        elif avg > 200:
            return avg * 1.03  # 3% increase
    elif flag == '1_2':
        if avg < 20:
            return avg * 1.2  # 20% increase
        elif 20 <= avg <= 30:
            return avg * 1.15  # 15% increase
        elif 30 < avg <= 50:
            return avg * 1.10  # 10% increase
        elif 50 < avg <= 100:
            return avg * 1.05  # 5% increase
        elif 100 < avg <= 200:
            return avg * 1.03  # 3% increase
        elif avg > 200:
            return avg * 1.03  # 3% increase
    elif flag == '0':
        return avg * 1.0  # No change for flag 0
    return avg

 # Apply predicted target logic
df_cmgr['Predicted_Target'] = df_cmgr.apply(lambda row:
    apply_percentage_increase(row['Jan_2425_Target'], row['Last_3_Month_Avg'], row['Achieved_Category']), axis=1).fillna(0).astype(int) 

df_cmgr['Predicted_Target_R'] = (df_cmgr['Predicted_Target'] / 5).apply(np.ceil).fillna(0).astype(int) * 5

# Calculate the total of the predicted target rounded values
total_predicted_target = df_cmgr['Predicted_Target_R'].sum()

# Calculate percentage distribution of the predicted target
df_cmgr['Percentage_PT_Dist'] = df_cmgr['Predicted_Target_R'] / total_predicted_target


last_6_months = ['Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']
df_cmgr['Last_3_Month_Sal'] = df_cmgr[last_6_months].sum(axis=1)


mapping = {
    "5_6": "High Achievement",
    "1_2": "Low Achievement",
    "3_4": "Moderate Achievement",
    "0": "No Achievement"
}

df_cmgr["Achieved_Type"] = np.where(
    df_cmgr["Last_3_Month_Sal"] == 0, 
    "Target Not Set",  # If Last_3_Month_Sal is 0
    df_cmgr["Achieved_Category"].map(mapping)  # Otherwise, use mapping
)


df_cmgr["Predicted_Target_R"] = np.where(
    df_cmgr["Achieved_Type"] == "Target Not Set", 
    0, 
   df_cmgr["Predicted_Target_R"]
)



# # Define percentage increase based on flag and value ranges
# def apply_percentage_increase(current_target, avg, flag):
#     if flag == '5_6':
#         if avg < 20:
#             return avg * 1.3  # 30% increase
#         elif 20 <= avg <= 30:
#             return avg * 1.3  # 30% increase
#         elif 30 < avg <= 50:
#             return avg * 1.2  # 20% increase
#         elif 50 < avg <= 100:
#             return avg * 1.15  # 15% increase
#         elif 100 < avg <= 200:
#             return avg * 1.10  # 10% increase
#         elif 200 < avg <= 400:
#             return avg * 1.05  # 5% increase
#         elif avg > 400:
#             return avg * 1.05  # 5% increase
#     elif flag == '3_4':
#         if 0 <= avg <= 30:
#             return avg * 1.2  # 20% increase
#         elif 30 < avg <= 50:
#             return avg * 1.15  # 15% increase
#         elif 50 < avg <= 100:
#             return avg * 1.10  # 10% increase
#         elif 100 < avg <= 200:
#             return avg * 1.05  # 5% increase
#         elif avg > 200:
#             return avg * 1.03  # 3% increase
#     elif flag == '1_2':
#         if avg < 20:
#             return avg * 1.2  # 20% increase
#         elif 20 <= avg <= 30:
#             return avg * 1.15  # 15% increase
#         elif 30 < avg <= 50:
#             return avg * 1.10  # 10% increase
#         elif 50 < avg <= 100:
#             return avg * 1.05  # 5% increase
#         elif 100 < avg <= 200:
#             return avg * 1.03  # 3% increase
#         elif avg > 200:
#             return avg * 1.03  # 3% increase
#     elif flag == '0':
#         return avg * 1.0  # No change for flag 0
#     return avg

#  # Apply predicted target logic
# df_cmgr['Predicted_Target'] = df_cmgr.apply(lambda row:
#     apply_percentage_increase(row['Jan_2425_Target'], row['Last_3_Month_Avg'], row['Achieved_Category']), axis=1).fillna(0).astype(int) 

# df_cmgr['Predicted_Target_R'] = (df_cmgr['Predicted_Target'] / 5).apply(np.ceil).fillna(0).astype(int) * 5

# # Calculate the total of the predicted target rounded values
# total_predicted_target = df_cmgr['Predicted_Target_R'].sum()

# # Calculate percentage distribution of the predicted target
# df_cmgr['Percentage_PT_Dist'] = df_cmgr['Predicted_Target_R'] / total_predicted_target


# last_6_months = ['Nov_2425_sales', 'Dec_2425_sales', 'Jan_2425_sales']
# df_cmgr['Last_3_Month_Sal'] = df_cmgr[last_6_months].sum(axis=1)


# mapping = {
#     "5_6": "High Achievement",
#     "1_2": "Low Achievement",
#     "3_4": "Moderate Achievement",
#     "0": "No Achievement"
# }

# df_cmgr["Achieved_Type"] = np.where(
#     df_cmgr["Last_3_Month_Sal"] == 0, 
#     "Target Not Set",  # If Last_3_Month_Sal is 0
#     df_cmgr["Achieved_Category"].map(mapping)  # Otherwise, use mapping
# )


# df_cmgr["Predicted_Target_R"] = np.where(
#     df_cmgr["Achieved_Type"] == "Target Not Set", 
#     0, 
#    df_cmgr["Predicted_Target_R"]
# )




# def calculate_predicted_target(row):
#     # If all last 6 months sales are 0, set Predicted_Target to 0 and Achieved_Category to 'N/A'
#     if all(row[col] == 0 for col in last_6_months):
#         row['Predicted_Target'] = 0
#         row['Achieved_Category'] = 'N/A'
#     else:
#         row['Predicted_Target_v2'] = max(
#             apply_percentage_increase(row['Sep_2425_Target'], row['Last_3_Month_Avg'], row['Achieved_Category']), 
#             row['Sep_2425_Target']
#         )
#     return row


# df_cmgr = df_cmgr.apply(calculate_predicted_target, axis=1).fillna(0)

# %%



# %% [markdown]
# 

# %%

# df_cmgr[['Dealer_Code',
#          'Oct_2324_sales','Nov_2324_sales','Dec_2324_sales',	
#          'Jan_2324_sales','Feb_2324_sales','Mar_2324_sales',         
#          'Apr_2425_sales','May_2425_sales','Jun_2425_sales', 
#          'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
#          'Apr_2425_Target','May_2425_Target','Jun_2425_Target', 
#          'Jul_2425_Target', 'Aug_2425_Target','Sep_2425_Target',
#          'Achieved_Type','Predicted_Target',]].to_csv('Data/test_0104_2.csv')



# %%
# # Set Current Month Target using the correct column
# df_cmgr['Current_Month_Target'] = df_cmgr['Sep_2425_sales']

# # Identify last 3 months for averaging
# last_3_months = ['Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales']

# # Compute Last 3-Month Average
# df_cmgr['Last_3_Month_Avg'] = df_cmgr[last_3_months].mean(axis=1)

# def calculate_predictive_target(row):
#     # Extract relevant sales values
#     sales_values = [row[col] for col in sales_cols if row[col] > 10 and row[col] > 0]  # Only consider values >10

#     if row['Achieved_Category'] == '5_6':
#         target = np.sum(sales_values[:3])/3 * 1.05 if sales_values else row['Current_Month_Target']

#     elif row['Achieved_Category'] == '3_4':
#         target = np.sum(sales_values[:3])/3 * 1.03 if sales_values else row['Current_Month_Target']

#     elif row['Achieved_Category'] == '1_2':
#         # Ensure at least 3 non-zero double-digit values, extend up to 6 months if needed
#         if len(sales_values) < 3:
#             target = np.sum(sales_values[:3])/3 if sales_values else row['Current_Month_Target']
#         else:
#             target = np.sum(sales_values[:3])/3

#     else:  # Achieved_Category == '0'
#         sales_values = [row[col] for col in sales_cols if row[col] >= 0]
#         target = np.sum(sales_values[:3])/len(sales_values) if sales_values else row['Current_Month_Target']

#     # Ensure target is at least `Current_Month_Target`
#     target = max(target, row['Current_Month_Target'])

#     return round(target, 0)  # Round to nearest whole number

# df_cmgr['Predictive_Target'] = df_cmgr.apply(calculate_predictive_target, axis=1)

# # Display Result
# df_cmgr = df_cmgr[['Dealer_Code',
#          'Oct_2324_sales','Nov_2324_sales','Dec_2324_sales',	
#          'Jan_2324_sales','Feb_2324_sales','Mar_2324_sales',         
#          'Apr_2425_sales','May_2425_sales','Jun_2425_sales', 
#          'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
#          'Apr_2425_Target','May_2425_Target','Jun_2425_Target', 
#          'Jul_2425_Target', 'Aug_2425_Target','Sep_2425_Target',
#          'Achieved_Category','Predictive_Target']]
# df_cmgr.head(500)


# %%


# df_pattern = df_cmgr

# Define new 6-month columns from Aug_2425 to Jan_2425
calc_cols = ["Aug_2425_sales", "Sep_2425_sales", "Oct_2425_sales",
             "Nov_2425_sales", "Dec_2425_sales", "Jan_2425_sales"]

target_cols = ["Aug_2425_Target", "Sep_2425_Target", "Oct_2425_Target",
               "Nov_2425_Target", "Dec_2425_Target", "Jan_2425_Target"]

# Mapping each sales month to the corresponding past 6 months
past_6m_mapping = {
    "Aug_2425_sales": ["Feb_2324_sales", "Mar_2324_sales", "Apr_2425_sales",
                       "May_2425_sales", "Jun_2425_sales", "Jul_2425_sales"],
    "Sep_2425_sales": ["Mar_2324_sales", "Apr_2425_sales", "May_2425_sales",
                       "Jun_2425_sales", "Jul_2425_sales", "Aug_2425_sales"],
    "Oct_2425_sales": ["Apr_2425_sales", "May_2425_sales", "Jun_2425_sales",
                       "Jul_2425_sales", "Aug_2425_sales", "Sep_2425_sales"],
    "Nov_2425_sales": ["May_2425_sales", "Jun_2425_sales", "Jul_2425_sales",
                       "Aug_2425_sales", "Sep_2425_sales", "Oct_2425_sales"],
    "Dec_2425_sales": ["Jun_2425_sales", "Jul_2425_sales", "Aug_2425_sales",
                       "Sep_2425_sales", "Oct_2425_sales", "Nov_2425_sales"],
    "Jan_2425_sales": ["Jul_2425_sales", "Aug_2425_sales", "Sep_2425_sales",
                       "Oct_2425_sales", "Nov_2425_sales", "Dec_2425_sales"]
}

#Compute rolling average for past 6 months
for target_col, past_cols in past_6m_mapping.items():
    avg_col_name = f"Avg_sales_{target_col}"
    df_pattern[avg_col_name] = df_pattern[past_cols].mean(axis=1).round(1)

#Categorization Function (Only for Last 6 Months)
def categorize_patterns(row, period_cols):
    sales_pattern, target_pattern = "", ""
    
    for p_col in period_cols:
        t_col = p_col.replace("sales", "Target")
        avg_col = f"Avg_sales_{p_col}"
        
        #Ensure rolling avg column exists before comparison
        if avg_col in row.index:
            sales_pattern += "H" if row[p_col] >= row[avg_col] else "L"
        else:
            sales_pattern += "L"  # Default to Low if no avg value
        
        #Target Pattern (A/N)
        if t_col in row.index and row[p_col] >= row[t_col]:  
            target_pattern += "A"  # Achieved
        else:
            target_pattern += "N"  # Not Achieved
            
    return sales_pattern, target_pattern

#Compute Overall Sales & Target Patterns for last 6 months only
df_pattern[["Sales_Pattern_Overall", "Target_Pattern_Overall"]] = df_pattern.apply(
    lambda row: pd.Series(categorize_patterns(row, calc_cols)), axis=1
)

# Dealer Classification Function (Overall Only for Last 6 Months)
def classify_dealer(sales_pattern, target_pattern):
    h_count, l_count = sales_pattern.count("H"), sales_pattern.count("L")
    a_count, n_count = target_pattern.count("A"), target_pattern.count("N")

    if h_count >= 4 and a_count >= 4:
        return "Consistently Strong Performer"
    elif l_count >= 4 and n_count >= 4:
        return "Consistently Weak Performer"
    elif h_count >= 4 and a_count < 4:
        return "Emerging Performer"
    elif a_count >= 4 and h_count < 4:
        return "Target-Oriented Performer"     
    elif "HHH" in sales_pattern and "AAA" in target_pattern:
        return "Momentum Gainer"
    elif "LLL" in sales_pattern and "NNN" in target_pattern:
        return "Declining Performer"
    else:
        return "Fluctuating Performer"

# Apply Dealer Classification for Overall Category (Last 6 Months Only)
df_pattern["Category_Overall"] = df_pattern.apply(
    lambda row: classify_dealer(row["Sales_Pattern_Overall"], row["Target_Pattern_Overall"]), axis=1
)

final_columns = ["Dealer_Code"] + sales_cols + target_cols + \
    ["Sales_Pattern_Overall", "Target_Pattern_Overall", "Category_Overall"]

# df_output = df_pattern[final_columns]
# df_output.head()

#--------######## venkatesh added 02-24-2025 ----------##########

print('verification df_oth  :',df_oth.columns)
df_cmgr = df_cmgr[['Dealer_Code',
         'Feb_2324_sales','Mar_2324_sales', 'Apr_2425_sales','May_2425_sales',
         'Jun_2425_sales', 'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
         'Oct_2425_sales','Nov_2425_sales','Dec_2425_sales','Jan_2425_sales',
         'Feb_2324_Target','Mar_2324_Target','Apr_2425_Target','May_2425_Target',
         'Jun_2425_Target','Jul_2425_Target', 'Aug_2425_Target','Sep_2425_Target',
         'Oct_2425_Target','Nov_2425_Target','Dec_2425_Target','Jan_2425_Target',
         'Sales_Pattern_Overall', 'Target_Pattern_Overall',
         'Achieved_Type','Predicted_Target','Predicted_Target_R', 'Percentage_PT_Dist', 'Category_Overall']]
    #.to_csv('output/predicted_target_0204_0.csv')

# Merge metrics from df_cmgr into df_display_sales_targets
df_display_final = df_display_sales_targets.merge(
    df_cmgr[['Dealer_Code', 'Sales_Pattern_Overall', 'Target_Pattern_Overall',
             'Achieved_Type', 'Predicted_Target_R', 'Percentage_PT_Dist', 'Category_Overall']],
    on='Dealer_Code',
    how='left'
)

# Make sure the output folder exists
os.makedirs("output", exist_ok=True)

# Create a timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output/predicted_target_{timestamp}.csv"

# Export the final dataframe to a CSV
# df_display_final.to_csv(filename, index=False)

print(f"File saved successfully")

print('verification df_cmgr  :',df_cmgr.columns)

# Merge df_cmgr and df_oth
df_display_final = pd.merge(df_display_final, df_oth, on = "Dealer_Code", how = 'left')
df_final = pd.merge(df_cmgr, df_oth, on='Dealer_Code', how='left')
print('verification df_final:', df_final.columns)

# Calculate MarketSizePer1000
df_final['MarketSizePer1000'] = (df_final['new_market_potential'] / df_final['population']) * 1000
df_display_final['MarketSizePer1000'] = df_final['MarketSizePer1000']
# Identify sales columns dynamically from df_final (not df)
sales_columns = [col for col in df_final.columns if '_sales' in col]

# Sort them in chronological order
#sales_columns.sort()  # Ensures correct order (Oct_2324, Nov_2324, ...)

# Select last 6 months dynamically
last_6_months = sales_columns[-6:]  # Picks the last 6 sales columns

# Calculate the average sales for the last 6 months
df_final['AVG_SALES'] = df_final[last_6_months].mean(axis=1)
df_display_final['AVG_SALES'] = df_final['AVG_SALES']

# Select last 12 months dynamically
last_12_months = sales_columns[-12:]  # Picks the last 6 sales columns

# Calculate the average sales for the last 12 months
df_final['AP_12'] = df_final[last_12_months].mean(axis=1)
df_display_final['AP_12'] = df_final['AP_12']

last_month_sales = sales_columns[-1:] 
df['Last_month_sales'] = df[last_month_sales]
df['Last_month_sales'] = df[last_month_sales]
#Identify counter columns dynamically
counter_columns = [col for col in df.columns if '_counter' in col]

# Sort them in chronological order
#counter_columns.sort()

#Select last 3 months dynamically
last_3_counter = counter_columns[-3:]  # Picks the last 3 counter columns
df['counter_sum'] = df[last_3_counter].sum(axis=1)


last_month_counter = counter_columns[-1:] 
df['last_month_counter'] = df[last_month_counter]

df = df.fillna(0)
df = df.replace(0,1)

# Check last 3 counter columns
print('Counter Columns:', counter_columns)
print('Last 3 Counter Columns:', last_3_counter)
df_final['sales_by_counter_3M'] = (df['Last_month_sales'] / df['counter_sum'])
df_final['counter_market_ratio'] = (df['last_month_counter'] / df['new_market_potential'])
df_display_final['sales_by_counter_3M'] = df_final['sales_by_counter_3M']
df_display_final['counter_market_ratio'] = df_final['counter_market_ratio']

scaler = MinMaxScaler()
df_final['NORM_counter_market_ratio'] = scaler.fit_transform(df_final[['counter_market_ratio']])
df_final['NORM_sales_by_counter_3M'] = scaler.fit_transform(df_final[['sales_by_counter_3M']])
df_final['AVG_SALES-N'] = scaler.fit_transform(df_final[['AVG_SALES']])
df_final['MarketSizePer1000_N'] = scaler.fit_transform(df_final[['MarketSizePer1000']])

#for display
df_display_final['NORM_counter_market_ratio'] = df_final['NORM_counter_market_ratio']
df_display_final['NORM_sales_by_counter_3M'] = df_final['NORM_sales_by_counter_3M']
df_display_final['AVG_SALES-N'] = df_final['AVG_SALES-N']
df_display_final['MarketSizePer1000_N'] = df_final['MarketSizePer1000_N']


df_final = df_final[['Dealer_Code','Dealer_Name','dealer_district','dealer_type', 'dealer_taluka',
         'Feb_2324_sales','Mar_2324_sales', 'Apr_2425_sales','May_2425_sales',
         'Jun_2425_sales', 'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
         'Oct_2425_sales','Nov_2425_sales','Dec_2425_sales','Jan_2425_sales',
         'Feb_2324_Target','Mar_2324_Target','Apr_2425_Target','May_2425_Target',
         'Jun_2425_Target','Jul_2425_Target','Aug_2425_Target','Sep_2425_Target',
         'Oct_2425_Target','Nov_2425_Target','Dec_2425_Target','Jan_2425_Target',
         'Sales_Pattern_Overall', 'Target_Pattern_Overall',
         'Achieved_Type', 'Predicted_Target_R', 'Percentage_PT_Dist', 'Category_Overall',
         'new_market_potential', 'AP_12',
         'NORM_counter_market_ratio','NORM_sales_by_counter_3M',
         'AVG_SALES-N','MarketSizePer1000_N']]

df_display_final = df_display_final[['Dealer_Code','Dealer_Name','dealer_district','dealer_type', 'dealer_taluka',
         'Feb_2324_sales','Mar_2324_sales', 'Apr_2425_sales','May_2425_sales',
         'Jun_2425_sales', 'Jul_2425_sales', 'Aug_2425_sales','Sep_2425_sales',
         'Oct_2425_sales','Nov_2425_sales','Dec_2425_sales','Jan_2425_sales',
         'Feb_2324_Target','Mar_2324_Target','Apr_2425_Target','May_2425_Target',
         'Jun_2425_Target','Jul_2425_Target','Aug_2425_Target','Sep_2425_Target',
         'Oct_2425_Target','Nov_2425_Target','Dec_2425_Target','Jan_2425_Target',
         'Sales_Pattern_Overall', 'Target_Pattern_Overall',
         'Achieved_Type', 'Predicted_Target_R', 'Percentage_PT_Dist', 'Category_Overall',
         'new_market_potential', 'AP_12',
         'NORM_counter_market_ratio','NORM_sales_by_counter_3M',
         'AVG_SALES-N','MarketSizePer1000_N']]

print('*********************target file loaded******************************')

# %%
