import time
import numpy as np
import river, uuid
from datetime import datetime
import h5py
import matplotlib.pyplot as plt
import cv2 

# REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
# REDIS_PORT = 11423
# REDIS_PASSWORD = 'Test@123'
REDIS_HOSTNAME = 'localhost'
REDIS_PORT = 6379



class RiverStreamWriter(object):
    """
    Implementation that writes a stream of data via River, a C++ library that uses Redis under the hood.
    """
    writer: river.StreamWriter

    def __init__(self, stream_name: str, sampling_rate: float, redis_connection: river.RedisConnection = None):
        self._stream_start = None
        self._streamName = stream_name
        self._samplingRate = sampling_rate
        self._schema = None
        self._writer = None  # We start as None and define it when we initialize the writer given the Redis connection
        self._written_data = []  # List to accumulate written data
        self._time_durations = []  # List to accumulate time taken for each record
        if redis_connection is not None:
            self._redis_connection = redis_connection
        else:
            self._redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT)

    def initialize(self):
        self._stream_start = datetime.now()
        print(f"Stream start time: {self._stream_start}")
        schema_fields = [
            ('deltatime', 'float'),
            ('neuron', 'int32'),
            ('stim_index', 'int'),
            ('next', 'float'),
            ('neuron2', 'int32'),
            ('stim_index2', 'int'),
            ('next2', 'float'),
            ('neuron3', 'float'),
            ('stim_index3', 'int'),
            ('next3', 'float'),
            ('neuron4', 'float'),
            ('stim_index4', 'float'),
            ('next4', 'float'),
            ('hdf5_data', 'float')  
        ]
        dt = np.dtype(schema_fields)
        self._writer = river.StreamWriter(self._redis_connection)
        try:
            self._writer.initialize(self._streamName, river.StreamSchema.from_dtype(dt))
        except river.StreamExistsException:
            print(f"Stream {self._streamName} already exists. Using the existing stream.")
            # Fetch the schema from the existing stream
            schema = self._writer.get_schema(self._streamName)
            self._writer = river.StreamWriter(self._redis_connection)
            self._writer.initialize(self._streamName, schema)

    def write(self, data: np.ndarray):
        start_time = time.perf_counter()  # Start time before writing the record
        current_time = datetime.now()
        deltatime = (current_time - self._stream_start).total_seconds()
        data['deltatime'] = deltatime
        self._writer.write(data)
        end_time = time.perf_counter()  # End time after writing the record
        
        # Record the time taken for this specific record
        time_taken = end_time - start_time
        self._time_durations.append(time_taken)
        
        self._written_data.append(data.copy())
        print(f"Data written: {data}")
        print(f"Time taken for this record: {time_taken:.6f} seconds")
        print(f"Number of records written: {len(self._written_data)}")

    def stop(self):
        self._writer.stop()

    def print_all_data(self):
        if self._written_data:
            all_data = np.concatenate(self._written_data)
            print("All data written to stream:")
            print(all_data)
        else:
            print("No data has been written to the stream yet.")

    def write_multiple_records(self, num_records: int):
        for _ in range(num_records):
            data_to_write = self._writer.new_buffer(1)
            data_to_write['neuron'] = np.random.randint(1, 100, size=1)
            data_to_write['stim_index'] = np.array([32])
            data_to_write['next'] = np.array([0.67])
            data_to_write['neuron2'] = np.random.randint(1, 100, size=1)
            data_to_write['stim_index2'] = np.array([22])
            data_to_write['next2'] = np.array([0.71])
            data_to_write['neuron3'] = np.random.randint(1, 100, size=1)
            data_to_write['stim_index3'] = np.array([21])
            data_to_write['next3'] = np.array([0.29])
            data_to_write['neuron4'] = np.random.randint(1, 100, size=1)
            data_to_write['stim_index4'] = np.array([28])
            data_to_write['next4'] = np.array([0.98])
            self.write(data_to_write)

    def plot_time_vs_records(self):
        plt.plot(range(1, len(self._time_durations) + 1), self._time_durations, marker='o')
        plt.title("Time taken to write each record vs. Number of records")
        plt.xlabel("Number of Records")
        plt.ylabel("Time taken (seconds)")
        plt.show()

def read_hdf5_file(file_path):
    with h5py.File(file_path, 'r') as hdf:
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
    return np_array

def main():
    stream_name = None
    writer = None
    while True:
        choice = input("Enter 'n' to create a new stream, or 'q' to quit: ").strip().lower()
        if choice == 'n':
            stream_name = str(uuid.uuid4())  # Generate a unique stream name
            writer = RiverStreamWriter(stream_name, sampling_rate=1.0)
            writer.initialize()
            print(f"New stream created with name: {stream_name}")
        elif choice == 'q':
            print("Quitting the program.")
            break
        else:
            print("Invalid choice. Please try again.")
            continue

        while True:
            data_choice = input("Enter 'w' to write data, 'a' to write multiple records, 'h' to write HDF5 data, 'c' to close stream, 'p' to print all data, 'plot' to plot graph, or 'm' to go back to main menu: ").strip().lower()
            if data_choice == 'w':
                data_to_write = writer._writer.new_buffer(1)
                data_to_write['neuron'] = np.random.randint(1, 100, size=1)
                data_to_write['stim_index'] = np.array([32])
                data_to_write['next'] = np.array([0.67])
                data_to_write['neuron2'] = np.random.randint(1, 100, size=1)
                data_to_write['stim_index2'] = np.array([22])
                data_to_write['next2'] = np.array([0.71])
                data_to_write['neuron3'] = np.random.randint(1, 100, size=1)
                data_to_write['stim_index3'] = np.array([21])
                data_to_write['next3'] = np.array([0.29])
                data_to_write['neuron4'] = np.random.randint(1, 100, size=1)
                data_to_write['stim_index4'] = np.array([28])
                data_to_write['next4'] = np.array([0.98])
                writer.write(data_to_write)
                print("Data written to stream.")
            elif data_choice == 'a':
                if writer:
                    num_records = int(input("Enter the number of records to write automatically: ").strip())
                    writer.write_multiple_records(num_records)
                else:
                    print("Stream is not initialized. Please create a new stream first by choosing 'n'.")
            elif data_choice == 'h':
                if writer:
                    file_path = input("Enter the path to the HDF5 file: ").strip()
                    hdf5_data = read_hdf5_file(file_path)
                    
                    # Assuming hdf5_data is a NumPy array
                    for record in hdf5_data:
                        data_to_write['hdf5_data'] = record  # Add the HDF5 data as another field
                        writer.write(data_to_write)
                    print("HDF5 data written to stream.")
                else:
                    print("Stream is not initialized. Please create a new stream first by choosing 'n'.")
            elif data_choice == 'c':
                if writer:
                    writer.stop()
                    print(f"Stream {stream_name} closed.")
                break
            elif data_choice == 'p':
                if writer:
                    writer.print_all_data()
            elif data_choice == 'plot':
                if writer:
                    writer.plot_time_vs_records()
            elif data_choice == 'm':
                break
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()

# import redis
# import numpy as np
# import river
# from datetime import datetime
# import uuid

# # Redis connection details
# REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
# REDIS_PORT = 11423
# REDIS_PASSWORD = 'Test@123'

# class RiverStreamWriter:
#     """
#     Implementation that writes a stream of data via River, using Redis under the hood.
#     """

#     def __init__(self, stream_name: str, redis_connection: river.RedisConnection = None):
#         self._stream_name = stream_name
#         self._writer = None
#         self._redis_connection = redis_connection or river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD)

#     def initialize(self):
#         """Initialize the stream and its schema."""
#         schema_fields = [
#             ('deltatime', 'float'),
#             ('neuron', 'int32'),
#             ('stim_index', 'int'),
#             ('next', 'float'),
#             ('neuron2', 'int32'),
#             ('stim_index2', 'int'),
#             ('next2', 'float'),
#             ('neuron3', 'float'),
#             ('stim_index3', 'int'),
#             ('next3', 'float'),
#             ('neuron4', 'float'),
#             ('stim_index4', 'float'),
#             ('next4', 'float'),
#             ('hdf5_data', 'float')
#         ]
#         dt = np.dtype(schema_fields)

#         self._writer = river.StreamWriter(self._redis_connection)

#         try:
#             self._writer.initialize(self._stream_name, river.StreamSchema.from_dtype(dt))
#             print(f"Stream '{self._stream_name}' initialized successfully.")
#         except river.StreamExistsException:
#             print(f"Stream '{self._stream_name}' already exists. Using the existing stream.")

#     def stop(self):
#         """Stop and cleanup the stream."""
#         if self._writer:
#             self._writer.stop()
#             print(f"Stream '{self._stream_name}' closed.")

# def main():
#     while True:
#         choice = input("Enter 'n' to create a new stream, or 'q' to quit: ").strip().lower()
#         if choice == 'n':
#             stream_name = str(uuid.uuid4())  # Generate a unique stream name
#             writer = RiverStreamWriter(stream_name)
#             writer.initialize()
#         elif choice == 'q':
#             print("Quitting the program.")
#             break
#         else:
#             print("Invalid choice. Please try again.")

# if __name__ == "__main__":
#     main()



