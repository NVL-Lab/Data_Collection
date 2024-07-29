# author: Nuria
# This code will access the info in the serial port to read from the ESP32 

import serial
import time
import serial.tools.list_ports

def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        print(f"Found port: {port.device}")

def read_from_serial(port, baud_rate=9600):
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
                    if data == 'Task2 is running': # to be changed by the serial message for sensor
                        print('XXXXXXX')
                        # do something
                    elif data == 'Task1 is running': # to be deleted, only here to debug
                        print('YYYYY')
                        # do something else
    except serial.SerialException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
