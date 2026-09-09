from pathlib import Path

from app.tts.synthesizer import synthesize_wav_bytes


def main() -> None:
    text = "O projeto TAP-01 esta setenta e cinco por cento concluido."
    output_path = Path("output.wav")

    wav_bytes, metrics = synthesize_wav_bytes(text)
    output_path.write_bytes(wav_bytes)

    print(f"Arquivo gerado: {output_path.resolve()}")
    print(f"Texto normalizado: {metrics['normalized_text']}")
    print(f"Silabas: {'-'.join(metrics['syllables'])}")
    print(f"Duracao: {metrics['duration_seconds']}s")
    print(f"Amostras: {metrics['sample_count']}")
    print(f"Pico: {metrics['peak_amplitude']}")
    print(f"RMS: {metrics['rms_amplitude']}")


if __name__ == "__main__":
    main()
