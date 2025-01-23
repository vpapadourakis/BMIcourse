import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile

def plot_wav_with_timestamps(wav_path, events_path, event_id="2"):
    # Read the WAV file
    samplerate, data = wavfile.read(wav_path)
    
    # Create time axis in seconds
    duration = len(data) / samplerate
    time_axis = np.linspace(0, duration, num=len(data))

    # Read the events file
    # TASK: edit the events file to correct the marker position
    events = read_events(events_path,event_id)
    if not events:
        print(f"No events found with ID={event_id}.")

    # make a list with the events to plot (a vertical line for each event)
    # TASK: add the 10 second offset for each task epoch
    events_to_plot = [events[0]]

    # Find indices where data crosses threshold
    # TASK: use the data to find the right threshold  ADDITIONAL TASK: Preprocess data to make threshold crossing more robust.
    threshold = 30000
    mask = data > threshold

    # Plot the EMG waveform
    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, data, label='EMG')

    # Plot a red dot for every timepoint above threshold
    plt.scatter(time_axis[mask], np.ones(np.sum(mask)) * threshold, color="red", marker="o", label=f">{threshold}")
    plt.axhline(y=threshold, color="gray", linestyle="--", alpha=0.7)

    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title(wav_path)

    # Plot a vertical line for each event
    for t in events_to_plot:
        plt.axvline(x=t, color='r', linestyle='--', alpha=0.8)

    plt.legend()
    plt.tight_layout()
    plt.show()

    #TASK: Save figure in some format



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
    subject="SM"
    wav_file_path = fr"data\on_off_10sec\on_off_10s_250110_{subject}.wav"
    events_file = fr"data\on_off_10sec\on_off_10s_250110_{subject}_events.txt" 
    plot_wav_with_timestamps(wav_file_path, events_file)