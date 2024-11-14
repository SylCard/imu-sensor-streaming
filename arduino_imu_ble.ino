#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

BLEService imuService("19b10000-e8f2-537e-4f6c-d104768a1214");
BLECharacteristic imuCharacteristic("19b10001-e8f2-537e-4f6c-d104768a1214", 
                                  BLERead | BLENotify, 
                                  24); // 6 floats * 4 bytes each = 24 bytes

void setup() {
  Serial.begin(9600);
  
  // Initialize IMU
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("Failed to initialize BLE!");
    while (1);
  }

  // Set advertised local name and service UUID
  BLE.setLocalName("Arduino Nano 33 BLE");
  BLE.setAdvertisedService(imuService);

  // Add characteristic to the service
  imuService.addCharacteristic(imuCharacteristic);

  // Add service
  BLE.addService(imuService);

  // Start advertising
  BLE.advertise();
  Serial.println("Bluetooth device active, waiting for connections...");
}

void loop() {
  BLEDevice central = BLE.central();
  
  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      float ax, ay, az;
      float gx, gy, gz;
      
      if (IMU.accelerationAvailable() && IMU.gyroscopeAvailable()) {
        IMU.readAcceleration(ax, ay, az);
        IMU.readGyroscope(gx, gy, gz);
        
        // Pack the data into a byte array
        float data[6] = {ax, ay, az, gx, gy, gz};
        imuCharacteristic.writeValue(data, sizeof(data));
      }
      
      delay(10); // Small delay to prevent flooding
    }
    
    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}
