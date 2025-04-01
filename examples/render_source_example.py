# Imports
import librosa
import soundfile as sf
from binamix.sadie_utilities import *


# Configure path to Audio and SADIE Subject Data
audio_path = "./audio/castanets.wav"
output_path = "./output/"

subject_id = "D2" 
ir_type = "HRIR"            # Options HRIR, BRIR
speaker_layout = "5.1.4"    # Options none, 5.1, 7.1, 7.1.4, 5.1.4, 9.1, 9.1.2, 9.1.4 etc
azimuth = 90
elevation = 20
mode = "nearest"            # Options: nearest, planar, two-point, three-point, auto

# Load the audio files
vocals, sr = librosa.load(audio_path, sr=44100, mono=True, duration=10)

# Render a single source at a given azimuth and elevation
output = render_source(vocals, subject_id, sr, ir_type, speaker_layout, azimuth, elevation, mode=mode)

# Gets the available angles for the given subject, sample rate, IR type, and speaker layout.
available_angles = get_available_angles(subject_id, 44100, ir_type, speaker_layout)

# Gets the nearest available angles to the given azimuth and elevation using Delaunay triangulation.
if has_elevation_speakers(speaker_layout):
    triangulation = delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=True)



# -----------------------------------------------------

audio_filename = audio_path.split("/")[-1]
audio_filename = audio_filename.split(".")[0]

# Save the output
sf.write(f"{output_path}{audio_filename}_{subject_id}_{ir_type}_layout={speaker_layout}_interp={mode}.wav", output.T, sr)


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