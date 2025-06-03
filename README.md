# ECG IOT PROJECT
An IOT project, using EPS32 and AD2832 to capture ECG activity, which is then analysed for heart rate variability (HRV)

-------------
This project provides a Python script for real-time ECG data acquisition from a serial port (ESP32), followed by (offline) signal processing, R-peak detection, Heart Rate Variability (HRV) analysis, and visualisation. The results are saved as a text report and plots.

Features
Serial Data Acquisition: Collects ECG data directly from a specified serial port.

ECG Signal Processing: Applies a Butterworth bandpass filter to clean the raw ECG signal.

R-peak Detection: Identifies R-peaks in the filtered ECG signal.

HRV Analysis: Calculates common time-domain Heart Rate Variability metrics (Mean RR, SDNN, RMSSD, pNN50).

Visualization: Generates plots of raw ECG, filtered ECG with detected R-peaks, and RR interval tachogram.

Reporting: Creates a comprehensive text report summarizing the analysis.

Modular Design: Code is organized into separate files for better maintainability and reusability.

Project Structure
ecg_analysis_project/
├── arduino/                  # Contains the Arduino (ESP32) firmware code.

├── config.py                 # Configuration parameters for serial port, ECG processing, and output.

├── data_acquisition.py       # Handles serial data collection.

├── docs/                     # Contains project documentation and images.

├── ecg_processing.py         # Contains functions for filtering, R-peak detection, and HRV calculation.

├── reporting_and_plotting.py # Manages plot generation and report writing.

├── main.py                   # The main script to run the entire workflow.

├── requirements.txt          # Lists all Python dependencies.

├── results/                  # Directory to store generated plots and analysis reports.

└── README.md                 # This file.

Setup:

![setup_picture 2-min](https://github.com/user-attachments/assets/b0673c16-1aeb-4766-a9f4-e2d771f1a071)
