# download_extract.py

from config import ZIP_URLS
import requests
import zipfile
from tqdm import tqdm
from helper import LAYER_CACHE_DIR, zip_filenames, extracted_names

# ========================
# DOWNLOAD AND EXTRACT ZIP
# ========================

def download_and_extract_all():
    """ Main function - download and extract all """
    shapefile_paths = {}
    for i in range(1, len(ZIP_URLS) +1):
        url = ZIP_URLS[i -1]
        filename = zip_filenames[i]
        extracted_name = extracted_names[i]

        # Download
        file_path = download_file(url, filename)
        if not file_path:
            continue  # Skip if download failed

        # Extract
        extract_path = extract_file(file_path, extracted_name)
        if not extract_path:
            continue  # Skip if extraction failed

        # Find the shapefile name
        shapefile_path = find_shapefile(extract_path)
        if shapefile_path:
            shapefile_paths[i] = shapefile_path
        else:
            print(f"No shapefile found in '{filename}'.")

    return shapefile_paths

def download_file(url, filename, cache_dir=LAYER_CACHE_DIR):
    """ Helper function - Download ZIP shapefiles from hyperlink URL's in config.py """
    file_path = cache_dir / filename

    # Check if ZIP file already exists
    if file_path.exists():
        print(f"ZIP file '{filename}' already exists. Skipping download.")
        return file_path
    else:
        # Make the request
        print(f"Downloading '{filename}' to '{cache_dir}'...")
        response = requests.get(url, stream=True)

        # Check if the request was successful
        if response.status_code == 200:
            content_type = response.headers.get('Content-Type', '')
            if 'application/zip' not in content_type and 'application/octet-stream' not in content_type:
                print(f"Unexpected Content-Type: {content_type}. The downloaded file may not be a ZIP archive.")
                return None

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
        else:
            print(f"Failed to download '{filename}'. Status code: {response.status_code}")
            return None

# Extract
def extract_file(file_path, extracted_name, cache_dir=LAYER_CACHE_DIR):
    """ Helper function - Extract ZIP shapefiles """
    extract_path = cache_dir / extracted_name

    # Check if the file is a valid ZIP archive
    if not zipfile.is_zipfile(file_path):
        print(f"The file '{file_path}' is not a valid ZIP archive. Cannot extract.")
        return None

    # Check if extraction folder already exists
    if extract_path.exists():
        print(f"Extraction folder '{extracted_name}' already exists. Skipping extraction.\n")
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

# Helper function to find shapefile in extracted folder
def find_shapefile(extract_path):
    """ Helper function - Locate .shp in extracted shapefile folder """
    shapefiles = list(extract_path.rglob("*.shp"))
    if shapefiles:
        return shapefiles[0]  # Return the first shapefile found