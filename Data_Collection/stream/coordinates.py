import uuid
import threading
import time
import numpy as np
from datetime import datetime
from pynput.mouse import Listener
from StreamWriter import RiverStreamWriter 


class CoordinateCapture:
    def __init__(self, stream_name: str):
        """
        Initializes the CoordinateCapture class and sets up the RiverStreamWriter.
        """
        self._stream_name = stream_name
        self._stream_writer = RiverStreamWriter(stream_name)

    def initialize(self):
        """
        Initializes the Redis stream with a schema.
        """
        schema_fields = [
            ('x', 'float'),
            ('y', 'float'),
            ('timestamp', 'float'),
        ]
        schema = np.dtype(schema_fields)
        self._stream_writer.initialize(schema)

    def write(self, x: float, y: float, timestamp: float):
        """
        Writes data to the Redis stream as a structured NumPy array.
        """
        try:
            data = np.array([(x, y, timestamp)], dtype=[
                ('x', 'float'),
                ('y', 'float'),
                ('timestamp', 'float'),
            ])
            self._stream_writer.write(data)
            print(f"Data written to stream: {data}")
        except Exception as e:
            print(f"Error writing to stream: {e}")
            raise


class MouseTracker:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.timestamp = None

    def on_move(self, x, y):
        """
        Captures the mouse movement and updates the coordinates and timestamp.
        """
        self.x = x
        self.y = y
        self.timestamp = datetime.now().timestamp()

    def start_listening(self):
        """
        Starts listening to mouse movements.
        """
        with Listener(on_move=self.on_move) as listener:
            listener.join()


def main():
    # Initialize the mouse tracker and the Redis stream writer
    tracker = MouseTracker()

    # Generate a unique stream name using UUID
    stream_name = str(uuid.uuid4())
    writer = CoordinateCapture(stream_name)
    writer.initialize()

    print(f"New stream created with name: {stream_name}")

    # Start the mouse listener in a separate thread
    listener_thread = threading.Thread(target=tracker.start_listening)
    listener_thread.daemon = True
    listener_thread.start()

    while True:
        # Ensure you have updated coordinates
        x = tracker.x
        y = tracker.y
        timestamp = tracker.timestamp

        # Only write data when the timestamp is valid
        if timestamp is not None:
            writer.write(x, y, timestamp)
        else:
            print(f"Waiting for valid timestamp...")

        # Sleep for a short interval
        time.sleep(0.1)  # Reduced sleep for near-real-time streaming


if __name__ == "__main__":
    main()
