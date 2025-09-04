from binamix.sadie_utilities import TrackObject, mix_tracks_binaural
import soundfile as sf
import librosa
import numpy as np

ak_audio, sr = librosa.load("cs2 sounds/weapons/ak47_01.wav", sr=44100)
gernade_audio, sr = librosa.load("cs2 sounds/grenade/hegrenade/hegrenade_detonate_02.wav", sr=44100)

# Ensure both audio clips are exactly 0.5 seconds (22050 samples at 44.1 kHz)
target_len = int(0.5 * sr)

def _ensure_half_second(audio, target_len):
    if len(audio) > target_len:
        return audio[:target_len]
    if len(audio) < target_len:
        return np.pad(audio, (0, target_len - len(audio)))
    return audio

ak_audio = _ensure_half_second(ak_audio, target_len)
gernade_audio = _ensure_half_second(gernade_audio, target_len)

# resampler = torchaudio.transforms.Resample(sr, 44100)
# mono_audio =  resampler(mono_audio)
# mono_audio, sr = librosa.load("cs2 sounds/weapons/ak47_01.wav", mono=True , sr = 44100)

track = TrackObject(
    name="positioned_source",
    azimuth=90,
    elevation=45,
    level=0.8,
    reverb=0,
    audio=ak_audio,
)

track2 = TrackObject(
    name="positioned_source",
    azimuth=315,
    elevation=0,
    level=0.8,
    reverb=0,
    audio=gernade_audio,
)
output = mix_tracks_binaural(
    tracks=[track, track2],
    subject_id='D1',
    sample_rate=sr,
    ir_type='HRIR',
    speaker_layout='none',
    mode="auto",
)
sf.write("both.wav", output.T, sr)
# sf.write("gernade.wav", output[1].T, sr)
