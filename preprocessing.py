#%%
#Importing libraries
import pandas as pd
import numpy as np
from datetime import datetime
import os
import custom_functions
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.preprocessing import MinMaxScaler

#Loading in the data
df = pd.read_csv('Data/final_raw_data_file_febmar.csv')
df_visual = df.copy() #For sales visualizations

#Extracting columns
sales_columns = ['Dealer_Code'] + [col for col in df.columns if 'sales' in col]
targets_columns = ['Dealer_Code'] + [col for col in df.columns if 'Target' in col]
counter_columns = ['Dealer_Code'] + [col for col in df.columns if 'counter' in col]
cols = sales_columns + targets_columns + counter_columns
other_columns = ['Dealer_Code'] + [col for col in df.columns if col not in cols]

#Separating into dataframes
df_dealers =df[other_columns].copy()
df_sales = df[sales_columns].copy()
df_targets = df[targets_columns].copy()
df_counter = df[counter_columns].copy()


#Initializing a display dataframe
df_display = df_dealers.copy()
df_display = df_display.merge(df_sales, on= "Dealer_Code", how= "left") \
                       .merge(df_targets, on= 'Dealer_Code', how= 'left')

#Finding active dealers using custom function - calculate_active_months()
df_sales = df_sales.fillna(0)
df_sales_active_months = custom_functions.calculate_active_months(df_sales)

#Active dealers extraction based on recent active months (3)
df_sales_active = df_sales_active_months[df_sales_active_months['Last_Active_Month']
                                         .isin(list(df_sales.columns[-3:]))][['Dealer_Code', 'Total_Active_Months']] \
                  .merge(df_sales, on= 'Dealer_Code', how= 'right').copy()
                #   .dropna(subset= ['Total_Active_Months']) \
                  
#des goes here

#Not doing outliers-------------------
#Automatically detect all unique year suffixes like '2223', '2324', etc.
year_groups = sorted(
    set(col.split("_")[1] for col in df_sales.columns if "sales" in col)
) #change df_sales_active to df_des_sales for deasonalization sales

# Initialize your working DataFrame
df_treated_sales_active = df_sales.copy() #change df_sales to df_des_sales for deasonalization sales

#Apply outlier detection for each year group (eliminated)
#Custom fucntion: detect_outliers_replace_with_avg
for year in year_groups:
    sales_cols = [col for col in df_treated_sales_active.columns if f"{year}_sales" in col]
    df_treated_sales_active = custom_functions.detect_outliers_replace_with_avg(df_treated_sales_active, sales_cols)

#Combining target to this
#Targets of inactive dealers are also retained for target distribution analysis
df_sales_targets = df_sales.merge(df_targets, on= "Dealer_Code", how = "left")
df_sales_targets

#Other_columns
other_columns = list(df_dealers.columns)

#Now for 1year
sales_12m = [col for col in df_sales_targets.columns if "sales" in col][-12:]
targets_12m = [col.replace('sales', 'Target') for col in sales_12m]

#Retaining only 12month data
df_sales_targets_12m = df_sales_targets[['Dealer_Code'] + sales_12m + targets_12m].copy()

#For display
#One year sales and targets for display
#Only previous 12m data considered for display
df_display_sales_targets = df_display[other_columns + sales_12m + targets_12m]

# Convert sales and target columns to nearest integer
df_display_sales_targets[sales_12m + targets_12m] = df_display_sales_targets[sales_12m + targets_12m].round().astype('Int64')

#Considering last 6m sales and target columns names
sales_6m = [col for col in df_sales_targets.columns if "sales" in col][-6:]
targets_6m = [col.replace('sales', 'Target') for col in sales_6m]


# Compare saless with targets
# Get sales and target arrays
sales_array = df_sales_targets_12m[sales_6m].values
target_array = df_sales_targets_12m[targets_6m].values

# Create a mask where target > 0
valid_mask = target_array > 0

# Only count where sales >= target AND target > 0
achievement = ((sales_array >= target_array) & valid_mask).astype(int)

#Storing number of months sales exceeded set target
df_sales_targets_12m['Achieved_Months_Count'] = achievement.sum(axis=1)

#Achievement labels
conditions = [
    (df_sales_targets_12m['Achieved_Months_Count'] == 0),
    (df_sales_targets_12m['Achieved_Months_Count'].between(1, 2)),
    (df_sales_targets_12m['Achieved_Months_Count'].between(3, 4)),
    (df_sales_targets_12m['Achieved_Months_Count'].between(5, 6))
]

labels = ['0', '1_2', '3_4', '5_6']

# Assign the output column based on conditions
df_sales_targets_12m['Achieved_Category'] = pd.cut(df_sales_targets_12m['Achieved_Months_Count'], 
                                 bins=[-1, 0, 2, 4, 6], 
                                 labels=labels, 
                                 right=True)

#Rolling average
rolling_avg = df_sales_targets_12m[sales_12m].rolling(window=6, axis =1).mean()
df_sales_targets_12m['Rolling_Avg_6m'] = rolling_avg.iloc[:, -1]


# Set Current Month Target using the correct column
df_sales_targets_12m['Current_Month_Target'] = df_sales_targets_12m[targets_6m[-1]]

# Compute Last 3-Month Average
df_sales_targets_12m['Last_3_Month_Avg'] = df_sales_targets_12m[sales_6m].apply(lambda x: x[x >= 5].tail(3).mean(), axis=1)

#Using previous month, last 2month avg and achievement label to find predicted target
#Custom function: apply_percentage_increase
df_sales_targets_12m['Predicted_Target'] = df_sales_targets_12m.apply(lambda row:
    custom_functions.apply_percentage_increase(row['Current_Month_Target'], row['Last_3_Month_Avg'], row['Achieved_Category']), axis=1).fillna(0).astype(int) 

#Predicted target rounded
df_sales_targets_12m['Predicted_Target_R'] = (df_sales_targets_12m['Predicted_Target'] / 5).apply(np.ceil).fillna(0).astype(int) * 5

#Last 3 month
sales_3m = sales_6m[-3:]
df_sales_targets_12m['Last_3_Month_Sal'] = df_sales_targets_12m[sales_3m].sum(axis=1)

#Setting Achievement Type
mapping = {
    "5_6": "High Achievement",
    "1_2": "Low Achievement",
    "3_4": "Moderate Achievement",
    "0": "No Achievement"
}

#Mapping Target not set as well
df_sales_targets_12m["Achieved_Type"] = np.where(
    df_sales_targets_12m["Last_3_Month_Sal"] == 0, 
    "Target Not Set",  # If Last_3_Month_Sal is 0
    df_sales_targets_12m["Achieved_Category"].map(mapping)  # Otherwise, use mapping
)

df_sales_targets_12m["Predicted_Target_R"] = np.where(
    df_sales_targets_12m["Achieved_Type"] == "Target Not Set", 
    0, 
   df_sales_targets_12m["Predicted_Target_R"]
)

# Calculate the total of the predicted target rounded values
total_predicted_target = df_sales_targets_12m['Predicted_Target_R'].sum()

# Calculate percentage distribution of the predicted target
df_sales_targets_12m['Percentage_PT_Dist'] = df_sales_targets_12m['Predicted_Target_R'] / total_predicted_target
df_sales_targets_12m['Percentage_PT_Dist'] = df_sales_targets_12m['Percentage_PT_Dist'] / df_sales_targets_12m['Percentage_PT_Dist'].sum()


#Past 6m mapping
past_6m_mapping = {}
for col in sales_6m:
    i = df_sales_targets_12m.columns.get_loc(col)
    past_6m_mapping[col] = list(df_sales_targets_12m.columns[i-6: i])


#Compute rolling average for past 6 months
for target_col, past_cols in past_6m_mapping.items():
    avg_col_name = f"Avg_sales_{target_col}"
    df_sales_targets_12m[avg_col_name] = df_sales_targets_12m[past_cols].mean(axis=1).round(1)


#Compute Overall Sales & Target Patterns for last 6 months only
#Custom function: categorize_patterns
df_sales_targets_12m[["Sales_Pattern_Overall", "Target_Pattern_Overall"]] = df_sales_targets_12m.apply(
    lambda row: pd.Series(custom_functions.categorize_patterns(row, sales_6m)), axis=1
)

# Apply Dealer Classification for Overall Category (Last 6 Months Only)
#Custom function: classify_dealer
df_sales_targets_12m["Category_Overall"] = df_sales_targets_12m.apply(
    lambda row: custom_functions.classify_dealer(row["Sales_Pattern_Overall"], row["Target_Pattern_Overall"]), axis=1
)

#Retaining only relavant columns
final_columns = ["Dealer_Code"] + sales_12m + targets_12m + ['Achieved_Type','Predicted_Target','Predicted_Target_R', 'Percentage_PT_Dist']+ \
    ["Sales_Pattern_Overall", "Target_Pattern_Overall", "Category_Overall"]
df_sales_targets_12m = df_sales_targets_12m[final_columns]

# df_display_sales_targets
# Merge metrics from df_cmgr into df_display_sales_targets
df_display_final = df_display_sales_targets.merge(
    df_sales_targets_12m[['Dealer_Code', 'Sales_Pattern_Overall', 'Target_Pattern_Overall',
             'Achieved_Type', 'Predicted_Target_R', 'Percentage_PT_Dist', 'Category_Overall']],
    on='Dealer_Code',
    how='left'
)


# Merge df_cmgr and df_dealers
df_final = pd.merge(df_sales_targets_12m, df_dealers, on='Dealer_Code', how='left')
print('Verification df_final:', df_final.columns)

# Calculate the average sales for the last 12 months
df_final['AP_12'] = df_final[sales_12m].mean(axis=1)
df_display_final['AP_12'] = df_final['AP_12']

#To CSV
# Make sure the output folder exists
# os.makedirs("output", exist_ok=True)
# Create a timestamped filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"output/predicted_target_{timestamp}.csv"
# Export the final dataframe to a CSV
# df_final.to_csv(filename, index=False)
print(f"File saved successfully")
print('*********************target file loaded******************************')


#%%
#------------------------- previous quater analysis--------------------------------
#Creating new dfs quater wise

# Create dictionaries to store sales and target dataframes by quarter
quarterly_sales = {}
quarterly_targets = {}

# Loop through quarters
for quarter in range(1, 5):
    # Assuming each quarter has 3 months, so 3*quarter = cumulative months
    cols_to_keep = -3 * (4 - quarter)  # To keep 3, 6, 9 months progressively
    
    # Use None if we want to include all columns (i.e., cols_to_keep = 0)
    sales_cols = df_sales.columns[:cols_to_keep] if cols_to_keep != 0 else df_sales.columns
    target_cols = df_targets.columns[:cols_to_keep] if cols_to_keep != 0 else df_targets.columns

    # Store in dictionaries
    quarterly_sales[f"Q{quarter}"] = df_sales[sales_cols]
    quarterly_targets[f"Q{quarter}"] = df_targets[target_cols]

quarterly_model_metrics = {}

for i in list(quarterly_sales.keys()):

    quarter = i
    df_sales = quarterly_sales[quarter].copy()
    df_targets = quarterly_targets[quarter].copy()

    df_sales_targets = df_sales.merge(df_targets, on= "Dealer_Code", how = "left")
    df_sales_targets

    #Other_columns
    other_columns = list(df_dealers.columns)

    #Now for 1year
    sales_12m = [col for col in df_sales_targets.columns if "sales" in col][-12:]
    targets_12m = [col.replace('sales', 'Target') for col in sales_12m]

    #Retaining only 12month data
    df_sales_targets_12m = df_sales_targets[['Dealer_Code'] + sales_12m + targets_12m].copy()

    #Considering last 6m sales and target columns names
    sales_6m = [col for col in df_sales_targets.columns if "sales" in col][-6:]
    targets_6m = [col.replace('sales', 'Target') for col in sales_6m]

    # Compare saless with targets
    # Get sales and target arrays
    sales_array = df_sales_targets_12m[sales_6m].values
    target_array = df_sales_targets_12m[targets_6m].values

    # Create a mask where target > 0
    valid_mask = target_array > 0

    # Only count where sales >= target AND target > 0
    achievement = ((sales_array >= target_array) & valid_mask).astype(int)

    #Storing number of months sales exceeded set target
    df_sales_targets_12m['Achieved_Months_Count'] = achievement.sum(axis=1)

    #Achievement labels
    conditions = [
        (df_sales_targets_12m['Achieved_Months_Count'] == 0),
        (df_sales_targets_12m['Achieved_Months_Count'].between(1, 2)),
        (df_sales_targets_12m['Achieved_Months_Count'].between(3, 4)),
        (df_sales_targets_12m['Achieved_Months_Count'].between(5, 6))
    ]

    labels = ['0', '1_2', '3_4', '5_6']

    # Assign the output column based on conditions
    df_sales_targets_12m['Achieved_Category'] = pd.cut(df_sales_targets_12m['Achieved_Months_Count'], 
                                    bins=[-1, 0, 2, 4, 6], 
                                    labels=labels, 
                                    right=True)

    #Rolling average
    rolling_avg = df_sales_targets_12m[sales_12m].rolling(window=6, axis =1).mean()
    df_sales_targets_12m['Rolling_Avg_6m'] = rolling_avg.iloc[:, -1]


    # Set Current Month Target using the correct column
    df_sales_targets_12m['Current_Month_Target'] = df_sales_targets_12m[targets_6m[-1]]

    # Compute Last 3-Month Average
    df_sales_targets_12m['Last_3_Month_Avg'] = df_sales_targets_12m[sales_6m].apply(lambda x: x[x >= 5].tail(3).mean(), axis=1)

    #Using previous month, last 2month avg and achievement label to find predicted target
    #Custom function: apply_percentage_increase
    df_sales_targets_12m['Predicted_Target'] = df_sales_targets_12m.apply(lambda row:
        custom_functions.apply_percentage_increase(row['Current_Month_Target'], row['Last_3_Month_Avg'], row['Achieved_Category']), axis=1).fillna(0).astype(int) 

    #Predicted target rounded
    df_sales_targets_12m['Predicted_Target_R'] = (df_sales_targets_12m['Predicted_Target'] / 5).apply(np.ceil).fillna(0).astype(int) * 5

    #Last 3 month
    sales_3m = sales_6m[-3:]
    df_sales_targets_12m['Last_3_Month_Sal'] = df_sales_targets_12m[sales_3m].sum(axis=1)

    #Setting Achievement Type
    mapping = {
        "5_6": "High Achievement",
        "1_2": "Low Achievement",
        "3_4": "Moderate Achievement",
        "0": "No Achievement"
    }

    #Mapping Target not set as well
    df_sales_targets_12m["Achieved_Type"] = np.where(
        df_sales_targets_12m["Last_3_Month_Sal"] == 0, 
        "Target Not Set",  # If Last_3_Month_Sal is 0
        df_sales_targets_12m["Achieved_Category"].map(mapping)  # Otherwise, use mapping
    )

    df_sales_targets_12m["Predicted_Target_R"] = np.where(
        df_sales_targets_12m["Achieved_Type"] == "Target Not Set", 
        0, 
    df_sales_targets_12m["Predicted_Target_R"]
    )

    #Past 6m mapping
    past_6m_mapping = {}
    for col in sales_6m:
        i = df_sales_targets_12m.columns.get_loc(col)
        past_6m_mapping[col] = list(df_sales_targets_12m.columns[i-6: i])


    #Compute rolling average for past 6 months
    for target_col, past_cols in past_6m_mapping.items():
        avg_col_name = f"Avg_sales_{target_col}"
        df_sales_targets_12m[avg_col_name] = df_sales_targets_12m[past_cols].mean(axis=1).round(1)


    #Compute Overall Sales & Target Patterns for last 6 months only
    #Custom function: categorize_patterns
    df_sales_targets_12m[["Sales_Pattern_Overall", "Target_Pattern_Overall"]] = df_sales_targets_12m.apply(
        lambda row: pd.Series(custom_functions.categorize_patterns(row, sales_6m)), axis=1
    )

    # Apply Dealer Classification for Overall Category (Last 6 Months Only)
    #Custom function: classify_dealer
    df_sales_targets_12m["Category_Overall"] = df_sales_targets_12m.apply(
        lambda row: custom_functions.classify_dealer(row["Sales_Pattern_Overall"], row["Target_Pattern_Overall"]), axis=1
    )

    #Retaining only relavant columns
    final_quarter_columns = ['Dealer_Code', 'Achieved_Type','Predicted_Target_R', 'Category_Overall']
    
    df_sales_targets_12m = df_sales_targets_12m[final_quarter_columns]

    quarterly_model_metrics[quarter] = df_sales_targets_12m




df_q1 = quarterly_model_metrics['Q1']
df_q2 = quarterly_model_metrics['Q2']
df_q3= quarterly_model_metrics['Q3']
df_q4 = quarterly_model_metrics['Q4']

df_q1['Quarter'] = 1
df_q2['Quarter'] = 2
df_q3['Quarter'] = 3
df_q4['Quarter'] = 4

df_long = pd.concat([df_q1, df_q2, df_q3, df_q4])
inactive_dealers = df_long[(df_long['Quarter'] == 4) & 
                           (df_long['Category_Overall'] == 'Inactive Dealer')]['Dealer_Code'].to_list()
df_long = df_long[~(df_long['Dealer_Code'].isin(inactive_dealers))].sort_values(by = ['Dealer_Code', 'Quarter'])

#%%
