from io import BytesIO

import numpy as np
from scipy.io import wavfile

from app.tts.normalizer import normalize_text
from app.tts.phonemizer import phonemize
from app.tts.prosody import phoneme_duration, phoneme_frequency
from app.tts.syllabifier import syllabify_text

VOWEL_FORMANTS = {
    "a": (730.0, 1090.0, 2440.0),
    "e": (530.0, 1840.0, 2480.0),
    "i": (270.0, 2290.0, 3010.0),
    "o": (570.0, 840.0, 2410.0),
    "u": (300.0, 870.0, 2240.0),
    "an": (610.0, 1050.0, 2350.0),
    "on": (520.0, 820.0, 2200.0),
}

VOICED_CONSONANTS = {"B", "D", "G", "J", "L", "LH", "M", "N", "NH", "R", "RR", "V", "Z"}


def synthesize_text(
    text: str,
    sample_rate: int = 22050,
    amplitude: float = 0.28,
) -> tuple[np.ndarray, dict]:
    normalized_text = normalize_text(text)
    syllables = syllabify_text(normalized_text)
    spoken_syllable_count = len([syllable for syllable in syllables if syllable != " "])
    chunks = [
        _synthesize_syllable(
            syllable,
            sample_rate,
            amplitude,
            _spoken_index(syllables, index),
            spoken_syllable_count,
        )
        for index, syllable in enumerate(syllables)
    ]

    if chunks:
        audio = _join_with_crossfade(chunks, int(sample_rate * 0.018))
    else:
        audio = np.zeros(int(sample_rate * 0.15), dtype=np.float32)

    audio = _normalize_audio(audio)
    metrics = analyze_audio(audio, sample_rate)
    metrics.update(
        {
            "original_text": text,
            "normalized_text": normalized_text,
            "syllables": syllables,
        }
    )

    return audio, metrics


def write_wav_bytes(audio: np.ndarray, sample_rate: int) -> bytes:
    buffer = BytesIO()
    pcm_audio = np.int16(np.clip(audio, -1.0, 1.0) * 32767)
    wavfile.write(buffer, sample_rate, pcm_audio)
    return buffer.getvalue()


def synthesize_wav_bytes(
    text: str,
    sample_rate: int = 22050,
    amplitude: float = 0.28,
) -> tuple[bytes, dict]:
    audio, metrics = synthesize_text(text, sample_rate, amplitude)
    return write_wav_bytes(audio, sample_rate), metrics


def analyze_audio(audio: np.ndarray, sample_rate: int) -> dict:
    if audio.size == 0:
        return {
            "sample_rate": sample_rate,
            "duration_seconds": 0.0,
            "sample_count": 0,
            "peak_amplitude": 0.0,
            "rms_amplitude": 0.0,
        }

    return {
        "sample_rate": sample_rate,
        "duration_seconds": round(float(audio.size / sample_rate), 3),
        "sample_count": int(audio.size),
        "peak_amplitude": round(float(np.max(np.abs(audio))), 4),
        "rms_amplitude": round(float(np.sqrt(np.mean(audio**2))), 4),
    }


def _synthesize_syllable(
    syllable: str,
    sample_rate: int,
    amplitude: float,
    syllable_index: int,
    syllable_total: int,
) -> np.ndarray:
    if syllable == " ":
        return np.zeros(int(sample_rate * 0.055), dtype=np.float32)

    phonemes = phonemize(syllable)
    chunks = [
        _synthesize_phoneme(
            phoneme,
            sample_rate,
            amplitude,
            syllable_index,
            syllable_total,
        )
        for phoneme in phonemes
        if phoneme != " "
    ]

    if not chunks:
        return np.zeros(int(sample_rate * 0.04), dtype=np.float32)

    syllable_audio = _join_with_crossfade(chunks, int(sample_rate * 0.012))
    return syllable_audio * _syllable_envelope(syllable_audio.size)


def _spoken_index(syllables: list[str], current_index: int) -> int:
    return len([syllable for syllable in syllables[:current_index] if syllable != " "])


def _synthesize_phoneme(
    phoneme: str,
    sample_rate: int,
    amplitude: float,
    index: int,
    total: int,
) -> np.ndarray:
    duration = phoneme_duration(phoneme)
    sample_count = max(1, int(sample_rate * duration))

    if phoneme == " ":
        return np.zeros(sample_count, dtype=np.float32)

    frequency = phoneme_frequency(phoneme)
    time = np.linspace(0.0, duration, sample_count, endpoint=False)
    pitch = _pitch_contour(index, total, time, duration)

    if phoneme in VOWEL_FORMANTS:
        wave = _vowel_wave(phoneme, time, pitch)
    elif _is_noise_phoneme(phoneme):
        wave = _noise_wave(phoneme, sample_count)
    elif phoneme in VOICED_CONSONANTS:
        wave = _voiced_consonant_wave(time, pitch, frequency)
    else:
        wave = _unvoiced_consonant_wave(time, frequency)

    return (amplitude * wave * _envelope(sample_count)).astype(np.float32)


def _pitch_contour(
    index: int,
    total: int,
    time: np.ndarray,
    duration: float,
) -> np.ndarray:
    if total <= 1:
        phrase_progress = 0.0
    else:
        phrase_progress = index / (total - 1)

    local_progress = time / max(duration, 1e-6)
    base_pitch = 135.0
    phrase_curve = 18.0 * np.sin(np.pi * phrase_progress) - 14.0 * phrase_progress
    local_curve = 4.0 * np.sin(2 * np.pi * local_progress)
    return base_pitch + phrase_curve + local_curve


def _vowel_wave(phoneme: str, time: np.ndarray, pitch: np.ndarray) -> np.ndarray:
    phase = 2 * np.pi * np.cumsum(pitch) * (time[1] - time[0] if time.size > 1 else 1.0)
    glottal = (
        np.sin(phase)
        + 0.45 * np.sin(2 * phase)
        + 0.22 * np.sin(3 * phase)
        + 0.10 * np.sin(4 * phase)
    )

    formant_1, formant_2, formant_3 = VOWEL_FORMANTS[phoneme]
    resonance = (
        0.55 * np.sin(2 * np.pi * formant_1 * time)
        + 0.30 * np.sin(2 * np.pi * formant_2 * time)
        + 0.15 * np.sin(2 * np.pi * formant_3 * time)
    )

    return 0.72 * glottal + 0.28 * resonance


def _noise_wave(phoneme: str, sample_count: int) -> np.ndarray:
    seed = sum(ord(char) for char in phoneme)
    rng = np.random.default_rng(seed)
    return rng.normal(0.0, 0.30, sample_count)


def _voiced_consonant_wave(
    time: np.ndarray,
    pitch: np.ndarray,
    frequency: float,
) -> np.ndarray:
    phase = 2 * np.pi * np.cumsum(pitch) * (time[1] - time[0] if time.size > 1 else 1.0)
    buzz = np.sin(phase) + 0.25 * np.sin(2 * phase)
    resonance = np.sin(2 * np.pi * max(frequency, 180.0) * time)
    return 0.45 * buzz + 0.25 * resonance


def _unvoiced_consonant_wave(time: np.ndarray, frequency: float) -> np.ndarray:
    return 0.22 * np.sin(2 * np.pi * max(frequency, 180.0) * time)


def _is_noise_phoneme(phoneme: str) -> bool:
    return phoneme in {"CH", "SS", "S", "X", "F", "V", "Z"}


def _envelope(sample_count: int) -> np.ndarray:
    attack = max(1, int(sample_count * 0.12))
    release = max(1, int(sample_count * 0.18))
    sustain = max(0, sample_count - attack - release)

    return np.concatenate(
        [
            np.linspace(0.0, 1.0, attack, endpoint=False),
            np.ones(sustain),
            np.linspace(1.0, 0.0, release, endpoint=True),
        ]
    )


def _syllable_envelope(sample_count: int) -> np.ndarray:
    attack = max(1, int(sample_count * 0.06))
    release = max(1, int(sample_count * 0.10))
    sustain = max(0, sample_count - attack - release)

    return np.concatenate(
        [
            np.linspace(0.15, 1.0, attack, endpoint=False),
            np.ones(sustain),
            np.linspace(1.0, 0.15, release, endpoint=True),
        ]
    ).astype(np.float32)


def _join_with_crossfade(chunks: list[np.ndarray], fade_samples: int) -> np.ndarray:
    if not chunks:
        return np.array([], dtype=np.float32)

    output = chunks[0].astype(np.float32)

    for chunk in chunks[1:]:
        chunk = chunk.astype(np.float32)
        fade = min(fade_samples, output.size, chunk.size)

        if fade <= 1:
            output = np.concatenate([output, chunk])
            continue

        fade_out = np.linspace(1.0, 0.0, fade, endpoint=True)
        fade_in = np.linspace(0.0, 1.0, fade, endpoint=True)
        overlap = output[-fade:] * fade_out + chunk[:fade] * fade_in
        output = np.concatenate([output[:-fade], overlap, chunk[fade:]])

    return output.astype(np.float32)


def _normalize_audio(audio: np.ndarray) -> np.ndarray:
    peak = np.max(np.abs(audio)) if audio.size else 0.0

    if peak == 0.0:
        return audio.astype(np.float32)

    return (audio / peak * 0.82).astype(np.float32)
