# IMU Sensor Streaming

Real-time streaming and visualization of IMU (Inertial Measurement Unit) data from an Arduino Nano 33 BLE board to a MacBook via Bluetooth Low Energy (BLE). The system captures accelerometer and gyroscope data, displays real-time plots, and saves the data to CSV files.

## Features

- Real-time BLE connection to Arduino Nano 33 BLE
- Live visualization of accelerometer and gyroscope data
- Data recording to CSV files
- Simple GUI with stop/save button
- Automatic device discovery and connection

## Requirements

- Arduino Nano 33 BLE board
- MacBook with Bluetooth capability
- Python 3.7 or higher
- Arduino IDE

## Setup Instructions

### Python Environment Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Arduino Setup

1. Open Arduino IDE

2. Install required libraries:
   - Go to Tools > Manage Libraries
   - Search for and install:
     - "ArduinoBLE" by Arduino
     - "Arduino_LSM9DS1" by Arduino

3. Set up your Arduino Nano 33 BLE:
   - Connect your board via USB
   - Select Tools > Board > Arduino Mbed OS Boards > Arduino Nano 33 BLE
   - Select the correct port under Tools > Port

4. Upload the provided Arduino sketch (arduino_imu_ble.ino)

## Usage

1. Make sure your Arduino Nano 33 BLE is powered on

2. Run the Python script:
```bash
python imu_ble_stream.py
```

3. The script will:
   - Automatically scan for and connect to your Arduino
   - Display real-time plots of accelerometer and gyroscope data
   - Show a "Stop & Save Data" button at the bottom of the window

4. To stop recording:
   - Click the "Stop & Save Data" button
   - The program will automatically save your data and close

## Data Output

The system saves two CSV files in the `output` directory:
- `accelerometer_[timestamp].csv`
  - time: seconds since start
  - x, y, z: acceleration in g (9.81 m/s²)

- `gyroscope_[timestamp].csv`
  - time: seconds since start
  - x, y, z: angular velocity in degrees/second

## Troubleshooting

- If the script can't find the Arduino:
  - Ensure the board is powered on
  - Verify the Arduino sketch is uploaded successfully
  - Check if the board appears in your system's Bluetooth devices

- If the plots aren't updating:
  - Check the Arduino IDE Serial Monitor for any error messages
  - Try resetting the Arduino board
  - Ensure the board hasn't lost power

## Data Interpretation

- Accelerometer data:
  - Units: g-forces (1g = 9.81 m/s²)
  - X: Roll (left/right)
  - Y: Pitch (forward/backward)
  - Z: Yaw (rotation)

- Gyroscope data:
  - Units: degrees per second (°/s)
  - X: Roll rate
  - Y: Pitch rate
  - Z: Yaw rate

## Project Structure

```
.
├── README.md
├── requirements.txt
├── arduino_imu_ble.ino
├── imu_ble_stream.py
└── output/
    ├── accelerometer_[timestamp].csv
    └── gyroscope_[timestamp].csv
