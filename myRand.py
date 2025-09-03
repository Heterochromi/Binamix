import numpy as np

# Initialize a deterministic seed (kept same as original)
np.random.seed(100)


def seed(seed_value: int):
    """
    Reseed the numpy RNG used by this module.
    Using this allows reproducible sequences in downstream code.
    """
    np.random.seed(seed_value)


def pick_random_from_range(min_angle: int = 0, max_angle: int = 360) -> int:
    """
    Pick a random angle between min_angle (inclusive) and max_angle (exclusive in practice).
    This mirrors the prior behavior where int(SystemRandom.uniform(a, b)) almost always
    produced values in [a, b) due to float-to-int truncation.
    """
    return int(np.random.uniform(min_angle, max_angle))


def pick_random_clip(clip_list):
    """
    Pick a random element from clip_list.
    """
    if not clip_list:
        raise ValueError("clip_list must not be empty")
    return np.random.choice(clip_list)


def pick_multiple_clips(clip_list, count: int):
    """
    Pick multiple random clips without replacement.
    If count > len(clip_list), returns all clips in random order.
    """
    if count <= 0 or not clip_list:
        return []
    size = min(count, len(clip_list))
    # np.random.choice without replacement yields a NumPy array; convert to list.
    return list(np.random.choice(clip_list, size=size, replace=False))


# Examples (kept similar to original; guarded to avoid side effects on import in other modules)
if __name__ == "__main__":
    angles = [pick_random_from_range() for _ in range(10)]
    print("Random angles:", angles[:10])

    audio_clips = ['clip1.wav', 'clip2.mp3', 'clip3.wav', 'clip4.aiff', 'clip5.wav']
    selected_clip = pick_random_clip(audio_clips)
    print("Selected clip:", selected_clip)

    multiple_clips = pick_multiple_clips(audio_clips, 3)
    print("Multiple clips:", multiple_clips)
