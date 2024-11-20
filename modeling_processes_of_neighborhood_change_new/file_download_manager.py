# file_download_manager.py

from config import ZIP_URLS
from tqdm import tqdm
from helper import LAYER_CACHE_DIR, layer_zip_filenames, layer_extract_filenames, CENSUS_DATA_CACHE_DIR
import zipfile
import requests

# ========================
# DOWNLOAD AND EXTRACT ZIP
# ========================

def download_and_extract_layers_all():
    """ Retrieve shapefile from extracted layer ZIP """
    shapefile_paths = {}
    for i in range(1, len(ZIP_URLS) +1):
        url = ZIP_URLS[i -1]
        zip_filename = layer_zip_filenames[i]
        extract_filename = layer_extract_filenames[i]
        
        extract_path = download_and_extract(url, zip_filename, extract_filename, LAYER_CACHE_DIR)
        
        shapefile_path = find_shapefile(extract_path)
        shapefile_paths[i] = shapefile_path

    return shapefile_paths

def download_and_extract_census_data(url, zip_filename, extract_filename):
    """ Retrieve correct EXCEL Sheet from extracted data ZIP """
    
    extract_path = download_and_extract(url, zip_filename, extract_filename, CENSUS_DATA_CACHE_DIR)
    if not extract_path:
        raise FileNotFoundError(f"ZIP extraction failed for URL: {url}")

    # Find the correct excel file
    excel_path = find_csv(extract_path)
    
    return excel_path

def download_and_extract(url, zip_filename, extract_filename, cache_dir):
    """ Helper function - Download and extract ZIP file """
    # Download
    file_path = download_zip_file(url, zip_filename, cache_dir)
    if not file_path:
        raise FileNotFoundError(f"ZIP download failed for URL: {url}")
    
    # Extract
    extract_path = extract_zip_file(file_path, extract_filename, cache_dir)
    if not extract_path:
        raise FileNotFoundError(f"ZIP extraction failed for URL: {url}")
    
    return extract_path

# download
def download_zip_file(url, filename, directory):
    """ Download file based on hyperlink URL """
    file_path = directory / filename

    # Check if file already exists
    if file_path.exists():
        print(f"File '{filename}' already exists. Skipping download.")
        return file_path
    else:
        # Make the request
        print(f"Downloading '{filename}' to '{directory}'...")
        response = requests.get(url, stream=True)

        # Get the total file size
        total_size = int(response.headers.get('content-length', 0))
        # Open the file and use tqdm for the progress bar
        with file_path.open('wb') as file, tqdm(
            desc='Downloading...',
            total=total_size,
            unit='iB',
            unit_scale=True,
            unit_divisor=1024,
        ) as progress_bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                progress_bar.update(size)
        print(f"Successfully downloaded '{filename}'.\n")
        return file_path  # Return the file path after successful download


# Extract
def extract_zip_file(file_path, extract_filename, cache_dir):
    """ Helper function - Extract ZIP shapefiles """
    extract_path = cache_dir / extract_filename

    # Check if the file is a valid ZIP archive
    if not zipfile.is_zipfile(file_path):
        print(f"The file '{file_path}' is not a valid ZIP archive. Cannot extract.")
        return None

    # Check if extraction folder already exists
    if extract_path.exists():
        print(f"Extraction folder '{extract_filename}' already exists. Skipping extraction.\n")
        return extract_path
    else:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Extract the ZIP file
            extract_path.mkdir(exist_ok=True)  # Create the extraction folder if it doesn't exist
            print(f"Extracting '{file_path.name}' to '{extract_path}'...")
            
            # Get the total number of files in the ZIP
            total_files = len(zip_ref.infolist())
            # Use tqdm for the extraction progress bar
            for file in tqdm(zip_ref.infolist(), desc="Extracting", total=total_files):
                zip_ref.extract(file, extract_path)
        
        print(f"Successfully extracted '{file_path.name}'.\n")
        return extract_path

def find_shapefile(extract_path):
    """ Helper function - Locate .shp in extracted shapefile folder """
    shapefiles = list(extract_path.rglob("*.shp"))
    if not shapefiles:
        raise FileNotFoundError(f"Shapefile was not found in {extract_path}")
    else:
        return shapefiles[0]  # Return the first shapefile
    
def find_csv(extract_path):
    """ Helper function - Locate EXCEL Sheets in extracted census data folder """
    all_files = list(extract_path.rglob("*"))
    csv_files = [f for f in all_files if '-data' in f.stem.lower() and f.suffix.lower() == '.csv']
    
    if not csv_files:
        raise FileNotFoundError(f"CSV file with '-data' in its name was not found in {extract_path}")
    else:
        return csv_files[0]  # Return the first excel sheet meeting the criteria