import json
import redis
import numpy as np
from abc import ABC, abstractmethod
import uuid
from datetime import datetime
import river

# Redis connection details
# REDIS_HOSTNAME = 'redis-11423.c283.us-east-1-4.ec2.redns.redis-cloud.com'
# REDIS_PORT = 11423
# REDIS_PASSWORD = 'Test@123'
REDIS_HOSTNAME = 'localhost'
REDIS_PORT = 6379




class StreamWriter(ABC):
    """
    Abstract base class for stream writers using River and Redis.
    Provides an interface for writing data to a stream.
    """

    def __init__(self, stream_name: str, redis_connection: river.RedisConnection = None):
        """
        Initializes the StreamWriter with a stream name and optional Redis connection.

        :param stream_name: The name of the stream to create/write to.
        :param redis_connection: An optional existing Redis connection.
        """
        self._stream_start = None
        self._stream_name = stream_name
        self._redis_connection = redis_connection if redis_connection else river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT)

    @abstractmethod
    def initialize(self) -> None:
        """
        Abstract method to initialize the stream.
        Subclasses must implement this method to define stream-specific behavior.
        """
        pass

    def stop(self) -> None:
        """
        Stops the stream writer and releases resources.
        """
        print(f"Stream stopped: {self._stream_name}")


class RiverStreamWriter(StreamWriter):
    def initialize(self, schema: np.dtype) -> None:
        """
        Initializes the stream writer with a schema.
        """
        self._stream_start = datetime.now()
        print(f"Stream start time: {self._stream_start}")

        self._writer = river.StreamWriter(self._redis_connection)

        try:
            self._writer.initialize(self._stream_name, river.StreamSchema.from_dtype(schema))
            print(f"Stream initialized: {self._stream_name}")
        except river.StreamExistsException:
            print(f"Stream {self._stream_name} already exists. Using the existing stream.")
        except Exception as e:
            print(f"Error initializing stream: {e}")
            raise

    def write(self, data: np.ndarray) -> None:
        """
        Writes data to the Redis stream.
        """
        if not isinstance(data, np.ndarray):
            raise ValueError("Data must be a NumPy structured array.")
        try:
            self._writer.write(data)
        except Exception as e:
            print(f"Error writing to stream: {e}")
            raise
