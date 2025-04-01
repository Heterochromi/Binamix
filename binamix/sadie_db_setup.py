import os
import sys
from binamix.file_utilities import *


# Set paths relative to script's own location
script_dir = os.path.dirname(os.path.abspath(__file__))
sadie_dir = os.path.join(script_dir, "..", "sadie")

# Check/create sadie folder if necessary
if not os.path.exists(sadie_base_path := os.path.join(script_dir, "..", "sadie")):
    os.makedirs(sadie_base_path)
else:
    print("You already have the SADIE Database in your directory.")

# Check and download if Database-Master_V1-4 doesn't exist
sadie_dataset_path = os.path.join(sadie_base_path, "Database-Master_V1-4")
if not os.path.exists(sadie_dataset_path := os.path.join(sadie_base_path, "Database-Master_V1-4")):
    url = 'https://www.york.ac.uk/sadie-project/Resources/SADIEIIDatabase/Database-Master_V1-4.zip'
    downloaded_file = download_file(url=url, dest_folder=sadie_base_path)
    unzip_file(downloaded_file, sadie_base_path)
    os.remove(downloaded_file)
    print(f"Zip file removed: {downloaded_file}")
    print("Setup Complete")
else:
    print("Database already exists, no download needed.")