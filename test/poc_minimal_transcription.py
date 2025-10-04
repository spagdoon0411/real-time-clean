import sys
import queue
import pyaudio
from google.cloud import speech_v1 as speech


RATE = 16000
CHUNK = 1024


class MicrophoneStream:
    def __init__(self, rate=RATE, chunk=CHUNK):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self._closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self._closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self._closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self._closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)


def main():
    print("=" * 70)
    print("Minimal Google Cloud Speech-to-Text Streaming POC")
    print("=" * 70)
    print("\nThis is a bare-bones example directly from Google Cloud docs.")
    print("Speak into your microphone. Press Ctrl+C to stop.\n")
    print("=" * 70)

    client = speech.SpeechClient()

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    with MicrophoneStream(RATE, CHUNK) as stream:

        def request_generator():
            yield speech.StreamingRecognizeRequest(streaming_config=streaming_config)
            for content in stream.generator():
                yield speech.StreamingRecognizeRequest(audio_content=content)

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

                if result.is_final:
                    print(f"✓ {transcript}")
                else:
                    print(f"\r  {transcript}", end="", flush=True)

        except KeyboardInterrupt:
            print("\n\nStopped by user")
        except Exception as e:
            print(f"\n\nError: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    main()
