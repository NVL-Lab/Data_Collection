


# REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
# REDIS_PORT = 11423
# REDIS_PASSWORD = 'Test@123'
REDIS_HOSTNAME = 'localhost'
REDIS_PORT = 6379

import os
import collections
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import river

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
            self._redis_connection = river.RedisConnection("localhost", 6379)

    def initialize(self):
        self._reader = river.StreamReader(self._redis_connection)
        self._reader.initialize(self._streamName, 1000)  # Buffer size of 1000

    def read(self, data: np.ndarray):
        return self._reader.read(data, 1)

    def stop(self):
        self._reader.stop()

def save_to_parquet(data_dict, file_counter):
    output_dir = 'parquet_files'
    os.makedirs(output_dir, exist_ok=True)  # Create the directory if it doesn't exist
    filename = os.path.join(output_dir, f'data_chunk_{file_counter}.parquet')

    df = pd.DataFrame(data_dict)
    df.to_parquet(filename, index=False)
    print(f'Saved {filename}')

def main():
    stream_name = input("Enter the stream name to read from: ").strip()
    reader = RiverStreamReader(stream_name)
    reader.initialize()

    batch_size = 250  # Process this many records per batch
    buffer_size = 300  # Total buffer size to maintain

    data = reader._reader.new_buffer(1)
    file_counter = 1
    ret = collections.defaultdict(list)

    try:
        while True:
            read_choice = input("Enter 'r' to read data, 'c' to close stream, or 'q' to quit: ").strip().lower()
            if read_choice == 'r':
                while True:
                    num_read = reader.read(data)
                    if num_read > 0:
                        # Convert buffer data to dictionary format
                        data_dict = {field: data[field].tolist() for field in data.dtype.names}

                        # Extend the buffer
                        for key, value in data_dict.items():
                            ret[key].extend(value)

                        # Check if we have enough data for a batch
                        if len(ret[list(ret.keys())[0]]) >= batch_size:
                            # Save only the first batch_size records
                            batch_to_save = {key: ret[key][:batch_size] for key in ret.keys()}
                            save_to_parquet(batch_to_save, file_counter)

                            # Remove saved records from the buffer
                            for key in ret.keys():
                                ret[key] = ret[key][batch_size:]

                            file_counter += 1

                    elif num_read == 0:
                        print("Timeout occurred. No new data to read.")
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
        # Save any remaining data in the buffer
        if ret and len(ret[list(ret.keys())[0]]) > 0:
            save_to_parquet(ret, file_counter)

        reader.stop()  # Ensure the stream is stopped

if __name__ == "__main__":
    main()


