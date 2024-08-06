# author: Nuria
# This code will access the info in the serial port to read/write from/to the ESP32
import serial
import time
import warnings
from typing import Optional


class SerialCommunicator:
    def __init__(self, port: str, baud_rate: int = 9600):
        self.port = port
        self.baud_rate = baud_rate
        try:
            self.ser = serial.Serial(self.port, self.baud_rate, timeout=1)
            print("Waiting for ESP32 to finish booting...")
            time.sleep(5)  # Wait for the ESP32 to finish booting
        except serial.SerialException as e:
            print(f"Error: {e}")
            self.ser = None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            self.ser = None

    def _write_in_serial(self, command: Optional[str] = None, frequency: Optional[int] = None,
                         duration: Optional[int] = None):
        if self.ser is None:
            print("Serial connection not established.")
            return

        t = time.time()
        try:
            if command == "activate":
                message = "activate"
            elif frequency is not None:
                if duration is None:
                    duration = 0
                message = "{},{}".format(frequency, duration)
            else:
                raise ValueError("Invalid command or parameters")

            self.ser.write(message.encode())
            print(f"Sent to ESP32: {message}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        elapsed = time.time() - t
        print(f"Elapsed time for send_command: {elapsed:.4f} seconds")

    def _read_from_serial(self):
        if self.ser is None:
            print("Serial connection not established.")
            return

        t = time.time()
        try:
            while True:
                if self.ser.in_waiting > 0:
                    try:
                        data = self.ser.readline().decode('utf-8').rstrip()
                        print(f"Received: {data}")
                    except UnicodeDecodeError:
                        data = self.ser.readline().decode('latin-1').rstrip()
                        print(f"Received (decoded with latin-1): {data}")

                    if data == 'Touch':  # to be changed by the serial message for sensor
                        print('XXXXXXX')
                        # do something
                    else:  # to be deleted, only here to debug
                        warnings.warn("Unexpected data received: {}".format(data))
                        # do something else

                    elapsed = time.time() - t
                    print(f"Elapsed time for read_from_serial: {elapsed:.4f} seconds")
                    t = time.time()
        except serial.SerialException as e:
            print(f"Error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    def trigger_water_reward(self):
        self._write_in_serial(command="activate")

    def trigger_tone(self, frequency: int):
        self._write_in_serial(frequency=frequency)

    def event_touch(self):
        self._read_from_serial()

    def close_serial(self):
        if self.ser is not None:
            self.ser.close()
            print("Serial connection closed.")
        else:
            print("Serial connection not established.")