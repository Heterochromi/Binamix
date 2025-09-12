import pandas as pd
import soundfile as sf
import numpy as np
import os

def verify_dataset(dataset_dir="output/dataset"):
    """Verify the generated dataset integrity"""

    # Check if directory exists
    if not os.path.exists(dataset_dir):
        print(f"Error: Dataset directory {dataset_dir} does not exist!")
        return False

    # Check if CSV exists
    csv_path = os.path.join(dataset_dir, "dataset_metadata.csv")
    if not os.path.exists(csv_path):
        print(f"Error: Metadata CSV {csv_path} does not exist!")
        return False

    # Load metadata
    df = pd.read_csv(csv_path)
    print(f"Dataset contains {len(df)} samples")
    print(f"Columns: {list(df.columns)}")

    # Verify CSV structure
    expected_columns = ['name_file', 'classes', 'azimuth', 'elevation', 'num_classes']
    if list(df.columns) != expected_columns:
        print(f"Warning: Unexpected columns. Expected: {expected_columns}")

    # Check first few samples
    print("\nFirst 5 samples:")
    print(df.head().to_string())

    # Verify audio files exist and have correct properties
    missing_files = []
    corrupt_files = []

    print(f"\nVerifying audio files...")
    for i, row in df.iterrows():
        audio_path = os.path.join(dataset_dir, row['name_file'])

        if not os.path.exists(audio_path):
            missing_files.append(row['name_file'])
            continue

        try:
            # Load audio file
            audio, sr = sf.read(audio_path)

            # Check properties
            if sr != 44100:
                print(f"Warning: {row['name_file']} has sample rate {sr}, expected 44100")

            if len(audio.shape) != 2 or audio.shape[1] != 2:
                print(f"Warning: {row['name_file']} is not stereo")

            if audio.shape[0] != int(0.5 * sr):
                print(f"Warning: {row['name_file']} duration is {audio.shape[0]/sr:.3f}s, expected 0.5s")

        except Exception as e:
            corrupt_files.append((row['name_file'], str(e)))

    # Report results
    if missing_files:
        print(f"\nMissing files ({len(missing_files)}):")
        for f in missing_files[:5]:  # Show first 5
            print(f"  - {f}")
        if len(missing_files) > 5:
            print(f"  ... and {len(missing_files) - 5} more")

    if corrupt_files:
        print(f"\nCorrupt files ({len(corrupt_files)}):")
        for f, err in corrupt_files[:5]:  # Show first 5
            print(f"  - {f}: {err}")
        if len(corrupt_files) > 5:
            print(f"  ... and {len(corrupt_files) - 5} more")

    # Statistics
    print(f"\nDataset Statistics:")
    print(f"  Total samples: {len(df)}")
    print(f"  Missing audio files: {len(missing_files)}")
    print(f"  Corrupt audio files: {len(corrupt_files)}")
    print(f"  Valid samples: {len(df) - len(missing_files) - len(corrupt_files)}")

    # Class distribution
    print(f"\nClass distribution:")
    all_classes = []
    for classes_str in df['classes']:
        all_classes.extend(classes_str.split(','))

    class_counts = pd.Series(all_classes).value_counts()
    print(class_counts.to_string())

    # Number of classes per sample
    print(f"\nNumber of classes per sample:")
    num_classes_dist = df['num_classes'].value_counts().sort_index()
    print(num_classes_dist.to_string())

    # Azimuth and elevation ranges
    print(f"\nSpatial distribution:")
    all_azimuths = []
    all_elevations = []

    for az_str, el_str in zip(df['azimuth'], df['elevation']):
        all_azimuths.extend([int(x) for x in az_str.split(',')])
        all_elevations.extend([int(x) for x in el_str.split(',')])

    print(f"  Azimuth range: {min(all_azimuths)} to {max(all_azimuths)} degrees")
    print(f"  Elevation range: {min(all_elevations)} to {max(all_elevations)} degrees")

    # Success rate
    success_rate = (len(df) - len(missing_files) - len(corrupt_files)) / len(df) * 100
    print(f"\nDataset integrity: {success_rate:.1f}%")

    return success_rate > 95

if __name__ == "__main__":
    success = verify_dataset()
    if success:
        print("\n✅ Dataset verification PASSED")
    else:
        print("\n❌ Dataset verification FAILED")
