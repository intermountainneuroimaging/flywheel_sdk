import warnings
warnings.filterwarnings("ignore")

import xml.etree.ElementTree as ET 
import nilearn.datasets, nilearn.image
from nibabel.affines import apply_affine
import pandas as pd
import numpy as np
import os
import sys

import numpy as np

import time

start_time = time.perf_counter()

def flatten_3d_with_position(array_3d):
    """
    Flattens a 3D array into a 2D array, retaining original position information.

    Args:
        array_3d (numpy.ndarray): A 3D NumPy array.

    Returns:
        numpy.ndarray: A 2D array where each row contains (original indices (z, y, x), value).
    """
    z_dim, y_dim, x_dim = array_3d.shape
    position = []
    values = []
    for z in range(z_dim):
        for y in range(y_dim):
            for x in range(x_dim):
                if array_3d[z, y, x] != 0:
                    mm = apply_affine(atlas.affine, [z, y, x]).astype(int)
                    position.append(mm)
                    values.append(array_3d[z, y, x])
                    
    position = np.array(position, dtype=int)
    values = np.array(values, dtype=int)
    return position, values


def write_labels(atlas,tree, ind_offset,filename):
    fdata = atlas.get_fdata()
    positions, values = flatten_3d_with_position(fdata)
    labels = values.tolist()

    all_labels = []
    all_positions = np.empty((0,3), dtype=int)

    for idx,elem in enumerate(tree.findall('.//data/label')):
        elem = tree.find('.//data/label[@index="'+str(idx)+'"]')

        # note - indexing starts at zero but maxprob atlas counter starts at 1
        new_list = [elem.text] * np.sum(values == idx+ind_offset)
        new_position = positions[values == idx+ind_offset, :]

        all_labels.extend(new_list)
        all_positions = np.vstack((all_positions, new_position))
        print(f"{idx+1}: {elem.text}")

    with open(filename,"w") as file:
        for i, pos in enumerate(all_positions):
            file.write(f"{pos[0]} {pos[1]} {pos[2]} {str(all_labels[i])} \n")

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Elapsed time: {elapsed_time} seconds")
    
# atlas=nilearn.image.load_img(os.environ["FSLDIR"]+'/data/atlases/HarvardOxford/HarvardOxford-cort-maxprob-thr25-1mm.nii.gz')
# tree = ET.parse(os.environ["FSLDIR"]+'/data/atlases/HarvardOxford-Cortical.xml')
# write_labels(atlas,tree, 1, "HarvardOxford-Cortical.txt")

# atlas=nilearn.image.load_img(os.environ["FSLDIR"]+'/data/atlases/HarvardOxford/HarvardOxford-sub-maxprob-thr25-1mm.nii.gz')
# tree = ET.parse(os.environ["FSLDIR"]+'/data/atlases/HarvardOxford-Subcortical.xml')
# write_labels(atlas,tree, 1, "HarvardOxford-Subortical.txt")

atlas=nilearn.image.load_img(os.environ["FSLDIR"]+'/data/atlases/Talairach/Talairach-labels-1mm.nii.gz')
tree = ET.parse(os.environ["FSLDIR"]+'/data/atlases/Talairach.xml')
write_labels(atlas,tree, 0, "Talairach.txt")

# use this method to find labels from output file...
#grep -e "^$x,$y,$z" my_file.txt | cut -d" " -f2-
