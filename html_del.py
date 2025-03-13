import os
import glob

# Set the directory where the .html files are located
directory = "D:\Heavy_Machines_Construction\Heavy_Machines"  # Change this to your target directory

# Find all .html files in the directory
html_files = glob.glob(os.path.join(directory, "*.html"))

# Delete each file
for file in html_files:
    try:
        os.remove(file)
        print(f"Deleted: {file}")
    except Exception as e:
        print(f"Error deleting {file}: {e}")

print("Deletion completed.")
