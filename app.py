import pandas as pd
import os

def split_and_save_csv_to_met_folder(input_csv):
    """
    Reads 'input_csv' with columns:
      State, District, Block, Date, Rainfall, Max_Temperature, Min_Temperature
    Groups by (State, District, Block) and writes:
      - A CSV with columns [State, District, Block, Date, Rainfall]
      - A CSV with columns [State, District, Block, Date, Max_Temperature, Min_Temperature]
    Filenames are saved to the 'Met' folder with the pattern:
      State_District_Block_Rainfall.csv
      State_District_Block_Temperature.csv
    """
    # Read the CSV, parsing the Date column (assuming DD-MM-YYYY).
    # Adjust parse_dates/dayfirst as needed for your date format.
    df = pd.read_csv(input_csv, parse_dates=['Date'], dayfirst=True)
    
    # Sort by Date to keep chronological order (optional)
    df.sort_values('Date', inplace=True)
    
    # Create the 'Met' folder if it doesn't exist
    output_folder = "Met"
    os.makedirs(output_folder, exist_ok=True)
    
    # Group by State, District, Block
    grouped = df.groupby(['State', 'District', 'Block'])
    
    for (state, district, block), group_data in grouped:
        # --- Rainfall CSV ---
        rainfall_data = group_data[['State', 'District', 'Block', 'Date', 'Rainfall']]
        rainfall_filename = f"{state}_{district}_{block}_Rainfall.csv"
        rainfall_filepath = os.path.join(output_folder, rainfall_filename)
        rainfall_data.to_csv(rainfall_filepath, index=False)
        
        # --- Temperature CSV ---
        temp_data = group_data[['State', 'District', 'Block', 'Date', 'Max_Temperature', 'Min_Temperature']]
        temp_filename = f"{state}_{district}_{block}_Temperature.csv"
        temp_filepath = os.path.join(output_folder, temp_filename)
        temp_data.to_csv(temp_filepath, index=False)

    print(f"Done! Split files have been saved in the '{output_folder}' folder.")

# Example usage:
if __name__ == "__main__":
    # Replace 'weather_data.csv' with the path to your main CSV file
    split_and_save_csv_to_met_folder("weather_data.csv")
