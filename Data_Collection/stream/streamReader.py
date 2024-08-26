__author__ = 'Dulce'


REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
REDIS_PORT = 11423
REDIS_PASSWORD = 'Test@123'


import collections
import os
import pandas as pd
import river
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

#time taken for each record

class RiverStreamReader(object):
    """
    Implementation that reads a stream of data via River, a C++ library that uses Redis under the hood.
    """
    reader: river.StreamReader

    def __init__(self, stream_name: str, redis_connection: river.RedisConnection = None):
        self._streamName = stream_name
        self._reader = None
        if redis_connection is not None:
            self._redis_connection = redis_connection
        else:
            self._redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD)

    def initialize(self):
        self._reader = river.StreamReader(self._redis_connection)
        self._reader.initialize(self._streamName, 1000)

    def read(self, data: np.ndarray):
        return self._reader.read(data, 1)

    def stop(self):
        self._reader.stop()

def save_to_parquet(data_dict, file_counter, limit):
    output_dir = 'parquet_files'
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    filename = os.path.join(output_dir, f'data_chunk_{file_counter}.parquet')

    if os.path.exists(filename):
        existing_df = pd.read_parquet(filename)
        new_df = pd.DataFrame(data_dict)
        combined_df = pd.concat([existing_df, new_df], ignore_index=True)

        if len(combined_df) > limit:
            # Save existing data and start a new file with only the new data
            existing_df.to_parquet(filename, index=False)
            print(f'Appended and saved to {filename}')
            
            file_counter += 1
            new_filename = os.path.join(output_dir, f'data_chunk_{file_counter}.parquet')
            new_df.to_parquet(new_filename, index=False)
            print(f'Created new file {new_filename} as limit exceeded')
            return file_counter, len(new_df)
        else:
            combined_df.to_parquet(filename, index=False)
            print(f'Appended and saved to {filename}')
            return file_counter, len(combined_df)
    else:
        df = pd.DataFrame(data_dict)
        df.to_parquet(filename, index=False)
        print(f'Saved {filename}')
        return file_counter, len(df)

def plot_boxplot(time_dict):
    plt.boxplot([time_dict[limit] for limit in sorted(time_dict.keys())], labels=[str(limit) for limit in sorted(time_dict.keys())])
    plt.title("Boxplot of Time Taken per Record vs. Parquet File Limit")
    plt.xlabel("Parquet File Row Limit")
    plt.ylabel("Time Taken per Record (seconds)")
    plt.grid(True)
    plt.show()

def main():
    stream_name = input("Enter the stream name to read from: ").strip()
    reader = RiverStreamReader(stream_name)
    reader.initialize()
    
    limits = [10000]  # Limits to compare
    time_dict = {limit: [] for limit in limits}  # To store time taken for each limit

    data = reader._reader.new_buffer(1)
    file_counter = 1
    ret = collections.defaultdict(list)

    try:
        for limit in limits:
            print(f"Testing with limit: {limit}")
            while True:
                read_choice = input("Enter 'r' to read data, 'c' to close stream, or 'q' to quit: ").strip().lower()
                if read_choice == 'r':
                    while True:
                        start_read_time = datetime.now()
                        num_read = reader.read(data)
                        end_read_time = datetime.now()
                        read_duration = (end_read_time - start_read_time).total_seconds()

                        print(f"Time taken to read data: {read_duration} seconds")

                        if num_read > 0:
                            data_dict = {field: data[field].tolist() for field in data.dtype.names}
                            for key, value in data_dict.items():
                                ret[key].extend(value)
                            print(f"Data read from stream. Number of records read: {num_read}")

                            start_write_time = datetime.now()
                            file_counter, last_index = save_to_parquet(ret, file_counter, limit)
                            end_write_time = datetime.now()
                            write_duration = (end_write_time - start_write_time).total_seconds()
                            
                            # Calculate time per record
                            time_per_record = write_duration / num_read
                            print(f"Time taken to write data: {write_duration} seconds")
                            print(f"Time taken per record: {time_per_record} seconds")
                            
                            # Store time per record in the corresponding list for the current limit
                            time_dict[limit].append(time_per_record)

                            ret.clear()  # Clear ret after saving
                        elif num_read == 0:
                            print('Timeout occurred.')
                            break
                        else:
                            print(f'EOF encountered for stream {reader._streamName}')
                            break
                elif read_choice == 'c':
                    reader.stop()
                    print(f"Stream {stream_name} closed.")
                    break
                elif read_choice == 'q':
                    print("Quitting the program.")
                    break
                else:
                    print("Invalid choice. Please try again.")
                    
    finally:
        if ret and len(ret[list(ret.keys())[0]]) > 0:  # Save any remaining data
            start_write_time = datetime.now()
            file_counter, last_index = save_to_parquet(ret, file_counter, limit)
            end_write_time = datetime.now()
            write_duration = (end_write_time - start_write_time).total_seconds()
            
            # Calculate time per record for remaining data
            time_per_record = write_duration / len(ret[list(ret.keys())[0]])
            time_dict[limit].append(time_per_record)
            print(f"Time taken to write remaining data: {write_duration} seconds")
            print(f"Time taken per record: {time_per_record} seconds")

        reader.stop()  # Ensure the stream is stopped
        
        # Plot the boxplot
        plot_boxplot(time_dict)

if __name__ == "__main__":
    main()