import sys
import time
import struct
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_streams import LocalAudioStream


def calculate_rms(audio_data):
    count = len(audio_data) // 2
    format_string = f"{count}h"
    shorts = struct.unpack(format_string, audio_data)
    sum_squares = sum(s**2 for s in shorts)
    rms = (sum_squares / count) ** 0.5
    return rms


def get_volume_bar(rms, max_rms=5000, bar_length=50):
    normalized = min(rms / max_rms, 1.0)
    filled = int(normalized * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)
    percentage = int(normalized * 100)
    return bar, percentage


def main():
    print("Live Audio Stream Test")
    print("=" * 70)
    print("\nThis will display real-time audio intensity from your microphone.")
    print("Speak or make noise to see the level indicators respond.\n")

    input("Press Enter to start monitoring...")
    print("\n" + "=" * 70)

    stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)

    try:
        stream.start()
        print(
            f"✓ Stream active | Rate: {stream.rate} Hz | Chunk size: {stream.chunk_size}"
        )
        print("=" * 70)
        print("\nMonitoring audio... (Ctrl+C to stop)\n")

        chunk_count = 0
        start_time = time.time()
        rms_history = []
        max_rms_seen = 0

        for audio_chunk in stream.get_chunk_generator():
            chunk_count += 1
            rms = calculate_rms(audio_chunk)
            rms_history.append(rms)

            if len(rms_history) > 10:
                rms_history.pop(0)

            avg_rms = sum(rms_history) / len(rms_history)
            max_rms_seen = max(max_rms_seen, rms)

            bar, percentage = get_volume_bar(rms)

            elapsed = time.time() - start_time

            status = ""
            if percentage > 60:
                status = "LOUD!"
            elif percentage > 30:
                status = "Speaking"
            elif percentage > 10:
                status = "Quiet"
            else:
                status = "Silent"

            print(
                f"\r[{bar}] {percentage:3d}% | "
                f"RMS: {int(rms):5d} | "
                f"Avg: {int(avg_rms):5d} | "
                f"Peak: {int(max_rms_seen):5d} | "
                f"{status:8s} | "
                f"Time: {elapsed:.1f}s",
                end="",
                flush=True,
            )

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Monitoring stopped by user")
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback

        traceback.print_exc()
    finally:
        stream.stop()
        elapsed = time.time() - start_time
        print("\n" + "=" * 70)
        print("Stream Statistics:")
        print(f"  Duration: {elapsed:.2f}s")
        print(f"  Chunks processed: {chunk_count}")
        print(f"  Average chunk rate: {chunk_count / elapsed:.1f} chunks/s")
        print(f"  Peak RMS level: {int(max_rms_seen)}")
        print("=" * 70)


if __name__ == "__main__":
    main()
