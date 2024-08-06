# Treadmill sensors

This project integrates FreeRTOS to manage concurrent tasks involving a touch sensor, a speaker, and a solenoid. The system architecture consists of five primary tasks, each serving a distinct function.

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Task Descriptions](#task-descriptions)
    - [Play Tone Task](#play-tone-task)
    - [Monitor Touch Sensor Task](#monitor-touch-sensor-task)
    - [Control Solenoid Task](#control-solenoid-task)
    - [Send Data Task](#send-data-task)
    - [Receive Data Task](#receive-data-task)
3. [Debug](#Debug)


## System Architecture

The system consists of the following components:
- **Touch Sensor**: Detects touch inputs.
- **Speaker**: Generates tones based on frequency and duration.
- **Solenoid**: Activates based on specific commands.

## Task Descriptions

### Play Tone Task

This task generates sound on the speaker. It continuously waits for tone parameters (frequency and duration) received through a queue (`toneQueue`). When valid parameters are received, the task uses the `tone()` function to produce the sound at the specified frequency and maintains it for the specified duration. After the duration elapses, the `noTone()` function stops the sound. This task runs in an infinite loop, periodically yielding control to other tasks.

### Monitor Touch Sensor Task

This task monitors a touch sensor connected to the microcontroller. It continuously reads the sensor's state and, upon detecting a touch (when the sensor pin reads HIGH), signals the `touchSemaphore`. This semaphore synchronizes with other tasks, particularly to trigger data sending or solenoid activation. The task includes a debounce delay to prevent multiple triggers from a single touch.

### Control Solenoid Task

This task controls a solenoid connected to the microcontroller. It waits for a semaphore signal (`solenoidSemaphore`) to activate the solenoid. Once activated, the solenoid is kept on for one second before deactivating. This task ensures that solenoid control is synchronized with other tasks that might trigger it, such as receiving data commands.

### Send Data Task

This task periodically sends data related to the touch sensor status. It operates every two seconds, waiting for the `touchSemaphore` to be available, indicating that the touch sensor has been triggered. The task reads the touch sensor status and simulates sending this data, which could be to a server or another system component. This periodic operation helps maintain up-to-date sensor status reporting.

### Receive Data Task

This task manages incoming serial data, including commands to control the solenoid or specify tone parameters. It reads characters from the Serial input, builds a command string, and processes it upon receiving a newline character. The task interprets commands such as "activate" (to trigger the solenoid) or CSV-formatted strings specifying tone parameters. It then activates the solenoid or places tone parameters into the queue for the Play Tone Task.

## Debug

1. **Upload the code**:
   - Connect your Arduino board to your computer.
   - Upload the `Treadmill.ino` file to your Arduino board.

2. **Monitor the Serial Output**:
   - Open the Serial Monitor in Arduino IDE to view the status messages.
