import os
import cv2
import numpy as np
import h5py

# Define paths
base_dir = r'C:\Users\Anukul\Downloads\archive\Images\Images'  # Path to your raw images
hdf5_path = 'C:/Users/Anukul/Documents/fyp/Assets/devanagari_dataset.h5'  # Path to save HDF5 file

# Image size and channels
image_size = (32, 32)
channels = 1  # For grayscale images

def save_to_hdf5(base_dir, hdf5_path):
    """Save images and labels to an HDF5 file."""
    images = []
    labels = []
    
    # Iterate over each class folder
    for class_idx, class_folder in enumerate(os.listdir(base_dir)):
        class_path = os.path.join(base_dir, class_folder)
        if os.path.isdir(class_path):
            # Iterate over each image file in the class folder
            for img_file in os.listdir(class_path):
                img_path = os.path.join(class_path, img_file)
                img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)  # Read image in grayscale
                img = cv2.resize(img, image_size)  # Resize image
                images.append(img)
                labels.append(class_idx)  # Use folder index as label

    # Convert lists to arrays
    images = np.array(images, dtype=np.uint8)
    labels = np.array(labels, dtype=np.int64)

    # Save data to HDF5
    with h5py.File(hdf5_path, 'w') as h5f:
        h5f.create_dataset('images', data=images, compression="gzip")
        h5f.create_dataset('labels', data=labels, compression="gzip")
    
    print(f"HDF5 file created at {hdf5_path}")

# Run the function
save_to_hdf5(base_dir, hdf5_path)
