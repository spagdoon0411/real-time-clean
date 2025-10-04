import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from google.cloud import speech_v1 as speech
from audio_streams import LocalAudioStream


def transcribe_streaming():
    print("=" * 70)
    print("Google Cloud Speech-to-Text Streaming Proof of Concept")
    print("=" * 70)
    print("\nThis POC demonstrates real-time transcription using:")
    print("  - LocalAudioStream for audio capture")
    print("  - Google Cloud Speech-to-Text streaming API")
    print("\nSpeak into your microphone to see real-time transcription...")
    print("Press Ctrl+C to stop\n")
    print("=" * 70)

    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
        enable_automatic_punctuation=True,
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config,
        interim_results=True,
    )

    audio_stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)

    def request_generator():
        yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)

        audio_stream.start()
        for audio_chunk in audio_stream.get_chunk_generator():
            yield speech.StreamingRecognizeRequest(audio_content=audio_chunk)

    try:
        requests = request_generator()
        responses = client.streaming_recognize(requests)

        print("\n🎤 Listening...\n")

        for response in responses:
            if not response.results:
                continue

            result = response.results[0]
            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            is_final = result.is_final

            if is_final:
                print(f"✓ FINAL: {transcript}")
            else:
                print(f"\r🔄 Interim: {transcript}", end="", flush=True)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Transcription stopped by user")
        print("=" * 70)
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
    finally:
        audio_stream.stop()
        print("\nAudio stream stopped")


if __name__ == "__main__":
    transcribe_streaming()
