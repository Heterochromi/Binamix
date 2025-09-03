#This is not meant for maintenance i am simply trying this tool please go to the original repo.


# Binamix - A Binaural Data Generation Library

This library contains a set of pipeline tools for programmatic binaural mixing using the [SADIE II Database](https://www.york.ac.uk/sadie-project/database.html). The tools include functions for binaurally mixing and rendering sources for any given azimuth and elevation using weighted IR interpolation where needed. The library can also simulate channel encoded surround sound speaker layouts. When using a speaker layout for binaural rendering, the tools will use interpolation methods which simulate the VBAP method to render the source at the virtual speaker position. This allows you to create simulated surround mixes (binaurally rendered) for any given speaker layout.

The library also provides functions to binaurally render multichannel surround encoded .wav files. The tools will automatically map the surround channels to the correct binaural positions based on the speaker layout definitions in `surround_utilities.py`. Current supported speaker layouts are: ['7.1', '7.1.4', '7.1.2', '5.1', '5.1.4', '5.1.2', '9.1.4', '9.1.2', '9.1'] but you can also define your own.

The library also includes helper functions for loading IR data, selecting file paths, extracting angles from filenames, checking angle availability and many others described below. You can use these functions to create your own custom pipelines.

<br>
The Binamix code is licensed under MIT license. Dependencies of the project are available under separate license terms.

<br>

## Citation
You can read the paper here: [arXiv:2505.01369](https://arxiv.org/abs/2505.01369)

```bibtex
@misc{barry2025binamixpythonlibrary,
      title={Binamix - A Python Library for Generating Binaural Audio Datasets}, 
      author={Dan Barry and Davoud Shariat Panah and Alessandro Ragano and Jan Skoglund and Andrew Hines},
      year={2025},
      eprint={2505.01369},
      journal={arXiv preprint arXiv:2505.01369},
      archivePrefix={arXiv},
      primaryClass={cs.SD},
      url={https://arxiv.org/abs/2505.01369}, 
}
```



# Setup
- Install the required packages by running `pip install -r requirements.txt` 
- Download and unzip the SADIE II Database by running `python -m binamix.sadie_db_setup`

- ## Optional
- Run the `python -m binamix.musdb18_setup` script to download and unzip the musDB18 audio stem database. This file is 22Gb and is only included here as a potential dataset to use with Binamix. The example scripts use a small subset of the musDB18 dataset which is already included in this repo.
- Add the path to opusenc and opusdec binaries in the `binamix/opus_transcode_utilities.py` file. *OSX and Windows binaries are already included in this repo
    
<br>

## Table of Contents
- [What can you use this library for?](#what-can-you-use-this-library-for)
- [Example Scripts](#example-scripts)
- [API Documentation](#api-documentation)
    - Main Functions
        - [render_source](#render_source) (audio_input, subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto")
        - [generate_sadie_ir](#generate_sadie_ir) (subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto", verbose=True)
        - [mix_tracks_binaural](#mix_tracks_binaural) (tracks, subject_id, sample_rate, ir_type, speaker_layout, mode="auto", reverb_type = "1")
        - [mix_tracks_stereo](#mix_tracks_stereo) (tracks, sample_rate, reverb_type = "1")
        - [render_surround_to_binaural](#render_surround_to_binaural) (surround_container, sr, subject_id, ir_type, input_layout, render_layout, mode="auto")
        - [surround.supported_layouts](#surroundsupported_layouts)
        - [surround.get_channel_angles](#surroundget_channel_angles) (layout)
    - Helper Functions
        - [load_sadie_ir](#load_sadie_ir) (subject_id, sample_rate, ir_type, azimuth, elevation)
        - [delaunay_triangulation](#delaunay_triangulation) (available_angles, azimuth, elevation, speaker_layout, plots=True)
        - [get_available_angles](#get_available_angles) (subject_id, sample_rate, ir_type, speaker_layout)
        - [get_nearest_angle](#get_nearest_angle) (subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)
        - [get_angle_distance](#get_angle_distance) (azimuth1, elevation1, azimuth2, elevation2)
        - [angle_exists](#angle_exists) (subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)
        - [get_nearest_elevation_angle](#get_nearest_elevation_angle) (subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)
        - [has_elevation_speakers](#has_elevation_speakers) (speaker_layout)
        - [get_elevation_range](#get_elevation_range) (available_angles)
        - [get_planar_neighbours](#get_planar_neighbours) (available_angles, azimuth, elevation, verbose=True)
        - [spherical_to_cartesian](#spherical_to_cartesian) (azimuth, elevation)
        - [cartesian_to_spherical](#cartesian_to_spherical) (x, y, z)
        - [construct_wav_filename](#construct_wav_filename) (azimuth, elevation)
        - [extract_azimuth_elevation](#extract_azimuth_elevation) (filename)
        - [pan_source](#pan_source) (pan, input_file)
        - [select_sadie_wav_subject](#select_sadie_wav_subject) (subject_id, sample_rate, file_type)
        - [select_sadie_sofa_subject](#select_sadie_sofa_subject) (subject_id, sample_rate, file_type)
    - Definitions
        - [Subject ID](#subject-id)
        - [IR Type](#ir-type)
        - [Speaker Layout](#speaker-layout)
        - [Azimuth](#azimuth)
        - [Elevation](#elevation)
        - [Mix Parameters](#mix-parameters)


<br>

## What can you use this library for?
- Generate binaural and stereo mixes for general testing and evaluation.
- Generate binaural mixes from stems (using `mix_tracks_binaural`) or multichannel surround encoded files using `render_surround_to_binaural`.
- Simulate various binaural reference and test conditions for audio codec creation and evaluation.
- Simulate various binaural reference and test conditions for audio quality metric creation and evaluation.
- Any task that requires programmatic and repeatable binaural mixing or rendering with the SADIE II Database.
- Generate large amounts of simulated real-world binaural source renders or binaural mix renders for training machine learning models. You can create large representative training datasets with a variety of conditions for:
    - [Subject ID](#subject-id) (e.g., D1, D2, H3, H4, H5 ... H20)
    - [IR Type](#ir-type) (HRIR or BRIR)
    - [Speaker Layout](#speaker-layout) (e.g., none, 5.1, 7.1, 7.1.4)
    - [Azimuth](#azimuth)
    - [Elevation](#elevation)
    - [Mix Parameters](#mix-parameters) (level, reverb, pan)
    - [Sample Rate](#sample-rate) (e.g., 44100, 48000, 96000)
    - [Audio Content](#audio-content) (any audio you want to mix or render)

<br>


## Example Scripts
The following scripts demonstrate how to use the library for various tasks and might serve as a useful template for your own projects:

- [binaural_mixer_example.py](examples/binaural_mixer_example.py) - Basic example of binaural mixing with 4 tracks.
- [render_surround_encoded_wav_example.py](examples/render_surround_encoded_wav_example.py) - Example of rendering a multichannel surround mix to binaural.
- [stereo_mixer_example.py](examples/stereo_mixer_example.py) - Basic example of stereo mixing with 4 tracks.
- [mix_for_all_speaker_layouts_example.py](examples/mix_for_all_speaker_layouts_example.py) - Render a single mix for all available speaker layouts.
- [opus_transcodes_example.py](examples/opus_transcodes_example.py) - Transcode audio files to opus format.
- [triangulation_with_plot_example.py](examples/triangulation_with_plot_example.py) - Example of Delaunay triangulation with plot.
- [generate_binaural_dataset_example.py](examples/generate_binaural_dataset_example.py) - Example of generating a binaural dataset 

To run, use: `python -m examples.name_of_example`
<br><br>

# API Documentation

[Back Table of Contents](#table-of-contents)
## render_source
```render_source(audio_input, subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto")```

**Description**: Binaurally renders a source for a given subject, sample rate, IR type, speaker layout, azimuth, and elevation, for an audio input. It uses the [generate_sadie_ir](#generate_sadie_ir) function to retrieve or generate the necessary IR data and then convolves the input audio with the IR data to render the source. Various angle interpolation methods are available depending on the applicaiton. the default interpolation setting is "auto" and will choose the best method based on desired angle and available angles.

**Interpolation Modes** 
- `auto`: Automatically selects the best interpolation method.
- `nearest`: Uses the nearest available discrete angle without interpolation.
- `planar`: Uses the nearest neighbours on the closest elevation plane.
- `two_point`: Uses two-point weighted interpolation. Automatically chooses between azimuth or elevation interpolation based on the speaker layout.
- `three_point`: Uses three-point weighted interpolation.

**Parameters**:

- `audio_input` (numpy array): Input audio file.
- `subject_id` (str): Identifier for the subject. (e.g., D1, D2, H3, H4, H5 ... H20).
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): IR type ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4', 'none').
- `azimuth` (float): Azimuth angle.
- `elevation` (float): Elevation angle.
- `mode` (str): Interpolation mode. Options are ('auto', 'nearest', 'planar', 'two_point', 'three_point'). Default is 'auto'.


**Usage Example**:
```python
output = render_source(input_audio, 'D1', 48000, 'BRIR', '7.1', 90.0, 0.0, mode="auto")
```

<br>

[Back Table of Contents](#table-of-contents)
## generate_sadie_ir
```generate_sadie_ir(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation, mode="auto", verbose=True)```

**Description**: Retrieves a discrete IR or generates an interpolated IR (where necessary) for a specified subject, sample rate, IR type, speaker layout, azimuth, and elevation. The function uses a modified Delaunay triangulation method to find the discrete angles which enclose the desired angle in 3D speaker layout and uses nearest planar neighbours in 2D speaker layouts.

**Interpolation Modes** 
- `auto`: Automatically selects the best interpolation method.
- `nearest`: Uses the nearest available discrete angle without interpolation.
- `planar`: Uses the nearest neighbours on the closest elevation plane.
- `two_point`: Uses two-point weighted interpolation. Automatically chooses between azimuth or elevation interpolation based on the speaker layout.
- `three_point`: Uses three-point weighted interpolation.

**Parameters**:
- `subject_id` (str): Identifier for the subject.
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): IR type ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4', 'none'). 
- `azimuth` (float): Azimuth angle.
- `elevation` (float): Elevation angle.
- `modes` (str): 'auto', 'nearest', 'planar', 'two_point', 'three_point'
- `verbose` (bool): Verbosity flag.

**Usage Example**:
```python
ir = generate_sadie_ir('H6', 96000, 'HRIR', '5.1', 50.0, 25.0, mode="auto", verbose=True)
```

<br>

[Back Table of Contents](#table-of-contents)

## mix_tracks_binaural
```mix_tracks_binaural(tracks, subject_id, sample_rate, ir_type, speaker_layout, mode="auto", reverb_type = "1")```

**Description**: Mixes multiple audio tracks binaurally using HRIR or BRIR data for a specified subject, sample rate, IR type, and speaker layout.

**Parameters**:
- `tracks` (list): List of [TrackObjects](#trackobject-class). See [TrackObject](#trackobject-class) class for details.
- `subject_id` (str): Identifier for the subject.
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): Type of data ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4'), 'none'.
- `mode` (str): Interpolation mode. Options are ('auto', 'nearest', 'planar', 'two_point', 'three_point'). Default is 'auto'.
- `reverb_type` (str): Type of reverb to apply. Default is "1". 
    - `1` = Theatre
    - `2` = Office
    - `3` = Small Room
    - `4` = Meeting Room

<br>

[Back Table of Contents](#table-of-contents)

**Interpolation Modes** 
- `auto`: Automatically selects the best interpolation method.
- `nearest`: Uses the nearest available discrete angle without interpolation.
- `planar`: Uses the nearest neighbours on the closest elevation plane.
- `two_point`: Uses two-point weighted interpolation. Automatically chooses between azimuth or elevation interpolation based on the speaker layout.
- `three_point`: Uses three-point weighted interpolation.

**Usage Example**:
```python
mixed_output = mix_tracks_binaural(tracks, 'H3', 44000, 'HRIR', 'none', mode="auto", reverb_type = "1")
```

<br>

## mix_tracks_stereo
```mix_tracks_stereo(tracks, sample_rate, reverb_type = "1")```

**Description**: Mixes multiple audio tracks in stereo format.

**Parameters**:
- `tracks` (list): List of [TrackObjects](#trackobject-class). See [TrackObject](#trackobject-class) class for details.
- `sample_rate` (int): Sampling rate.
- `reverb_type` (str): Type of reverb to apply. Default is "1". 
    - `1` = Theatre
    - `2` = Office
    - `3` = Small Room
    - `4` = Meeting Room
 

**Usage Example**:
```python
mixed_output = mix_tracks_stereo(tracks, 44000, reverb_type = "1")
```

<br>

[Back Table of Contents](#table-of-contents)

## render_surround_to_binaural
```render_surround_to_binaural(surround_container, sr, subject_id, ir_type, input_layout, render_layout, mode="auto")```

**Description**: Renders a multichannel surround mix to binaural using a specified SADIE II subject. The function takes a surround encoded .wav file and renders it to binaural using the specified subject, speaker layout and interpolation method. You must specify the correct `input_layout` in order for the channel mapping to be correct. The function will automatically map the surround channels to the correct binaural positions based on the speaker layout definitions in `surround_utilities.py`. You can however choose to render the mix to a different speaker layout by specifying the `render_layout` parameter. The function will approximate a typical downmix process through the IR interpolation methods in the `generate_sadie_ir` function.

**Parameters**:
- `surround_container` (numpy array): Multichannel surround audio file.
- `sr` (int): Sampling rate.
- `subject_id` (str): Identifier for the subject.
- `ir_type` (str): Type of data ('HRIR' or 'BRIR').
- `input_layout` (str): Surround speaker layout (e.g., '5.1', '7.1', '7.1.4').
- `render_layout` (str): Binaural speaker layout (e.g., 'none', '5.1', '7.1.4').
- `mode` (str): Interpolation mode. Options are ('auto', 'nearest', 'planar', 'two_point', 'three_point'). Default is 'auto'.   

**Usage Example**:
```python
output = render_surround_to_binaural(surround_container, 48000, 'H3', 'HRIR', '7.1.4', '5.1.2', mode="auto")
```


<br>

[Back Table of Contents](#table-of-contents)

## TrackObject Class:
**Description**: A class to represent an audio track with associated mix parameters. The same TrackObject can be used for either:
- binaural mixing - by providing azimuth and elevation angles
- stereo mixing - by providing pan position -1.0 to 1.0

**Class Definition**:

```python
class TrackObject:
    def __init__(self, name, azimuth=None, elevation=None, pan=None, level=0, reverb=0, audio=None):
        self.name = name
        self.azimuth = azimuth
        self.elevation = elevation
        self.pan = pan
        self.level = level
        self.reverb = reverb
        self.audio = audio

    def __repr__(self):
        return f"Track Name={self.name}, Azimuth={self.azimuth}°, Elevation={self.elevation}°, Pan={self.pan}°, Level={self.level}, Reverb={self.reverb}"
```

**Usage Example**:
```python

# level: 0.0 to 1.0, 
# reverb: 0.0 to 1.0
# azimuth: -180.0 to 180.0 or 0 to 360
# elevation: -180.0 to 180.0 or 0 to 360
# pan: -1.0 to 1.0


# for binaural mixing
track1 = TrackObject('vocals', azimuth=45.0, elevation=0.0, level=0.5, reverb=0.2, audio=audio_data)
track2 = TrackObject('guitar', azimuth=-45.0, elevation=0.0, level=0.7, reverb=0.1, audio=audio_data)

tracks = [track1, track2]

output_binaural = mix_tracks_binaural(tracks, 'H3', 44000, 'HRIR', 'none', mode="auto", reverb_type = "1")

# for stereo mixing
track1 = TrackObject('guitar', pan=0.5, level=0.7, reverb=0.1, audio=audio_data)
track2 = TrackObject('bass', pan=-0.5, level=0.5, reverb=0.2, audio=audio_data)

tracks = [track1, track2]

output_stereo = mix_tracks_stereo(tracks, 44000)

```

[Back Table of Contents](#table-of-contents)


## surround.supported_layouts 
```surround.supported_layouts()```

**Description**: Returns a list of supported speaker layouts for binaural rendering. This function can be used to check the available speaker layouts for simulating various direct surround renders in binaural. They can be used for creating a mix for a specific speaker layout or for rendering a surround mix to binaural.

**Usage Example**:
```python
layouts = surround.supported_layouts()
print(layouts)  # Output: List of supported speaker layouts.
```

<br>

[Back Table of Contents](#table-of-contents)

## surround.get_channel_angles
```surround.get_channel_angles(layout)```

**Description**: Returns the channel names and orders (using Dolby spec) along with azimuth and elevation angles for a given speaker layout. This function can be used to get the azimuth and elevation angles for each channel in a desired speaker layout. The function returns a list of [SurroundChannelPosition](#surroundchannelposition-class) objects.

**Parameters**:
- `layout` (str): Speaker layout (e.g., '5.1', '7.1', '7.1.4').

**Usage Example**:
```python
channels = surround.get_channel_angles('7.1.4')
print(channels)  # Output: List of channel names and angles.
```

<br>

[Back Table of Contents](#table-of-contents)

<br><br>

# Helper Functions
<br>


## load_sadie_ir
```load_sadie_ir(subject_id, sample_rate, ir_type, azimuth, elevation)```

**Description**: Loads the HRIR or BRIR impulse response data for the specified subject, sample rate, IR type, azimuth, and elevation.

**Parameters**:
- `subject_id` (str): Identifier for the subject (e.g., 'D1', 'H3').
- `sample_rate` (int): Sampling rate (e.g., 44100, 48000, 96000).
- `ir_type` (str): Type of data ('HRIR' or 'BRIR').
- `azimuth` (float): Azimuth angle in degrees.
- `elevation` (float): Elevation angle in degrees.

**Usage Example**:
```python
y = load_sadie_ir('H5', 44100, 'HRIR', 30.0, 15.0)
```

<br>

[Back Table of Contents](#table-of-contents)

## delaunay_triangulation
```delaunay_triangulation(available_angles, azimuth, elevation, speaker_layout, plots=True)```

**Description**: Performs a Delaunay triangulation on the available angles to find the closest angles to the desired azimuth and elevation. Delaunay triangulation is normally used for 2D and 3D triangulation with cartesian coordinates. This function considers the angles and elevations to be an equirectangular projection of the sphere 
which is valid to find the bounding triangle for the desired angle but not valid to calculate distances.
The distances are calculated elsewhere using cartesian conversion and Euclidean distance.

**Parameters**:
- `available_angles` (list): List of available azimuth and elevation angles. Obtained using `get_available_angles`.
- `azimuth` (float): Desired azimuth angle.
- `elevation` (float): Desired elevation angle.
- `speaker_layout` (str): Speaker layout (e.g., none, '5.1', '7.1.4').
- `plots` (bool): Flag to display a plot of the triangulation.

**Usage Example**:
```python
triangulation = delaunay_triangulation(available_angles, 45.0, 30.0, '7.1.4', plots=True)
print(triangulation)  # Output: Delaunay triangulation object.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_available_angles
```get_available_angles(subject_id, sample_rate, ir_type, speaker_layout)```

**Description**: Returns all available azimuth and elevation angles for a given subject, sample rate, IR type, and speaker layout.

**Parameters**:
- `subject_id` (str): Identifier for the subject.
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): IR type ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4') or 'none' for all available angles.

**Usage Example**:
```python
angles = get_available_angles('H3', 48000, 'BRIR', '5.1')
print(angles)  # Output: List of available azimuth and elevation angles.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_nearest_angle
```get_nearest_angle(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)```

**Description**: Returns the nearest available angle to a specified azimuth and elevation.

**Parameters**:
- `subject_id` (str): Identifier for the subject.
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): IR type ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4').
- `azimuth` (float): Azimuth angle.
- `elevation` (float): Elevation angle.

**Usage Example**:
```python
nearest_angle = get_nearest_angle('D2', 44100, 'HRIR', 'none', 45.0, 10.0)
print(nearest_angle)  # Output: Nearest available angle.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_angle_distance
```get_angle_distance(azimuth1, elevation1, azimuth2, elevation2)```

**Description**: Calculates the Euclidean distance between two origin angles specified in azimuth and elevation.

**Parameters**:
- `azimuth1`, `elevation1`, `azimuth2`, `elevation2` (float): Angles in degrees.

**Usage Example**:
```python
distance = get_angle_distance(30.0, 15.0, 35.0, 20.0)
print(distance)  # Output: Total difference between the angles.
```

<br>

[Back Table of Contents](#table-of-contents)

## angle_exists
```angle_exists(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)```

**Description**: Checks if a specified angle exists for a given subject, sample rate, IR type, and speaker layout.

**Parameters**:
- `subject_id` (str): Identifier for the subject.
- `sample_rate` (int): Sampling rate.
- `ir_type` (str): IR type ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1.4').
- `azimuth` (float): Azimuth angle.
- `elevation` (float): Elevation angle.

**Usage Example**:
```python
exists = angle_exists('H10', 48000, 'BRIR', '7.1', 60.0, 20.0)
print(exists)  # Output: True or False.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_nearest_elevation_angle
```get_nearest_elevation_angle(subject_id, sample_rate, ir_type, speaker_layout, azimuth, elevation)```

**Description**: Gets the nearest available angle with elevation to a given azimuth and elevation for a specified subject, sample rate, IR type, and speaker layout.

**Parameters**:
- `subject_id` (str): Identifier for the subject (e.g., 'D1', 'H3').
- `sample_rate` (int): Sampling rate (e.g., 44100, 48000, 96000).
- `ir_type` (str): Type of data ('HRIR' or 'BRIR').
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1').
- `azimuth` (float): Azimuth angle.
- `elevation` (float): Elevation angle.

**Usage Example**:
```python
nearest_angle, distance = get_nearest_elevation_angle('H6', 96000, 'HRIR', '5.1', 50.0, 25.0)
print(nearest_angle, distance)
```

<br>

[Back Table of Contents](#table-of-contents)

## has_elevation_speakers
```has_elevation_speakers(speaker_layout)```

**Description**: Checks if a given speaker layout has elevation speakers.

**Parameters**:
- `speaker_layout` (str): Speaker layout (e.g., '5.1', '7.1', '7.1.4').

**Usage Example**:
```python
has_elevation = has_elevation_speakers('7.1.4')
print(has_elevation)  # Output: True or False.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_elevation_range
```get_elevation_range(available_angles)```

**Description**: Returns the range of elevation angles available in a list of azimuth and elevation angles.

**Parameters**:
- `available_angles` (list): List of available azimuth and elevation angles. Obtained using `get_available_angles`.

**Usage Example**:
```python
min_ele, max_ele = get_elevation_range(available_angles)
print(min_ele, max_ele)  # Output: Minimum and maximum elevation angles.
```

<br>

[Back Table of Contents](#table-of-contents)

## get_planar_neighbours

```get_planar_neighbours(available_angles, azimuth, elevation, verbose=True)```

**Description**: Returns the planar neighbours of a given azimuth and elevation angle from a list of available angles.

**Parameters**:
- `available_angles` (list): List of available azimuth and elevation angles. Obtained using `get_available_angles`.
- `azimuth` (float): Desired Azimuth angle.
- `elevation` (float): Desired Elevation angle.

**Usage Example**:
```python
neighbours = get_planar_neighbours(available_angles, 45.0, 30.0)
print(neighbours)  # Output: List of planar neighbours.
```

<br>

[Back Table of Contents](#table-of-contents)

## pan_source
```pan_source(pan, input_file)```

**Description**: Pans an input audio file to a specified position in the stereo field based on constant power amplitude panning.

**Parameters**:
- `pan` (float): Pan position (-1.0 to 1.0) where -1.0 is all the way left and 1.0 is all the way right.
- `input_file` (numpy array): Input audio file.

**Usage Example**:
```python
output = pan_source(0.5, input_audio)
```

<br>

[Back Table of Contents](#table-of-contents)

## spherical_to_cartesian
```spherical_to_cartesian(azimuth, elevation)```

**Description**: Converts spherical coordinates (azimuth and elevation) to Cartesian coordinates.

**Parameters**:
- `azimuth` (float): Azimuth angle in degrees.
- `elevation` (float): Elevation angle in degrees.

**Usage Example**:
```python
x, y, z = spherical_to_cartesian(45.0, 30.0)
print(x, y, z)  # Output: Cartesian coordinates.
```

<br>

[Back Table of Contents](#table-of-contents)

## cartesian_to_spherical
```cartesian_to_spherical(x, y, z)```

**Description**: Converts Cartesian coordinates to spherical coordinates (azimuth and elevation).

**Parameters**:
- `x`, `y`, `z` (float): Cartesian coordinates.

**Usage Example**:
```python
azimuth, elevation = cartesian_to_spherical(0.5, 0.5, 0.5)
print(azimuth, elevation)  # Output: Azimuth and elevation angles.
```
<br>

[Back Table of Contents](#table-of-contents)

## select_sadie_wav_subject
```select_sadie_wav_subject(subject_id, sample_rate, file_type)```

**Description**: This function selects the correct path to the WAV files for a given subject ID, sample rate, and IR type (either HRIR or BRIR).

**Parameters**:
- `subject_id` (str): Identifier for the subject (e.g., 'D1', 'H3').
- `sample_rate` (int): Sampling rate (e.g., 44100, 48000, 96000).
- `file_type` (str): Type of data ('HRIR' or 'BRIR').

**Usage Example**:
```python
path = select_sadie_wav_subject('D1', 48000, 'HRIR')
print(path)  # Output: Path to the corresponding WAV directory.
```

<br>

[Back Table of Contents](#table-of-contents)

## select_sadie_sofa_subject
```select_sadie_sofa_subject(subject_id, sample_rate, file_type)```

**Description**: This function selects the correct path to the SOFA files for a given subject ID, sample rate, and IR type (HRIR or BRIR).

**Parameters**:
- `subject_id` (str): Identifier for the subject (e.g., 'D1', 'H3').
- `sample_rate` (int): Sampling rate (e.g., 44100, 48000, 96000).
- `file_type` (str): Type of data ('HRIR' or 'BRIR').

**Usage Example**:
```python
path = select_sadie_sofa_subject('H4', 96000, 'BRIR')
print(path)  # Output: Path to the corresponding SOFA file.
```

<br>

[Back Table of Contents](#table-of-contents)

## construct_wav_filename
```construct_wav_filename(azimuth, elevation)```

**Description**: Generates a SADIE II format filename for a .wav audio file based on azimuth and elevation angles.

**Parameters**:
- `azimuth` (float): Azimuth angle in degrees.
- `elevation` (float): Elevation angle in degrees.

**Usage Example**:
```python
filename = construct_wav_filename(45.0, 30.0)
print(filename)  # Output: 'azi_45,0_ele_30,0.wav'
```

<br>

[Back Table of Contents](#table-of-contents)

## extract_azimuth_elevation
```extract_azimuth_elevation(filename)```

**Description**: Extracts the azimuth and elevation angles from a SADIE II filename.

**Parameters**:
- `filename` (str): The filename from which to extract angles.

**Usage Example**:
```python
azimuth, elevation = extract_azimuth_elevation('azi_30,0_ele_15,0.wav')
print(azimuth, elevation)  # Output: 30.0, 15.0
```

<br>

[Back Table of Contents](#table-of-contents)

# Definitions


[Back Table of Contents](#table-of-contents)
## Subject ID
```subject_id```<br>
**Description**: The identifier for the subject from the SADIE II Database. There are 20 subjects in the database, two dummy heads and 18 human subjects. The subjects are identified by a single letter followed by a number. The letter represents the type of subject (D for dummy head, H for human subject), and the number represents the subject number. Each has differing numbers of azimuth and elevation angles available ranging from 8802 points for dummy heads and between 2114 and 2818 points for human subjects for HRIRs. There are significantly less points for the BRIR data. All data can be found in the [SADIE II Database](https://www.york.ac.uk/sadie-project/database.html)
- **Examples**: D1, D2, H3, H4, H5 ... H20


[Back Table of Contents](#table-of-contents)
## IR type
```ir_type```<br>
**Description**: The type of impulse response data used for binaural rendering. HRIR (Head-Related Impulse Response) and BRIR (Binaural Room Impulse Response) are the two types available.
- **Options**: HRIR, BRIR


[Back Table of Contents](#table-of-contents)
## Speaker layout
```speaker_layout```<br>
**Description**: The configuration of speakers used for rendering the audio. Different layouts can be used to simulate various surround sound setups. The speaker layout can be specified as 'none' for direct binaural rendering using all possible angles for a SADIE subject. Alternatively you can specify a layout by name.

- **Examples**: none, 5.1, 5.1.4, 7.1, 7.1.4

You can add your own speaker layouts by adding the speaker positions in the `surround_utilities.py` file. The surround channel positions are defined by the following class:
```python
class SurroundChannelPosition:
    def __init__(self, name, azi, ele):
        self.name = name
        self.azi = azi
        self.ele = ele

    def __repr__(self):
        return f"Name={self.name}, Azimuth={self.azi}°, Elevation={self.ele}°"
```

Specififying your own speaker layout can then be done in the `get_channel_angles()` function within `surround_utilities.py` file as follows:
```python
if layout == '7.1':

    
        L = SurroundChannelPosition('L', 30, 0)       # Front Left 
        R = SurroundChannelPosition('R', 330, 0)      # Front Right 
        C = SurroundChannelPosition('C', 0, 0)        # Center
        Lfe = SurroundChannelPosition('Lfe', 0, 0)    # Low Frequency - Mapped to Center for Binaural Rendering
        Lss = SurroundChannelPosition('Lss', 90, 0)   # Surround Left
        Rss = SurroundChannelPosition('Rss', 270, 0)  # Surround Right
        Lrs = SurroundChannelPosition('Lrs', 135, 0)  # Surround Back Left
        Rrs = SurroundChannelPosition('Rrs', 225, 0)  # Surround Back Right

        channels = [L, R, C, Lfe, Lss, Rss, Lrs, Rrs]
    
        return channels
```

[Back Table of Contents](#table-of-contents)
## Azimuth
```azimuth```<br>
**Description**: The horizontal angle of the sound source relative to the listener's head. It is measured in degrees and can range from -180 to 180 or 0 to 360.
- **Range**: -180.0 to 180.0 or 0 to 360


[Back Table of Contents](#table-of-contents)
## Elevation
```elevation```<br>
**Description**: The vertical angle of the sound source relative to the listener's head. It is measured in degrees and can range from -180 to 180 or 0 to 360.
- **Range**: -180.0 to 180.0 or 0 to 360


[Back Table of Contents](#table-of-contents)
## Mix Parameters
**Description**: Parameters that control the mixing of audio tracks. These include level, reverb, and pan.
- **Level**: The volume level of the track, ranging from 0.0 to 1.0.
- **Reverb**: The amount of reverb applied to the track, ranging from 0.0 to 1.0.
- **Pan**: The stereo panning position of the track, ranging from -1.0 (left) to 1.0 (right).

see [TrackObject](#trackobject-class) class for details.
.

