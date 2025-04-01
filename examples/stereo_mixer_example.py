# Imports
import pandas as pd
import librosa
import soundfile as sf
from binamix.sadie_utilities import *

# Configure path and SADIE Subject Data
audio_path = "./audio/musdb18_samples/"
output_path = "./output/"
song_id = "Angels In Amplifiers - I'm Alright"


# Load the audio files
bass, sr = librosa.load(f"{audio_path}{song_id}/bass.wav", sr=44100, mono=True, duration=10)
drums, sr = librosa.load(f"{audio_path}{song_id}/drums.wav", sr=44100, mono=True, duration=10)
other, sr = librosa.load(f"{audio_path}{song_id}/other.wav", sr=44100, mono=True, duration=10)
vocals, sr = librosa.load(f"{audio_path}{song_id}/vocals.wav", sr=44100, mono=True, duration=10)

# Setup your mix parameters

# Level:    0 to 1     
# Reverb:   0 to 1
# Pan:      (-1) to (1) where -1 is left, 0 is center, 1 is right

track1 = TrackObject(name="bass", pan=-0.25, level=0.95, reverb=0.0, audio=bass)
track2 = TrackObject(name="drums", pan=0.25, level=0.95, reverb=0.2 , audio=drums)
track3 = TrackObject(name="other", pan=0.75, level=0.95, reverb=0.0 , audio=other)
track4 = TrackObject(name="vocals", pan=0, level=0.5, reverb=0.1, audio=vocals)

# Place all tracks for mixdown in an array
tracks = [track1, track2, track3, track4]

# Mix the tracks
output = mix_tracks_stereo(tracks, sr, reverb_type="1")

# -----------------------------------------------------

# Save the output
sf.write(f"{output_path}{song_id}_stereo_mixture.wav", output.T, sr)

# Write track mix parameters to a csv file
df = pd.DataFrame([{
    'name': track.name,
    'pan': track.pan,
    'level': track.level,
    'reverb': track.reverb,
    'audio_path': f"{audio_path}{song_id}/{track.name}.wav"
} for track in tracks])
df.to_csv(f"{output_path}{song_id}_stereo_mixture.csv")

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