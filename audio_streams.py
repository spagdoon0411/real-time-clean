from abc import ABC, abstractmethod
from typing import Generator, Optional
import pyaudio
import queue
import threading


class AudioStream(ABC):
    @abstractmethod
    def get_chunk_generator(self) -> Generator[bytes, None, None]:
        pass

    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def is_active(self) -> bool:
        pass


class LocalAudioStream(AudioStream):
    def __init__(
        self,
        format: int = pyaudio.paInt16,
        channels: int = 1,
        rate: int = 16000,
        chunk_size: int = 1024,
        input_device_index: Optional[int] = None,
    ):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk_size = chunk_size
        self.input_device_index = input_device_index

        self._audio = pyaudio.PyAudio()
        self._stream: Optional[pyaudio.Stream] = None
        self._audio_queue: queue.Queue = queue.Queue()
        self._is_active = False
        self._stop_event = threading.Event()

    def _audio_callback(self, in_data, frame_count, time_info, status):
        if status:
            print(f"Audio callback status: {status}")
        self._audio_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def start(self) -> None:
        if self._is_active:
            return

        self._stop_event.clear()
        self._is_active = True

        self._stream = self._audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            input_device_index=self.input_device_index,
            stream_callback=self._audio_callback,
        )

        self._stream.start_stream()

    def stop(self) -> None:
        if not self._is_active:
            return

        self._is_active = False
        self._stop_event.set()

        if self._stream:
            self._stream.stop_stream()
            self._stream.close()
            self._stream = None

        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break

    def is_active(self) -> bool:
        return self._is_active

    def get_chunk_generator(self) -> Generator[bytes, None, None]:
        while self._is_active:
            try:
                chunk = self._audio_queue.get(timeout=0.1)
                yield chunk
            except queue.Empty:
                if not self._is_active:
                    break
                continue

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()
        self._audio.terminate()

    def __del__(self):
        self.stop()
        if hasattr(self, "_audio"):
            self._audio.terminate()
