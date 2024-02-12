__author__ = 'Nuria'

import time
import numpy as np
import river

from utils.connectionPorts import REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD


class RiverStreamWriter(object):
    """
    Implementation that writes a stream of data via River, a C++ library that uses Redis under the hood.
    """

    writer: river.StreamWriter

    def __init__(self, stream_name: str, sampling_rate: float, redis_connection: river.RedisConnection = None):
        """
        :param stream_name: name of the stream where we are writing
        :param sampling_rate: sampling rate
        :param redis_connection:
        """
        self._stream_start = None
        self._streamName = stream_name
        self._samplingRate = sampling_rate

        self._schema = None
        self._writer = None # we start as none and define it when we initialize the writer given the redis connection
        if redis_connection is not None:
            self._redis_connection = redis_connection
        else:
            self._redis_connection = river.RedisConnection(REDIS_HOSTNAME, REDIS_PORT, REDIS_PASSWORD)

    def initialize(self):
        """
        Function that initialize the stream writer
        """
        self._stream_start = time.time_ns()
        self._writer = river.StreamWriter(self._redis_connection)
        self._writer.initialize(self._streamName, self._schema)

    def write(self, data: np.ndarray):
        """ Writes data to the stream.
        The given data buffer of type DataT will be recast to a raw (e.g. char *) array and
        written to redis according to each sample size. If the schema has only fixed-width fields,
        then the data buffer will be advanced according to the fixed-width size given in #initialize();
         otherwise (i.e. if it has variable-width fields), the sizes buffer is necessary to determine
          the size of each sample.
     """
        self._writer.write(data)

    def stop(self):
        self._writer.stop()
