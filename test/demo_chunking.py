import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audio_streams import LocalAudioStream
from transcriber import Transcriber, TranscriberConfig
from topic_manager import TopicManager


def main():
    print("Real-Time Transcription with AI Chunking Demo")
    print("=" * 70)
    print("\nThis demo will transcribe audio and automatically chunk it by topics")
    print("using Gemini through Vertex AI.\n")
    print("Configuration:")
    print("  - Minimum words before dump: 10")
    print("  - Minimum time between dumps: 5 seconds")
    print("  - AI Model: Gemini 2.0 Flash")
    print("\n" + "=" * 70)

    input("\nPress Enter to start transcription...")

    config = TranscriberConfig(
        language_code="en-US",
        sample_rate_hertz=16000,
        min_word_count=10,
        min_time_since_dump=5.0,
        enable_automatic_punctuation=True,
        vertex_project_id=None,
        vertex_location="us-central1",
    )

    audio_stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)
    topic_manager = TopicManager()

    def on_working_buffer_update(text: str):
        print(f"\r\033[K📝 Working: {text}", end="", flush=True)

    def on_dump(text: str):
        print(f"\n\n💾 DUMPED TO CHUNKING:")
        print(f"   {text[:100]}{'...' if len(text) > 100 else ''}")
        print("-" * 70)

    def on_chunks_produced(chunks: dict):
        print(f"\n\n✨ CHUNKS PRODUCED:")
        print(f"   Topic IDs: {list(chunks.keys())}")
        for topic_id, content in chunks.items():
            print(f"\n   📌 {topic_id}:")
            print(f"      {content[:80]}{'...' if len(content) > 80 else ''}")
        print("-" * 70)

    transcriber = Transcriber(
        audio_stream=audio_stream,
        topic_manager=topic_manager,
        config=config,
        on_working_buffer_update=on_working_buffer_update,
        on_dump=on_dump,
        on_chunks_produced=on_chunks_produced,
    )

    print("\n" + "=" * 70)
    print("🎤 Transcription started. Speak into your microphone...")
    print("   Press Ctrl+C to stop and view full transcript")
    print("=" * 70 + "\n")

    try:
        transcriber.start()

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n" + "=" * 70)
        print("Stopping transcription...")
        transcriber.stop()

        print("\n" + "=" * 70)
        print("📋 FINAL TRANSCRIPT:")
        print("=" * 70)

        full_transcript = transcriber.get_full_transcript()
        if full_transcript:
            print(f"\n{full_transcript}\n")
        else:
            print("\nNo transcript available.\n")

        print("=" * 70)
        print("\n📊 BUFFER STATISTICS:")
        long_term_text = transcriber.get_long_term_buffer_text()
        working_text = transcriber.get_working_buffer_text()

        if long_term_text:
            long_term_words = len(long_term_text.split())
            print(f"   Long-term buffer: {long_term_words} words")
        else:
            print(f"   Long-term buffer: 0 words")

        if working_text:
            working_words = len(working_text.split())
            print(f"   Working buffer: {working_words} words")
        else:
            print(f"   Working buffer: 0 words")

        print("\n📚 TOPIC STATISTICS:")
        all_topics = topic_manager.get_all_topics()
        print(f"   Total topics: {len(all_topics)}")
        total_chunks = sum(len(topic.chunk_stack) for topic in all_topics.values())
        print(f"   Total chunks: {total_chunks}")

        print("=" * 70)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        transcriber.stop()


if __name__ == "__main__":
    main()
