# main.py

import config
import data_acquisition
import ecg_processing
import reporting_and_plotting
import os

def main():
    """
    Main function for ECG data acquisition, processing, and reporting.
    """
    print("--- Starting ECG Analysis Script ---")

    # --- Step 1: Data Acquisition ---
    print("\n--- Step 1: Data Acquisition ---")
    timestamps, raw_ecg_data, duration_
