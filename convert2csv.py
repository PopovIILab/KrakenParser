import sys
import pandas as pd

def convert_to_csv(input_file, output_file):
    # Read the entire file into a DataFrame
    data = pd.read_csv(input_file, sep='\t', header=None)
    
    # Set the first row as the header
    data.columns = data.iloc[0]
    data = data.drop(data.index[0])
    
    # Transpose the DataFrame so that sample names become rows and bacteria species with their abundance become columns
    data_transposed = data.T
    data_transposed.columns = data_transposed.iloc[0]
    data_transposed = data_transposed.drop(data_transposed.index[0])
    
    # Save the transposed data to a new CSV file
    data_transposed.to_csv(output_file, index_label='Sample_id')
    print(f"Data has been successfully converted and saved as '{output_file}'.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: ./convert2csv.py <input_file_path> <output_file_path>")
        sys.exit(1)

    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]
    convert_to_csv(input_file_path, output_file_path)