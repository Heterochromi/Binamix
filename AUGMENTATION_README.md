# Audio Augmentation Pipeline

This document describes the comprehensive audio augmentation pipeline implemented in `augment.py` that combines multiple audio processing techniques to create synthetic HRIR (Head-Related Impulse Response) datasets.

## Overview

The pipeline creates synthetic 3D audio environments by:
1. Randomly selecting 1-4 audio clips from different sound classes
2. Processing each clip with random windowing and temporal shifting
3. Positioning sounds in 3D space using random azimuth and elevation
4. Mixing all sounds using binaural processing (HRIR)
5. Adding ambient background noise
6. Generating comprehensive metadata

## Pipeline Components

### 1. Random Clip Selection
- **Function**: `getRandomClip()` from `randManipulateAudio.py`
- **Source**: Audio files from `cs2 sounds/classifiables/` directory
- **Metadata**: Uses `cs2 sounds/classifiables.csv` for class labels
- **Range**: 1-4 clips per sample (randomly determined)

### 2. Temporal Processing
- **Window Extraction**: 40ms random windows from source audio
- **Random Shifting**: Audio shifted by 1-35ms within the 40ms window
- **Final Length**: All clips padded/cropped to 0.5 seconds total

### 3. Spatial Positioning
- **Azimuth**: Random angle 0-360 degrees
- **Elevation**: Random angle -90 to +90 degrees
- **Audio Level**: Random level between 0.5-1.0
- **3D Processing**: Uses binaural mixing with HRIR for realistic spatial audio

### 4. Background Ambience
- **Source**: `cs2 sounds/ambient/` directory
- **Processing**: Random window selection matching clip duration
- **Integration**: Added using AudioMentations with random dB levels (-45 to -15 dB)
- **Fallback**: Creates silence if no ambient files available

## Output Format

### Audio Files
- **Format**: WAV, 44.1kHz, 16-bit, Stereo
- **Duration**: 0.5 seconds
- **Naming**: `sample_XXXX.wav` (zero-padded 4 digits)
- **Location**: `output/dataset/`

### Metadata CSV
**File**: `output/dataset/dataset_metadata.csv`

**Columns**:
- `name_file`: Audio filename
- `classes`: Comma-separated class names (ordered by clip position)
- `azimuth`: Comma-separated azimuth values (ordered by clip position)
- `elevation`: Comma-separated elevation values (ordered by clip position)
- `num_classes`: Total number of sound sources in the sample

**Example**:
```csv
name_file,classes,azimuth,elevation,num_classes
sample_0000.wav,footsteps,44,32,1
sample_0003.wav,"weapons,footsteps","3,319","-55,-19",2
sample_0006.wav,"doors,footsteps,footsteps,footsteps","295,138,298,151","74,58,-71,-8",4
```

## Usage

### Basic Usage
```python
from augment import create_augmented_dataset

# Generate 100 samples
create_augmented_dataset(dataset_size=100)
```

### Custom Output Directory
```python
create_augmented_dataset(dataset_size=50, output_dir="custom/path")
```

### With Reproducible Results
```python
import myRand
import numpy as np

# Set seeds for reproducibility
myRand.seed(42)
np.random.seed(42)

create_augmented_dataset(dataset_size=100)
```

## Dependencies

### Required Python Packages
- `numpy`
- `pandas`
- `librosa`
- `soundfile`
- `audiomentations`
- `binamix` (SADIE utilities)

### Required Files
- `myRand.py` - Random number utilities
- `randManipulateAudio.py` - Audio manipulation functions
- `cs2 sounds/classifiables.csv` - Audio file metadata
- Audio files in `cs2 sounds/classifiables/`
- Optional: Ambient files in `cs2 sounds/ambient/`

## Features

### Error Handling
- Graceful handling of missing audio files
- Automatic creation of dummy files for testing
- Comprehensive error reporting
- Fallback to silence for missing ambient audio

### Quality Assurance
- Input validation for CSV structure
- Audio format verification
- Metadata consistency checks
- Comprehensive logging

### Verification Tools
Use `verify_dataset.py` to check dataset integrity:
```bash
python verify_dataset.py
```

## Dataset Statistics (Example Output)

```
Dataset contains 99 samples
Class distribution:
footsteps       134
weapons          88
molotov           6
doors             5
incgrenade        3
hegrenade         3
smokegrenade      2

Number of classes per sample:
1    27
2    27
3    20
4    25

Spatial distribution:
  Azimuth range: 0 to 357 degrees
  Elevation range: -89 to 90 degrees

Dataset integrity: 100.0%
```

## Technical Details

### Audio Processing Pipeline
1. **Source Selection**: Random selection from classified audio database
2. **Windowing**: Extract 40ms segments using `getRandomTimeWindow()`
3. **Temporal Shifting**: Apply `randomlyShiftAudioStartTime()` for variation
4. **Spatial Processing**: Create `TrackObject` instances with random 3D coordinates
5. **Binaural Mixing**: Use `mix_tracks_binaural()` for HRIR processing
6. **Background Addition**: Apply `AddBackgroundNoise` transformation
7. **Output Generation**: Save stereo WAV files with metadata

### 3D Audio Implementation
- Uses SADIE HRIR database for realistic spatial processing
- Supports subject ID 'D1' for consistent head model
- Automatic interpolation for non-measured angles
- Real-time processing with 'auto' mode

### Data Augmentation Benefits
- **Spatial Diversity**: Full 360° azimuth and ±90° elevation coverage
- **Temporal Variation**: Random windowing and shifting
- **Multi-source Complexity**: 1-4 simultaneous sound sources
- **Realistic Ambience**: Background noise integration
- **Class Balance**: Automatic tracking of sound class distribution

## Troubleshooting

### Common Issues
1. **Missing Audio Files**: Pipeline automatically creates dummy files for testing
2. **Memory Issues**: Reduce `dataset_size` parameter for large datasets
3. **Format Errors**: Ensure all source audio is readable by librosa
4. **Path Issues**: Verify `cs2 sounds/` directory structure

### Performance Optimization
- Process samples in smaller batches for large datasets
- Use SSD storage for faster I/O operations
- Monitor memory usage during binaural processing
- Consider parallel processing for production use

## Future Enhancements
- Support for additional HRIR subjects
- Real-time augmentation during training
- Advanced environmental acoustics
- Dynamic range compression options
- Custom spatial distribution patterns