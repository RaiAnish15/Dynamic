import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper: Load and group CSV data
# -----------------------------
@st.cache_data
def load_data(csv_path):
    """
    Reads the CSV (State, District, Block, Date, Rainfall, Max_Temperature, Min_Temperature),
    parses 'Date' as datetime, and groups by (State, District, Block).
    
    Returns a nested dictionary:
      data_dict[state][f"{district}-{block}"] = DataFrame for that group
    """
    if not os.path.exists(csv_path):
        st.error(f"CSV file not found at: {csv_path}")
        return {}

    df = pd.read_csv(csv_path, parse_dates=['Date'], dayfirst=True)
    df.sort_values('Date', inplace=True)
    
    data_dict = {}
    for (state, district, block), group_df in df.groupby(['State', 'District', 'Block']):
        # Key for second dropdown is "District-Block"
        district_block = f"{district}-{block}"
        # Store the subset DataFrame in a nested dict
        data_dict.setdefault(state, {})[district_block] = group_df
    return data_dict

def plot_timeseries(df, variable):
    """
    Returns an Altair line chart for the given DataFrame (df) and variable
    (which can be Rainfall, Max_Temperature, Min_Temperature).
    """
    # Create an Altair chart
    chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y(f'{variable}:Q', title=variable),
            tooltip=['Date', variable]
        )
        .properties(width=700, height=300, title=f"{variable} over time")
    )
    return chart

if section == "Meteorological Variable":
    st.sidebar.header("Meteorological Variable Options")
    
    # Load data from Met/weather_data.csv
    csv_path = os.path.join("Met", "weather_data.csv")  # Adjust if needed
    data_dict = load_data(csv_path)
    
    if not data_dict:
        st.info("No data available. Please check your CSV file path or contents.")
    else:
        # 1) State dropdown
        state_options = sorted(data_dict.keys())
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            # 2) District-Block dropdown
            district_block_options = sorted(data_dict[state_selected].keys())
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                # 3) Variable dropdown
                variables = ["Max_Temperature", "Min_Temperature", "Rainfall"]
                variable_options = ["select", "All"] + variables
                variable_selected = st.sidebar.selectbox("Select Variable", variable_options)
                
                if variable_selected != "select":
                    df_subset = data_dict[state_selected][district_block_selected]
                    
                    if variable_selected == "All":
                        # Show all variables
                        for var in variables:
                            chart = plot_timeseries(df_subset, var)
                            st.altair_chart(chart, use_container_width=True)
                    else:
                        # Show one variable
                        chart = plot_timeseries(df_subset, variable_selected)
                        st.altair_chart(chart, use_container_width=True)

elif section == "Market":
    st.sidebar.header("Market Options")
    market_option = st.sidebar.selectbox("Select Market Option", ["Option A", "Option B", "Option C"])
    st.write("## Market Section")
    st.write(f"You selected: **{market_option}**")
    st.write("Add your Market-related plots or data here.")

elif section == "What If":
    st.sidebar.header("What If Options")
    what_if_option = st.sidebar.selectbox("Select What If Scenario", ["Scenario 1", "Scenario 2", "Scenario 3"])
    st.write("## What If Section")
    st.write(f"You selected: **{what_if_option}**")
    st.write("Add your What If scenario analysis or plots here.")
