# import cv2
# import time
# import uuid
# import numpy as np
# import matplotlib.pyplot as plt
# from datetime import datetime
# import river  # Assume this is the River library you're using
# import collections

# REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
# REDIS_PORT = 11423
# REDIS_PASSWORD = 'Test@123'
# class RiverStreamWriter(object):
#     """
#     Implementation that writes a stream of data via River, a C++ library that uses Redis under the hood.
#     """
#     writer: river.StreamWriter

#     def __init__(self, stream_name: str, sampling_rate: float, redis_connection: river.RedisConnection = None):
#         self._stream_start = None
#         self._streamName = stream_name
#         self._samplingRate = sampling_rate
#         self._schema = None
#         self._writer = None
#         self._written_data = []
#         self._time_durations = []
#         if redis_connection is not None:
#             self._redis_connection = redis_connection
#         else:
#             self._redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD)

#     def initialize(self):
#         self._stream_start = datetime.now()
#         print(f"Stream start time: {self._stream_start}")
#         schema_fields = [
#             ('frame_index', 'int32'),
#             ('timestamp', 'float')
#         ]
#         dt = np.dtype(schema_fields)
#         self._writer = river.StreamWriter(self._redis_connection)
#         try:
#             self._writer.initialize(self._streamName, river.StreamSchema.from_dtype(dt))
#         except river.StreamExistsException:
#             print(f"Stream {self._streamName} already exists. Using the existing stream.")
#             schema = self._writer.get_schema(self._streamName)
#             self._writer = river.StreamWriter(self._redis_connection)
#             self._writer.initialize(self._streamName, schema)

#     def write_frame_info(self, frame_index: int, timestamp: float):
#         start_time = time.perf_counter()
#         data_to_write = self._writer.new_buffer(1)
#         data_to_write['frame_index'] = frame_index
#         data_to_write['timestamp'] = timestamp
#         self._writer.write(data_to_write)
#         end_time = time.perf_counter()

#         time_taken = end_time - start_time
#         self._time_durations.append(time_taken)
        
#         self._written_data.append(data_to_write.copy())
#         print(f"Frame {frame_index} at {timestamp:.6f}s written to stream.")
#         print(f"Time taken: {time_taken:.6f} seconds")

#     def stop(self):
#         self._writer.stop()

#     def plot_time_vs_records(self):
#         plt.plot(range(1, len(self._time_durations) + 1), self._time_durations, marker='o')
#         plt.title("Time taken to write each record vs. Number of records")
#         plt.xlabel("Number of Records")
#         plt.ylabel("Time taken (seconds)")
#         plt.show()

# def process_video(video_path: str, writer: RiverStreamWriter):
#     cap = cv2.VideoCapture(video_path)
#     if not cap.isOpened():
#         print("Error opening video file")
#         return
    
#     frame_index = 0
#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             break
        
#         timestamp = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0
#         writer.write_frame_info(frame_index, timestamp)
        
#         frame_index += 1
    
#     cap.release()

# def main():
#     stream_name = None
#     writer = None
#     while True:
#         choice = input("Enter 'n' to create a new stream, or 'q' to quit: ").strip().lower()
#         if choice == 'n':
#             stream_name = str(uuid.uuid4())
#             writer = RiverStreamWriter(stream_name, sampling_rate=1.0)
#             writer.initialize()
#             print(f"New stream created with name: {stream_name}")
#         elif choice == 'q':
#             print("Quitting the program.")
#             break
#         else:
#             print("Invalid choice. Please try again.")
#             continue

#         while True:
#             data_choice = input("Enter 'v' for video processing, 'c' to close stream, 'plot' to plot graph, or 'm' to go back to main menu: ").strip().lower()
#             if data_choice == 'v':
#                 if writer:
#                     video_path = input("Enter the path to the video file: ").strip()
#                     process_video(video_path, writer)
#                 else:
#                     print("Stream is not initialized. Please create a new stream first by choosing 'n'.")
#             elif data_choice == 'c':
#                 if writer:
#                     writer.stop()
#                     print(f"Stream {stream_name} closed.")
#                 break
#             elif data_choice == 'plot':
#                 if writer:
#                     writer.plot_time_vs_records()
#             elif data_choice == 'm':
#                 break
#             else:
#                 print("Invalid choice. Please try again.")

# if __name__ == "__main__":
#     main()


import cv2

def get_frame_from_index(video_path, frame_index):
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error opening video file")
        return None
    
    # Set the frame position to the desired frame index
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    
    # Read the frame at the current position
    ret, frame = cap.read()
    
    cap.release()
    
    if ret:
        return frame
    else:
        print("Failed to retrieve the frame at index", frame_index)
        return None

# Example usage
video_path = "/Users/rishiteshganesham/Desktop/work/nvl_new/Data_Collection/stream/big_buck_bunny_720p_1mb.mp4"
frame_index = 10  # Example frame index
frame = get_frame_from_index(video_path, frame_index)

if frame is not None:
    # Display the frame
    cv2.imshow(f"Frame at index {frame_index}", frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
