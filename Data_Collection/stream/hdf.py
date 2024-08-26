import h5py
import numpy as np

# Open the HDF5 file
with h5py.File('hdf5_example.hdf5', 'r') as hdf:
    # List all groups in the file
    print("Keys in the file:", list(hdf.keys()))
    
    # Access the group 't0'
    group_t0 = hdf['t0']
    
    # List all datasets in the group 't0'
    print("Keys in group 't0':", list(group_t0.keys()))
    
    # Access the dataset 'channel0' within the group 't0'
    dataset_channel0 = group_t0['channel0']
    
    # Convert the dataset to a NumPy array
    np_array = np.array(dataset_channel0)
    
    print("Data as NumPy array:", np_array)
