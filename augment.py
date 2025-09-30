import os
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import multiprocessing as mp
from functools import lru_cache
from typing import Dict, List, Tuple
from binamix.sadie_utilities import TrackObject, mix_tracks_binaural
import myRand
from randManipulateAudio import getRandomTimeWindow, randomlyShiftAudioStartTime

# ---------------------------
# Configuration
# ---------------------------
SR = 44100
WINDOW_TIME = 1  # 40 ms
TARGET_LEN_SAMPLES = int(WINDOW_TIME * SR)
MAX_CLIPS_PER_SAMPLE = 4

# Classes (fixed & cleaned)
CLASS_CSV_MAP = {
    "doors": ("cs2 sounds/doors", "csv_output/doors.csv"),
    "footsteps": ("cs2 sounds/footsteps", "csv_output/footsteps.csv"),
    "flashbang": ("cs2 sounds/grenade/flashbang", "csv_output/flashbang.csv"),
    "hegrenade": ("cs2 sounds/grenade/hegrenade", "csv_output/hegrenade.csv"),
    "incgrenade": ("cs2 sounds/grenade/incgrenade", "csv_output/incgrenade.csv"),
    "molotov": ("cs2 sounds/grenade/molotov", "csv_output/molotov.csv"),
    "smokegrenade": ("cs2 sounds/grenade/smokegrenade", "csv_output/smokegrenade.csv"),
    "weapons": ("cs2 sounds/weapons", "csv_output/weapons.csv"),
}

AMBIENT_DIR = "cs2 sounds/ambient"
AMBIENT_CSV = "csv_output/ambient.csv"


# ---------------------------
# CSV / metadata caching
# ---------------------------
@lru_cache(maxsize=None)
def load_csv(csv_path: str) -> pd.DataFrame:
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    return pd.read_csv(csv_path)


def get_random_clip_from_class(class_key: str) -> Tuple[np.ndarray, int, str]:
    """
    Returns (audio, sr, class_name)
    """
    directory, csv_path = CLASS_CSV_MAP[class_key]
    df = load_csv(csv_path)
    row = df.sample(1).iloc[0]
    audio_path = os.path.join(directory, row["name"])
    # Fast load
    audio, sr = sf.read(audio_path, always_2d=False)
    if audio.ndim > 1:
        # Mix to mono if stereo
        audio = np.mean(audio, axis=1)
    if sr != SR:
        # Faster resample option via librosa with kaiser_fast
        audio = librosa.resample(
            audio, orig_sr=sr, target_sr=SR, res_type="kaiser_fast"
        )
        sr = SR
    return audio, sr, row["class"]


# ---------------------------
# Ambient handling
# ---------------------------
def ensure_ambient_csv():
    if not os.path.exists(AMBIENT_CSV):
        if os.path.isdir(AMBIENT_DIR):
            ambient_files = [
                f for f in os.listdir(AMBIENT_DIR) if f.lower().endswith(".wav")
            ]
            if ambient_files:
                os.makedirs(os.path.dirname(AMBIENT_CSV), exist_ok=True)
                pd.DataFrame(
                    {"name": ambient_files, "class": ["ambient"] * len(ambient_files)}
                ).to_csv(AMBIENT_CSV, index=False)


@lru_cache(maxsize=1)
def list_ambient_files() -> List[str]:
    ensure_ambient_csv()
    if not os.path.exists(AMBIENT_CSV):
        return []
    df = pd.read_csv(AMBIENT_CSV)
    return [
        os.path.join(AMBIENT_DIR, n)
        for n in df["name"]
        if os.path.exists(os.path.join(AMBIENT_DIR, n))
    ]


def get_random_ambient_window(
    window_time: float = WINDOW_TIME, sr: int = SR
) -> np.ndarray:
    files = list_ambient_files()
    if not files:
        return np.zeros(int(window_time * sr), dtype=np.float32)
    path = np.random.choice(files)
    audio, file_sr = sf.read(path, always_2d=False)
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if file_sr != sr:
        audio = librosa.resample(
            audio, orig_sr=file_sr, target_sr=sr, res_type="kaiser_fast"
        )
    window = getRandomTimeWindow(audio, window_time, sr)
    if len(window) < int(window_time * sr):
        window = np.pad(window, (0, int(window_time * sr) - len(window)))
    return window.astype(np.float32)


# ---------------------------
# Utility
# ---------------------------
def ensure_length_exact(audio: np.ndarray, target: int) -> np.ndarray:
    if len(audio) > target:
        return audio[:target]
    elif len(audio) < target:
        return np.pad(audio, (0, target - len(audio)))
    return audio


def apply_random_start_shift(window_audio: np.ndarray, is_first: bool) -> np.ndarray:
    if is_first:
        return ensure_length_exact(window_audio, TARGET_LEN_SAMPLES)
    shifted = randomlyShiftAudioStartTime(
        window_audio, minShiftBy=0.001, maxShiftBy=0.8, total_time=WINDOW_TIME, sr=SR
    )
    return ensure_length_exact(shifted, TARGET_LEN_SAMPLES)


def scale_to_rms_db(x: np.ndarray, target_db: float) -> np.ndarray:
    # target_db is negative (e.g., -30)
    rms = np.sqrt(np.mean(x**2)) + 1e-12
    target_rms = 10.0 ** (target_db / 20.0)
    return x * (target_rms / rms)


def _match_length(arr: np.ndarray, target_len: int) -> np.ndarray:
    if len(arr) == target_len:
        return arr
    if len(arr) > target_len:
        return arr[:target_len]
    return np.pad(arr, (0, target_len - len(arr)))


# ---------------------------
# Core single-sample generation
# ---------------------------
def generate_single(sample_id: int, output_dir: str) -> Dict:
    num_clips = np.random.randint(1, MAX_CLIPS_PER_SAMPLE + 1)
    class_keys = list(CLASS_CSV_MAP.keys())

    tracks = []
    class_list = []
    az_list = []
    el_list = []

    for idx in range(num_clips):
        try:
            class_key = np.random.choice(class_keys)
            audio, sr, class_name = get_random_clip_from_class(class_key)

            # Extract 40ms window
            window_audio = getRandomTimeWindow(audio, WINDOW_TIME, SR)
            window_audio = ensure_length_exact(window_audio, TARGET_LEN_SAMPLES)
            shifted_audio = apply_random_start_shift(window_audio, is_first=(idx == 0))

            azimuth = myRand.pick_random_from_range(0, 360)
            elevation = myRand.pick_random_from_range(-80, 81)
            level = np.random.uniform(0.6, 1.0)

            track = TrackObject(
                name=f"source_{idx}",
                azimuth=azimuth,
                elevation=elevation,
                level=level,
                reverb=0,
                audio=shifted_audio,
            )
            tracks.append(track)
            class_list.append(class_name)
            az_list.append(azimuth)
            el_list.append(elevation)
        except Exception as e:
            print(f"[Worker] Error clip {idx} sample {sample_id}: {e}")
            continue

    if not tracks:
        return {}

    try:
        binaural = mix_tracks_binaural(
            tracks=tracks,
            subject_id="D1",
            sample_rate=SR,
            ir_type="HRIR",
            speaker_layout="none",
            mode="auto",
        )  # shape (2, N)
    except Exception as e:
        print(f"[Worker] Binaural mix error sample {sample_id}: {e}")
        return {}

    # Ambient addition (direct)
    try:
        b_len = binaural.shape[1]
        # Generate ambient window matching binaural duration
        ambient = get_random_ambient_window(window_time=b_len / SR, sr=SR)
        ambient = _match_length(ambient, b_len).astype(np.float32)
        if np.any(ambient):
            noise_db = -myRand.pick_random_from_range(25, 46)  # -25..-45
            ambient = scale_to_rms_db(ambient, noise_db)
            # Add (broadcast manually)
            binaural[0, :] += ambient
            binaural[1, :] += ambient
    except Exception as e:
        print(f"[Worker] Ambient add error sample {sample_id}: {e}")

    # Save file
    fname = f"sample_{sample_id:04d}.wav"
    fpath = os.path.join(output_dir, fname)
    try:
        sf.write(fpath, binaural.T, SR)
    except Exception as e:
        print(f"[Worker] Write error {fpath}: {e}")
        return {}

    return {
        "name_file": fname,
        "classes": ",".join(class_list),
        "azimuth": ",".join(map(str, az_list)),
        "elevation": ",".join(map(str, el_list)),
        "num_classes": len(class_list),
    }


# ---------------------------
# Multiprocessing wrapper
# ---------------------------
def _init_worker(seed_base: int):
    # Reseed RNG per process for full randomness
    np.random.seed(seed_base + os.getpid())


def create_dataset(
    dataset_size: int = 1000,
    output_dir: str = "output/dataset_parallel",
    parallel: bool = True,
    processes: int = None,
    chunk_size: int = 50,
):
    os.makedirs(output_dir, exist_ok=True)

    # Validate CSVs exist
    missing = [k for k, (d, c) in CLASS_CSV_MAP.items() if not os.path.exists(c)]
    if missing:
        print(f"Warning: Missing CSVs for: {missing}. They will never appear.")
    ensure_ambient_csv()

    indices = list(range(dataset_size))
    metadata_records = []

    if parallel:
        if processes is None:
            processes = max(1, mp.cpu_count() - 1)
        print(f"Starting multiprocessing with {processes} processes...")

        from functools import partial

        worker_fn = partial(generate_single, output_dir=output_dir)

        with mp.Pool(
            processes=processes,
            initializer=_init_worker,
            initargs=(np.random.randint(0, 10_000_000),),
        ) as pool:
            for md in pool.imap_unordered(worker_fn, indices, chunksize=chunk_size):
                if md:
                    metadata_records.append(md)
                    # Optional progress logging
                    if len(metadata_records) % 100 == 0:
                        print(
                            f"Progress: {len(metadata_records)}/{dataset_size} samples done"
                        )
    else:
        for sid in indices:
            md = generate_single(sid, output_dir)
            if md:
                metadata_records.append(md)
            if (sid + 1) % 100 == 0:
                print(f"Progress: {sid + 1}/{dataset_size}")

    if metadata_records:
        df = pd.DataFrame(metadata_records)
        csv_path = os.path.join(output_dir, "dataset_metadata.csv")
        df.to_csv(csv_path, index=False)
        print(f"Done. {len(df)} samples written. Metadata at {csv_path}")
        print(f"Avg classes per sample: {df['num_classes'].mean():.2f}")
    else:
        print("No samples generated successfully.")


if __name__ == "__main__":
    np.random.seed(1234)
    create_dataset(
        dataset_size=100,
        output_dir="output/dataset_parallel",
        parallel=True,
        processes=None,
        chunk_size=64,
    )
