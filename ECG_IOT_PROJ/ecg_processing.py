# ecg_processing.py

import numpy as np
from scipy.signal import butter, filtfilt, find_peaks
import config # Import configuration parameters

def butter_bandpass_filter(data):
    """Applies a Butterworth bandpass filter to the data using parameters from config.py."""
    lowcut = config.FILTER_LOWCUT_HZ
    highcut = config.FILTER_HIGHCUT_HZ
    fs = config.SAMPLING_RATE_HZ
    order = config.FILTER_ORDER

    nyquist = 0.5 * fs
    low = lowcut / nyquist
    high = highcut / nyquist

    if low <= 0 or high >= 1 or low >= high:
        print(f"Warning: Invalid critical frequencies for bandpass filter: lowcut={lowcut} ({low}), highcut={highcut} ({high}). Must be 0 < low < high < fs/2. Returning original data.")
        return data # Return original data if filter parameters are invalid

    # Ensure data length is sufficient for the filter order
    if len(data) < order * 3: # filtfilt requires data length > 3 * order
         print(f"Warning: Data length ({len(data)}) is too short for filter order ({order}). Skipping filtering.")
         return data # Return original data if data is too short

    try:
        b, a = butter(order, [low, high], btype='band', analog=False)
        y = filtfilt(b, a, data)
        return y
    except ValueError as e:
        print(f"Error applying filter: {e}. Check filter parameters and data. Returning original data.")
        return data

def detect_r_peaks(filtered_ecg_signal):
    """
    Detects R-peaks in the filtered ECG signal using parameters from config.py.
    """
    if filtered_ecg_signal is None or len(filtered_ecg_signal) == 0:
        print("No signal data available for R-peak detection.")
        return np.array([])

    # Parameters for find_peaks might need tuning based on your signal characteristics
    # Minimum height: Using a threshold based on the median and standard deviation, robust to outliers
    median_val = np.median(filtered_ecg_signal)
    std_dev = np.std(filtered_ecg_signal)
    peak_height_threshold = median_val + config.PEAK_HEIGHT_THRESHOLD_MULTIPLIER * std_dev

    # Ensure signal is not all zeros or constant before calculating max
    if np.max(filtered_ecg_signal) - np.min(filtered_ecg_signal) < 1e-6: # Check for flat signal
         print("Warning: Filtered signal is flat or near-constant. Cannot detect peaks.")
         return np.array([])

    # Minimum distance between peaks (in samples)
    # e.g., for a max heart rate of 220 bpm (3.33 bps), min distance is fs / 3.33
    if config.SAMPLING_RATE_HZ <= 0:
         print(f"Error: Invalid sampling rate ({config.SAMPLING_RATE_HZ} Hz) for peak distance calculation.")
         return np.array([])

    min_distance_samples = int(config.SAMPLING_RATE_HZ * (60.0 / config.MAX_HR_BPM_FOR_PEAK_DISTANCE))

    # Ensure min_distance_samples is at least 1 and not greater than signal length
    min_distance_samples = max(1, min_distance_samples)
    min_distance_samples = min(min_distance_samples, len(filtered_ecg_signal) - 1)
    if min_distance_samples <= 0:
         print("Warning: Minimum peak distance is zero or negative. Cannot detect peaks.")
         return np.array([])

    peaks, _ = find_peaks(filtered_ecg_signal, height=peak_height_threshold, distance=min_distance_samples)
    return peaks

def calculate_rr_intervals(r_peaks_indices):
    """Calculates RR intervals in milliseconds from R-peak indices."""
    if r_peaks_indices is None or len(r_peaks_indices) < 2:
        return np.array([])
    rr_intervals_samples = np.diff(r_peaks_indices)
    if config.SAMPLING_RATE_HZ <= 0:
         print(f"Error: Invalid sampling rate ({config.SAMPLING_RATE_HZ} Hz) for RR interval calculation.")
         return np.array([])
    rr_intervals_ms = (rr_intervals_samples / config.SAMPLING_RATE_HZ) * 1000  # Convert to milliseconds
    return rr_intervals_ms

def calculate_hrv_metrics(rr_intervals_ms):
    """Calculates basic time-domain HRV metrics."""
    metrics = {}
    if rr_intervals_ms is None or len(rr_intervals_ms) < 2: # Need at least 2 RR intervals for SDNN, RMSSD
        metrics['Mean_RR_ms'] = np.nan
        metrics['SDNN_ms'] = np.nan
        metrics['RMSSD_ms'] = np.nan
        metrics['pNN50_percent'] = np.nan
        metrics['Mean_Heart_Rate_BPM'] = np.nan
        return metrics

    metrics['Mean_RR_ms'] = np.mean(rr_intervals_ms)
    metrics['SDNN_ms'] = np.std(rr_intervals_ms) # Standard deviation of NN intervals

    if len(rr_intervals_ms) >= 2:
        diff_rr = np.diff(rr_intervals_ms)
        metrics['RMSSD_ms'] = np.sqrt(np.mean(diff_rr**2)) # Root mean square of successive differences
        nn50 = np.sum(np.abs(diff_rr) > 50)
        metrics['pNN50_percent'] = (nn50 / len(diff_rr)) * 100 if len(diff_rr) > 0 else 0
    else:
        metrics['RMSSD_ms'] = np.nan
        metrics['pNN50_percent'] = np.nan

    if metrics['Mean_RR_ms'] > 0:
        metrics['Mean_Heart_Rate_BPM'] = 60000.0 / metrics['Mean_RR_ms'] # Average heart rate in BPM
    else:
        metrics['Mean_Heart_Rate_BPM'] = np.nan

    return metrics

def process_ecg_data(timestamps, raw_ecg_signal, source_identifier, duration_minutes):
    """
    Orchestrates the ECG data processing (filters, detects R-peaks, calculates HRV).
    Returns filtered_ecg, r_peaks, rr_intervals, hrv_metrics.
    """
    print(f"\nProcessing ECG data from {source_identifier}...")

    if raw_ecg_signal is None or len(raw_ecg_signal) == 0:
        print("Error: No raw ECG signal data provided for processing.")
        return None, None, None, {}

    print(f"Data length: {len(raw_ecg_signal)} samples")
    print(f"Processing Sampling Rate: {config.SAMPLING_RATE_HZ} Hz")

    if len(raw_ecg_signal) < config.SAMPLING_RATE_HZ * 2: # Need at least a couple of seconds of data
         print(f"Warning: Data is very short ({len(raw_ecg_signal)/config.SAMPLING_RATE_HZ:.2f}s). Results may be unreliable or impossible to calculate.")
         if len(raw_ecg_signal) < config.FILTER_ORDER * 3 : # filtfilt padding requirement
             print("Error: Data is too short to apply the filter. Aborting processing.")
             return None, None, None, {}


    # 1. Filter ECG signal
    print("Filtering ECG signal...")
    filtered_ecg = butter_bandpass_filter(raw_ecg_signal)

    # 2. Detect R-peaks
    print("Detecting R-peaks...")
    r_peaks = detect_r_peaks(filtered_ecg)

    if len(r_peaks) < 2:
        print(f"Warning: Less than 2 R-peaks detected ({len(r_peaks)}). HRV analysis will be limited or not possible.")
        print("Consider adjusting R-peak detection parameters (min_height, distance) or checking signal quality.")
        rr_intervals = np.array([]) # Empty array
        hrv_metrics = calculate_hrv_metrics(rr_intervals) # Will return NaNs
    else:
        print(f"Detected {len(r_peaks)} R-peaks.")
        # 3. Calculate RR intervals
        rr_intervals = calculate_rr_intervals(r_peaks)
        print(f"Calculated {len(rr_intervals)} RR intervals.")
        # 4. Calculate HRV metrics
        hrv_metrics = calculate_hrv_metrics(rr_intervals)
        print("HRV Metrics:", hrv_metrics)

    print("ECG processing complete.")
    return filtered_ecg, r_peaks, rr_intervals, hrv_metrics
