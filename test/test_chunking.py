import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from chunking import chunk_transcript_by_topics


def main():
    print("Testing AI-based Chunking")
    print("=" * 70)

    test_transcript = """
    Hello everyone, I wanted to talk about three main things today. 
    First, let me introduce the project. We're building a real-time transcription 
    system that can automatically organize speech into topics.
    
    Now for the second point, the technical architecture. We're using Google Cloud 
    Speech-to-Text for transcription and Gemini for intelligent chunking. The system 
    has two buffers: a working buffer for recent speech and a long-term buffer for 
    completed topics.
    
    Finally, let me discuss the benefits. This approach allows us to automatically 
    structure conversations without manual intervention. Users can see their speech 
    organized by topic in real-time. It's particularly useful for meetings, lectures, 
    and interviews.
    
    So that covers everything I wanted to
    """

    print("\nTest Transcript:")
    print(test_transcript)
    print("\n" + "=" * 70)
    print("Calling Gemini to chunk transcript...\n")

    try:
        result = chunk_transcript_by_topics(test_transcript.strip())

        print("✨ CHUNKING RESULTS:")
        print("=" * 70)

        complete_chunks = result.get("complete_chunks", {})
        incomplete_text = result.get("incomplete_text", "")

        if complete_chunks:
            print(f"\n📌 Complete Chunks ({len(complete_chunks)} topics):\n")
            for topic_id, content in complete_chunks.items():
                print(f"  Topic ID: {topic_id}")
                print(f"  Content: {content}\n")

        if incomplete_text:
            print(f"⏳ Incomplete Text (topics still being developed):")
            print(f"  {incomplete_text}\n")

        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
