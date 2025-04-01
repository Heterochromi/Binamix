# Imports
import pandas as pd
import librosa
import soundfile as sf
from binamix.sadie_utilities import *


# Configure path and SADIE Subject Data
audio_path = "./audio/musdb18_samples/"
output_path = "./output/"
song_id = "Angels In Amplifiers - I'm Alright"
subject_id = "D2" 
ir_type = "HRIR" # Options HRIR, BRIR
speaker_layouts = ["none","5.1","7.1","5.1.4","7.1.4"]
# speaker_layouts = ["none","5.1"]

# Load the audio files
bass, sr = librosa.load(f"{audio_path}{song_id}/bass.wav", sr=44100, mono=True, duration=10)
drums, sr = librosa.load(f"{audio_path}{song_id}/drums.wav", sr=44100, mono=True, duration=10)
other, sr = librosa.load(f"{audio_path}{song_id}/other.wav", sr=44100, mono=True, duration=10)
vocals, sr = librosa.load(f"{audio_path}{song_id}/vocals.wav", sr=44100, mono=True, duration=10)

# Setup your mix parameters

# Level 0 - 1     
# Reverb 0 - 1
# Azimuth 0 - 360 (anti-clockwise) but also accepts negative values
# Elevation 0 - 360  but also accepts negative values

track1 = TrackObject(name="bass", azimuth=0, elevation=0, level=0.2, reverb=0.0, audio=bass)
track2 = TrackObject(name="drums", azimuth=-60, elevation=0, level=0.1, reverb=0.0, audio=drums)
track3 = TrackObject(name="other", azimuth=140, elevation=0, level=0.05, reverb=0.0, audio=other)
track4 = TrackObject(name="vocals", azimuth=40, elevation=45, level=0.12, reverb=0.0, audio=vocals)

# Place all tracks for mixdown in an array
tracks = [track1, track2, track3, track4]

# ----------------- Mix for all layouts -----------------

# Slug for the filename... example: "mixture(no_elevation)" or "mixture(with_elevation)"
name = "binaural_mixture"

for speaker_layout in speaker_layouts:
    # Mix the tracks

    print(f"Mixing for layout: {speaker_layout}")
    output = mix_tracks_binaural(tracks, subject_id, sr, ir_type, speaker_layout, mode="auto", reverb_type="1")

    # Save the output
    sf.write(f"{output_path}{song_id}_{subject_id}_{ir_type}_layout={speaker_layout}_{name}.wav", output.T, sr)

    # Write track mix parameters to a csv file
    df = pd.DataFrame([{
        'name': track.name,
        'azimuth': track.azimuth,
        'elevation': track.elevation,
        'level': track.level,
        'reverb': track.reverb,
        'audio_path': f"{audio_path}{song_id}/{track.name}.wav"
    } for track in tracks])
    df.to_csv(f"{output_path}{song_id}_{subject_id}_{ir_type}_layout={speaker_layout}_{name}.csv")

    # Optional - Show an audio player widget in the interactive window if IPython is available
    try:
        from IPython.display import Audio, display
        ipython_available = True
    except ImportError:
        ipython_available = False

    if ipython_available:
        display(Audio(output, rate=sr))
        print("Audio output(s) have been saved to:", f"{output_path}")
    else:
        print("IPython is not available. Audio cannot be played.")
        print("Audio output(s) have been saved to:", f"{output_path}")
   