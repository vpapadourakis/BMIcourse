import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import medfilt

date=[ "250117", ]
subject = ["PA"]
# subject=["AM", "GS", "KK", "KN", "LG", "MG", "MK","MP", "OG", "SM", "KM", "PA", "VK",]

def plot_wav_with_timestamps(wav_path, events_path, event_id="2"):
    # read the WAV file
    samplerate, data = wavfile.read(wav_path)
    
    # If stereo, select only one channel (e.g., left channel)
    # if data.ndim == 2:
    #     data = data[:, 0]

    # create time axis in seconds
    duration = len(data) / samplerate
    time_axis = np.linspace(0, duration, num=len(data))

    # read the events file
    events = read_events(events_path,event_id)
    if not events:
        print(f"No events found with ID={event_id}.")

    # discard data that are before the start of the task
    data = data[(time_axis>=(events[0]-10)) & (time_axis<=(events[0]+60))]
    duration = len(data) / samplerate
    time_axis = np.linspace(0, duration, num=len(data))
    events[0] = 10 # after discarding data, marker will always be at 10 seconds

    # add the 10 second offset for each task epoch
    events_to_plot = [events[0] + 10 * i for i in range(6)]
    
    # rectify and smooth data
    data_abs=np.abs(data)
    window_size = 501
    kernel = np.ones(window_size) / window_size
    data_smooth = np.convolve(data_abs, kernel, mode='same')
    # data_smooth = medfilt(data_abs, kernel_size=window_size)

    processed_data = data_smooth

    # find appropriate threshold and find indices where data crosses threshold
    threshold = 0.05*np.max(data)
    mask = data > threshold

    proc_threshold = 0.05*np.max(processed_data)
    proc_mask = processed_data > proc_threshold

    #compute RMS instead of smoothing
    # Choose a window size in samples (e.g. 50 ms window at 1000 Hz -> 50 samples)
    window_ms = 100  # 50 ms
    window_size = int(window_ms * samplerate / 1000)  # convert ms to number of samples
    
    emg_rms = compute_rms(data_abs, window_size=window_size)
    
    # Because we computed RMS in a sliding window, we have fewer samples:
    # the length of emg_rms is len(emg_rectified) - window_size + 1
    # We'll trim the 'force' array and 'time' array to match
    time_trimmed = time_axis[window_size - 1:]

    force_level = 1

    # this creates a mask based on time 
    # mask = (time_axis >= events_to_plot[0]) & (time_axis <= events_to_plot[1])

    # plot the EMG waveform

    # Create a figure and two subplots in one column (2 rows x 1 column)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
   
    # make a subplot of the original EMG
    ax1.plot(time_axis, data, label='EMG')
    
    #plot a horizontal line at threshold
    ax1.axhline(y=threshold, color="gray", linestyle="--", alpha=0.7)
    
    #plot a red dot for every threshold crossing
    ax1.scatter(time_axis[mask], np.ones(np.sum(mask)) * threshold, 
                s=5, color="red", marker=".", label=f">{threshold:.0f}", zorder=3)
   
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Amplitude')

    # plot a vertical line for each event
    for t in events_to_plot:
        ax1.axvline(x=t, color='r', linestyle='--', alpha=0.8)
    
    ax1.legend()
    
    # make a subplot of the processed EMG
    ax2.plot(time_axis, processed_data, label='processed EMG')
    # ax2.plot(time_trimmed, emg_rms, label='RMS')

    #plot a horizontal line at threshold
    ax2.axhline(y=proc_threshold, color="gray", linestyle="--", alpha=0.7)
    
    #plot a red dot for every threshold crossing
    ax2.scatter(time_axis[proc_mask], np.ones(np.sum(proc_mask)) * proc_threshold, 
                s=5, color="red", marker=".", label=f">{proc_threshold:.0f}", zorder=3)
   
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Amplitude')

    # plot a vertical line for each event
    for t in events_to_plot:
        ax2.axvline(x=t, color='r', linestyle='--', alpha=0.8)
    
    ax2.legend()

    # show or save
    plt.title(wav_path)
    plt.tight_layout()
    plt.show(block=False)
    figurename = fr"figures\on_off_10s_{date}_{subject}.png"       
    plt.savefig(figurename, dpi=300, bbox_inches='tight')

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

def read_events(filename, marker_id_to_return):
    events = []

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines or comment lines (lines starting with "#")
            if not line or line.startswith('#'):
                continue
            
            # Each valid line should be "id, time_in_seconds"
            parts = line.split(',')
            if len(parts) < 2:
                continue  # skip malformed lines

            event_id = parts[0].strip()
            try:
                time_in_seconds = float(parts[1].strip())
            except ValueError:
                # If we can't parse the time as float, skip the line
                continue

            # Pick only the timestamps whose ID is "2"
            if event_id == marker_id_to_return:
                events.append(time_in_seconds)

    return events

if __name__ == "__main__":
    for date in date:
        for subject in subject:
            wav_file_path = fr"data\on_off_10sec\on_off_10s_{date}_{subject}.wav"
            if os.path.isfile(wav_file_path):
                events_file = fr"data\on_off_10sec\on_off_10s_{date}_{subject}_events.txt" 
                plot_wav_with_timestamps(wav_file_path, events_file)