import h5py
import matplotlib.pyplot as plt
import numpy as np
import math

# Load the HDF5 dataset
file_path = 'C:/Users/Anukul/Documents/fyp/Assets/devanagari_dataset.h5'
with h5py.File(file_path, 'r') as hf:
    images = hf['images'][:]   # Load all images
    labels = hf['labels'][:]   # Load all labels

# Get unique classes (labels)
unique_classes = np.unique(labels)

# Calculate grid size
num_classes = len(unique_classes)
grid_size = math.ceil(math.sqrt(num_classes))  # Square root for balanced rows and columns

# Display a sample image for each class
plt.figure(figsize=(grid_size * 2, grid_size * 2))  # Adjust figure size for clarity
for idx, label in enumerate(unique_classes):
    # Get the first image with the current label
    image_index = np.where(labels == label)[0][0]
    image = images[image_index]

    # Plot the image
    plt.subplot(grid_size, grid_size, idx + 1)
    plt.imshow(image, cmap='gray')
    plt.title(f"Class {label}")
    plt.axis('off')

plt.suptitle("Sample Images for Each Class")
plt.show()
