import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_streams import LocalAudioStream


def main():
    print("Audio Stream Demo")
    print("=" * 50)
    print("\nThis demo will capture audio from your microphone")
    print("for 5 seconds and display chunk information.\n")

    input("Press Enter to start recording...")

    stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)

    try:
        stream.start()
        print(f"\n✓ Stream started")
        print(f"  Sample rate: {stream.rate} Hz")
        print(f"  Channels: {stream.channels}")
        print(f"  Chunk size: {stream.chunk_size} frames")
        print("\nCapturing audio chunks...\n")

        start_time = time.time()
        chunk_count = 0
        total_bytes = 0

        for audio_chunk in stream.get_chunk_generator():
            chunk_count += 1
            total_bytes += len(audio_chunk)

            elapsed = time.time() - start_time
            print(
                f"Chunk {chunk_count}: {len(audio_chunk)} bytes | "
                f"Elapsed: {elapsed:.2f}s | "
                f"Total: {total_bytes / 1024:.2f} KB",
                end="\r",
            )

            if elapsed >= 5.0:
                break

        print("\n\nCapture complete!")
        print(f"Total chunks: {chunk_count}")
        print(f"Total data: {total_bytes / 1024:.2f} KB")
        print(f"Average rate: {total_bytes / elapsed / 1024:.2f} KB/s")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        stream.stop()
        print("Stream stopped")


if __name__ == "__main__":
    main()
