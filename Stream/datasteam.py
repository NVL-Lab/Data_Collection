
import numpy as np
import river


class RiverDataStream():

    reader: river.StreamReader

    def __init__(self, stream_name: str,redis_connection: river.RedisConnection = None):

        self.stream_name = stream_name
        self.reader = None
        self.redis_connection = redis_connection
     
     #def initialize(self):