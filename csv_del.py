import os
import glob

# Set the directory where the .csv files are located
directory = "D:\Heavy_Machines_Construction\Heavy_Machines\equipment_data"  # Change this to your target directory

# Find all .csv files in the directory
csv_files = glob.glob(os.path.join(directory, "*.csv"))

# Delete each file
for file in csv_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("CSV file deletion completed.")
