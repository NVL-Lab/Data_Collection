# author: Nuria
# This code will access the info in the serial port to read from the ESP32
from typing import Optional

import serial
import time
import warnings


def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Found port: {port.device}")


def read_from_serial(port: str, baud_rate: int = 9600):
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            print("Waiting for ESP32 to finish booting...")
            time.sleep(5)  # Wait for the ESP32 to finish booting

            while True:
                if ser.in_waiting > 0:
                    try:
                        data = ser.readline().decode('utf-8').rstrip()
                        print(f"Received: {data}")
                    except UnicodeDecodeError:
                        data = ser.readline().decode('latin-1').rstrip()
                        print(f"Received (decoded with latin-1): {data}")
                    if data == 'Touch':  # to be changed by the serial message for sensor
                        print('XXXXXXX')
                        # do something
                    else:  # to be deleted, only here to debug
                        warnings.warn("Unexpected data received: {}".format(data))
                        # do something else
    except serial.SerialException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def write_in_serial(port: str, baud_rate: int = 9600, command:Optional[str]=None, frequency:Optional[int]=None, duration:Optional[int]=None):
    try:
        with serial.Serial(port, baud_rate, timeout=1) as ser:
            if command == "activate":
                message = "activate"
            elif frequency is not None:
                if duration is None:
                    duration = 0
                message = "{},{}".format(frequency, duration)
            else:
                raise ValueError("Invalid command or parameters")

            ser.write(message.encode())
            print(f"Sent to ESP32: {message}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")