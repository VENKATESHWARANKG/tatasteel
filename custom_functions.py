#Importing Liraries
import numpy as np
import pandas as pd
from statsmodels.tsa.seasonal import seasonal_decompose
import streamlit as st
from datetime import datetime

def calculate_active_months(df):

    """
    Calculates dealer activity based on monthly sales.

    For each dealer, it finds:
    - The first and last month with non-zero sales
    - The total number of active months (inclusive)

    Returns a summary DataFrame with these metrics per dealer.
    """

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

#---------------------------------------------------------------------


def convert_fy_to_price(col_name):

    """
    Converts column names from fiscal year format (e.g., "Aug_22_23") to "Month-YY" format (e.g., "Aug-22").

    - If the column is "Dealer_Code", it is returned unchanged.
    - Assumes fiscal years start in April:
        - Months from Apr to Dec are assigned to the first fiscal year.
        - Months from Jan to Mar are assigned to the second fiscal year.
    - If parsing fails, the original column name is returned.
    """

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
    
#-------------------------------------------------------------------

import pandas as pd

def get_latest_complete_window(df, date_col='Date', min_months=24):
    """
    Filters the DataFrame to the most recent complete N-month window ending in a December,
    where N is the largest multiple of 12 (≥ min_months) that fits within the data.

    Parameters:
    - df: Input DataFrame with a date column
    - date_col: Name of the date column (default 'Date')
    - min_months: Minimum number of months required (must be a multiple of 12)

    Returns:
    - Tuple: (filtered_df, expected_dates_range, actual_months_used)
    """
    df = df.copy()
    df[date_col] = pd.to_datetime(df[date_col])

    latest_date = df[date_col].max()

    # Snap to most recent December
    if latest_date.month == 12:
        end_date = pd.Timestamp(latest_date.year, 12, 1)
    else:
        end_date = pd.Timestamp(latest_date.year - 1, 12, 1)

    # Calculate available months till the earliest date
    total_months = ((end_date.year - df[date_col].min().year) * 12 +
                    (end_date.month - df[date_col].min().month) + 1)

    # Find largest multiple of 12 ≥ min_months that fits
    window_months = (total_months // 12) * 12
    if window_months < min_months:
        raise ValueError(f"Not enough data to extract at least {min_months} months.")

    start_date = end_date - pd.DateOffset(months=window_months - 1)
    expected_dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    df_filtered = df[df[date_col].between(start_date, end_date)]

    return df_filtered, expected_dates, window_months

#------------------------------------------------------------
def calculate_district_seasonality(district_df, model_type='additive'):
    """Calculate monthly seasonal indices for a district"""

    decomposition = seasonal_decompose(
        district_df['Value'], 
        model=model_type, 
        period=12
    )

    seasonal_component = decomposition.seasonal[:12]

    # Determine the start month from the first date
    start_month = district_df['Date'].min().month  # e.g., 2 for Feb

    # Create correct mapping from month number to seasonal index
    month_map = {}
    for i, value in enumerate(seasonal_component):
        month_number = ((start_month - 1 + i) % 12) + 1  # Ensure it wraps around after December
        month_map[month_number] = value

    return month_map


def deseasonalize(row, district_seasonality):
    """Apply district-level seasonal adjustment to dealer data"""

    district = row['dealer_district']
    #dealer = row['Dealer_Code']
    
    month = row.name.month  # Assuming datetime index
    # if row['Dealer_Code'] in dealer_seasonality.keys():
    #     seasonal_index = dealer_seasonality[dealer][month]
    if row['dealer_district'] in district_seasonality.keys():
        seasonal_index = district_seasonality[district][month]
    else:
        seasonal_index = 1
    
    #Choose additive or multiplicative adjustment
    #return row['Value'] - seasonal_index  # Additive model
    return row['Value'] / seasonal_index  # Multiplicative model

#--------------------------------------------------------

# Function to detect outliers using IQR and replace with rolling 6-month average at the row level
def detect_outliers_replace_with_avg(df, columns, window=6):
    """
    Detects and replaces outliers in each row using the IQR method and a rolling 6-month average.
    Outliers are defined as values outside [Q1 - 2*IQR, Q3 + 2*IQR] for that row.
    These outliers are replaced with the row’s rolling average (window=6 or less).
    
    Parameters:
        df (DataFrame): Input DataFrame.
        columns (list): List of column names with time-series data.
        window (int): Rolling window size (default is 6).

    Returns:
        DataFrame with outliers replaced.
    """

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

#CMGR
def calculate_cmgr(start_value, end_value, months):
    if pd.isna(start_value) or pd.isna(end_value) or start_value == 0:
        return np.nan  # Handle zero or missing starting values safely
    return ((end_value / start_value) ** (1 / months)) - 1


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


def has_streak_after(pattern, before_char, streak_char, streak_len=3):
    """
    Returns True if there's a `before_char` that comes before a `streak_char * streak_len`
    and the pattern ends with the `streak_char`
    """
    try:
        before_index = pattern.index(before_char)
    except ValueError:
        return False

    streak = streak_char * streak_len
    streak_index = pattern.find(streak)

    return streak_index > before_index and pattern.endswith(streak_char)

def classify_dealer(sales_pattern, target_pattern):
    sales_pattern = sales_pattern.upper()
    target_pattern = target_pattern.upper()

    # Special case: Inactive Dealer
    if sales_pattern == "HHHHHH" and target_pattern == "NNNNNN":
        return "Inactive Dealer"

    h_count = sales_pattern.count('H')
    l_count = sales_pattern.count('L')
    a_count = target_pattern.count('A')
    n_count = target_pattern.count('N')

    # 1. Strong performer
    if h_count >= 4 and a_count >= 4:
        return "Consistently Strong Performer"

    # 2. Weak performer
    elif l_count >= 4 and n_count >= 4:
        return "Consistently Weak Performer"

    # 3. Emerging performer
    elif h_count >= 4 and a_count < 4:
        return "Emerging Performer"

    # 4. Target-Oriented performer
    elif a_count >= 4 and h_count < 4:
        return "Target-Oriented Performer"

    # 5. Momentum Gainer
    elif has_streak_after(sales_pattern, 'L', 'H') and has_streak_after(target_pattern, 'N', 'A'):
        return "Momentum Gainer"

    # 6. Declining Performer
    elif has_streak_after(sales_pattern, 'H', 'L') and has_streak_after(target_pattern, 'A', 'N'):
        return "Declining Performer"

    # 7. Fluctuating
    else:
        return "Fluctuating Performer"
    
#Stream lit app functions --------------------------------------

# Function to calculate composite score
def calculate_score(row, weights):
    return (
        row['MPA'] * (weights['mpa']/100) +
        row['SOB'] * (weights['sob']/100) +
        row['AP_normalized'] * (weights['asp']/100)
    )


def get_tier_incentives(method, min_inc_per_ton, max_inc_per_ton):
    tiers = [f'Tier {i}' for i in range(1, 7)]
    
    if method == "exponential":
        return {
            tier: round(min_inc_per_ton + (max_inc_per_ton - min_inc_per_ton) * np.exp(-0.3*(i-1)))
            for i, tier in enumerate(tiers, 1)
        }
    
    elif method == "steps":
        steps = [3000, 2500, 2200, 1800, 1500, 1200, 900, 700, 600, 500]
        return {tier: round(steps[i]) for i, tier in enumerate(tiers)}
    
    else:  # linear
        return {
            tier: round(min_inc_per_ton + (max_inc_per_ton - min_inc_per_ton) * (10 - i)/9)
            for i, tier in enumerate(tiers, 1)
        }
    

# ---- Function to Display Logo at the Top Right ----
def display_logo(base64_string):
    logo_html = f"""
    <div>
        <img src="data:image/png;base64,{base64_string}" class="top-right-image">
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

# --------- Supporting functions

# Function to calculate composite score
def calculate_score(row, weights):
    return (
        row['MPA'] * (weights['mpa']/100) +
        row['SOB'] * (weights['sob']/100) +
        row['AP_normalized'] * (weights['asp']/100)
    )

def get_tier_incentives(method, min_inc_per_ton, max_inc_per_ton):
    tiers = [f'Tier {i}' for i in range(1, 7)]
    
    if method == "exponential":
        return {
            tier: round(min_inc_per_ton + (max_inc_per_ton - min_inc_per_ton) * np.exp(-0.3*(i-1)))
            for i, tier in enumerate(tiers, 1)
        }
    
    elif method == "steps":
        steps = [3000, 2500, 2200, 1800, 1500, 1200, 900, 700, 600, 500]
        return {tier: round(steps[i]) for i, tier in enumerate(tiers)}
    
    else:  # linear
        return {
            tier: round(min_inc_per_ton + (max_inc_per_ton - min_inc_per_ton) * (10 - i)/9)
            for i, tier in enumerate(tiers, 1)
        }

 
def round_nearest(series, base=5):
    return base * (series / base).round()
    

def convert_column_for_display(col_name):
    """
    Converts column names like 'Jan_2425_sales' or 'Jan_2425_Target'
    into 'January 2025 Sales' or 'January 2025 Target' for display.

    Returns the original name if it doesn't match the expected pattern.
    """
    try:
        if "_sales" in col_name:
            base = col_name.replace("_sales", "")
            suffix = "Sales"
        elif "_Target" in col_name:
            base = col_name.replace("_Target", "")
            suffix = "Target"
        else:
            return col_name  # Leave untouched if not a sales/target column

        month_abbr, fy_code = base.split("_")
        fy_start = int("20" + fy_code[:2])
        year = fy_start if month_abbr in ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"] else fy_start + 1

        dt = datetime.strptime(f"{month_abbr} {year}", "%b %Y")
        return f"{dt.strftime('%B %Y')} {suffix}"
    except:
        return col_name  # Fail-safe: return original if pattern fails
