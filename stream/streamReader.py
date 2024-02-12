__author__ = 'Dulce'

import time
import river
import numpy as np

from typing import Tuple

from utils.connectionPorts import REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD, STREAM_READER_INITIALIZATION_TIMEOUT


class RiverDataStream():
    """
    Implementation that reads from a stream of data via River,
    """

    reader: river.StreamReader

    def __init__(self, stream_name: str, redis_connection: river.RedisConnection = None):
        """

        :param stream_name: name of the stream
        :param redis_connection: redis connection that should already exist
        """

        self._streamName = stream_name
        self._reader = None
        self._stream_start = None
        self._redis_connection = redis_connection

        if redis_connection is not None:
            self._redis_connection = redis_connection
        else:
            self._redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD)

    def initialize(self):
        """
        Function that initialize the stream reader
        """
        self._stream_start = time.time_ns()  # TODO: done in the writer and reader?
        self.reader = river.StreamReader(self._redis_connection)
        self.reader.initialize(self._streamName, STREAM_READER_INITIALIZATION_TIMEOUT)

    def read(self, num_samples: np.double) -> Tuple[np.array, int]:
        """
        Reads data to the stream.
        :param num_samples: number of samples to read
        :return: tuple of information inside the buffer and number of samples read
        """
        info_buffer = np.empty(num_samples, dtype=np.double)
        num_samples_read = self.reader.read(info_buffer)
        return info_buffer, num_samples_read
