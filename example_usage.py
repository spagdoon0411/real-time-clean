from audio_streams import LocalAudioStream
from transcriber import Transcriber, TranscriberConfig


def main():
    config = TranscriberConfig(
        language_code="en-US",
        sample_rate_hertz=16000,
        min_word_count=10,
        min_time_since_dump=5.0,
        enable_automatic_punctuation=True,
    )
    audio_stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)

    with Transcriber(audio_stream=audio_stream, config=config) as transcriber:
        print("Transcribing... Press Ctrl+C to stop")

        try:
            import time

            while True:
                time.sleep(1)
                print(f"\rWorking: {transcriber.get_working_buffer_text()}", end="")

        except KeyboardInterrupt:
            print("\n\nFull transcript:")
            print(transcriber.get_full_transcript())


if __name__ == "__main__":
    main()
