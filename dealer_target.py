import streamlit as st
import pandas as pd
import numpy as np
import base64
import preprocessing
import custom_functions 
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from datetime import datetime
import altair as alt
import re

#Page configuration

st.set_page_config(
    page_title="Dealer Incentive Dashboard",
    page_icon="📊tata steel",
    layout="wide",
    initial_sidebar_state="collapsed"
)

#Markdown type

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

#Defining KPI Style

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

# ---- Base64 Encoded Logo (Replace with actual base64 string) ----
logo_base64  = "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"

# ---- Display the Logo ----
custom_functions.display_logo(logo_base64)

# ---- App Title ----
st.title("Dealer Incentive Allocation")

# ---- Load CSV File ----
try:
    df_tar = preprocessing.df_final #For input and calcutations
    print('***********target file read fully**********')
    print('sample',df_tar)

    df_dis = preprocessing.df_display_final #For Display

except FileNotFoundError:
    st.error(f"File not found. Please ensure it exists in the specified location.")
    st.stop()

#Removing Inactive dealers
input_data = df_tar[df_tar['Category_Overall'] != 'Inactive Dealer'].copy()
df_dis = df_dis[df_dis['Category_Overall'] != 'Inactive Dealer'].copy()

with st.expander("🔍 Tab Descriptions & Purpose"):
    st.markdown("""
    <div style="font-size: 12px;">
        • <strong>Master View</strong>: Review the complete dataset and final predicted incentive outputs per dealer. <br>
        • <strong>Target Distribution</strong>: Analyze how predicted targets and actuals are distributed across achievement categories, with a summary table. <br>
        • <strong>Dealer Performance Analysis</strong>: Filter dealers by performance and target achievement, with a view of their sales/target growth over recent quarters. <br>
        • <strong>Dashboard</strong>: Analyze dealer sales, targets, and achievement % through interactive line, bar, and heatmap visualizations with flexible filters by region, dealer, and time.
    </div>
    """, unsafe_allow_html=True)

#Yabs
tab1, tab2, tab3, tab4= st.tabs(["Master View", "Target Distribution", "Dealer Performance Analysis", "Dashboard"])

# ---- Display Data Table ----

#Tab 1: Incentive Configuration & Display Table + KPIs
with tab1:

    col_sidebar, col_kpi_table = st.columns([0.8, 3.2])

     # ---- Incentive Configuration Sidebar----
    with col_sidebar:
        st.markdown("#### **Incentive Configuration**")

         # ---- Setting Target Type ----
        st.markdown("**Target Type**")
        target_type = st.radio("Select Target Type:", options=["Fixed", "Not Fixed"], index=1, horizontal=True)

        #  Fixed and Not Fixed target type selection
        if target_type == "Fixed": 
            #User input of targer cap
            fixed_total_target = st.number_input("Enter Total Fixed Target (MT)", min_value=1000, max_value=100000, value=11700, step=100)

            # Compute predicted targets based on percentage distribution
            input_data['Predicted_Target_Fixed'] = input_data['Percentage_PT_Dist'] * fixed_total_target
            # Round to nearest integer
            input_data['Predicted_Target_Rounded'] = input_data['Predicted_Target_Fixed'].round().astype(int)

            # Adjust rounding difference to match fixed target exactly
            diff = fixed_total_target - input_data['Predicted_Target_Rounded'].sum()
            unit = 1

            if diff != 0:
                n_adjustments = abs(diff)
                adjustment_col = input_data['Predicted_Target_Fixed'] - input_data['Predicted_Target_Rounded']
                if diff > 0:
                    top_indices = adjustment_col.nlargest(n_adjustments).index
                    input_data.loc[top_indices, 'Predicted_Target_Rounded'] += unit
                else:
                    top_indices = adjustment_col.nsmallest(n_adjustments).index
                    input_data.loc[top_indices, 'Predicted_Target_Rounded'] -= unit


            # Final assignment
            input_data['Predicted_Target'] = input_data['Predicted_Target_Rounded']

        else:
            #Non-Fixed total
            input_data['Predicted_Target'] = input_data['Predicted_Target_R']

        
        # ---- Input Fields for Incentive Range or Average----
        st.markdown("**Set Incentive Range or Average**")
        incentive_type = st.radio("Select Incentive Input Type:", options=["Average", "Range"], index=1, horizontal=True)
        
        if incentive_type == 'Range':
            min_incentive = st.number_input("Minimum Incentive", min_value=100, max_value=5000, value=500, step=100)
            max_incentive = st.number_input("Maximum Incentive", min_value=100, max_value=10000, value=2000, step=100)
        
        elif incentive_type == 'Average':
            avg_inc_pt = st.number_input("Enter Average Incentive per Ton", min_value=100, max_value=10000, value=750, step=50)
            total_incentive = avg_inc_pt * input_data['Predicted_Target'].sum()

        # ---- Weightage Inputs ----
        weights = {}
        st.markdown("**Set Weightages**")

        st.markdown(
            """
            <div style='font-size: 12px; font-color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px;  margin-bottom: 10px;'>
                <strong><span style='color: #1f4e79;'>Sum of weights should be 100%</span></strong>
            </div>
            """,
            unsafe_allow_html=True
        )

        weights['mpa'] = st.number_input("Market potential Achieved", min_value=0, max_value=100, value=0)
        weights['sob'] = st.number_input("Share of Business", min_value=0, max_value=100, value=0)
        weights['asp'] = st.number_input("Average Sales", min_value=0, max_value=100, value=100)

        # ---- Validate Weightage Sum ----
        total_weight = weights['mpa'] + weights['sob'] + weights['asp']
        # Warning display set at col_kpi_table
        
        # ---- Performance Weightages ----
        st.markdown("**Performance Weightages**")
        Consistently_Strong_Performer = st.number_input("Consistently Strong Performer", min_value=0, max_value=100, value= 20)
        Emerging_Performer = st.number_input("Emerging Performer", min_value=0, max_value=100, value= 10)
        Target_oriented_performer = st.number_input("Target-Oriented Performer", min_value=0, max_value=100, value= 5)
        Momentum_gainer = st.number_input("Momentum Gainer", min_value=0, max_value=100, value= 5)
        Consistently_Weak_Performer = st.number_input("Consistently Weak Performer", min_value=0, max_value=100, value=0)
        Fluctuating_Performer = st.number_input("Fluctuating Performer", min_value=0, max_value=100, value=0)
        Declining_Performer = st.number_input("Declining Performer", min_value=0, max_value=100, value=0)

        # ---- Performance Bonuses ----
        category_bonus = {
            "Consistently Strong Performer": Consistently_Strong_Performer / 100,
            "Emerging Performer": Emerging_Performer / 100,
            "Target-Oriented Performer": Target_oriented_performer / 100,
            "Momentum Gainer": Momentum_gainer / 100,
            "Consistently Weak Performer": Consistently_Weak_Performer / 100,
            "Fluctuating Performer": Fluctuating_Performer / 100,
            "Declining Performer": Declining_Performer / 100
        }

        # ---- Calculate Metrics --------
        input_data['MPA'] = (input_data['CS'].astype(float) / input_data['market_potential'].astype(float)) * 100
        input_data['SOB'] = (input_data['AP_12'].astype(float) / input_data['CS'].astype(float)) * 100
        input_data['MPA'] = input_data['MPA'].clip(upper=100)
        input_data['SOB'] = input_data['SOB'].clip(upper=100)

        #Handling null values for appropriate incentive setting
        input_data['MPA'] = input_data['MPA'].fillna(0)
        input_data['SOB'] = input_data['SOB'].fillna(0)

        #Normalising average
        input_data['AP_normalized'] = (input_data['AP_12'] - input_data['AP_12'].min()) / (input_data['AP_12'].max() - input_data['AP_12'].min())
        input_data['AP_normalized'] = input_data['AP_normalized'] * 100


        # Score and Tier Assignment
        input_data['Score'] = input_data.apply(lambda row: custom_functions.calculate_score(row, weights), axis=1)
        input_data['Tier'] = pd.qcut(input_data['Score'], q=6, labels=[f'Tier {i}' for i in range(6, 0, -1)])

        def round_nearest(series, base=5):
            return base * (series / base).round()
        
        # ---- Apply Incentives Based on Selection from Radio Buttom ----
        if incentive_type == "Range":
            tier_incentives = custom_functions.get_tier_incentives('exponenetial', min_incentive, max_incentive)

            #Obtaining the Incentive based on tier
            input_data['Incentive_per_Ton_exponential'] = input_data['Tier'].map(tier_incentives)
            input_data['Incentive_per_Ton_exponential'] = pd.to_numeric(input_data['Incentive_per_Ton_exponential'], errors='coerce')

            #Adding the bonus incentive
            input_data["Final_Incentive"] = round(
                input_data["Incentive_per_Ton_exponential"] * 
                (1 + input_data["Category_Overall"].map(category_bonus).fillna(0))
            )

            #Bonus incentive value
            input_data["Perfomance_Bonus"] = input_data["Final_Incentive"] - input_data["Incentive_per_Ton_exponential"]

            #Rounding to nearest 5 multiple
            input_data["Incentive_per_Ton_exponential"] = custom_functions.round_nearest(input_data["Incentive_per_Ton_exponential"])
            input_data["Perfomance_Bonus"] = custom_functions.round_nearest(input_data["Perfomance_Bonus"])
            input_data["Final_Incentive"] = custom_functions.round_nearest(input_data["Final_Incentive"])
            input_data["Predicted_Incentive"] = (input_data["Final_Incentive"] * input_data["Predicted_Target"]).round(-1)
            
        elif incentive_type == "Average":

            # Dynamically generate min and max incentive around the average
            min_incentive = int(avg_inc_pt * 0.6)
            max_incentive = int(avg_inc_pt * 1.4)

            # Generate tier incentives based on exponential pattern
            tier_incentives = custom_functions.get_tier_incentives('exponential', min_incentive, max_incentive)
 
            # Map base tier incentive to each dealer
            input_data['Incentive_per_Ton_exponential'] = input_data['Tier'].map(tier_incentives)
            input_data['Incentive_per_Ton_exponential'] = pd.to_numeric(input_data['Incentive_per_Ton_exponential'], errors='coerce')

            # Apply performance bonus (category-based)
            input_data["Perfomance_Bonus"] = (
                input_data["Incentive_per_Ton_exponential"] * 
                input_data["Category_Overall"].map(category_bonus).fillna(0)
            ).round()

            # Totalling 
            input_data["Final_Incentive"] = (
                input_data["Incentive_per_Ton_exponential"] + input_data["Perfomance_Bonus"]
            ).round()

            # Calculate unscaled total payout
            input_data["Predicted_Incentive"] = input_data["Final_Incentive"] * input_data["Predicted_Target"]
            total_base_payout = input_data["Predicted_Incentive"].sum()

            # Compute scaling factor to match average-based total incentive cap
            # total_incentive found in the avg incentive number input section
            scaling_factor = total_incentive / total_base_payout if total_base_payout != 0 else 0

            # Scale each relevant component proportionally
            input_data["Incentive_per_Ton_exponential"] = (input_data["Incentive_per_Ton_exponential"] * scaling_factor).round()
            input_data["Perfomance_Bonus"] = (input_data["Perfomance_Bonus"] * scaling_factor).round()
            input_data["Final_Incentive"] = (input_data["Final_Incentive"] * scaling_factor).round()

            #Rounding to the nearest multiple of 5
            input_data["Incentive_per_Ton_exponential"] = custom_functions.round_nearest(input_data["Incentive_per_Ton_exponential"])
            input_data["Perfomance_Bonus"] = custom_functions.round_nearest(input_data["Perfomance_Bonus"])
            input_data["Final_Incentive"] = custom_functions.round_nearest(input_data["Final_Incentive"])

            # Recompute predicted incentive after scaling
            input_data["Predicted_Incentive"] = (input_data["Final_Incentive"] * input_data["Predicted_Target"]).round(-1)

        df = input_data

        # Get the columns in `input_data` that are not in `display_data`
        missing_columns = [col for col in input_data.columns if col not in df_dis.columns]

        # Merge only the missing columns from `input_data` into `display_data`
        # We merge on 'Dealer_Code', assuming it exists in both dataframes
        display_data = pd.merge(
            df_dis,
            input_data[['Dealer_Code'] + missing_columns], 
            on='Dealer_Code',
            how='left'
        )

        #Downloading a csv output
        display_data.to_csv('Data/output.csv', index = False)

        sales_col = [col for col in df.columns if 'sales' in col]
        target_col = [col.replace('sales', 'Target') for col in sales_col]
        prev_target_month = target_col[-1]

        column_labels = {
            "Dealer_Code": "Dealer Code",
            "Dealer_Name": "Dealer Name",
            "dealer_district": "District",
            "dealer_taluka" : "Taluka",
            "dealer_type": "Dealer Type",
            "Achieved_Type":"Target Achievement",
            "Category_Overall" : "Sales Performance",
            prev_target_month : "Previous Month's Target",
            "Tier": "Incentive Tier",
            "Incentive_per_Ton_exponential": "Base Incentive",
            "Perfomance_Bonus": "Performance Bonus",
            "Final_Incentive" : "Incentive per Ton",
            "Predicted_Target" : "Predicted Target",
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
            prev_target_month,
            "Predicted_Target",
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
        df_to_display = df[display_columns].rename(columns=column_labels)

        # Ensure "Not Set" is a valid category first
        df_to_display['Incentive Tier'] = df_to_display['Incentive Tier'].cat.add_categories(['Not Set'])
        # Now fill the NaNs
        df_to_display['Incentive Tier'] = df_to_display['Incentive Tier'].fillna('Not Set')
        df_to_display["Previous Month's Target"] = df_to_display["Previous Month's Target"].fillna(0).round().astype(int)
        df_to_display['Base Incentive'] = df_to_display['Base Incentive'].fillna(0)
        df_to_display['Performance Bonus'] = df_to_display['Performance Bonus'].fillna(0)
        df_to_display['Incentive per Ton'] = df_to_display['Incentive per Ton'].fillna(0)
        df_to_display['Predicted Incentive'] = df_to_display['Predicted Incentive'].fillna(0)

    #   ------ KPIs and display table ------------
    with col_kpi_table:
        
        #Adding all the warnings for incorrect inputs
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
                <p>{df_to_display['Dealer Code'].nunique()}</p>
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

#-----------------------------------
# Target Distribution Analysis

sales_col = [col for col in input_data.columns if 'sales' in col]
target_col = [col.replace('sales', 'Target') for col in sales_col]
prev_target_month = target_col[-1]
prev_sale_month = sales_col[-1]

prev_target_rename = custom_functions.convert_column_for_display(prev_target_month)
prev_sale_rename = custom_functions.convert_column_for_display(prev_sale_month)

summary_table = (
    input_data
    .groupby("Achieved_Type")
    .agg({
        "Dealer_Code": pd.Series.nunique,  # count of unique dealers
        prev_sale_month : "sum",
        prev_target_month: "sum",
        "Predicted_Target": "sum"
        
    })
    .rename(columns={
        prev_sale_month: prev_sale_rename,
        prev_target_month: prev_target_rename,
        "Predicted_Target": "Predicted Target",
        "Dealer_Code": "No. of Dealers"
    })
    .reset_index()
)

# Convert amounts to integers (whole numbers)
summary_table["No. of Dealers"] = summary_table["No. of Dealers"].astype(int)
summary_table[prev_sale_rename] = summary_table[prev_sale_rename].astype(int)
summary_table[prev_target_rename] = summary_table[prev_target_rename].astype(int)
summary_table["Predicted Target"] = summary_table["Predicted Target"].astype(int)

# Rename 'Achieved_Type' to 'Target Achievement'
summary_table = summary_table.rename(columns={"Achieved_Type": "Target Achievement"})

achievement_order = [
    "High Achievement",
    "Moderate Achievement",  
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
    prev_sale_rename: [summary_table[prev_sale_rename].sum()],
    prev_target_rename: [summary_table[prev_target_rename].sum()],
    "Predicted Target": [summary_table["Predicted Target"].sum()],
    "No. of Dealers": [summary_table["No. of Dealers"].sum()]
})

# Final table
summary_table = pd.concat([summary_table, grand_total], ignore_index=True)
summary_table_display = summary_table.loc[:,["Target Achievement", "March 2025 Sales", "March 2025 Target", "Predicted Target"]].copy()

# Highlight Grand Total row
def highlight_total_row(row):
    if row["Target Achievement"] == "Grand Total":
        return ['background-color: #e0f7fa; color: #1f4e79; font-weight: bold;' for _ in row]
    return ['' for _ in row]

# Tab 2: Target Distribution Validation
with tab2:

    # st.data_editor(target_sales_cross,key="cross_table")
    st.subheader(f"{prev_sale_rename[:-6]} Summary, Dealer Count & Predicted Target by Achievement Type")
    st.dataframe(summary_table.style.apply(highlight_total_row, axis=1), use_container_width=True)

    # Remove Grand Total row
    summary_chart_data = summary_table[summary_table["Target Achievement"] != "Grand Total"].copy()

    # Calculate averages
    summary_chart_data[f"Avg {prev_target_rename}"] = summary_chart_data[prev_target_rename] / summary_chart_data["No. of Dealers"]
    summary_chart_data["Avg Predicted Target"] = summary_chart_data["Predicted Target"] / summary_chart_data["No. of Dealers"]

    # Apply custom order
    summary_chart_data["Target Achievement"] = pd.Categorical(
        summary_chart_data["Target Achievement"],
        categories=achievement_order,
        ordered=True
    )

    # st.subheader("Predicted Target Model Distribution")
    # Set up columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"##### Average {prev_target_rename} per Dealer")
        mar_target_chart = alt.Chart(summary_chart_data).mark_bar().encode(
            x=alt.X("Target Achievement:N", sort=None, title="Achievement Type"),
            y=alt.Y(f"Avg {prev_target_rename}:Q", title=f"Average {prev_target_rename[:-11]} Target"),
            tooltip=["Target Achievement", f"Avg {prev_target_rename}"]
        ).properties(width=350, height=400)
        st.altair_chart(mar_target_chart, use_container_width=True)

    with col2:
        st.markdown("##### Average Predicted Target per Dealer")
        pred_target_chart = alt.Chart(summary_chart_data).mark_bar(color="#83C9FF").encode(
            x=alt.X("Target Achievement:N", sort=None, title="Achievement Type"),
            y=alt.Y("Avg Predicted Target:Q", title="Average Predicted Target"),
            tooltip=["Target Achievement", "Avg Predicted Target"]
        ).properties(width=350, height=400)
        st.altair_chart(pred_target_chart, use_container_width=True)

#3 months

sales_col = [col for col in input_data.columns if 'sales' in col]
target_col = [col.replace('sales', 'Target') for col in sales_col]

recent_months_sales = sales_col[-3:]
previous_months_sales = sales_col[-6:-3]

recent_months =[]
prev_months = []
for col in recent_months_sales:
    rename = custom_functions.convert_column_for_display(col)
    recent_months.append(rename[:-11])

for col in previous_months_sales:
    rename = custom_functions.convert_column_for_display(col)
    prev_months.append(rename[:-11])


recent_months_target = target_col[-3:]
previous_months_target = target_col[-6:-3]

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

#For the plotting
df_long = preprocessing.df_long

#Tab 3 : Dealer Analysis
with tab3:

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

    # --- Validation: Check if user has made selections and if data is available
    if not selected_perf or not selected_achv:
        st.warning("Please select at least one Sales Performance Category and one Target Achievement to proceed.")
        st.stop()

    # --- Filter the growth-enhanced data
    filtered_dealers = growth_df[
        growth_df["Category_Overall"].isin(selected_perf) &
        growth_df["Achieved_Type"].isin(selected_achv)
    ]

    if filtered_dealers.empty:
        st.warning("No dealers match the selected Sales Performance Category and Target Achievement. Please try a different combination.")
        st.stop()

    #For the plotting
    df_long = preprocessing.df_long
    selected_dealers = df_long[(df_long['Quarter'] == 4) & 
                           (df_long['Category_Overall'].isin(selected_perf)) &
                           (df_long['Achieved_Type'].isin(selected_achv))]['Dealer_Code'].to_list()
    
    df_long = df_long[(df_long['Dealer_Code'].isin(selected_dealers))].sort_values(by = ['Dealer_Code', 'Quarter'])

    dealer_table, dealer_graph = st.columns(2)

    with dealer_table:
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

        achievement_order = {
            'Target Not Set': -1,
            'No Achievement': 0,
            'Low Achievement': 1,
            'Moderate Achievement': 2,
            'High Achievement': 3
        }

        category_order = {
            'Consistently Weak Performer': 0,
            'Declining Performer': 1,
            'Fluctuating Performer': 2,
            'Momentum Gainer': 3,
            'Target-Oriented Performer': 4,
            'Emerging Performer': 5,
            'Consistently Strong Performer': 6
        }

        df_long['Achievement_Score'] = df_long['Achieved_Type'].map(achievement_order)
        df_long['Category_Score'] = df_long['Category_Overall'].map(category_order)

        # Get Q1 and Q4 scores
        summary = df_long[df_long['Quarter'].isin([3, 4])].copy()

        # Pivot to get Q1 and Q4 in columns
        pivoted = summary.pivot(index='Dealer_Code', columns='Quarter', values=['Achievement_Score', 'Category_Score'])

        # Rename columns for clarity
        pivoted.columns = ['Achievement_Score_Q3', 'Achievement_Score_Q4', 'Category_Score_Q3', 'Category_Score_Q4']
        pivoted = pivoted.reset_index()

        # Calculate net change
        pivoted['Achievement_Change_Overall'] = pivoted['Achievement_Score_Q4'] - pivoted['Achievement_Score_Q3']
        pivoted['Category_Change_Overall'] = pivoted['Category_Score_Q4'] - pivoted['Category_Score_Q3']

        # Define labels
        pivoted["Recent Quarter's Achievement Trend"] = pivoted['Achievement_Change_Overall'].apply(
            lambda x: 'Improved' if x > 0 else ('Declined' if x < 0 else 'No Change')
        )

        pivoted["Recent Quarter's Category Trend"] = pivoted['Category_Change_Overall'].apply(
            lambda x: 'Improved' if x > 0 else ('Declined' if x < 0 else 'No Change')
        )

        display_df =  display_df.merge(pivoted[["Dealer_Code", "Recent Quarter's Achievement Trend", "Recent Quarter's Category Trend"]],
                                       left_on= 'Dealer Code',
                                       right_on= 'Dealer_Code',
                                       how= 'left').drop('Dealer_Code', axis= 1)
        display_df.sort_values(by= 'Dealer Code', inplace= True)
        # --- Show the clean table
        st.markdown(f"##### {len(display_df)} Dealers Matching Selection")

        st.markdown("""
            <style>
            .stAlert > div {
                font-size: 0.85rem;
                
            }
            </style>
        """, unsafe_allow_html=True)

        st.dataframe(display_df, use_container_width=True, height=450)

        # Join month names with commas
        recent_str = ", ".join(recent_months)
        prev_str = ", ".join(prev_months)

        st.markdown(
            f"""
        <div style='font-size: 12px; color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px; margin-bottom: 10px;'>
            <strong><span style='color: #1f4e79;'>Note:</span></strong><br>
            <span style='color: #1f4e79;'>Quarter-on-quarter growth is calculated by comparing:</span><br>
            <span style='color: #1f4e79;'>- <b>Recent Quarter:</b> {recent_str}</span><br>
            <span style='color: #1f4e79;'>- <b>Previous Quarter:</b> {prev_str}</span><br>
            <span style='color: #1f4e79;'><b>Achievement and category trends</b> are based on performance progression from the previous to the most recent quarter.</span>
        </div>

            """,
            unsafe_allow_html=True
        )


    with dealer_graph:
        st.markdown(f"##### Achievement Trend Visualization")

        # Step 1: Create multi-select to select one or more dealers
        dealer_options = sorted(pivoted['Dealer_Code'].unique().tolist())
        selected_dealers = st.multiselect(
            "Select one or more Dealer Codes to view their trend:",
            options=dealer_options,
            default=dealer_options[:1]  # optionally pre-select one
        )

        if not selected_dealers:
            st.warning("No dealers selected. Choose atleast one dealer to visualise achievement trend.")
            st.stop()

        # Step 2: Prepare data for selected dealers (FIX: .isin instead of .isnin)
        dealer_data = df_long[df_long['Dealer_Code'].isin(selected_dealers)].sort_values(by='Quarter')

        # Step 3: Create an Altair chart with color by Dealer_Code
        chart = alt.Chart(dealer_data).mark_line(
            point=alt.OverlayMarkDef(filled=True, size=75),
            strokeWidth=3
        ).encode(
            x=alt.X('Quarter:O', title='Quarter'),
            y=alt.Y('Achievement_Score:Q', title='Achievement Score', scale=alt.Scale(domain=[-1.5, 3.5])),
            color=alt.Color('Dealer_Code:N', title='Dealer Code'),  # Different lines for each dealer
            tooltip=[
                alt.Tooltip('Dealer_Code:N', title='Dealer Code'),
                alt.Tooltip('Quarter:O'),
                alt.Tooltip('Achieved_Type:N', title='Achievement Type'),
                alt.Tooltip('Achievement_Score:Q', title='Score')
            ]
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=13
        )

        # Step 4: Show in Streamlit
        st.altair_chart(chart, use_container_width=True)


        st.markdown(
        """
        <div style='font-size: 12px; color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px; margin-bottom: 10px;'>
            <span style='color: #1f4e79;'><strong>Achievement Categories</strong> used in the graph:</span><br><br>
            <span style='color: #1f4e79;'>0: High Achievement</span><br>
            <span style='color: #1f4e79;'>1: Moderate Achievement</span><br>
            <span style='color: #1f4e79;'>2: Low Achievement</span><br>
            <span style='color: #1f4e79;'>3: No Achievement</span><br>
            <span style='color: #1f4e79;'>-1: Target Not Set (New Dealer or Becoming Inactive)</span>
        </div>
        """,
        unsafe_allow_html=True
        )



#Visualizations
#All previous sales and targets data
all_data = preprocessing.df_visual
all_data = all_data[all_data['Dealer_Code'].isin(df_dis['Dealer_Code'])]

sales_columns = [col for col in all_data.columns if re.search(r'\d+_sales$', col)]
target_columns = [col for col in all_data.columns if re.search(r'\d+_Target$', col)]
counter_columns= [col for col in all_data.columns if re.search(r'\d+_counter$', col)]
oth_columns = [col for col in all_data if col not in sales_columns+target_columns+counter_columns]


sales = all_data[oth_columns + sales_columns]
targets = all_data[oth_columns + target_columns]

#Renaming using function defined in target_pr
alltime_sales = sales.rename(columns={col: custom_functions.convert_fy_to_price(col) for col in sales.columns})
alltime_targets = targets.rename(columns={col: custom_functions.convert_fy_to_price(col) for col in targets.columns})

#Reshaping
#Obtianing the month columns
month_year_cols = [col for col in alltime_sales.columns if '-' in col] 

sales_reshaped = alltime_sales.melt(id_vars=oth_columns, 
                    value_vars=month_year_cols, var_name='Month-Year', value_name='Sales')

targets_reshaped = alltime_targets.melt(id_vars=oth_columns,
                                value_vars=month_year_cols, var_name='Month-Year', value_name='Targets')

sales_reshaped['Date'] = pd.to_datetime(sales_reshaped['Month-Year'], format='%b-%y')
targets_reshaped['Date'] = pd.to_datetime(targets_reshaped['Month-Year'], format='%b-%y')

sales_reshaped.drop('Month-Year', axis = 1, inplace = True)
targets_reshaped.drop('Month-Year', axis = 1, inplace = True)

sales_targets = pd.merge(sales_reshaped,
                         targets_reshaped,
                         on = oth_columns + ['Date'],
                         how = 'inner')

with tab4:

    col_linechart, col_barchart = st.columns(2)

    with col_linechart:

        st.markdown("### Sales vs Target Over Time")

        col_time, col_filter, col_subfilter = st.columns(3)
        
        with col_time:
            agg_type = st.radio("Select Aggregation:", ("Month-wise", "Year-wise"))

        with col_filter:
            filter_type = st.selectbox("Select Filter Type:", ["All", "State", "District", "Dealer"])
            filtered_data = sales_targets.copy()

        with col_subfilter:
            if filter_type == "State":
            
                state_option = st.selectbox("Select State:", ["All", "Andhra Pradesh", "Telangana"])

                if state_option == "Andhra Pradesh":
                    filtered_data = filtered_data[filtered_data['Dealer_Code'].str.startswith('SIPA')]
                elif state_option == "Telangana":
                    filtered_data = filtered_data[filtered_data['Dealer_Code'].str.startswith('SIPT')]

            elif filter_type == "District":
                district_list = sorted(filtered_data['dealer_district'].dropna().unique())
                district_options = ["All"] + district_list
                selected_district = st.selectbox("Select District:", options=district_options)

                if selected_district != "All":
                    filtered_data = filtered_data[filtered_data['dealer_district'] == selected_district]

            elif filter_type == "Dealer":
                dealer_list = sorted(filtered_data['Dealer_Name'].dropna().unique())
                dealer_options = ["All"] + dealer_list
                selected_dealer = st.selectbox("Select Dealer:", options=dealer_options)

                if selected_dealer != "All":
                    filtered_data = filtered_data[filtered_data['Dealer_Name'] == selected_dealer]


        # Aggregation
        if agg_type == "Month-wise":
            st_line_chart = filtered_data.groupby('Date')[['Sales', 'Targets']].sum().reset_index()
            x_axis = alt.X('Date:T', title='Month-Year')
        else:
            filtered_data['Year'] = filtered_data['Date'].dt.year
            st_line_chart = filtered_data.groupby('Year')[['Sales', 'Targets']].sum().reset_index()
            x_axis = alt.X('Year:O', title='Year')

        # Melt the data for Altair (long format)
        st_line_chart_melted = st_line_chart.melt(id_vars=[st_line_chart.columns[0]], 
                                                  value_vars=['Sales', 'Targets'],
                                                  var_name='Metric', value_name='Value')

        # Build the Altair chart
        chart = alt.Chart(st_line_chart_melted).mark_line(point=True).encode(
            x=x_axis,
            y=alt.Y('Value:Q', title='Total Value (MT)'),
            color='Metric:N',
            tooltip=[st_line_chart_melted.columns[0], 'Metric', 'Value']
        ).properties(
            width=800,
            height=300
        ).interactive()

        st.altair_chart(chart, use_container_width= True)

    with col_barchart:

        st.markdown("### District Sales Split and Achievement %")

        col_state, col_year, col_month = st.columns(3)

        with col_state:
        # -------- Filter Controls ----------
            state_selected = st.radio("Select State:", ["Andhra Pradesh", "Telangana"], index=0)

            # Filter based on State
            if state_selected == "Andhra Pradesh":
                barchart_data = sales_targets[sales_targets['Dealer_Code'].str.startswith('SIPA')].copy()
            else:
                barchart_data = sales_targets[sales_targets['Dealer_Code'].str.startswith('SIPT')].copy()

            # Extract Year and Month
            barchart_data['Year'] = barchart_data['Date'].dt.year
            barchart_data['Month'] = barchart_data['Date'].dt.month_name()

        with col_year:
            # Year Filter
            years_list = sorted(barchart_data['Year'].dropna().unique())
            year_options = ["All"] + [str(year) for year in years_list]
            selected_year = st.selectbox("Select Year:", options=year_options, index=0)

        with col_month:
            # Month Filter
            months_list = barchart_data['Month'].dropna().unique()
            months_order = ['January', 'February', 'March', 'April', 'May', 'June',
                            'July', 'August', 'September', 'October', 'November', 'December']
            months_list_sorted = [month for month in months_order if month in months_list]
            month_options = ["All"] + months_list_sorted
            selected_month = st.selectbox("Select Month:", options=month_options, index=0)

        # --------- Apply Filters ---------
        if selected_year != "All":
            barchart_data = barchart_data[barchart_data['Year'] == int(selected_year)]

        if selected_month != "All":
            barchart_data = barchart_data[barchart_data['Month'] == selected_month]

        # -------- Data Preparation ----------
        district_summary = barchart_data.groupby(['dealer_district', 'dealer_type']).agg({'Sales':'sum', 'Targets':'sum'}).reset_index()

        achievement_summary = district_summary.groupby('dealer_district').agg({'Sales':'sum', 'Targets':'sum'}).reset_index()
        achievement_summary['Achievement %'] = (achievement_summary['Sales'] / achievement_summary['Targets']) * 100

        # -------- Altair Chart ----------
        bar = alt.Chart(district_summary).mark_bar().encode(
            x=alt.X('dealer_district:N', sort='-y', title='District'),
            y=alt.Y('Sales:Q', title='Sales (MT)'),
            color=alt.Color('dealer_type:N', title='Dealer Type'),
            tooltip=['dealer_district', 'dealer_type', 'Sales']
        )

        line = alt.Chart(achievement_summary).mark_line(point=True, color='black').encode(
            x=alt.X('dealer_district:N'),
            y=alt.Y('Achievement %:Q', title='Achievement (%)', axis=alt.Axis(titleColor='black')),
            tooltip=['dealer_district', 'Achievement %']
        ).interactive()

        final_chart = alt.layer(bar, line).resolve_scale(
            y='independent'
        ).properties(
            width=750,
            height=300
        )

        st.altair_chart(final_chart, use_container_width= True)

    st.markdown("### Achievement % Heatmap for Top Long-Term High-Volume Dealers")

    # Start fresh
    heatmap_data = sales_targets.copy()

    # Filter Controls
    col_hmap_agg, col_hmap_state, col_hmap_dist = st.columns(3)

    with col_hmap_agg:
        agg_type = st.radio("Aggregation", ["Month-wise", "Year-wise"], key="heatmap_agg")

    with col_hmap_state:
        hmap_state_option = st.selectbox("State", ["All", "Andhra Pradesh", "Telangana"], key="heatmap_state")
        if hmap_state_option == "Andhra Pradesh":
            heatmap_data = heatmap_data[heatmap_data['Dealer_Code'].str.startswith("SIPA")]
        elif hmap_state_option == "Telangana":
            heatmap_data = heatmap_data[heatmap_data['Dealer_Code'].str.startswith("SIPT")]

    with col_hmap_dist:
        districts = sorted(heatmap_data['dealer_district'].dropna().unique())
        selected_district = st.selectbox("District", ["All"] + districts, key="heatmap_district")
        if selected_district != "All":
            heatmap_data = heatmap_data[heatmap_data['dealer_district'] == selected_district]

    # Time column for grouping
    if agg_type == "Month-wise":
        heatmap_data["Time"] = heatmap_data["Date"].dt.strftime("%b-%Y")
        time_sort_order = list(heatmap_data["Time"].dropna().unique())
    else:
        heatmap_data["Time"] = heatmap_data["Date"].dt.year.astype(str)
        time_sort_order = sorted(heatmap_data["Time"].dropna().unique())

    # Step 1: Aggregate achievement % per dealer code (unique identifier)
    dealer_achievement = (
        heatmap_data.groupby(["Dealer_Code", "Dealer_Name"])[["Sales", "Targets"]]
        .sum()
        .reset_index()
    )

    dealer_achievement["Achievement %"] = (dealer_achievement["Sales"] / dealer_achievement["Targets"]) * 100

    # Step 2: Select Top 5 dealers by Sales (using Dealer_Code)
    top_5_dealers = (
        dealer_achievement.sort_values("Sales", ascending=False)
        .head(5)["Dealer_Code"]
        .tolist()
    )

    # Step 3: Filter original data for these top dealer codes
    heatmap_data_filtered = heatmap_data[heatmap_data["Dealer_Code"].isin(top_5_dealers)].copy()

    # Recalculate Achievement % per row (optional, but keeps data consistent)
    heatmap_data_filtered["Achievement %"] = (heatmap_data_filtered["Sales"] / heatmap_data_filtered["Targets"]) * 100

    # Step 4: Create heatmap using Dealer_Code on y-axis
    heatmap = alt.Chart(heatmap_data_filtered).mark_rect().encode(
        x=alt.X("Time:N", title="Time", sort=time_sort_order),
        y=alt.Y("Dealer_Code:N", title="Dealer ID", sort="-x"),
        color=alt.Color("Achievement %:Q", scale=alt.Scale(scheme='blues'), title="Achievement %"),
        tooltip=[
            "Dealer_Code",
            "Dealer_Name",
            "Time",
            alt.Tooltip("Achievement %:Q", format=".2f")
        ],
    ).properties(
        width=800,
        height=300
    )
    # Step 5: Show a markdown legend below the heatmap mapping Dealer_Code to Dealer_Name
    # Extract the mapping for the top 5 dealers
    dealer_map = dealer_achievement[dealer_achievement["Dealer_Code"].isin(top_5_dealers)][["Dealer_Code", "Dealer_Name"]]
    # Create inline mapping string: "D001: ABC Steels | D002: XYZ Traders | ..."
    mapping_list = [
        f"<strong>{row['Dealer_Code']}</strong>: {row['Dealer_Name']}" 
        for _, row in dealer_map.iterrows()
    ]
    mapping_string = " | ".join(mapping_list)

    st.markdown(
        f"""
        <div style='text-align: center;'>
            <div style='display: inline-block; font-size: 12px; color: #1f4e79; padding: 5px 10px; background-color: #e0f7fa; border-left : 5px solid #1f4e79; border-radius: 5px; margin-bottom: 10px;'>
                <span style='color: #1f4e79;'>{mapping_string}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.altair_chart(heatmap, use_container_width=True)



