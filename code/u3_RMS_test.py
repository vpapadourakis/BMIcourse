import numpy as np
import pandas as pd
from scipy.signal import butter, filtfilt
from sklearn.linear_model import LinearRegression
import matplotlib.pyplot as plt

def butter_bandpass(lowcut, highcut, fs, order=4):
    """
    Design a Butterworth bandpass filter.
    
    :param lowcut: lower frequency cutoff (Hz)
    :param highcut: upper frequency cutoff (Hz)
    :param fs: sampling frequency (Hz)
    :param order: filter order
    :return: b, a (filter coefficients)
    """
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def apply_bandpass_filter(signal, lowcut, highcut, fs, order=4):
    """
    Apply a Butterworth bandpass filter to the input signal.
    """
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    filtered_signal = filtfilt(b, a, signal)
    return filtered_signal

def compute_rms(signal, window_size):
    """
    Compute the RMS of a 1D signal using a moving window.

    :param signal: 1D numpy array of EMG data
    :param window_size: number of samples in the RMS window
    :return: numpy array of RMS values (length = len(signal) - window_size + 1)
    """
    rms_values = []
    # Slide the window across the signal
    for i in range(len(signal) - window_size + 1):
        window = signal[i : i + window_size]
        # RMS calculation
        rms_val = np.sqrt(np.mean(window**2))
        rms_values.append(rms_val)
    return np.array(rms_values)

def generate_fake_data(num_samples=5000, fs=1000.0):
    """
    Generate a synthetic EMG-like signal and a corresponding 'force' for demonstration.
    This is just for illustration; replace with real data in practice.
    """
    time = np.arange(num_samples) / fs
    # Fake EMG: combination of sinusoids, random noise, and some amplitude modulation
    emg_raw = (0.5 * np.sin(2 * np.pi * 50 * time) +
               0.3 * np.sin(2 * np.pi * 100 * time) +
               0.05 * np.random.randn(num_samples))

    # Fake force: some linear relationship to RMS(EMG) plus noise
    # (We won't compute it exactly yet, just define it for demonstration.)
    force = np.linspace(0, 30, num_samples) + 2.0 * np.random.randn(num_samples)
    return time, emg_raw, force

def main():
    # ------------------------------
    # 1. Load or Generate Data
    # ------------------------------
    fs = 1000.0  # Sampling frequency (Hz)
    time, emg_raw, force = generate_fake_data(num_samples=5000, fs=fs)
    
    # If you have real data in a file, e.g. "emg_data.csv" with columns ['time','emg','force']:
    # df = pd.read_csv("emg_data.csv")
    # time = df['time'].to_numpy()
    # emg_raw = df['emg'].to_numpy()
    # force = df['force'].to_numpy()
    
    # ------------------------------
    # 2. Filter the EMG
    # ------------------------------
    lowcut = 20.0    # typical lower band for EMG (Hz)
    highcut = 450.0  # typical upper band for EMG (Hz)
    emg_filtered = apply_bandpass_filter(emg_raw, lowcut, highcut, fs, order=4)
    
    # ------------------------------
    # 3. Rectify (Optional before RMS)
    # ------------------------------
    # Full-wave rectification
    emg_rectified = np.abs(emg_filtered)
    
    # ------------------------------
    # 4. Compute RMS
    # ------------------------------
    # Choose a window size in samples (e.g. 50 ms window at 1000 Hz -> 50 samples)
    window_ms = 50  # 50 ms
    window_size = int(window_ms * fs / 1000)  # convert ms to number of samples
    
    emg_rms = compute_rms(emg_rectified, window_size=window_size)
    
    # Because we computed RMS in a sliding window, we have fewer samples:
    # the length of emg_rms is len(emg_rectified) - window_size + 1
    # We'll trim the 'force' array and 'time' array to match
    force_trimmed = force[window_size - 1:]
    time_trimmed = time[window_size - 1:]
    
    # ------------------------------
    # 5. Linear Fit (EMG RMS vs. Force)
    # ------------------------------
    # Reshape RMS and force for sklearn (2D arrays for features)
    X = emg_rms.reshape(-1, 1)
    y = force_trimmed.reshape(-1, 1)
    
    lin_reg = LinearRegression()
    lin_reg.fit(X, y)
    
    # Get slope (a) and intercept (b)
    slope = lin_reg.coef_[0][0]
    intercept = lin_reg.intercept_[0]
    print(f"Linear Model: Force = {slope:.4f} * EMG_RMS + {intercept:.4f}")
    
    # Predicted force
    force_pred = lin_reg.predict(X)
    
    # ------------------------------
    # 6. Plotting (Optional)
    # ------------------------------
    plt.figure(figsize=(10, 6))
    
    # Plot raw EMG
    plt.subplot(3, 1, 1)
    plt.plot(time, emg_raw, label='Raw EMG', color='gray')
    plt.title("Raw EMG Signal")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude (mV?)")
    
    # Plot filtered + rectified + RMS
    plt.subplot(3, 1, 2)
    plt.plot(time, emg_filtered, label='Filtered EMG', color='blue', alpha=0.5)
    plt.plot(time, emg_rectified, label='Rectified EMG', color='orange', alpha=0.5)
    # Overlay RMS (shortened time axis)
    plt.plot(time_trimmed, emg_rms, label='RMS', color='red')
    plt.title("Filtered, Rectified, and RMS of EMG")
    plt.xlabel("Time (s)")
    plt.ylabel("Amplitude")
    plt.legend()
    
    # Plot force vs. predicted force
    plt.subplot(3, 1, 3)
    plt.plot(time_trimmed, force_trimmed, label='Actual Force', color='green')
    plt.plot(time_trimmed, force_pred, label='Predicted Force', color='red')
    plt.title("Actual Force vs. Estimated Force")
    plt.xlabel("Time (s)")
    plt.ylabel("Force (N or Nm?)")
    plt.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
