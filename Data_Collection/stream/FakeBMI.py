import numpy as np
import uuid
import time
import json
from datetime import datetime
from StreamWriter import RedisStreamWriter 


class BMIStreamGenerator:
    def __init__(self):
        # Generate a unique stream name
        self.stream_name = str(uuid.uuid4())
        self._writer = RedisStreamWriter(self.stream_name)
        self._writer.initialize()  # Initialize the Redis stream
        print(f"New stream created with name: {self.stream_name}")

    def generate_dummy_data(self):
        # Generate dummy arrays for weight and height
        weights = np.random.uniform(50, 100, size=10)  # Array of weights in kg
        heights = np.random.uniform(1.5, 2.0, size=10)  # Array of heights in meters

        # Calculate BMI for each weight and height
        bmi_values = weights / (heights ** 2)

        # Prepare data for Redis
        timestamp = datetime.now().timestamp()
        data_to_write = {
            'weights': weights.tolist(),  # Convert to list for JSON serialization
            'heights': heights.tolist(),  # Convert to list for JSON serialization
            'bmi_values': bmi_values.tolist(),  # Convert to list for JSON serialization
            'timestamp': float(timestamp)
        }

        # Convert to JSON
        data_as_json = json.dumps(data_to_write)

        # Write to Redis
        self._writer.write(data_as_json)
        print(f"Data written to stream: {data_to_write}")

def main():
    bmi_generator = BMIStreamGenerator()

    # Simulate generating data every second
    while True:
        bmi_generator.generate_dummy_data()
        time.sleep(1)  # Generate data every second

if __name__ == "__main__":
    main()