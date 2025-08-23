import os
import argparse
import pandas as pd
import librosa
import soundfile as sf
from datetime import datetime

"""
Dataset generator: renders each input WAV as binaural audio over a 10x10 grid of
azimuth and elevation values using Binamix HRIR (subject D1, HRIR, layout "none").

Angles:
- Azimuths: 10 values, 0..324 in 36° steps (0, 36, ..., 324)
- Elevations: 10 values, [-90, -70, -50, -30, -10, 0, 10, 30, 50, 70]

Outputs are saved under output/dataset/<relative_input_dir>/<stem>_az{azi}_el{ele}.wav
and a single CSV index is written to output/dataset_index.csv.
"""

DEFAULT_INPUT_DIRS = [
    "sounds/grenade",
    "sounds/footsteps",
    "sounds/weapons",
]

OUTPUT_ROOT = "output"


def build_angle_grids():
    # Azimuth: 0..324 inclusive, step 36 (10 values)
    azimuths = list(range(0, 360, 36))
    # Elevation: 10 values in 18° steps across 180° span; start at -90 and exclude +90 to keep count 10
    elevations = [-90 + 18 * k for k in range(10)]  # [-90, -72, ..., 72]
    return azimuths, elevations


def find_wav_files(input_paths):
    files = []
    for base in input_paths:
        if os.path.isfile(base) and base.lower().endswith(".wav"):
            files.append(os.path.abspath(base))
        elif os.path.isdir(base):
            for root, _, filenames in os.walk(base):
                for fn in filenames:
                    if fn.lower().endswith(".wav"):
                        files.append(os.path.abspath(os.path.join(root, fn)))
    return sorted(files)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def render_variations_for_file(
    file_path,
    subject_id,
    sample_rate,
    ir_type,
    speaker_layout,
    level,
    reverb,
    azimuths,
    elevations,
    output_dataset_root,
    dry_run=False,
):
    # Keep the input's directory structure under the dataset root
    rel_parent = os.path.dirname(os.path.relpath(file_path, start=os.path.abspath(".")))

    out_dir = os.path.join(output_dataset_root, rel_parent)
    ensure_dir(out_dir)

    rows = []

    if dry_run:
        mono_audio = None
        sr = sample_rate
    else:
        mono_audio, sr = librosa.load(file_path, sr=sample_rate, mono=True)

    stem = os.path.splitext(os.path.basename(file_path))[0]

    for ele in elevations:
        for azi in azimuths:
            out_name = f"{stem}_az{int(azi)}_el{int(ele)}.wav"
            out_path = os.path.join(out_dir, out_name)

            if not dry_run:
                # Import HRIR engine lazily to avoid requiring SADIE dataset during dry runs
                from binamix.sadie_utilities import TrackObject, mix_tracks_binaural
                track = TrackObject(
                    name="positioned_source",
                    azimuth=azi,
                    elevation=ele,
                    level=level,
                    reverb=reverb,
                    audio=mono_audio,
                )
                output = mix_tracks_binaural(
                    tracks=[track],
                    subject_id=subject_id,
                    sample_rate=sr,
                    ir_type=ir_type,
                    speaker_layout=speaker_layout,
                    mode="auto",
                )
                sf.write(out_path, output.T, sr)

            rows.append(
                {
                    "input_file": file_path,
                    "output_file": out_path,
                    "subject_id": subject_id,
                    "ir_type": ir_type,
                    "speaker_layout": speaker_layout,
                    "sample_rate": sample_rate,
                    "level": level,
                    "reverb": reverb,
                    "azimuth_deg": azi,
                    "elevation_deg": ele,
                }
            )

    return rows


def parse_args():
    parser = argparse.ArgumentParser(description="Generate a labeled binaural dataset over azimuth/elevation grids.")
    parser.add_argument(
        "--inputs",
        nargs="*",
        default=DEFAULT_INPUT_DIRS,
        help="Input WAV files or directories (recursively scanned). Defaults to 'sounds'.",
    )
    parser.add_argument("--subject", default="D1", help="SADIE subject id (D1, D2, H3..H20). Default: D1")
    parser.add_argument("--sr", type=int, default=44100, help="Sample rate for processing. Default: 44100")
    parser.add_argument("--ir_type", default="HRIR", choices=["HRIR", "BRIR"], help="IR type. Default: HRIR")
    parser.add_argument(
        "--layout",
        default="none",
        help="Speaker layout for angle availability (use 'none' for full sphere). Default: none",
    )
    parser.add_argument("--level", type=float, default=0.8, help="Output track level scaling [0..1]. Default: 0.8")
    parser.add_argument("--reverb", type=float, default=0.0, help="Reverb mix [0..1]. Default: 0.0")
    parser.add_argument("--dry-run", action="store_true", help="Do not render audio, only emit metadata plan.")
    parser.add_argument(
        "--max-files",
        type=int,
        default=None,
        help="Limit the number of input files processed (useful for quick checks).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    azimuths, elevations = build_angle_grids()

    input_files = find_wav_files(args.inputs)
    if args.max_files is not None:
        input_files = input_files[: args.max_files]

    dataset_root = os.path.join(OUTPUT_ROOT, "dataset")
    ensure_dir(dataset_root)

    all_rows = []
    print(f"Found {len(input_files)} input WAV file(s). Rendering {len(azimuths)} azimuths x {len(elevations)} elevations each.")
    for idx, wav_path in enumerate(input_files, 1):
        print(f"[{idx}/{len(input_files)}] Processing: {wav_path}")
        rows = render_variations_for_file(
            file_path=wav_path,
            subject_id=args.subject,
            sample_rate=args.sr,
            ir_type=args.ir_type,
            speaker_layout=args.layout,
            level=args.level,
            reverb=args.reverb,
            azimuths=azimuths,
            elevations=elevations,
            output_dataset_root=dataset_root,
            dry_run=args.dry_run,
        )
        all_rows.extend(rows)

    index_path = os.path.join(OUTPUT_ROOT, "dataset_index.csv")
    df = pd.DataFrame(all_rows)
    df.insert(0, "created_at", datetime.utcnow().isoformat())
    df.to_csv(index_path, index=False)
    print(f"Wrote metadata index: {index_path}")
    if args.dry_run:
        print("Dry run complete. No audio rendered.")


if __name__ == "__main__":
    main()
