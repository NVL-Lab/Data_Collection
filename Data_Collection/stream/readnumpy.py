import numpy as np
import cv2

# Path to the NumPy file
numpy_file_path = '/Users/rishiteshganesham/Desktop/work/nvl_new/video_output/np30.npy'  # Change the filename to your specific file

# Load the NumPy array from the file
frames = np.load(numpy_file_path)

# Get the total number of frames
total_frames = frames.shape[0]
print(f"Total frames: {total_frames}")

# Function to display a specific frame by frame number
def show_frame(frame_number):
    if frame_number < 0 or frame_number >= total_frames:
        print(f"Frame number {frame_number} is out of bounds.")
        return
    
    frame = frames[frame_number]  # Access the frame by index
    print(f"Displaying frame {frame_number}")

    # Display the frame using OpenCV
    cv2.imshow(f"Frame {frame_number}", frame)
    
    # Wait for a key press to close the window
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Example: Show the 10th frame (frame number 9)
frame_number = 88  # Change to the frame number you want
show_frame(frame_number)
