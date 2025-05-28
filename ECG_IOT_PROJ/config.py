# config.py

import datetime

# --- Configuration Parameters ---

# Serial Port Configuration
SERIAL_PORT = '/dev/cu.usbserial-10'  # serial port used for this project (IOS)
BAUD_RATE = 115200    # ESP32's baud rate
DATA_COLLECTION_DURATION_MINUTES = 1 # Duration to collect data from serial port

# ECG Processing Configuration
SAMPLING_RATE_HZ = 250  #  sampling rate of the ECG sensor
FILTER_LOWCUT_HZ = 0.5  # Low cut-off frequency for bandpass filter (Hz)
FILTER_HIGHCUT_HZ = 40.0 # High cut-off frequency for bandpass filter (Hz)
FILTER_ORDER = 3        # Order of the Butterworth filter

# R-peak Detection Parameters (tuned for general ECG, may need further adjustment)
# This threshold is based on median + multiplier * std_dev. Adjust multiplier (e.g., 0.5 to 1.0)
# based on your signal quality. Higher values make it less sensitive.
PEAK_HEIGHT_THRESHOLD_MULTIPLIER = 0.7
# Minimum distance between peaks in samples, based on a maximum plausible heart rate (e.g., 220 bpm)
# min_distance_samples = int(SAMPLING_RATE_HZ * (60.0 / MAX_HR_BPM))
MAX_HR_BPM_FOR_PEAK_DISTANCE = 220

# Output Files and Directories
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"
OUTPUT_REPORT_FILENAME_TEMPLATE = "results/hrv_report_{timestamp}.txt" #Output in results dir
OUTPUT_PLOT_DIR_TEMPLATE = "results/ecg_plots_{timestamp}"

# Plotting Configuration
PLOT_DPI = 300 # plot resolution 

# --- End of Configuration Parameters ---

# Generate unique filenames/directories based on current timestamp
current_time_str = datetime.datetime.now().strftime(TIMESTAMP_FORMAT)
OUTPUT_REPORT_FILE = OUTPUT_REPORT_FILENAME_TEMPLATE.format(timestamp=current_time_str)
OUTPUT_PLOT_DIR = OUTPUT_PLOT_DIR_TEMPLATE.format(timestamp=current_time_str)
