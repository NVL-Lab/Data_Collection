from stream.streamReader import RiverDataStream
from stream.streamWriter import RiverStreamWriter
import numpy as np

def testStreams():
    # Create and initialize the stream reader
    with RiverDataStream(stream_name='test_stream') as stream_reader:
        stream_reader.initialize()

        # Create and initialize the stream writer
        with RiverStreamWriter(stream_name='test_stream', sampling_rate=20) as stream_writer:
            stream_writer.initialize()

            data = np.arange(10)
            print(data)

            # Write the data to the stream
            stream_writer.write(data)

# Call the testStreams function to execute the test
testStreams()