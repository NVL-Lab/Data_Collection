import os
import pandas as pd
import river
import time

# Constants
REDIS_HOSTNAME = "localhost"
REDIS_PORT = 6379
BATCH_SIZE = 250
BUFFER_SIZE = 300
OUTPUT_DIR = "parquet_files"

# Helper Function to Save Data
def save_to_parquet(data_dict, file_counter):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filename = os.path.join(OUTPUT_DIR, f"data_chunk_{file_counter}.parquet")
    df = pd.DataFrame(data_dict)
    df.to_parquet(filename, index=False)
    print(f"Saved {len(df)} records to {filename}")
    return file_counter + 1

# Ingestor Class
class RiverIngestor:
    def __init__(self, stream_name, redis_connection=None):
        self.stream_name = stream_name
        self.file_counter = 1
        if redis_connection is None:
            self.redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT)
        else:
            self.redis_connection = redis_connection
        self.reader = river.StreamReader(self.redis_connection)
        self.reader.initialize(self.stream_name, BUFFER_SIZE)

    def ingest(self):
        buffer = self.reader.new_buffer(BUFFER_SIZE)
        data_dict = {key: [] for key in buffer.dtype.names}

        while True:
            try:
                # Read data from the stream
                num_read = self.reader.read(buffer, BUFFER_SIZE)
                if num_read > 0:
                    print(f"Read {num_read} records from stream.")
                    # Convert buffer to dictionary
                    for field in buffer.dtype.names:
                        data_dict[field].extend(buffer[field][:num_read])

                    # Check if we have enough data to write a batch
                    if len(data_dict[next(iter(data_dict))]) >= BATCH_SIZE:
                        batch_dict = {key: data_dict[key][:BATCH_SIZE] for key in data_dict}
                        data_dict = {key: data_dict[key][BATCH_SIZE:] for key in data_dict}
                        
                        # Save batch to Parquet
                        self.file_counter = save_to_parquet(batch_dict, self.file_counter)
                else:
                    print("No new data to read. Retrying...")
                    time.sleep(1)
            except KeyboardInterrupt:
                print("Ingestor stopped by user.")
                break
            except Exception as e:
                print(f"Error during ingestion: {e}")
                break

# Main Function
def main():
    stream_name = input("Enter the stream name to ingest from: ").strip()
    ingestor = RiverIngestor(stream_name)
    try:
        print(f"Starting ingestion from stream: {stream_name}")
        ingestor.ingest()
    finally:
        ingestor.reader.stop()
        print("Ingestor stopped.")

if __name__ == "__main__":
    main()
