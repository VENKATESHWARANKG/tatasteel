import streamlit as st
import pandas as pd
import numpy as np
import base64
import target_pre 
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from datetime import datetime
import altair as alt


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


#Page configuration

st.set_page_config(
    page_title="Dealer Incentive Dashboard",
    page_icon="📊tata steel",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)


# ---- Custom CSS for Full-Screen Mode & Image Positioning ----
st.markdown(
    """
    <style>
        .main .block-container {
            padding: 10px;
            margin: 10px ;
            max-width: 90% ;
            width: 90vw ;
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

kpi_style = """
<style>
.kpi-card {
    background-color: #e0f7fa;  /* Light soft blue/white background */
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    font-family: 'Segoe UI', sans-serif;
    color: #2a2a2a;
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    margin-bottom: 15px;
}

.kpi-card p {
    font-size: 1.5rem;  /* Value size */
    font-weight: bold;
    color: #1f4e79;  /* Strong blue for the numbers */
    margin: 0;
}

.kpi-card h4 {
    font-size: 0.85rem; /* Label size */
    font-weight: 500;
    color: #6c757d;  /* Soft grey for label */
    margin: 5px 0 0;
}
</style>
"""

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
display_logo(logo_base64)

# ---- App Title ----
st.title("Dealer Incentive Allocation")

# ---- Load CSV File ----
# load input file for incentive calculation
input_data = pd.read_csv('Data/dealer_incentive_model_v2.csv')
prev_data = pd.read_csv('Data/prev_oct_predicted_target.csv')


try:
    df_tar = target_pre.df_final
    print('***********target file read fully**********')
    print('sample',df_tar)

    df_dis = target_pre.df_display_final

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

with st.expander("🔍 Tab Descriptions & Purpose"):
    st.markdown("""
    <div style="font-size: 12px;">
        • <strong>Master View</strong>: Review the complete dataset and final predicted incentive outputs per dealer.  
        • <strong>Dealer Performance Analysis</strong>: Filter dealers by performance and target achievement, with a view of their sales/target growth over recent quarters.  
        • <strong>Target Distribution</strong>: Analyze how predicted targets and actuals are distributed across achievement categories, with a summary table.
    </div>
    """, unsafe_allow_html=True)

#tabs
tab1, tab3, tab2= st.tabs(["Master View", "Target Distribution", "Dealer Performance Analysis"])

# ---- Display Data Table ----
with tab1:

    col_sidebar, col_kpi_table = st.columns([0.8, 3.2])

    with col_sidebar:
        # ---- Incentive Configuration ----
        st.markdown("#### **Incentive Configuration**")

        st.markdown("**Target Type**")

        target_type = st.radio("Select Target Type:", options=["Fixed", "Not Fixed"], index=1, horizontal=True)

        # Apply predicted target logic only if Not Fixed
        if target_type == "Fixed":
        # Ask user to input a fixed total target value (default = 12,000)
            fixed_total_target = st.number_input("Enter Total Fixed Target (MT)", min_value=1000, max_value=100000, value=12000, step=100)

            # Calculate fixed targets using the entered total and round to nearest 5
            input_data['Predicted_Target_Fixed'] = input_data['Percentage_PT_Dist'] * fixed_total_target
            input_data['Predicted_Target_Fixed_R'] = (input_data['Predicted_Target_Fixed'] / 5).apply(np.ceil).astype(int) * 5

            input_data['Predicted_Target'] = input_data['Predicted_Target_Fixed_R']
        
        else:
            input_data['Predicted_Target'] = input_data['Predicted_Target_R']


        # ---- Input Fields for Incentive Range ----
        st.markdown("**Set Incentive Range**")
        min_incentive = st.number_input("Minimum Incentive", min_value=100, max_value=5000, value=500, step=100)
        max_incentive = st.number_input("Maximum Incentive", min_value=100, max_value=10000, value=2000, step=100)
        
        # if min_incentive > max_incentive:
        #     st.warning("⚠️ Please make sure your minimum incentive value is greater than your maximum incentive value.")
        #     st.stop()

        # ---- Weightage Inputs ----
        weights = {}
        st.markdown("**Set Weightages**")

        st.markdown(
            """
            <div style='font-size: 12px; font-color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px;  margin-bottom: 10px;'>
                <strong><span style='color: #1f4e79;'>Sum of weigths should be 100%</span></strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        weights['mpa'] = st.number_input("Market potential Achieved", min_value=0, max_value=100, value=20)
        weights['sob'] = st.number_input("Share of Business", min_value=0, max_value=100, value=20)
        weights['asp'] = st.number_input("Average Sales", min_value=0, max_value=100, value=60)

        # ---- Validate Weightage Sum ----
        total_weight = weights['mpa'] + weights['sob'] + weights['asp']

        # if total_weight != 100:
        #     st.warning("⚠️ Please adjust the inputs so that the total weightage is exactly 100%.")
        #     st.stop()

        # ---- Performance Weightages ----
        st.markdown("**Performance Weightages**")
        Consistently_Strong_Performer = st.number_input("Consistently Strong Performer", min_value=0, max_value=100, value=0)
        Emerging_Performer = st.number_input("Emerging Performer", min_value=0, max_value=100, value=0)
        Target_oriented_performer = st.number_input("Target-Oriented Performer", min_value=0, max_value=100, value=0)
        Momentum_gainer = st.number_input("Momentum Gainer", min_value=0, max_value=100, value=0)
        Consistently_Weak_Performer = st.number_input("Consistently Weak Performer", min_value=0, max_value=100, value=0)
        Fluctuating_Performer = st.number_input("Fluctuating Performer", min_value=0, max_value=100, value=0)
        Declining_Performer = st.number_input("Declining Performer", min_value=0, max_value=100, value=0)

        # ---- Calculate Metrics --------
        input_data['MPA'] = (input_data['CS'].astype(float) / input_data['new_market_potential'].astype(float)) * 100
        input_data['SOB'] = (input_data['AP_12'].astype(float) / input_data['CS'].astype(float)) * 100
        input_data['MPA'] = input_data['MPA'].clip(upper=100)
        input_data['SOB'] = input_data['SOB'].clip(upper=100)
        input_data['AP_normalized'] = (input_data['AP_12'] - input_data['AP_12'].min()) / (input_data['AP_12'].max() - input_data['AP_12'].min())
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

        # Define additional percentage based on Category_Overall
        category_bonus = {
            "Consistently Strong Performer": Consistently_Strong_Performer / 100,  # 10%
            "Emerging Performer": Emerging_Performer / 100,  # 3%
            "Target-Oriented Performer": Target_oriented_performer / 100,  # 3%
            "Momentum Gainer": Momentum_gainer / 100,
            "Consistently Weak Performer": Consistently_Weak_Performer / 100,
            "Fluctuating Performer": Fluctuating_Performer / 100,
            "Declining Performer": Declining_Performer / 100
        }

        # Apply additional incentive based on category
        input_data["Final_Incentive"] = round(input_data["Incentive_per_Ton_exponential"] * (1 + input_data["Category_Overall"].map(category_bonus).fillna(0)))
        input_data["Perfomance_Bonus"] =  input_data["Final_Incentive"] - input_data["Incentive_per_Ton_exponential"] 
        input_data["Predicted_Incentive"] = (input_data["Final_Incentive"] * input_data["Predicted_Target_R"]).round(-1)
        #input_data["dealer_type"] =  input_data["dealer_type"].fillna("Non-Exclusive")
        #input_data["AVG_SALES-N"] = input_data["AVG_SALES-N"].round(0)
        df = input_data

        # Get the columns in `input_data` that are not in `display_data`
        missing_columns = [col for col in input_data.columns if col not in df_dis.columns]

        # Step 2: Merge only the missing columns from `input_data` into `display_data`
        # We merge on 'Dealer_Code', assuming it exists in both dataframes
        display_data = pd.merge(
            df_dis,
            input_data[['Dealer_Code'] + missing_columns],  # Include 'Dealer_Code' + the missing columns
            on='Dealer_Code',
            how='left'  # Use left join to keep all rows in display_data intact
        )


        display_data.to_csv('Data/output.csv')

        column_labels = {
            "Dealer_Code": "Dealer Code",
            "Dealer_Name": "Dealer Name",
            "dealer_district": "District",
            "dealer_taluka" : "Taluka",
            "dealer_type": "Dealer Type",
            "Achieved_Type":"Target Achievement",
            "Category_Overall" : "Sales Performance",
            "Jan_2425_Target" : "Previous Month's Target",
            "Tier": "Incentive Tier",
            "Incentive_per_Ton_exponential": "Base Incentive",
            "Perfomance_Bonus": "Perfomance Bonus",
            "Final_Incentive" : "Final Incentive",
            "Predicted_Target_R" : "Predicted Target",
            "Predicted_Incentive": "Predicted Incentive"
        }

        # ---- Default (core) columns using internal names ----
        default_columns = [
            "Dealer_Code",
            "Dealer_Name",
            "dealer_district",
            "dealer_taluka",
            "dealer_type",
            "Achieved_Type",
            "Category_Overall",
            "Tier",
            "Jan_2425_Target",
            "Predicted_Target_R",
            "Incentive_per_Ton_exponential",
            "Perfomance_Bonus",
            "Final_Incentive",
            "Predicted_Incentive",
            
        ]

        incentive_columns = [
            "Dealer_Code",
            "Dealer_Name",
            # "dealer_district",
            # "dealer_taluka",
            # "dealer_type",
            # "Achieved_Type",
            # "Category_Overall",
            "Tier",
            # "Jan_2425_Target",
            # "Predicted_Target_R",
            "Incentive_per_Ton_exponential",
            "Perfomance_Bonus",
            "Final_Incentive",
            "Predicted_Incentive",
            
        ]

        # ---- Identify additional columns ----
        all_columns = df.columns.tolist()
        extra_columns = list(set(all_columns) - set(default_columns))

        

        # ---- Final display columns ----
        display_columns = default_columns
        #+ selected_extra_columns
        df_to_display = df[display_columns].rename(columns=column_labels)
        df_incentive = df[incentive_columns].rename(columns=column_labels)


    with col_kpi_table:

        if min_incentive > max_incentive:
            st.warning("⚠️ Please make sure your minimum incentive value is greater than your maximum incentive value.")
            st.stop()

        if total_weight != 100:
            st.warning("⚠️ Please adjust the inputs so that the total weightage is exactly 100%.")
            st.stop()

        # Inject the style into Streamlit
        st.markdown(kpi_style, unsafe_allow_html=True)

        # KPI display columns
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class='kpi-card'>
                <p>{df_to_display['Dealer Name'].nunique()}</p>
                <h4>Number of Dealers</h4>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class='kpi-card'>
                <p>₹{df_to_display['Predicted Incentive'].sum()/10000000:,.2f} Cr</p>
                <h4>Total Predicted Incentive</h4>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class='kpi-card'>            
                <p>{df_to_display['Predicted Target'].sum():,}</p>
                <h4>Total Predicted Target (MT)</h4>
            </div>
            """, unsafe_allow_html=True)

 
        st.data_editor(df_to_display, key="dealer_table", height=1200)

# Target Distribution Analysis
summary_table = (
    input_data
    .groupby("Achieved_Type")[["Jan_2425_sales", "Jan_2425_Target", "Predicted_Target_R"]]
    .sum()
    .rename(columns={
        "Jan_2425_sales": "January 2025 Sales",
        "Jan_2425_Target": "January 2025 Target",
        "Predicted_Target_R": "Predicted Target"
    })
    .reset_index()
)

# Convert amounts to integers (whole numbers)
summary_table["January 2025 Sales"] = summary_table["January 2025 Sales"].astype(int)
summary_table["January 2025 Target"] = summary_table["January 2025 Target"].astype(int)
summary_table["Predicted Target"] = summary_table["Predicted Target"].astype(int)

# Rename 'Achieved_Type' to 'Target Achievement'
summary_table = summary_table.rename(columns={"Achieved_Type": "Target Achievement"})

achievement_order = [
    "High Achievement",
    "Moderate Achievement",   # double check spelling here — should it be 'Achievement'?
    "Low Achievement",
    "No Achievement",
    "Target Not Set"
]

# Set the order using Categorical
summary_table["Target Achievement"] = pd.Categorical(
    summary_table["Target Achievement"],
    categories=achievement_order,
    ordered=True
)

# Sort by that order
summary_table = summary_table.sort_values("Target Achievement")

# Append a Grand Total row
grand_total = pd.DataFrame({
    "Target Achievement": ["Grand Total"],
    "January 2025 Sales": [summary_table["January 2025 Sales"].sum()],
    "January 2025 Target": [summary_table["January 2025 Target"].sum()],
    "Predicted Target": [summary_table["Predicted Target"].sum()]
})

# Final table
summary_table = pd.concat([summary_table, grand_total], ignore_index=True)

# Optional: highlight Grand Total row
def highlight_total_row(row):
    if row["Target Achievement"] == "Grand Total":
        return ['background-color: #e0f7fa; color: #1f4e79; font-weight: bold;' for _ in row]
    return ['' for _ in row]




#Growth Indicator

# # Define recent and previous month groups
#6 months
# recent_months_sales = ["Aug_2425_sales", "Sep_2425_sales", "Oct_2425_sales", "Nov_2425_sales", "Dec_2425_sales", "Jan_2425_sales"]
# previous_months_sales = ["Feb_2324_sales", "Mar_2324_sales", "Apr_2425_sales", "May_2425_sales", "Jun_2425_sales", "Jul_2425_sales"]

#3 months
recent_months_sales = ["Nov_2425_sales", "Dec_2425_sales", "Jan_2425_sales"]
previous_months_sales = ["Aug_2425_sales", "Sep_2425_sales", "Oct_2425_sales"]

#6
# recent_months_target = ["Aug_2425_Target", "Sep_2425_Target", "Oct_2425_Target", "Nov_2425_Target", "Dec_2425_Target", "Jan_2425_Target"]
# previous_months_target = ["Feb_2324_Target", "Mar_2324_Target", "Apr_2425_Target", "May_2425_Target", "Jun_2425_Target", "Jul_2425_Target"]
#3
recent_months_target = ["Nov_2425_Target", "Dec_2425_Target", "Jan_2425_Target"]
previous_months_target = ["Aug_2425_Target", "Sep_2425_Target", "Oct_2425_Target"]

# Calculate totals
input_data["Recent_Sales"] = input_data[recent_months_sales].sum(axis=1)
input_data["Previous_Sales"] = input_data[previous_months_sales].sum(axis=1)

input_data["Recent_Target"] = input_data[recent_months_target].sum(axis=1)
input_data["Previous_Target"] = input_data[previous_months_target].sum(axis=1)

# Calculate Growth %
input_data["Sales_Growth_%"] = ((input_data["Recent_Sales"] - input_data["Previous_Sales"]) / input_data["Previous_Sales"].replace(0, np.nan)) * 100
input_data["Target_Growth_%"] = ((input_data["Recent_Target"] - input_data["Previous_Target"]) / input_data["Previous_Target"].replace(0, np.nan)) * 100

# Calculate Achievement in both periods
input_data["Recent_Achievement_%"] = (input_data["Recent_Sales"] / input_data["Recent_Target"].replace(0, np.nan)) * 100
input_data["Previous_Achievement_%"] = (input_data["Previous_Sales"] / input_data["Previous_Target"].replace(0, np.nan)) * 100

# Round results
input_data["Sales_Growth_%"] = input_data["Sales_Growth_%"].round(2).fillna(0)
input_data["Target_Growth_%"] = input_data["Target_Growth_%"].round(2).fillna(0)
input_data["Recent_Achievement_%"] = input_data["Recent_Achievement_%"].round(2).fillna(0)
input_data["Previous_Achievement_%"] = input_data["Previous_Achievement_%"].round(2).fillna(0)


# Final table for review
growth_df = input_data[[
    "Dealer_Code", "Dealer_Name", 
    "Previous_Sales", "Recent_Sales", "Sales_Growth_%",
    "Previous_Target", "Recent_Target", "Target_Growth_%",
    "Previous_Achievement_%", "Recent_Achievement_%",
    "Category_Overall", "Achieved_Type"
]]


# Achievements Tab
ordered_achievements = ["High Achievement", "Moderate Achievement", "Low Achievement", "No Achievement"]
target_sales_cross = pd.crosstab(growth_df["Category_Overall"], growth_df["Achieved_Type"])
target_sales_cross = target_sales_cross.reindex(columns=ordered_achievements, fill_value=0)

target_sales_cross.index.name = None




with tab3:

    # st.data_editor(target_sales_cross,key="cross_table")
    st.subheader("January 2025 Summary by Achievement Type")
    st.dataframe(summary_table.style.apply(highlight_total_row, axis=1), use_container_width=True)


with tab2:


    st.subheader("Dealer Count by Performance, Achievement & Growth")

    st.markdown("##### Achievement and Performance Cross-tab")

    # --- Display cross-tab summary
    st.dataframe(target_sales_cross, use_container_width=True)

    # --- Interactive Filters
    st.markdown("##### Filter Dealers by Selection")

    col1, col2 = st.columns(2)

    with col1:
        selected_perf = st.multiselect(
            "Select Sales Performance Category",
            options=growth_df["Category_Overall"].unique().tolist(),
            default="Consistently Strong Performer"
        )

    with col2:
        selected_achv = st.multiselect(
            "Select Target Achievement",
            options=ordered_achievements,
            default="High Achievement"
        )

    # --- Filter the growth-enhanced data
    filtered_dealers = growth_df[
        growth_df["Category_Overall"].isin(selected_perf) &
        growth_df["Achieved_Type"].isin(selected_achv)
    ]

    # --- Select and rename columns for display
    display_cols = {
        "Dealer_Code": "Dealer Code",
        "Dealer_Name": "Dealer Name",
        "Category_Overall": "Sales Performance",
        "Achieved_Type": "Target Achievement",
        "Previous_Sales": "Previous Quarter Sales",
        "Recent_Sales": "Recent Quarter Sales",
        "Sales_Growth_%": "Sales Growth (%)",
        "Previous_Target": "Previous Quarter Target",
        "Recent_Target": "Recent Quarter Target",
        "Target_Growth_%": "Target Growth (%)",
        "Previous_Achievement_%": "Previous Achievement (%)",
        "Recent_Achievement_%": "Recent Achievement (%)",
    }
            # "Growth_Indicator": "Growth Indicator"
# 

    display_df = filtered_dealers[list(display_cols.keys())].rename(columns=display_cols)

    # --- Round numeric values to nearest integer
    for col in display_df.columns:
        if display_df[col].dtype in ['float64', 'int64']:
            display_df[col] = display_df[col].round(0).astype('Int64')  # Keeps empty cells clean (no .0)

    # --- Show the clean table
    st.markdown(f"##### {len(display_df)} Dealers Matching Selection")

    st.markdown("""
        <style>
        .stAlert > div {
            font-size: 0.85rem;
            
        }
        </style>
    """, unsafe_allow_html=True)

    st.dataframe(display_df, use_container_width=True)

    st.markdown(
    """
    <div style='font-size: 12px; font-color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px;  margin-bottom: 10px;'>
        <strong><span style='color: #1f4e79;'>Note:</span></strong><br>
        <prev><span style='color: #1f4e79;'>    Quarter-on-quarter growth is calculated as the comparison between:</span></prev><br>
        <prev> <span style='color: #1f4e79;'>   - <b>Recent Quarter:</b> November, December, January</span></prev><br>
        <prev> <span style='color: #1f4e79;'>   - <b>Previous Quarter:</b> August, September, October</span></prev>
    </div>
    """,
    unsafe_allow_html=True
    )

