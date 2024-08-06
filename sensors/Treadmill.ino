// Define pins
#define SPEAKER_PIN 25
#define TOUCH_SENSOR_PIN 32
#define SOLENOID_PIN 33

// Create semaphore handle for touch sensor
SemaphoreHandle_t touchSemaphore;
// Define the solenoid semaphore
SemaphoreHandle_t solenoidSemaphore;

// Create queue handle for tone parameters
QueueHandle_t toneQueue;

// Structure to hold tone parameters
struct ToneParameters {
  int frequency;
  int duration;
};

// Function prototypes
void playTone(void *parameter);
void monitorTouchSensor(void *parameter);
void controlSolenoid(void *parameter);
void sendData(void *parameter);
void receiveData(void *parameter);

// Task to generate tone on the speaker
void playTone(void *parameter) {
  struct ToneParameters toneParams;
  while (1) {
    // Wait to receive tone parameters from the queue
    if (xQueueReceive(toneQueue, &toneParams, portMAX_DELAY) == pdTRUE) {
      if (toneParams.frequency > 0) {
        tone(SPEAKER_PIN, toneParams.frequency);
        if toneParams.duration > 0 {
          vTaskDelay(toneParams.duration / portTICK_PERIOD_MS);
          noTone(SPEAKER_PIN);
        }
      }
    }
    vTaskDelay(10);  
  }
}

// Task to monitor the TTP223 touch sensor
void monitorTouchSensor(void *parameter) {
  pinMode(TOUCH_SENSOR_PIN, INPUT);
  while (true) {
    // Check if touch sensor is activated
    if (digitalRead(TOUCH_SENSOR_PIN) == HIGH) {
      // Give semaphore on touch detection
      xSemaphoreGive(touchSemaphore);
      // Debounce delay
      vTaskDelay(50 / portTICK_PERIOD_MS);
    }
    vTaskDelay(10);  
  }
}

// Task to control the solenoid
void controlSolenoid(void *parameter) {
  pinMode(SOLENOID_PIN, OUTPUT);
  while (1) {
    // Wait for the semaphore from the receiveData task
    if (xSemaphoreTake(solenoidSemaphore, portMAX_DELAY) == pdTRUE) {
      digitalWrite(SOLENOID_PIN, HIGH); // Activate solenoid
      vTaskDelay(1000 / portTICK_PERIOD_MS); // Keep solenoid active for 1 second
      digitalWrite(SOLENOID_PIN, LOW); // Deactivate solenoid
    }
    vTaskDelay(10); 
  }
}

// Task to send sensor data periodically
void sendData(void *parameter) {
  while (1) {
    // Wait for the semaphore from the touch sensor
    if (xSemaphoreTake(touchSemaphore, portMAX_DELAY) == pdTRUE) {
      // Read touch sensor status and send data in CSV format
      Serial.println("Touch");
    }
    vTaskDelay(10 / portTICK_PERIOD_MS);
  }
}

// Task to receive data and process commands
void receiveData(void *parameter) {
  char buffer[20]; // Buffer to hold incoming data
  int index = 0;
  struct ToneParameters toneParams;
  while (1) {
    if (Serial.available() > 0) {
      char c = Serial.read();
      if (c == '\n') { // End of line
        buffer[index] = '\0'; // Null-terminate the buffer

        // Check for the command "activate"
        if (strcmp(buffer, "activate") == 0) {
          xSemaphoreGive(solenoidSemaphore); // Give semaphore to activate solenoid
        } else if (sscanf(buffer, "%d,%d", &toneParams.frequency, &toneParams.duration) == 2) {
          xQueueSend(toneQueue, &toneParams, portMAX_DELAY);
        }

        index = 0; // Reset buffer index for next input
      } else {
        if (index < sizeof(buffer) - 1) { // Prevent buffer overflow
          buffer[index++] = c; // Add character to buffer
        }
      }
    }
    vTaskDelay(10 / portTICK_PERIOD_MS); 
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(SPEAKER_PIN, OUTPUT);
  
  // Initialize semaphore for touch sensor
  touchSemaphore = xSemaphoreCreateBinary();
  solenoidSemaphore = xSemaphoreCreateBinary();
  
  // Create queue for tone parameters
  toneQueue = xQueueCreate(1, sizeof(ToneParameters));

  // Create tasks
  xTaskCreate(playTone, "Play Tone", 2048, NULL, 1, NULL);
  xTaskCreate(monitorTouchSensor, "Monitor Touch Sensor", 2048, NULL, 1, NULL);
  xTaskCreate(controlSolenoid, "Control Solenoid", 2048, NULL, 1, NULL);
  xTaskCreate(sendData, "Send Data", 2048, NULL, 1, NULL); 
  xTaskCreate(receiveData, "Receive Data", 2048, NULL, 1, NULL); 
}

void loop() {
  // Main loop can be used for additional tasks if required
}
