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
        topic_id="introduction",
        chunk_content="Hello everyone, welcome to the demo.",
        chunk_blurb="Introduction and greeting",
        topic_description="Opening remarks",
    )
    tm.add_chunk(
        topic_id="introduction",
        chunk_content="Today we'll cover three main points.",
        chunk_blurb="Overview of agenda",
        topic_description="Opening remarks",
    )
    tm.add_chunk(
        topic_id="main_argument",
        chunk_content="First, let's discuss the architecture.",
        chunk_blurb="Architecture overview",
        topic_description="Technical discussion",
    )
    tm.add_chunk(
        topic_id="example_1",
        chunk_content="Here's a concrete example of how it works.",
        chunk_blurb="Practical demonstration",
        topic_description="Practical demonstration",
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
            print(f"      #{i}:")
            print(f"         Blurb: {chunk.blurb}")
            print(f"         Content: {chunk.content}")

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
