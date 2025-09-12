import myRand
import numpy as np
import os
import pandas as pd
import librosa



def getRandomClip(directory : str , csv : str):
    """
    Get a random clip from a directory of audio files

    Args:
        directory (str): the directory containing the audio files
        csv (str): the csv file containing the audio file names and metadata, csv should have columns 'name' and 'class'

    Returns:
        array of just the audio data
    """
    df = pd.read_csv(csv)
    random_index = np.random.choice(df.index)
    audio_path = os.path.join(directory, df.loc[random_index, 'name'])
    class_name = df.loc[random_index, 'class']
    audio , sr = librosa.load(audio_path)
    return audio , sr ,class_name



def getRandomTimeWindow(audio, time : float , sr : int | float):
    """
    Pick a random window time frame within an audio file

    Args:
        audio: the audio data array (from librosa or torchaudio)
        time (float): the time frame size in seconds.
        sr (int): the sample rate of the audio file.

    Returns:
        array of just the audio data
    """
    target_len = int(time * sr)
    audio_total_length = len(audio)

    # If the audio is shorter than the target length, return the whole audio
    if audio_total_length <= target_len:
        return audio

    # Calculate the maximum starting position
    max_start = audio_total_length - target_len

    # Get a random starting position
    start_pos = np.random.randint(0, max_start)

    # Extract the window
    end_pos = start_pos + target_len
    return audio[start_pos:end_pos]

def randomlyShiftAudioStartTime(audio, minShiftBy : float , maxShiftBy : float , total_time : float, sr : int | float):
    """
    Randomly shift the start time of an audio clip

    Args:
        audio: the audio data array (from librosa or torchaudio)
        minShiftBy (float): the minimum time frame will be shifted by in seconds.
        maxShiftBy (float): the maximum time frame will be shifted by in seconds.
        total_time (float): the total time of the frame size in seconds.
        sr (int): the sample rate of the audio file.

    Returns:
        array of just the audio data
    """
    target_len = int(total_time * sr)

    # Convert shift times to samples
    min_shift_samples = int(minShiftBy * sr)
    max_shift_samples = int(maxShiftBy * sr)

    # Get a random shift amount within the specified range
    shift_samples = np.random.randint(min_shift_samples, max_shift_samples + 1)

    # Create a new array filled with zeros (silence) of the target length
    shifted_audio = np.zeros(target_len, dtype=audio.dtype if hasattr(audio, 'dtype') else np.float32)

    # Calculate how much of the original audio we can fit after the shift
    available_space = target_len - shift_samples
    audio_to_copy = min(len(audio), available_space)

    # Copy the original audio starting at the shift position
    if audio_to_copy > 0:
        shifted_audio[shift_samples:shift_samples + audio_to_copy] = audio[:audio_to_copy]

    return shifted_audio




if __name__ == "__main__":
    import soundfile as sf

    for i in range(3):
        audio,sr,class_name = getRandomClip("cs2 sounds/classifiables" , "cs2 sounds/classifiables.csv")
        audio_random_window = getRandomTimeWindow(audio,0.04,sr)
        shifted_audio = randomlyShiftAudioStartTime(audio_random_window, 0.01, 0.035, 0.04, sr)
        sf.write(f"output_{i}_shifted.wav", shifted_audio, sr)
        sf.write(f"output_{i}.wav", audio_random_window, sr)
