# gif.py

from config import N_JOBS
from PIL import Image
import os
from collections import defaultdict
import fitz
from joblib import Parallel, delayed

# Convert pdfs to images
def pdf_to_images(pdf_path):
    """Converts a PDF to a list of PIL Image objects."""
    doc = fitz.open(pdf_path)
    images = []
    for page_num in range(doc.page_count):
        page = doc[page_num]
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def images_to_gif(images, output_path, duration, num_pause_frames):
    """Creates a GIF from a list of PIL Image objects."""

    pause_frame = images[-1].copy()
    images = images + [pause_frame] * num_pause_frames
    
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        optimize=False,
        duration=duration,
        loop=0,
    )

# Create correct GIF's based on file names
def create_gif(key, file_tuples, duration, num_pause_frames, output_directory):
    # Sort by NUM
    file_tuples.sort()
    pdf_files = [filepath for _, filepath in file_tuples]
    all_images = []
    for pdf_file in pdf_files:
        images = pdf_to_images(pdf_file)
        all_images.extend(images)

    if all_images:
        # Add back prefix
        example_filename = os.path.basename(pdf_files[0])
        prefix = "_".join(example_filename.split("_")[:-5])
        
        output_gif = os.path.join(output_directory, f"{prefix}_{'_'.join(key)}.gif")
        images_to_gif(all_images, output_gif, duration=duration, num_pause_frames=num_pause_frames)
        print(f"Created GIF: {output_gif}")
    else:
        print(f"No images found for group: {key}")
        
# Multiprocessing based on image groupings
def process_pdfs_to_gifs(pdf_directory, output_directory, duration, num_pause_frames):
    """Processes all PDFs in a directory, groups by filename pattern, and creates GIFs."""
    # Dictionary to group files
    groups = defaultdict(list)
    for filename in os.listdir(pdf_directory):
        if filename.endswith(".pdf"):
            parts = filename.replace(".pdf", "").split("_")
            X, Y, Z, NUM = parts[-5:-1]
            key = (X, Y, Z)
            groups[key].append((int(NUM), os.path.join(pdf_directory, filename)))
    
    Parallel(n_jobs=N_JOBS, backend='loky')(
            delayed(create_gif)(
                key, file_tuples, duration, num_pause_frames, output_directory
            )
            for key, file_tuples in groups.items()
        )