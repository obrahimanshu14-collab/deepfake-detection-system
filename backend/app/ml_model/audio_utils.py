"""
Audio preprocessing: converts a raw audio file into a mel-spectrogram
image, which the existing CNN pipeline can then classify exactly like
a face image -- reusing the same architecture pattern rather than
building an entirely separate audio model type.
"""
import librosa
import numpy as np
import cv2

SAMPLE_RATE = 16000   # standard rate for speech analysis
DURATION_SECONDS = 4  # clips are trimmed/padded to a fixed length
N_MELS = 128           # frequency resolution of the spectrogram


def audio_to_spectrogram_image(filepath: str, img_size: int = 160) -> np.ndarray:
    """Load an audio file and convert it into a 3-channel image
    (so it's compatible with the ImageNet-pretrained MobileNetV2 input
    format) representing its mel-spectrogram.
    """
    audio, sr = librosa.load(filepath, sr=SAMPLE_RATE, duration=DURATION_SECONDS)

    # Pad short clips with silence so every input has a consistent length --
    # required because the model expects a fixed-size input.
    target_len = SAMPLE_RATE * DURATION_SECONDS
    if len(audio) < target_len:
        audio = np.pad(audio, (0, target_len - len(audio)))
    else:
        audio = audio[:target_len]

    mel_spec = librosa.feature.melspectrogram(y=audio, sr=sr, n_mels=N_MELS)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    # Normalize to 0-255 (standard image pixel range) for CNN compatibility.
    normalized = cv2.normalize(mel_spec_db, None, 0, 255, cv2.NORM_MINMAX)
    normalized = normalized.astype(np.uint8)

    resized = cv2.resize(normalized, (img_size, img_size))
    # Stack the single-channel spectrogram into 3 channels (R=G=B),
    # matching the 3-channel input the pretrained backbone expects.
    image_3ch = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
    return image_3ch