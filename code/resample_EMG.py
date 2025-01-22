import os
import librosa
import soundfile as sf

def resample_all_wavs(input_folder, output_folder, target_sr=16000):
    """
    Reads all .wav files from `input_folder`, resamples them to `target_sr`,
    and saves them into `output_folder` using the same filename.
    """
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
    
    # List all files in the input folder
    for filename in os.listdir(input_folder):
        # Process only .wav files
        if filename.lower().endswith(".wav"):
            input_path = os.path.join(input_folder, filename)
            
            # Load and resample audio
            audio, sr = librosa.load(input_path, sr=target_sr)
            
            # Construct the output path
            output_path = os.path.join(output_folder, filename)
            
            # Save downsampled file
            sf.write(output_path, audio, target_sr)
            
            print(f"Resampled '{filename}' to {target_sr} Hz -> '{output_path}'")

if __name__ == "__main__":
    # Example usage:
    input_wav_folder = r"data\on_off_10sec\250117"
    output_wav_folder = r"data\on_off_10sec\250117\resampled_2k"
    new_sample_rate = 2000  # e.g., 16 kHz

    resample_all_wavs(input_wav_folder, output_wav_folder, target_sr=new_sample_rate)