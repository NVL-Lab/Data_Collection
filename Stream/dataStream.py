from typing import Tuple

import numpy as np
import river


class RiverDataStream():

    reader: river.StreamReader

    def __init__(self, streamName: str, redis_connection: river.RedisConnection = None):

        self._stream_name = streamName
        self._reader = None
        self._redis_connection = redis_connection
     
     #def initialize(self):

    def read(self, numSamples: np.double) -> Tuple[np.array, int]:
        infoBuffer = np.empty(numSamples, dtype=np.double)
        numSamplesRead = self.reader.read(infoBuffer)
        return infoBuffer, numSamplesRead

