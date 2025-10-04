import logging
from typing import Dict, Optional, List
import instructor
from pydantic import BaseModel, Field


logger = logging.getLogger(__name__)


class TopicAssignment(BaseModel):
    existing_topic_id: Optional[str] = Field(
        None, description="ID of an existing topic if this chunk matches one"
    )
    new_topic_id: Optional[str] = Field(
        None, description="ID for a new topic if this content represents a new topic"
    )
    updated_description: Optional[str] = Field(
        None,
        description="Updated description if the topic has evolved significantly from this chunk",
    )
    chunk_content: str = Field(description="The actual text content of the chunk")
    is_complete: bool = Field(
        True, description="Whether this chunk represents a complete thought or topic"
    )


class ChunkingResult(BaseModel):
    assignments: List[TopicAssignment] = Field(
        description="List of topic assignments for chunks"
    )
    incomplete_text: str = Field(
        "", description="Any text that doesn't form a complete chunk yet"
    )


def chunk_transcript_by_topics(
    transcript: str,
    existing_topics: Optional[str] = None,
    project_id: str = None,
    location: str = "us-central1",
) -> Dict[str, any]:
    logger.debug(f"Chunking transcript of length {len(transcript)}")

    client = instructor.from_provider(
        "google/gemini-2.0-flash-exp",
        vertexai=True,
        project=project_id,
        location=location,
    )

    existing_topics_text = ""
    if existing_topics:
        existing_topics_text = f"""
Here are the existing topics that have been identified so far:
{existing_topics}

IMPORTANT: When a chunk matches an existing topic, use 'existing_topic_id' with the exact ID from the list above.
Only create a 'new_topic_id' if the content represents a distinctly new topic not covered by existing ones.
If a chunk adds significant new context to an existing topic, provide an 'updated_description' to reflect the evolution.
"""
        logger.debug("Using existing topics in prompt")

    prompt = f"""Analyze this transcript and break it into chunks by distinct points or topics the speaker made.

{existing_topics_text}

For each chunk of content:
1. Determine if it matches an existing topic (use existing_topic_id) or needs a new topic (use new_topic_id)
2. Extract the relevant text content (chunk_content)
3. If the topic has evolved significantly with this chunk, provide an updated_description
4. Mark is_complete=True only if the speaker clearly finished that thought
5. Any incomplete thoughts should go into incomplete_text

Guidelines:
- Use descriptive topic IDs (e.g., "introduction", "main_argument", "example_1")
- Only one of existing_topic_id or new_topic_id should be set per assignment
- updated_description should only be provided when the topic's meaning has notably shifted
- If text is mid-thought or unfinished, include it in incomplete_text instead of creating an assignment

Transcript:
{transcript}"""

    logger.info("Calling Gemini via Instructor for chunking")
    try:
        result = client.chat.completions.create(
            response_model=ChunkingResult,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        logger.info(
            f"Successfully got structured response with {len(result.assignments)} assignments"
        )
        logger.debug(f"Incomplete text length: {len(result.incomplete_text)}")

        complete_chunks = {}
        topic_descriptions = {}

        for assignment in result.assignments:
            if assignment.is_complete:
                topic_id = assignment.existing_topic_id or assignment.new_topic_id
                if topic_id:
                    complete_chunks[topic_id] = assignment.chunk_content
                    if assignment.updated_description:
                        topic_descriptions[topic_id] = assignment.updated_description
                    logger.info(f"Assigned chunk to topic: {topic_id}")
            else:
                if result.incomplete_text:
                    result.incomplete_text += " " + assignment.chunk_content
                else:
                    result.incomplete_text = assignment.chunk_content

        return {
            "complete_chunks": complete_chunks,
            "incomplete_text": result.incomplete_text,
            "topic_descriptions": topic_descriptions,
        }

    except Exception as e:
        logger.error(f"Error calling Instructor: {e}", exc_info=True)
        return {
            "complete_chunks": {},
            "incomplete_text": transcript,
            "topic_descriptions": {},
        }
