# JPEG/PNG/BMP 
# MP4/AVI/MKV



# import cv2
# import numpy as np

# # Open a connection to the camera
# cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         break
#     # Convert the frame to a NumPy array
#     np_array = np.array(frame)
#     print(np_array)

#     # Display the frame (optional)
#     cv2.imshow('Frame', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()



#convert to hdf5



# import cv2
# import h5py
# import numpy as np

# # Open a connection to the camera
# cap = cv2.VideoCapture(0)  # Use 0 for the default camera

# # Create an HDF5 file
# hdf5_file = h5py.File('camera_data.h5', 'w')

# # Define a dataset for the images
# num_images = 10  # Number of images to capture
# frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))

# # Dataset to store images, here we assume 3 channels (RGB)
# dataset = hdf5_file.create_dataset('images', (num_images, frame_height, frame_width, 3), dtype='uint8')

# # Capture images and save to HDF5 file
# for i in range(num_images):
#     ret, frame = cap.read()
#     if not ret:
#         break
#     # Convert the frame to a NumPy array and store it in the HDF5 dataset
#     dataset[i, ...] = frame

#     # Display the frame (optional)
#     cv2.imshow('Frame', frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Release the camera and close all OpenCV windows
# cap.release()
# cv2.destroyAllWindows()

# # Close the HDF5 file
# hdf5_file.close()
