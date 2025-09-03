from audiomentations import AddBackgroundNoise, PolarityInversion
import librosa
import soundfile as sf
import numpy as np
from binamix.sadie_utilities import TrackObject, mix_tracks_binaural
from myRand import pick_random_from_range
import torchaudio


mono_audio , sr = torchaudio.load("cs2 sounds/weapons/ak47_01.wav" , normalize=True)
resampler = torchaudio.transforms.Resample(sr, 44100)
# mono_audio =  resampler(mono_audio)
# mono_audio, sr = librosa.load("cs2 sounds/weapons/ak47_01.wav", mono=True , sr = 44100)

track = TrackObject(
    name="positioned_source",
    azimuth=90,
    elevation=45,
    level=0.8,
    reverb=0,
    audio=mono_audio,
)
output = mix_tracks_binaural(
    tracks=[track],
    subject_id='D1',
    sample_rate=sr,
    ir_type='HRIR',
    speaker_layout='none',
    mode="auto",
)



rmbs_db = pick_random_from_range(15 , 45)

rmbs_db = -rmbs_db

left_channel = output[0, :]
right_channel = output[1, :]

transform = AddBackgroundNoise(
    sounds_path="cs2 sounds/ambient/air_02.wav",
    noise_rms="absolute",
    min_absolute_rms_db=rmbs_db,
    max_absolute_rms_db=rmbs_db,
    noise_transform=PolarityInversion(),
    p=1.0
)
left_augmented_sound = transform(samples=left_channel, sample_rate=44100)
right_augmented_soubd = transform(samples=right_channel, sample_rate=44100)


augmented_stereo = np.vstack([left_augmented_sound, right_augmented_soubd])


sf.write("testBack.wav", augmented_stereo.T, 44100)
