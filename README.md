# Real-Time Audio Transcription

A Python library for real-time audio transcription using Google Cloud Speech-to-Text API with intelligent buffer management.

## Features

- **Generic Audio Stream Interface**: Extensible design for various audio sources
- **Local Audio Stream**: Capture audio from microphone using PyAudio
- **Smart Buffer Management**:
  - Working buffer for interim results
  - Long-term buffer for finalized transcripts
  - Configurable dump conditions (word count and time-based)
- **Real-time Transcription**: Stream audio to Google Cloud Speech-to-Text API
- **Callback Support**: React to buffer updates and dumps

## Installation

```bash
pip install -r requirements.txt
```

Or using uv:

```bash
uv pip install .
```

## Google Cloud Setup

1. Create a Google Cloud project and enable the Speech-to-Text API
2. Create a service account and download the JSON key file
3. Set the environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
```

## Quick Start

```python
from audio_streams import LocalAudioStream
from transcriber import Transcriber, TranscriberConfig

config = TranscriberConfig(
    language_code="en-US",
    sample_rate_hertz=16000,
    min_word_count=10,
    min_time_since_dump=5.0,
)

audio_stream = LocalAudioStream(rate=16000, channels=1)

with Transcriber(audio_stream=audio_stream, config=config) as transcriber:
    import time
    while True:
        time.sleep(1)
        print(transcriber.get_working_buffer_text())
```

## Usage Examples

### Basic Transcription

```bash
python example_usage.py
```

### Interactive Demo

```bash
python test/demo_transcriber.py
```

### Audio Stream Test

```bash
python test/test_audio_stream.py
```

## Architecture

### AudioStream (Abstract Interface)

```python
class AudioStream(ABC):
    def get_chunk_generator(self) -> Generator[bytes, None, None]: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def is_active(self) -> bool: ...
```

### LocalAudioStream

Captures audio from the microphone using PyAudio with configurable parameters:

- Sample rate (default: 16000 Hz)
- Channels (default: 1 - mono)
- Format (default: 16-bit PCM)
- Chunk size (default: 1024 frames)

### Transcriber

Manages real-time transcription with dual-buffer architecture:

**Working Buffer**: Holds interim and recent final transcripts
**Long-term Buffer**: Stores dumped segments from working buffer

**Dump Conditions** (both must be met):

- Minimum word count reached
- Minimum time elapsed since last dump

### TranscriberConfig

```python
@dataclass
class TranscriberConfig:
    language_code: str = "en-US"
    sample_rate_hertz: int = 16000
    encoding: AudioEncoding = LINEAR16
    min_word_count: int = 10
    min_time_since_dump: float = 5.0
    enable_automatic_punctuation: bool = True
    model: str = "default"
```

## API Reference

### Transcriber Methods

- `start()`: Start transcription
- `stop()`: Stop transcription and dump remaining buffer
- `get_working_buffer_text()`: Get current working buffer as text
- `get_long_term_buffer_text()`: Get long-term buffer as text
- `get_full_transcript()`: Get complete transcript
- `clear_buffers()`: Clear all buffers
- `dump_ready()`: Check if conditions are met for dumping

### Callbacks

```python
def on_working_buffer_update(text: str):
    print(f"Current: {text}")

def on_dump(text: str):
    print(f"Dumped: {text}")

transcriber = Transcriber(
    audio_stream=audio_stream,
    config=config,
    on_working_buffer_update=on_working_buffer_update,
    on_dump=on_dump,
)
```

## Configuration

### Audio Stream Parameters

- `rate`: Sample rate in Hz (16000 recommended for Speech-to-Text)
- `channels`: Number of audio channels (1 for mono)
- `chunk_size`: Frames per buffer (affects latency)
- `input_device_index`: Specific microphone to use (None for default)

### Transcriber Parameters

- `min_word_count`: Minimum words in working buffer before dump
- `min_time_since_dump`: Minimum seconds between dumps
- `language_code`: BCP-47 language code
- `enable_automatic_punctuation`: Add punctuation automatically

## Thread Safety

The `Transcriber` class is thread-safe with internal locking for buffer operations.

## License

MIT
