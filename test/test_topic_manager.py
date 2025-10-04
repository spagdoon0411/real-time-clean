import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from topic_manager import TopicManager


def main():
    print("Testing TopicManager")
    print("=" * 70)

    tm = TopicManager()

    print("\n1. Adding chunks to topics...")
    tm.add_chunk(
        "introduction", "Hello everyone, welcome to the demo.", "Opening remarks"
    )
    tm.add_chunk(
        "introduction", "Today we'll cover three main points.", "Opening remarks"
    )
    tm.add_chunk(
        "main_argument",
        "First, let's discuss the architecture.",
        "Technical discussion",
    )
    tm.add_chunk(
        "example_1",
        "Here's a concrete example of how it works.",
        "Practical demonstration",
    )

    print("\n2. Getting topic summaries:")
    summaries = tm.get_topic_summaries()
    for topic_id, description in summaries.items():
        print(f"   - {topic_id}: {description}")

    print("\n3. Getting formatted topic summaries:")
    print(tm.get_topic_summaries_formatted())

    print("\n4. Updating a topic description...")
    tm.update_description("main_argument", "Deep dive into system design")

    print("\n5. Getting all topics:")
    all_topics = tm.get_all_topics()
    for topic_id, topic in all_topics.items():
        print(f"\n   Topic: {topic_id}")
        print(f"   Description: {topic.description}")
        print(f"   Chunks ({len(topic.chunk_stack)}):")
        for i, chunk in enumerate(topic.chunk_stack, 1):
            print(f"      #{i}: {chunk}")

    print("\n6. Getting chunks for specific topic:")
    intro_chunks = tm.get_chunks_for_topic("introduction")
    print(f"   Introduction has {len(intro_chunks)} chunks")

    print("\n7. Getting all chunks:")
    all_chunks = tm.get_all_chunks()
    print(f"   Total topics: {len(all_chunks)}")
    for topic_id, chunks in all_chunks.items():
        print(f"   - {topic_id}: {len(chunks)} chunks")

    print("\n" + "=" * 70)
    print("All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
