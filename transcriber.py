import time
import threading
from typing import Generator, Optional, Callable
from dataclasses import dataclass
from google.cloud import speech_v1 as speech
from audio_streams import AudioStream


@dataclass
class TranscriberConfig:
    language_code: str = "en-US"
    sample_rate_hertz: int = 16000
    encoding: speech.RecognitionConfig.AudioEncoding = (
        speech.RecognitionConfig.AudioEncoding.LINEAR16
    )
    min_word_count: int = 10
    min_time_since_dump: float = 5.0
    enable_automatic_punctuation: bool = True
    model: str = "default"


class Transcriber:
    def __init__(
        self,
        audio_stream: AudioStream,
        config: Optional[TranscriberConfig] = None,
        on_working_buffer_update: Optional[Callable[[str], None]] = None,
        on_dump: Optional[Callable[[str], None]] = None,
    ):
        self.audio_stream = audio_stream
        self.config = config or TranscriberConfig()
        self.on_working_buffer_update = on_working_buffer_update
        self.on_dump = on_dump

        self.working_buffer: str = ""
        self.long_term_buffer: str = ""

        self._last_interim_text: str = ""
        self._last_dump_time: float = time.time()
        self._is_running = False
        self._transcription_thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

        self.client = speech.SpeechClient()

    def dump_ready(self) -> bool:
        with self._lock:
            if not self.working_buffer:
                return False

            word_count = len(self.working_buffer.split())
            time_since_dump = time.time() - self._last_dump_time

            return (
                word_count >= self.config.min_word_count
                and time_since_dump >= self.config.min_time_since_dump
            )

    def _dump_to_long_term(self) -> None:
        with self._lock:
            if self.working_buffer:
                if self.long_term_buffer:
                    self.long_term_buffer += " " + self.working_buffer
                else:
                    self.long_term_buffer = self.working_buffer

                dumped_text = self.working_buffer
                self.working_buffer = ""
                self._last_interim_text = ""
                self._last_dump_time = time.time()

                if self.on_dump:
                    self.on_dump(dumped_text)

    def _create_streaming_config(self) -> speech.StreamingRecognitionConfig:
        recognition_config = speech.RecognitionConfig(
            encoding=self.config.encoding,
            sample_rate_hertz=self.config.sample_rate_hertz,
            language_code=self.config.language_code,
            enable_automatic_punctuation=self.config.enable_automatic_punctuation,
            model=self.config.model,
        )
        streaming_config = speech.StreamingRecognitionConfig(config=recognition_config)
        return streaming_config

    def _audio_generator(
        self,
    ) -> Generator[speech.StreamingRecognizeRequest, None, None]:
        for audio_chunk in self.audio_stream.get_chunk_generator():
            if not self._is_running:
                break
            if not isinstance(audio_chunk, bytes):
                raise TypeError(f"Audio chunk must be bytes, got {type(audio_chunk)}")
            if len(audio_chunk) == 0:
                continue
            yield speech.StreamingRecognizeRequest(audio_content=audio_chunk)

    def _process_responses(
        self, responses: Generator[speech.StreamingRecognizeResponse, None, None]
    ) -> None:
        for response in responses:
            if not self._is_running:
                break

            if not response.results:
                continue

            result = response.results[0]

            if not result.alternatives:
                continue

            transcript = result.alternatives[0].transcript
            is_final = result.is_final

            with self._lock:
                if is_final:
                    if self.working_buffer and self._last_interim_text:
                        final_text = self.working_buffer[
                            : -len(self._last_interim_text)
                        ]
                        self.working_buffer = final_text + transcript
                    else:
                        if self.working_buffer:
                            self.working_buffer += " " + transcript
                        else:
                            self.working_buffer = transcript
                    self._last_interim_text = ""
                else:
                    if self._last_interim_text:
                        base_text = self.working_buffer[: -len(self._last_interim_text)]
                    else:
                        base_text = self.working_buffer

                    if base_text and transcript:
                        self.working_buffer = base_text + " " + transcript
                    elif transcript:
                        self.working_buffer = transcript
                    else:
                        self.working_buffer = base_text

                    self._last_interim_text = (
                        " " + transcript if base_text and transcript else transcript
                    )

                if self.on_working_buffer_update:
                    self.on_working_buffer_update(self.working_buffer)

            if is_final and self.dump_ready():
                self._dump_to_long_term()

    def _transcription_loop(self) -> None:
        try:
            streaming_config = self._create_streaming_config()
            audio_stream = self._audio_generator()
            responses = self.client.streaming_recognize(streaming_config, audio_stream)
            self._process_responses(responses)
        except Exception as e:
            print(f"Transcription error: {e}")
            import traceback

            traceback.print_exc()
            self._is_running = False

    def start(self) -> None:
        if self._is_running:
            return

        self._is_running = True
        self.audio_stream.start()

        self._transcription_thread = threading.Thread(
            target=self._transcription_loop, daemon=True
        )
        self._transcription_thread.start()

    def stop(self) -> None:
        if not self._is_running:
            return

        self._is_running = False
        self.audio_stream.stop()

        if self._transcription_thread:
            self._transcription_thread.join(timeout=5.0)
            self._transcription_thread = None

        if self.working_buffer:
            self._dump_to_long_term()

    def get_working_buffer_text(self) -> str:
        with self._lock:
            return self.working_buffer

    def get_long_term_buffer_text(self) -> str:
        with self._lock:
            return self.long_term_buffer

    def get_full_transcript(self) -> str:
        with self._lock:
            if self.long_term_buffer and self.working_buffer:
                return self.long_term_buffer + " " + self.working_buffer
            elif self.long_term_buffer:
                return self.long_term_buffer
            else:
                return self.working_buffer

    def clear_buffers(self) -> None:
        with self._lock:
            self.working_buffer = ""
            self.long_term_buffer = ""
            self._last_interim_text = ""
            self._last_dump_time = time.time()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
