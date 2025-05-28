# data_acquisition.py

import serial
import time
import numpy as np
import config # Import configuration parameters

def collect_serial_data():
    """
    Collects data from the serial port for a specified duration.
    Assumes data is sent as one numerical value per line.
    Returns collected timestamps and ECG values as NumPy arrays.
    Returns (None, None, None) on failure.
    """
    collected_data = [] # Temporarily stores [timestamp, ecg_value]
    sample_count = 0

    print(f"Attempting to connect to serial port {config.SERIAL_PORT} at {config.BAUD_RATE} baud...")
    try:
        with serial.Serial(config.SERIAL_PORT, config.BAUD_RATE, timeout=1) as ser:
            print(f"Successfully connected to {config.SERIAL_PORT}. Collecting data for {config.DATA_COLLECTION_DURATION_MINUTES} minutes...")

            # Give some time for the serial connection to stabilise
            time.sleep(2)
            ser.flushInput() # Clear any old data in the buffer

            collection_start_time = time.time()
            end_collection_time = collection_start_time + (config.DATA_COLLECTION_DURATION_MINUTES * 60)

            while (time.time() < end_collection_time):
                if ser.in_waiting > 0:
                    try:
                        line_bytes = ser.readline()
                        # Use errors='ignore' to handle potential non-UTF-8 bytes
                        line = line_bytes.decode('utf-8', errors='ignore').strip()

                        if line: # Ensure line is not empty
                            try:
                                ecg_value = float(line)
                                # Generate a timestamp relative to the start of collection
                                current_timestamp = (time.time() - collection_start_time)
                                collected_data.append([current_timestamp, ecg_value])
                                sample_count += 1

                                if sample_count % config.SAMPLING_RATE_HZ == 0: # Print progress every second (approx)
                                    print(f"Collected {sample_count} samples... Time elapsed: {current_timestamp:.2f}s")

                            except ValueError:
                                print(f"Warning: Could not convert data to float: '{line}'. Skipping.")

                    except UnicodeDecodeError:
                        print(f"Warning: Unicode decode error. Skipping line.")
                    except serial.SerialException as e:
                        print(f"Serial read error: {e}")
                        break # Exit loop on serial error
                # Small delay to prevent busy-waiting, adjust if necessary
                time.sleep(0.001) # Sleep for a fraction of sample interval

        print(f"Data collection complete. Total samples collected: {len(collected_data)}")

        if not collected_data:
            print("No data was collected. Please check your ESP32 connection and data transmission.")
            return None, None, None # Return None for data and duration on failure

        # Separate timestamps and ECG values
        timestamps = np.array([d[0] for d in collected_data])
        ecg_values = np.array([d[1] for d in collected_data])

        # Calculate actual duration from collected data timestamps
        actual_duration_seconds = timestamps[-1] if len(timestamps) > 0 else 0
        actual_duration_minutes = actual_duration_seconds / 60.0

        print(f"Actual collection duration: {actual_duration_minutes:.2f} minutes.")
        print(f"Effective sampling rate (based on collected data): {len(ecg_values) / actual_duration_seconds:.2f} Hz" if actual_duration_seconds > 0 else "Effective sampling rate: N/A")

        return timestamps, ecg_values, actual_duration_minutes

    except serial.SerialException as e:
        print(f"Error: Could not open serial port {config.SERIAL_PORT}: {e}")
        print("Please check the port name, ensure the ESP32 is connected, and drivers are installed.")
        return None, None, None
    except Exception as e:
        print(f"An unexpected error occurred during data collection: {e}")
        return None, None, None
