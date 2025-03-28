import streamlit as st
import pandas as pd
import altair as alt
import os

st.set_page_config(page_title="Smart Agri: Basmati Intelligence Portal", layout="wide")
st.title("Smart Agri: Basmati Intelligence Portal")

# Top-level section selection
section = st.radio("Select Section", options=["Meteorological Variable", "Market", "What If"], horizontal=True)

# -----------------------------
# Helper: Build file dictionary from CSV files in the Met folder
# -----------------------------
def build_file_dict_from_met_folder(folder):
    """
    Reads CSV files from the specified folder and builds a nested dictionary:
      {
         state: {
             "District-Block": {
                 "Rainfall": file_path,
                 "Temperature": file_path
             }
         }
      }
    Expected filenames:
      State_District_Block_Rainfall.csv  
      State_District_Block_Temperature.csv
    """
    file_dict = {}
    if not os.path.exists(folder):
        st.error(f"Folder '{folder}' not found.")
        return None

    csv_files = [f for f in os.listdir(folder) if f.endswith(".csv")]
    if not csv_files:
        st.error(f"No CSV files found in the folder '{folder}'.")
        return None

    for filename in csv_files:
        # Remove extension and split by underscore
        name_no_ext = filename.split(".")[0]
        parts = name_no_ext.split("_")
        if len(parts) < 4:
            st.warning(f"Filename '{filename}' does not have enough parts. Skipping.")
            continue
        
        state = parts[0]
        district = parts[1]
        block = parts[2]
        variable = parts[3]  # Should be either 'Rainfall' or 'Temperature'
        
        district_block = f"{district}-{block}"
        file_dict.setdefault(state, {}).setdefault(district_block, {})[variable] = os.path.join(folder, filename)
    
    return file_dict

# -----------------------------
# Helper: Plot temperature (Max & Min together) using Altair
# -----------------------------
def plot_temperature(df):
    """
    Returns an Altair chart with two lines:
      - Max_Temperature in dark red
      - Min_Temperature in light red
    The y-axis is labeled as "Temperature".
    """
    base = alt.Chart(df).encode(x=alt.X('Date:T', title='Date'))
    
    max_line = base.mark_line().encode(
        y=alt.Y('Max_Temperature:Q', title='Temperature'),
        tooltip=['Date', 'Max_Temperature']
    ).encode(color=alt.value("darkred"))
    
    min_line = base.mark_line().encode(
        y=alt.Y('Min_Temperature:Q', title='Temperature'),
        tooltip=['Date', 'Min_Temperature']
    ).encode(color=alt.value("lightcoral"))
    
    chart = alt.layer(max_line, min_line).resolve_scale(y='shared').properties(
        width=700, height=300, title="Temperature over time"
    )
    return chart

# -----------------------------
# Helper: Plot rainfall using Altair
# -----------------------------
def plot_rainfall(df):
    """
    Returns an Altair chart for Rainfall with a blue line.
    """
    chart = (
        alt.Chart(df)
        .mark_line()
        .encode(
            x=alt.X('Date:T', title='Date'),
            y=alt.Y('Rainfall:Q', title='Rainfall'),
            tooltip=['Date', 'Rainfall']
        )
        .properties(title="Rainfall over time", width=700, height=300)
        .encode(color=alt.value("blue"))
    )
    return chart

# -----------------------------
# Meteorological Variable Section using CSV files from the Met folder
# -----------------------------
if section == "Meteorological Variable":
    st.sidebar.header("Meteorological Variable Options")
    
    # Set folder name; ensure it exists and contains the CSV files
    folder = "Met"  # Assuming the CSV files are in the 'Met' folder
    file_dict = build_file_dict_from_met_folder(folder)
    
    if file_dict:
        # 1) State dropdown
        state_options = sorted(file_dict.keys())
        state_selected = st.sidebar.selectbox("Select State", ["select"] + state_options)
        
        if state_selected != "select":
            # 2) District-Block dropdown
            district_block_options = sorted(file_dict[state_selected].keys())
            district_block_selected = st.sidebar.selectbox("Select District-Block", ["select"] + district_block_options)
            
            if district_block_selected != "select":
                # 3) Variable dropdown: only Temperature, Rainfall, or All
                variable_options = ["select", "Temperature", "Rainfall", "All"]
                variable_selected = st.sidebar.selectbox("Select Variable", variable_options)
                
                if variable_selected != "select":
                    # Load the CSV files for the selected state and district-block
                    df_temp = None
                    df_rain = None
                    
                    if "Temperature" in file_dict[state_selected][district_block_selected]:
                        df_temp = pd.read_csv(file_dict[state_selected][district_block_selected]["Temperature"], parse_dates=['Date'], dayfirst=True)
                        df_temp.sort_values('Date', inplace=True)
                    if "Rainfall" in file_dict[state_selected][district_block_selected]:
                        df_rain = pd.read_csv(file_dict[state_selected][district_block_selected]["Rainfall"], parse_dates=['Date'], dayfirst=True)
                        df_rain.sort_values('Date', inplace=True)
                    
                    if variable_selected == "Temperature":
                        if df_temp is not None:
                            chart = plot_temperature(df_temp)
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.error("Temperature data not available for the selected group.")
                    elif variable_selected == "Rainfall":
                        if df_rain is not None:
                            chart = plot_rainfall(df_rain)
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.error("Rainfall data not available for the selected group.")
                    elif variable_selected == "All":
                        if df_temp is not None:
                            chart = plot_temperature(df_temp)
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.error("Temperature data not available for the selected group.")
                        if df_rain is not None:
                            chart = plot_rainfall(df_rain)
                            st.altair_chart(chart, use_container_width=True)
                        else:
                            st.error("Rainfall data not available for the selected group.")

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
