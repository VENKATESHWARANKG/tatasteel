import streamlit as st
import pandas as pd
import numpy as np
import base64
import target_pre




# --------- Supporting functions

# Function to calculate composite score
def calculate_score(row, weights):
    return (
        row['MPA'] * (weights['mpa']/100) +
        row['SOB'] * (weights['sob']/100) +
        row['AP_normalized'] * (weights['asp']/100)
    )



def get_tier_incentives(method, min_inc_per_ton, max_inc_per_ton):
    tiers = [f'Tier {i}' for i in range(1, 6)]
    
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



# ---- Custom CSS for Full-Screen Mode & Image Positioning ----
st.markdown(
    """
    <style>
        .main .block-container {
            padding: 0 !important;
            margin: 0 !important;
            max-width: 100% !important;
            width: 100vw !important;
        }
        .top-right-image {
            position: absolute;
            top: 0.2px;
            right: 1px;
            max-width: 10px;
            height: auto;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---- Function to Display Logo at the Top Right ----
def display_logo(base64_string):
    logo_html = f"""
    <div>
        <img src="data:image/png;base64,{base64_string}" class="top-right-image">
    </div>
    """
    st.markdown(logo_html, unsafe_allow_html=True)

# ---- Base64 Encoded Logo (Replace with actual base64 string) ----
logo_base64  = "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"

# ---- Display the Logo ----
#display_logo(logo_base64)

# ---- App Title ----
st.markdown(
    """
    <style>
    .center-title {
        text-align: center;
        font-size: 30px;
        margin-top: 50px;  /* Adjust this value to move the title further down */
    }
    </style>
    <div class="center-title">
        Dealer Incentive Allocation
    </div>
    """, 
    unsafe_allow_html=True
)

# ---- Load CSV File ----
# load input file for incentive calculation
input_data = pd.read_csv('tata/dealer_incentive_model_v2.csv')

try:
    df_tar = target_pre.df_final
    print('***********target file read fully**********')
    print('sample',df_tar)

except FileNotFoundError:
    st.error(f"File not found. Please ensure it exists in the specified location.")
    st.stop()

# merge data

input_data = pd.merge(
        df_tar,
        input_data,
        left_on='Dealer_Code',
        right_on='Code',
        how='inner'  # or 'left' depending on your needs
    )




# ---- Sidebar Inputs ----
st.sidebar.header("Incentive Configuration")

# ---- Input Fields for Incentive Range ----
st.sidebar.markdown("**Set Incentive Range**")
min_incentive = st.sidebar.number_input("Minimum Incentive", min_value=100, max_value=5000, value=500, step=100)
max_incentive = st.sidebar.number_input("Maximum Incentive", min_value=100, max_value=10000, value=2000, step=100)

# ---- Weightage Inputs ----
weights = {}
st.sidebar.markdown("**Set Weightages (Sum should be 100%)**")
#MarketSizePer1000_N_weightage = st.sidebar.number_input("Market size per 1000", min_value=0, max_value=100, value=0)
weights['mpa'] = st.sidebar.number_input("Market potential Acheived", min_value=0, max_value=100, value=20)
weights['sob'] = st.sidebar.number_input("Share of Business", min_value=0, max_value=100, value=20)
weights['asp'] = st.sidebar.number_input("Average sales", min_value=0, max_value=100, value=60)




# ---- Validate Weightage Sum ----
total_weight = (
weights['mpa'] + 
weights['sob'] +
weights['asp']
)


if total_weight != 100:
    st.warning("⚠️ Please adjust the inputs so that the total weightage is exactly 100%.")
    st.stop()

st.sidebar.write(f"**Total Weightage: {total_weight}% (Must be 100%)**")

st.sidebar.markdown("**Performance Weightages**")
Consistently_Strong_Performer = st.sidebar.number_input("Consistently strong performer", min_value=0, max_value=100, value=0)
Emerging_Performer = st.sidebar.number_input("Emerging performer", min_value=0, max_value=100, value=0)
Target_oriented_performer = st.sidebar.number_input("Target oriented performer", min_value=0, max_value=100, value=0)
Momentum_gainer = st.sidebar.number_input("Momentum gainer", min_value=0, max_value=100, value=0)
Consistently_Weak_Performer = st.sidebar.number_input("Consistently Weak Performer", min_value=0, max_value=100, value=0)
Fluctuating_Performer = st.sidebar.number_input("Fluctuating Performer", min_value=0, max_value=100, value=0)
Declining_Performer = st.sidebar.number_input("Declining Performer", min_value=0, max_value=100, value=0)


# ---- Calculate Metrics --------

input_data['MPA'] = (input_data['CS'].astype(float)/input_data['MP'].astype(float)) * 100
input_data['SOB'] = (input_data['AP'].astype(float)/input_data['CS'].astype(float)) * 100
input_data['MPA'] = input_data['MPA'].clip(upper=100)
input_data['SOB'] = input_data['SOB'].clip(upper=100)
input_data['AP_normalized'] =  (input_data['AP'] - input_data['AP'].min()) / (input_data['AP'].max() - input_data['AP'].min())
input_data['AP_normalized'] = input_data['AP_normalized'] * 100

# ------- Calculate dealer score ----------

input_data['Score'] = input_data.apply(lambda row: calculate_score(row, weights), axis=1)

# Calculate tier

input_data['Tier'] = pd.qcut(
    input_data['Score'],
    q=6,
    labels=[f'Tier {i}' for i in range(6, 0, -1)]  # ['Tier 6', ..., 'Tier 1']
)

# Calculate incentive tier - linear
tier_incentives = get_tier_incentives('linear', min_incentive, max_incentive)
input_data['Incentive_per_Ton_linear'] = input_data['Tier'].map(tier_incentives)

# Calculate incentive tier - exponential
tier_incentives = get_tier_incentives('exponential', min_incentive, max_incentive)
input_data['Incentive_per_Ton_exponential'] = input_data['Tier'].map(tier_incentives)

input_data.to_csv("tata/output.csv")

# -------- 

# ---- Normalize Weightages (Convert to 0-1 scale) ----
#MarketSizePer1000_N_weightage /= 100
#NORM_sales_by_counter_3M_weightage /= 100
#NORM_counter_market_ratio_weightage /= 100
#AVG_SALES_N_weightage /= 100

# ---- Calculate Dealer Score ----
#df_tar["Dealer_score"] = (
 #   (MarketSizePer1000_N_weightage * np.exp(np.log(df_tar["MarketSizePer1000_N"]))).fillna(0.5) +
  #  (NORM_sales_by_counter_3M_weightage * np.exp(np.log(df_tar["NORM_sales_by_counter_3M"]))) +
   # (NORM_counter_market_ratio_weightage * np.exp(np.log(df_tar["NORM_counter_market_ratio"]))) +
   # (AVG_SALES_N_weightage * np.exp(np.log(df_tar["AVG_SALES-N"])))
#)




# Define additional percentage based on Category_Overall
category_bonus = {
    "Consistently Strong Performer": Consistently_Strong_Performer/100 ,  # 10%
    "Emerging Performer": Emerging_Performer/100,  # 3%
    "Target-Oriented Performer": Target_oriented_performer/100,  # 3%
    "Momentum Gainer": Momentum_gainer/100,
    "Consistently Weak Performer": Consistently_Weak_Performer/100,
    "Fluctuating Performer": Fluctuating_Performer/100,
    "Declining_Performer" : Declining_Performer/100
}

# Apply additional incentive based on category
input_data["Final_Incentive"] = round(input_data["Incentive_per_Ton_exponential"] * (1 + input_data["Category_Overall"].map(category_bonus).fillna(0)))
input_data["Perfomance_Bonus"] =  input_data["Final_Incentive"] - input_data["Incentive_per_Ton_exponential"] 
input_data["Predicted_Incentive"] = (input_data["Final_Incentive"] * input_data["Predicted_Target"]).round(-1)
#input_data["dealer_type"] =  input_data["dealer_type"].fillna("Non-Exclusive")
#input_data["AVG_SALES-N"] = input_data["AVG_SALES-N"].round(0)
df = input_data
df.to_csv('tata/output.csv')

column_labels = {
    "Dealer_Code": "Dealer Code",
    "Dealer_Name": "Dealer Name",
    "dealer_district": "District",
    "dealer_taluka" : "Dealer",
    "dealer_type": "Dealer Type",
    "Sep_2425_Target" : "Previous Month's Target",
     "Achieved_Type":"Target Acheivement",
     "Predicted_Target" : "Predicted Target",
    "Category_Overall" : "Sales Performance",
    "Tier": "Incentive Tier",
    "Incentive_per_Ton_exponential": "Base Incentive",
    "Perfomance_Bonus": "Perfomance Bonus",
    "Predicted_Incentive": "Predicted Incentive",
    "Final_Incentive" : "Final Incentive"
}

# ---- Default (core) columns using internal names ----
default_columns = [
    "Dealer_Code",
    "Dealer_Name",
    "dealer_district",
    "dealer_taluka",
    "dealer_type",
    "Sep_2425_Target",
    "Achieved_Type",
    "Predicted_Target",
    "Category_Overall",
    "Incentive_per_Ton_exponential",
    "Tier",
    "Perfomance_Bonus",
    "Predicted_Incentive",
    "Final_Incentive"
]
# ---- Identify additional columns ----
all_columns = df.columns.tolist()
extra_columns = list(set(all_columns) - set(default_columns))

# ---- User selects additional columns ----
#with st.expander("➕ Select Additional Columns"):
 #   selected_extra_columns = st.multiselect(
  #      "Choose additional columns:",
   #     options=extra_columns,
    #    default=[]
  #  )

# ---- Final display columns ----
display_columns = default_columns
#+ selected_extra_columns
df_to_display = df[display_columns].rename(columns=column_labels)

# ---- Display Data Table ----
st.data_editor(df_to_display, key="dealer_table")


