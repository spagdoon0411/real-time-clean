import logging
import os
from chunking import chunk_transcript_by_topics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


def test_new_topics():
    print("=" * 70)
    print("TEST 1: Creating chunks with new topics")
    print("=" * 70)

    transcript = """
    Hello everyone, welcome to today's presentation. I want to talk about three main things.
    
    First, let me introduce the concept of real-time transcription. It's a technology that 
    converts speech to text as you speak, with minimal delay. This is incredibly useful for 
    accessibility and productivity.
    
    Second, I want to discuss the challenges we face. The main issues are handling background 
    noise, dealing with different accents, and managing the computational cost of real-time 
    processing. These are not trivial problems.
    """

    result = chunk_transcript_by_topics(
        transcript=transcript.strip(),
        existing_topics=None,
        project_id=PROJECT_ID,
        location=LOCATION,
    )

    print("\nResults:")
    print(f"Complete chunks: {len(result['complete_chunks'])}")
    for topic_id, content in result["complete_chunks"].items():
        print(f"\n  Topic: {topic_id}")
        print(f"  Content: {content[:100]}...")
        if topic_id in result.get("topic_descriptions", {}):
            print(f"  Description: {result['topic_descriptions'][topic_id]}")

    print(
        f"\nIncomplete text: {result['incomplete_text'][:100] if result['incomplete_text'] else 'None'}"
    )
    print()


def test_existing_topics():
    print("=" * 70)
    print("TEST 2: Assigning chunks to existing topics")
    print("=" * 70)

    existing_topics_str = """
- introduction: Welcome and overview of the presentation
- real_time_transcription: Technology for converting speech to text in real-time
- challenges: Issues and problems with implementation
"""

    transcript = """
    Now let me give you a concrete example of how this works in practice. Imagine you're in 
    a meeting and someone is speaking about quarterly results. The transcription system needs 
    to keep up with their pace while maintaining accuracy.
    
    Going back to the challenges I mentioned earlier, the computational cost is particularly 
    significant when you're processing multiple audio streams simultaneously. We've found that 
    GPU acceleration helps a lot, but it does increase infrastructure costs.
    """

    result = chunk_transcript_by_topics(
        transcript=transcript.strip(),
        existing_topics=existing_topics_str,
        project_id=PROJECT_ID,
        location=LOCATION,
    )

    print("\nResults:")
    print(f"Complete chunks: {len(result['complete_chunks'])}")
    for topic_id, content in result["complete_chunks"].items():
        print(f"\n  Topic: {topic_id}")
        print(f"  Content: {content[:100]}...")
        if topic_id in result.get("topic_descriptions", {}):
            print(f"  Updated Description: {result['topic_descriptions'][topic_id]}")

    print(
        f"\nIncomplete text: {result['incomplete_text'][:100] if result['incomplete_text'] else 'None'}"
    )
    print()


def test_description_update():
    print("=" * 70)
    print("TEST 3: Testing topic description updates")
    print("=" * 70)

    existing_topics_str = """
- challenges: Issues and problems with implementation
"""

    transcript = """
    Let me clarify something important about the challenges. It's not just about technical 
    issues like noise and accents. There are also significant business challenges. We need 
    to think about data privacy, GDPR compliance, and how to handle sensitive conversations. 
    The legal implications are massive, and this fundamentally changes what we mean by 
    'challenges' in this context.
    """

    result = chunk_transcript_by_topics(
        transcript=transcript.strip(),
        existing_topics=existing_topics_str,
        project_id=PROJECT_ID,
        location=LOCATION,
    )

    print("\nResults:")
    print(f"Complete chunks: {len(result['complete_chunks'])}")
    for topic_id, content in result["complete_chunks"].items():
        print(f"\n  Topic: {topic_id}")
        print(f"  Content: {content[:100]}...")
        if topic_id in result.get("topic_descriptions", {}):
            print(f"  🔄 Updated Description: {result['topic_descriptions'][topic_id]}")

    print()


if __name__ == "__main__":
    if PROJECT_ID == "your-project-id":
        print("⚠️  Warning: Please set GOOGLE_CLOUD_PROJECT environment variable")
        print("   Example: export GOOGLE_CLOUD_PROJECT=my-project-id\n")
        exit(1)

    try:
        test_new_topics()
        test_existing_topics()
        test_description_update()

        print("=" * 70)
        print("✓ All tests completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise
