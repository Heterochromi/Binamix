# This example script shows how to generate transcodes of an audio file using the Opus codec at different bitrates.

# Imports
from binamix.opus_transcode_utilities import generate_transcodes

# Path to audio file
input_path = "./audio/vega.wav"
output_path = "./output/"

# Generate transcodes
generate_transcodes(input_path, output_path)

# The script will generate the following files in the same folder as the input file:
# example_opus32k.wav
# example_opus64k.wav
# example_opus128k.wav
# example_opus256k.wav
# example_opus512k.wav





# -----------------------------------------------------

