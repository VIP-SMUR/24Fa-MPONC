import pickle
from helper import SAVED_IDS_FILE
from pathlib import Path
#saved_IDS.pyg

def save_current_IDS(id_list, file_path=SAVED_IDS_FILE):
    """ Save current ID's to cache """
    with open(file_path, 'wb') as file:
        pickle.dump(id_list, file)
    print(f"Current ID's saved.\n")

def load_previous_IDS(file_path=SAVED_IDS_FILE):
    """ Load previous ID's from cache """
    if Path(file_path).exists(): # If exists
        with open(file_path, 'rb') as f:
            saved_IDS = pickle.load(f)
    else: # Initialize empty array
        saved_IDS = []
    return saved_IDS