import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from transcriber import TranscriberConfig


def main():
    print("=" * 70)
    print("Transcriber Stream Restart Feature Demo")
    print("=" * 70)
    print()

    print("The restart_interval_seconds parameter controls how often")
    print("the transcription stream automatically restarts.")
    print()

    print("Default configuration:")
    config_default = TranscriberConfig()
    print(f"  restart_interval_seconds: {config_default.restart_interval_seconds}s")
    print(
        f"  (This means the stream will restart every {config_default.restart_interval_seconds / 60:.1f} minutes)"
    )
    print()

    print("Custom configurations:")
    print()

    print("  1. Short interval for testing (30 seconds):")
    config_test = TranscriberConfig(restart_interval_seconds=30.0)
    print(f"     restart_interval_seconds: {config_test.restart_interval_seconds}s")
    print()

    print("  2. Standard interval (5 minutes):")
    config_standard = TranscriberConfig(restart_interval_seconds=300.0)
    print(f"     restart_interval_seconds: {config_standard.restart_interval_seconds}s")
    print()

    print("  3. Long interval (10 minutes):")
    config_long = TranscriberConfig(restart_interval_seconds=600.0)
    print(f"     restart_interval_seconds: {config_long.restart_interval_seconds}s")
    print()

    print("  4. Disable auto-restart (set to 0 or negative):")
    config_disabled = TranscriberConfig(restart_interval_seconds=0)
    print(f"     restart_interval_seconds: {config_disabled.restart_interval_seconds}s")
    print()

    print("=" * 70)
    print("How it works:")
    print("=" * 70)
    print()
    print("1. The transcriber starts a stream and tracks the start time")
    print("2. During transcription, it checks if restart_interval_seconds has elapsed")
    print("3. When the interval is reached:")
    print("   - The working buffer is dumped to long-term buffer")
    print("   - Chunks are created from the buffer content")
    print("   - The stream is restarted automatically")
    print("   - Transcription continues seamlessly")
    print()
    print("4. This prevents issues with long-running streams and ensures")
    print("   regular processing of accumulated transcription data")
    print()
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
