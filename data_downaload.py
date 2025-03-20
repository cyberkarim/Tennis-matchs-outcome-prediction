from urllib.request import urlopen
import os.path as osp
import os
import logging
import zipfile
from glob import glob
from urllib.error import HTTPError
import requests
import pandas as pd






# Function to download zip file
def download_file(url_str, path):
    url = urlopen(url_str)
    output = open(path, 'wb')
    output.write(url.read())
    output.close()

# Function to extract zip file
def extract_file(archive_path, target_dir):
    zip_file = zipfile.ZipFile(archive_path, 'r')
    zip_file.extractall(target_dir)
    zip_file.close()

# Function to download XLSX file from URL and save it to a directory
def download_xlsx_file(url, directory):
    # Create the directory if it doesn't exist
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Extract filename from the URL
    filename = os.path.join(directory, url.split("/")[-1])

    # Send GET request to the URL
    response = requests.get(url)

    # Check if request was successful
    if response.status_code == 200:
        # Save the file
        with open(filename, 'wb') as f:
            f.write(response.content)
        print("File downloaded successfully.")
    else:
        print("Failed to download file.")



BASE_URL = 'http://tennis-data.co.uk'
DATA_DIR = "tennis_data"
ATP_DIR = './{}/ATP'.format(DATA_DIR)
WTA_DIR = './{}/WTA'.format(DATA_DIR)

ATP_URLS = [BASE_URL + "/%i/%i.zip" % (i,i) for i in range(2000,2025)]
WTA_URLS = [BASE_URL + "/%iw/%i.zip" % (i,i) for i in range(2007,2025)]

os.makedirs(osp.join(ATP_DIR, 'archives'), exist_ok=True)
os.makedirs(osp.join(WTA_DIR, 'archives'), exist_ok=True)

for files, directory in ((ATP_URLS, ATP_DIR), (WTA_URLS, WTA_DIR)):
    for dl_path in files:
        logging.info("downloading & extracting file %s", dl_path)
        archive_path = osp.join(directory, 'archives', osp.basename(dl_path))
        try:
          # if the data file provided by the server is a compressed file (.zip), it will be downloaded and extracted into the ATP/WTP folder
          download_file(dl_path, archive_path)
          extract_file(archive_path, directory)

        except HTTPError as e:
          if e.code == 300:
            substring_before_last_four = dl_path[:-4]

         # Define the new ending
            new_ending = ".xlsx"

            # Concatenate the substring before the last 4 characters with the new ending
            new_dl_path = substring_before_last_four + new_ending
            download_xlsx_file(new_dl_path, directory)

          else:
            print("HTTP Error:", e)
        


ATP_FILES = sorted(glob("%s/*.xls*" % ATP_DIR))
WTA_FILES = sorted(glob("%s/*.xls*" % WTA_DIR))

## concat all individual xlsx files relating each year matches into one dataframe
df_atp = pd.concat([pd.read_excel(f) for f in ATP_FILES], ignore_index=True)
df_wta = pd.concat([pd.read_excel(f) for f in WTA_FILES], ignore_index=True)

logging.info("%i matches ATP in df_atp", df_atp.shape[0])
logging.info("%i matches WTA in df_wta", df_wta.shape[0])