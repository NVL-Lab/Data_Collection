import cv2
import numpy as np
import os
import time
from datetime import datetime
import uuid
from StreamWriter import RiverStreamWriter  
import json
import os



class CameraStream:
    def __init__(self, stream_name: str):
        self._stream_name = stream_name
        self._stream_writer = RiverStreamWriter(stream_name)

    def initialize(self):
        schema_fields = [
            ('frame_index', 'float'),
            ('timestamp', 'float'),
        ]
        schema = np.dtype(schema_fields)
        self._stream_writer.initialize(schema)

    def write_frame_info(self, frame_index: int, timestamp: float):
        """
        Write frame information to the Redis stream.
        """
        data = np.array([(frame_index, timestamp)], dtype=[
            ('frame_index', 'float'),
            ('timestamp', 'float'),
        ])
        self._stream_writer.write(data)




def main():
    stream_name = None
    writer = None

    # choice = input("Enter 'n' to create a new stream, or 'q' to quit: ").strip().lower()
    # if choice == 'n':
    stream_name = str(uuid.uuid4())  # Generate a unique stream name
    writer = CameraStream(stream_name)
    writer.initialize()
    print(f"New stream created with name: {stream_name}")
    
    # while True:
    #             if writer:
    #                 capture_and_save_video(writer)
    #             user_input = input("Do you want to continue streaming? (y/n): ")
    #             if user_input.lower() != 'y':
    #                 break
    if writer:
                    capture_and_save_video(writer)


# Create a folder to store the videos and NumPy arrays
output_folder = 'video_output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def get_next_video_number():
    """Get the next available video number based on existing files in the output folder."""
    existing_files = os.listdir(output_folder)
    video_files = [f for f in existing_files if f.startswith('out') and f.endswith('.mp4')]

    if not video_files:
        return 1  # Start with 1 if no files exist

    # Extract numbers from filenames and return the next number
    numbers = [int(f[len('out'):-len('.mp4')]) for f in video_files]
    return max(numbers) + 1

def capture_and_save_video(writer: CameraStream):
    video_number = get_next_video_number()

    # Initialize video capture for an external camera 
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open external camera.")
        return

    start_time = time.time()
    # Define the codec and create VideoWriter object to save the video in MP4 format
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for .mp4
    video_filename = os.path.join(output_folder, f'out{video_number}.mp4')
    output = cv2.VideoWriter(video_filename, fourcc, 30.0, (640, 480))  # Adjust frame rate & resolution if needed

    # List to store frames as NumPy arrays
    frames = []

    print(f"Recording video {video_number}. Press 'q' to stop.")

    frame_index = 0

    while True:
        ret, frame = cap.read()  # Read a frame from the camera

        if not ret:
            print(f"Failed to capture frame for video {video_number}.")
            break

        now = datetime.now()
        timestamp = now.timestamp()
        writer.write_frame_info(frame_index, timestamp)

        frames.append(np.array(frame))

        # Write the frame to the output video file
        output.write(frame)

        # Display the frame in a window
        cv2.imshow(f'Video {video_number}', frame)

        # Check if the user pressed the 'q' key to stop recording
        if cv2.waitKey(1) & 0xFF == ord('q'):
            print(f"Stopping recording for video {video_number}.")
            break

        frame_index += 1

    # Release everything
    cap.release()
    output.release()
    cv2.destroyAllWindows()

    # Convert list of frames to a NumPy array
    frames_np = np.array(frames)

    # Save the NumPy array with a unique filename
    numpy_filename = os.path.join(output_folder, f'np{video_number}.npy')
    np.save(numpy_filename, frames_np)

    # Print confirmation and total frames captured
    print(f"Saved video as {video_filename}")
    print(f"Saved corresponding NumPy array as {numpy_filename}")
    print(f"Total frames captured: {frame_index}")



if __name__ == "__main__":
    main()
