# This example script allows you to generate binaural audio datasets for use in model training for example
# Given a directory of audio files, it will generate a dataset of binaural audio renderings of the files at every angle available.
# This example script only uses actual discrete angles available in the SADIE dataset and does not apply any interpolation.

#!/usr/bin/env python3

# Imports
from IPython.display import Audio
import matplotlib.pyplot as plot
import numpy as np
import pandas as pd
import librosa
import soundfile as sf
from binamix.sadie_utilities import *
import os

# -----------------------------------------------------
# CONFIGURE THE SCRIPT HERE

# Set input and output paths for audio files
filepath = "./audio/"
outpath = "./output/"

# Array to store the label data
data = []

# Set the sample rate for processing (44100, 48000, 96000) - Your files will automatically be loaded at this sample rate
sample_rate = 44100

# Set the sample rate for the output files
output_sample_rate = 44100

# Specify all the subjects and IR types you want to generate
# subjects = ["D1", "D2", "H3" , "H4", "H5", "H6", "H7", "H8", "H9", "H10", "H11", "H12", "H13", "H14", "H15", "H16", "H17", "H18", "H19", "H20"]
# ir_types = ["HRIR", "BRIR"]

# TESTING - Use only one subject and ir type for testing - uncomment above for full dataset
subjects = ["H3"]
ir_types = ["BRIR"]

# -----------------------------------------------------

angle_irs = [] # Array for angle IRs

# Collect all .wav files in the folder
wav_files = [file_name for file_name in os.listdir(filepath) if file_name.endswith(".wav")]

# TESTING - Use only the first file for testing
wav_files = [wav_files[0]]

# Process collected files
for file_name in wav_files:

    # Load the audio file using the IR sample rate
    input_file_name = f"{filepath}{file_name}"
    input_file , sr = librosa.load(input_file_name, sr=sample_rate, mono=True)

    for ir_type in ir_types:

        for subject in subjects:
          
            angle_path = select_sadie_wav_subject(subject, sample_rate, ir_type)
            angle_irs = [angle_ir for angle_ir in os.listdir(angle_path) if angle_ir.endswith(".wav")]

            for angle_ir in angle_irs:

                print(f"Generating {subject} {ir_type} {file_name[:-4]} {angle_ir} ")
                
                angle_file = f"{angle_path}{angle_ir}"

                # Load the IR
                ir , sr = librosa.load(angle_file, sr=None, mono=False) 

                # Convolve the audio file with the IRs
                ir_left = ir[0]
                ir_right = ir[1]

                # Convolve the input audio with the corresponding left and right IR and create stereo file
                output = np.convolve(input_file, ir_left)
                output = np.vstack([output , np.convolve(input_file, ir_right)])

                # Save the binaural output to a wav file
                output_file_name = f"{outpath}{file_name[:-4]}_{subject}_{ir_type}_{angle_ir}"
                sf.write(output_file_name, output.T, output_sample_rate) 
                          
                # Update the CSV with the path and label data
                azimuth , elevation = extract_azimuth_elevation(angle_ir)
                output_file_name = output_file_name.split("/")[-1]

                has_elevation = 1 if elevation != 0 else 0
                ir_path = angle_file.split("Sadie/")[-1]

                data.append({
                    'file_name': output_file_name,
                    'azimuth': azimuth,
                    'elevation': elevation,
                    'subject': subject,
                    'ir_type': ir_type,
                    'has_elevation': has_elevation,
                    'output_sample_rate': output_sample_rate,
                    'processing_sample_rate': sample_rate,
                    'ir_file': ir_path


                })


# Create the DataFrame from the collected data
df = pd.DataFrame(data)

df.to_csv(f'{outpath}label_data.csv', index=False)

# Display the first few rows of the DataFrame
print(df.head())












   





















