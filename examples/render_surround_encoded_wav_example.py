# Imports
import pandas as pd
import librosa
import soundfile as sf
from binamix.sadie_utilities import *
from binamix.file_utilities import *

# Configure Audio path and SADIE Subject Data
# audio_path = "audio/Macbeth_7_1_4.wav"

# Download the audio file
audio_url = "https://zenodo.org/record/10571315/files/Macbeth_7_1_4.wav"
destination_folder = "./audio/"
audio_file_path = os.path.join(destination_folder, "Macbeth_7_1_4.wav")

if not os.path.exists(audio_file_path):
    downloaded_file = download_file(audio_url, destination_folder)
else:
    print(f"File already exists at {audio_file_path}")

audio_path = "./audio/Macbeth_7_1_4.wav"
output_path = "./output/"

subject_id = "D2" 
ir_type = "HRIR"        # Options HRIR, BRIR *note that BRIR does not have the necessary angles for a direct binaural render

input_layout = "7.1.4"    # The actual channel layout of the input audio file
render_layout = "7.1.4"   # The layout that you want to render the audio to. Normally the same as the input_layout but can be any layout with a lower number of channels.

# Load the surround audio file. Dolby Channel ordering is assumed for the input audio file                           
surround_container, sr = librosa.load(f"{audio_path}", sr=48000, mono=False)

# Call the render_surround_to_binaural function. You must specify the correct input_layout associated with the input audio file.
# The render_layout is the layout that you want to render the audio to. Normally the same as the input_layout but can be any layout with a lower number of channels.
# The output is the binaural render of the input surround audio file.
output, sr = render_surround_to_binaural(surround_container, sr, subject_id, ir_type, input_layout, render_layout, mode="auto")


# Save the output
sf.write(f"{output_path}direct_binaural_render.wav", output.T, sr)


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

