# Imports
import pandas as pd
import librosa
import soundfile as sf
from binamix.sadie_utilities import *

# Configure Audio path and SADIE Subject Data
audio_path = "./audio/musdb18_samples/"
output_path = "./output/"
song_id = "Angels In Amplifiers - I'm Alright" 
subject_id = "D2" 
ir_type = "HRIR" # Options HRIR, BRIR
speaker_layout = "none" # Options none, 5.1, 7.1, 7.1.4, 5.1.4 etc... run surround.supported_layouts() to see all supported layouts

# Load the audio files
bass, sr = librosa.load(f"{audio_path}{song_id}/bass.wav", sr=44100, mono=True, duration=10)
drums, sr = librosa.load(f"{audio_path}{song_id}/drums.wav", sr=44100, mono=True, duration=10)
other, sr = librosa.load(f"{audio_path}{song_id}/other.wav", sr=44100, mono=True, duration=10)
vocals, sr = librosa.load(f"{audio_path}{song_id}/vocals.wav", sr=44100, mono=True, duration=10)

# Setup your mix parameters

# Level         0 - 1     
# Reverb        0 - 1
# Azimuth       0 - 360 (anti-clockwise) but also accepts negative values
# Elevation     0 - 360  but also accepts negative values

track1 = TrackObject(name="bass", azimuth=0, elevation=0, level=0.8, reverb=0.0, audio=bass)
track2 = TrackObject(name="drums", azimuth=-60, elevation=0, level=0.4, reverb=0.0 , audio=drums)
track3 = TrackObject(name="other", azimuth=140, elevation=0, level=0.2, reverb=0.0 , audio=other)
track4 = TrackObject(name="vocals", azimuth=30, elevation=45, level=0.32, reverb=0.5, audio=vocals)

# Place all TrackObject tracks in an array for mixdown
tracks = [track1, track2, track3, track4]

# Mix the tracks
output = mix_tracks_binaural(tracks, subject_id, sr, ir_type, speaker_layout, mode="auto", reverb_type="1")

# -----------------------------------------------------

# Optional: Save the output
sf.write(f"{output_path}{song_id}_{subject_id}_{ir_type}_layout={speaker_layout}_binaural_mixture.wav", output.T, sr)



# Optional: Write track mix parameters to a csv file
df = pd.DataFrame([{
    'name': track.name,
    'azimuth': track.azimuth,
    'elevation': track.elevation,
    'level': track.level,
    'reverb': track.reverb,
    'audio_path': f"{audio_path}{song_id}/{track.name}.wav"
} for track in tracks])
df.to_csv(f"{output_path}{song_id}_{subject_id}_{ir_type}_layout={speaker_layout}_binaural_mixture.csv")

# -----------------------------------------------------

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