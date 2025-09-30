import numpy as np
import os
import pandas as pd
import librosa
import soundfile as sf
from audiomentations import AddBackgroundNoise, PolarityInversion
from binamix.sadie_utilities import TrackObject, mix_tracks_binaural
import myRand
from randManipulateAudio import getRandomClip, getRandomTimeWindow, randomlyShiftAudioStartTime



def create_ambient_csv_if_needed():
    """Create CSV for ambient sounds if it doesn't exist"""
    ambient_dir = "cs2 sounds/ambient"
    ambient_csv = "cs2 sounds/ambient.csv"

    if not os.path.exists(ambient_csv) and os.path.exists(ambient_dir):
        ambient_files = [f for f in os.listdir(ambient_dir) if f.endswith('.wav')]
        if ambient_files:
            df = pd.DataFrame({
                'name': ambient_files,
                'class': ['ambient'] * len(ambient_files)
            })
            df.to_csv(ambient_csv, index=False)
            return True
    return os.path.exists(ambient_csv)


def get_random_ambient_audio(target_length_seconds=0.5, sr=44100):
    """Get random ambient audio or create silence if no ambient files available"""
    if create_ambient_csv_if_needed():
        try:
            ambient_audio, ambient_sr, _ = getRandomClip("cs2 sounds/ambient", "csv_output/ambient.csv")
            if ambient_sr != sr:
                ambient_audio = librosa.resample(ambient_audio, orig_sr=ambient_sr, target_sr=sr)
            return getRandomTimeWindow(ambient_audio, target_length_seconds, sr)
        except:
            pass

    # Return silence if no ambient files available
    return np.zeros(int(target_length_seconds * sr))


def ensure_target_length(audio, target_len):
    """Ensure audio is exactly target_len samples"""
    if len(audio) > target_len:
        return audio[:target_len]
    if len(audio) < target_len:
        return np.pad(audio, (0, target_len - len(audio)))
    return audio


def generate_single_augmented_sample(sample_id, output_dir="output/dataset"):
    """Generate a single augmented audio sample with metadata"""

    # Step 1: Randomly decide how many clips (1-4)
    num_clips = np.random.randint(1, 5)

    # Audio parameters
    window_time = 0.040 # 40ms window
    sr = 44100
    target_len = int(window_time * sr)

    tracks = []
    classes = []
    azimuths = []
    elevations = []
    csv_files = ["doors", "footsteps","footsteps", "flashbang", "hegrenade", "incgrenade", "molotov", "smokegrenade", "weapons"]

    # Step 2: Generate clips with random positioning
    for i in range(num_clips):
        try:
            # Get random audio clip
            randClass = np.random.choice(csv_files)

            if randClass in ("decoy", "flashbang", "smokegrenade", "hegrenade", "incgrenade", "molotov"):
                wavDirectorypath = "cs2 sounds/grenade/" + randClass
            else:
                wavDirectorypath = "cs2 sounds/" + randClass

            audio, clip_sr, class_name = getRandomClip(wavDirectorypath, "csv_output/" + randClass + ".csv")

            # Resample if necessary
            if clip_sr != sr:
                audio = librosa.resample(audio, orig_sr=clip_sr, target_sr=sr)

            # Extract random window of 40ms
            windowed_audio = getRandomTimeWindow(audio, window_time, sr)

            # For the first clip (i==0), don't shift - let it play the entire time
            # For subsequent clips, randomly shift start time
            if i == 0:
                # First clip: no shifting, ensure it plays for the full duration
                shifted_audio = windowed_audio
            else:
                # Other clips: randomly shift start time (shift between 1ms to 35ms within the 40ms window)
                shifted_audio = randomlyShiftAudioStartTime(
                    windowed_audio,
                    minShiftBy=0.001,
                    maxShiftBy=0.035,
                    total_time=window_time,
                    sr=sr
                )

            # Ensure consistent length
            shifted_audio = ensure_target_length(shifted_audio, int(window_time * sr))

            # Pad to total length (0.5s) with the shifted audio at the beginning
            final_audio = np.zeros(target_len)
            final_audio[:len(shifted_audio)] = shifted_audio

            # Generate random azimuth and elevation
            azimuth = myRand.pick_random_from_range(0, 360)
            elevation = myRand.pick_random_from_range(-80, 81)

            # Generate random audio level between 0.7 and 1.0
            audio_level = np.random.uniform(0.6, 1.0)

            # Create track object
            track = TrackObject(
                name=f"source_{i}",
                azimuth=azimuth,
                elevation=elevation,
                level=audio_level,
                reverb=0,
                audio=final_audio,
            )

            tracks.append(track)
            classes.append(class_name)
            azimuths.append(azimuth)
            elevations.append(elevation)

        except Exception as e:
            print(f"[ERROR] Clip {i} failed. Class choice might be invalid or file missing.")
            print(f"  Chosen class: {randClass}")
            print(f"  Expected CSV: csv_output/{randClass}.csv")
            print(f"  WAV directory: {wavDirectorypath}")
            print(f"  Exception: {e}")
            continue

    if not tracks:
        print(f"No valid tracks generated for sample {sample_id}")
        return None

    # Step 3: Mix tracks using binaural processing
    try:
        binaural_output = mix_tracks_binaural(
            tracks=tracks,
            subject_id='D1',
            sample_rate=sr,
            ir_type='HRIR',
            speaker_layout='none',
            mode="auto",
        )
    except Exception as e:
        print(f"Error in binaural mixing for sample {sample_id}: {e}")
        return None

    # Step 4: Add ambient background noise
    try:
        # Generate random dB level for background noise (between -45 to -25 dB)
        rmbs_db = -myRand.pick_random_from_range(25, 46)

        # Get ambient audio
        ambient_audio = get_random_ambient_audio(window_time, sr)

        if np.any(ambient_audio):  # If we have actual ambient audio (not just silence)
            # Apply background noise to both channels
            left_channel = binaural_output[0, :]
            right_channel = binaural_output[1, :]

            # Create temporary ambient file for audiomentations
            temp_ambient_file = "temp_ambient.wav"
            sf.write(temp_ambient_file, ambient_audio, sr)

            transform = AddBackgroundNoise(
                sounds_path=temp_ambient_file,
                noise_rms="absolute",
                min_absolute_rms_db=rmbs_db,
                max_absolute_rms_db=rmbs_db,
                noise_transform=PolarityInversion(),
                p=1.0
            )

            left_augmented = transform(samples=left_channel, sample_rate=sr)
            right_augmented = transform(samples=right_channel, sample_rate=sr)

            final_output = np.vstack([left_augmented, right_augmented])

            # Clean up temporary file
            if os.path.exists(temp_ambient_file):
                os.remove(temp_ambient_file)
        else:
            # No ambient audio available, use original binaural output
            final_output = binaural_output

    except Exception as e:
        print(f"Error adding background noise for sample {sample_id}: {e}")
        final_output = binaural_output

    # Step 5: Save audio file
    filename = f"sample_{sample_id:04d}.wav"
    filepath = os.path.join(output_dir, filename)

    try:
        sf.write(filepath, final_output.T, sr)
    except Exception as e:
        print(f"Error saving file {filepath}: {e}")
        return None

    # Step 6: Return metadata
    metadata = {
        'name_file': filename,
        'classes': ','.join(classes),
        'azimuth': ','.join(map(str, azimuths)),
        'elevation': ','.join(map(str, elevations)),
        'num_classes': len(classes)
    }

    return metadata


def create_augmented_dataset(dataset_size=50, output_dir="output/dataset"):
    """Create a complete augmented dataset with CSV metadata"""

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Validate that we have CSV output directory and files
    if not os.path.exists("csv_output"):
        print("Error: csv_output directory not found! Run create_csv.py first.")
        return

    # Check if at least some CSV files exist
    csv_files = ["ambient", "decoy", "doors", "footsteps", "flashbang", "hegrenade", "incgrenade", "molotov", "smokegrenade", "weapons"]
    existing_csvs = []
    for csv_name in csv_files:
        csv_path = f"csv_output/{csv_name}.csv"
        if os.path.exists(csv_path):
            existing_csvs.append(csv_name)

    if not existing_csvs:
        print("Error: No CSV files found in csv_output directory!")
        return

    print(f"Found CSV files for: {', '.join(existing_csvs)}")

    # Initialize metadata list
    all_metadata = []

    print(f"Generating {dataset_size} augmented audio samples...")

    for i in range(dataset_size):
        print(f"Processing sample {i+1}/{dataset_size}")

        metadata = generate_single_augmented_sample(i, output_dir)

        if metadata:
            all_metadata.append(metadata)
        else:
            print(f"Failed to generate sample {i}")

    # Create CSV file with all metadata
    if all_metadata:
        df = pd.DataFrame(all_metadata)
        csv_path = os.path.join(output_dir, "dataset_metadata.csv")
        df.to_csv(csv_path, index=False)

        print(f"Dataset creation complete!")
        print(f"Generated {len(all_metadata)} audio files")
        print(f"Metadata saved to: {csv_path}")
        print(f"Audio files saved to: {output_dir}")

        # Print some statistics
        print("\nDataset Statistics:")
        print(f"Average number of classes per sample: {df['num_classes'].mean():.2f}")
        print(f"Class distribution:")
        all_classes = []
        for classes_str in df['classes']:
            all_classes.extend(classes_str.split(','))
        class_counts = pd.Series(all_classes).value_counts()
        print(class_counts.to_string())

    else:
        print("No samples were successfully generated!")


if __name__ == "__main__":
    # Set random seed for reproducibility (optional)
    # myRand.seed(42)
    np.random.seed(100)

    print("Setting up audio augmentation pipeline...")


    print("Setup complete. Starting dataset generation...")

    # Create dataset
    create_augmented_dataset(dataset_size=600000)
