import myRand
import numpy as np
import os

def getRandomClip():
    # Get a random file from the directory
    files = os.listdir("cs2 sounds/classifiables")
    return files



def getRandomTimeWindow(audio, time : float , sr : int):
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




if __name__ == "__main__":
    # myRand.seed(200)
    #
    for i in range(10):
     result = myRand.pick_random_clip(getRandomClip())
     print(result)
