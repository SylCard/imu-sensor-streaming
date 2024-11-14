import asyncio
from bleak import BleakScanner, BleakClient
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import numpy as np
from datetime import datetime
import struct
import logging
import os
import seaborn as sns
from pathlib import Path
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Arduino Nano 33 BLE IMU service and characteristic UUIDs
IMU_SERVICE_UUID = "19b10000-e8f2-537e-4f6c-d104768a1214"
IMU_CHARACTERISTIC_UUID = "19b10001-e8f2-537e-4f6c-d104768a1214"

# Create output directory
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

class IMUPlotter:
    def __init__(self):
        # Set the style
        sns.set_theme(style="darkgrid")
        sns.set_palette("husl")
        
        # Initialize data lists
        self.accel_data_x = []
        self.accel_data_y = []
        self.accel_data_z = []
        self.gyro_data_x = []
        self.gyro_data_y = []
        self.gyro_data_z = []
        self.time_points = []
        
        # Buffer size for real-time plotting
        self.buffer_size = 100
        
        # Setup real-time plots
        plt.ion()
        self.fig = plt.figure(figsize=(12, 10))  # Made figure taller for button
        
        # Create subplot grid with space for button
        gs = self.fig.add_gridspec(3, 1, height_ratios=[1, 1, 0.1])
        
        # Create subplots
        self.ax1 = self.fig.add_subplot(gs[0])
        self.ax2 = self.fig.add_subplot(gs[1])
        
        # Initialize lines for accelerometer
        self.accel_lines = [
            self.ax1.plot([], [], label=f'Accel {axis}', linewidth=2)[0]
            for axis in ['X', 'Y', 'Z']
        ]
        self.customize_plot(self.ax1, 'Accelerometer Data', 'Time (s)', 'Acceleration (g)')
        
        # Initialize lines for gyroscope
        self.gyro_lines = [
            self.ax2.plot([], [], label=f'Gyro {axis}', linewidth=2)[0]
            for axis in ['X', 'Y', 'Z']
        ]
        self.customize_plot(self.ax2, 'Gyroscope Data', 'Time (s)', 'Angular Velocity (deg/s)')
        
        # Add Stop & Save button
        self.button_ax = self.fig.add_subplot(gs[2])
        self.stop_button = Button(self.button_ax, 'Stop & Save Data')
        self.stop_button.on_clicked(self.stop_and_save)
        
        plt.tight_layout()
        self.start_time = datetime.now()
        self.running = True

    def customize_plot(self, ax, title, xlabel, ylabel):
        ax.set_title(title, fontsize=14, pad=10)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.tick_params(labelsize=10)

    def stop_and_save(self, event):
        if self.running:
            self.running = False
            self.save_data()
            plt.close('all')
            logger.info("Stopping data collection and saving...")

    def update_plot(self, accel_data, gyro_data):
        if not self.running:
            return False

        current_time = (datetime.now() - self.start_time).total_seconds()
        
        # Store data
        self.time_points.append(current_time)
        self.accel_data_x.append(accel_data[0])
        self.accel_data_y.append(accel_data[1])
        self.accel_data_z.append(accel_data[2])
        self.gyro_data_x.append(gyro_data[0])
        self.gyro_data_y.append(gyro_data[1])
        self.gyro_data_z.append(gyro_data[2])
        
        # Get the last buffer_size points for real-time display
        display_slice = slice(max(0, len(self.time_points) - self.buffer_size), None)
        time_display = self.time_points[display_slice]
        
        # Update accelerometer plot
        for i, line in enumerate(self.accel_lines):
            data = [self.accel_data_x, self.accel_data_y, self.accel_data_z][i]
            line.set_data(time_display, data[display_slice])
        
        # Update gyroscope plot
        for i, line in enumerate(self.gyro_lines):
            data = [self.gyro_data_x, self.gyro_data_y, self.gyro_data_z][i]
            line.set_data(time_display, data[display_slice])
        
        # Update axis limits
        for ax in [self.ax1, self.ax2]:
            ax.relim()
            ax.autoscale_view()
            ax.set_xlim(time_display[0], time_display[-1])
        
        # Update the display
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        
        return self.running

    def save_data(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save accelerometer data
        accel_df = pd.DataFrame({
            'time': self.time_points,
            'x': self.accel_data_x,
            'y': self.accel_data_y,
            'z': self.accel_data_z
        })
        accel_path = OUTPUT_DIR / f'accelerometer_{timestamp}.csv'
        accel_df.to_csv(accel_path, index=False)
        
        # Save gyroscope data
        gyro_df = pd.DataFrame({
            'time': self.time_points,
            'x': self.gyro_data_x,
            'y': self.gyro_data_y,
            'z': self.gyro_data_z
        })
        gyro_path = OUTPUT_DIR / f'gyroscope_{timestamp}.csv'
        gyro_df.to_csv(gyro_path, index=False)
        
        logger.info(f"Data saved to {accel_path} and {gyro_path}")

async def find_arduino():
    logger.info("Scanning for Arduino Nano 33 BLE...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device.name and "Arduino" in device.name:
            logger.info(f"Found Arduino device: {device.name} ({device.address})")
            return device.address
    return None

def parse_imu_data(data):
    try:
        if len(data) != 24:
            logger.error(f"Received incorrect data length: {len(data)} bytes")
            return None, None

        values = struct.unpack('6f', data)
        accel_data = values[:3]
        gyro_data = values[3:]
        
        return accel_data, gyro_data
    except Exception as e:
        logger.error(f"Error parsing IMU data: {e}")
        return None, None

async def notification_handler(sender, data):
    accel_data, gyro_data = parse_imu_data(data)
    if accel_data is not None and gyro_data is not None:
        if not plotter.update_plot(accel_data, gyro_data):
            # If update_plot returns False, stop the program
            raise KeyboardInterrupt

async def main():
    global plotter
    
    # Create the plotter
    plotter = IMUPlotter()
    
    # Find the Arduino
    address = await find_arduino()
    if not address:
        logger.error("No Arduino device found!")
        return
    
    logger.info(f"Connecting to {address}...")
    
    async with BleakClient(address) as client:
        logger.info("Connected! Recording data...")
        logger.info("Click 'Stop & Save Data' button to quit")
        
        # Subscribe to notifications
        await client.start_notify(IMU_CHARACTERISTIC_UUID, notification_handler)
        
        # Keep running until button is clicked
        while plotter.running:
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        if 'plotter' in globals():
            if plotter.running:
                logger.info("Saving data...")
                plotter.save_data()
        logger.info("Program terminated")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise
