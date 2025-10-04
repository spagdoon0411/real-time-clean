import instructor
from pydantic import BaseModel, Field
from typing import List
import os


PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")


class Person(BaseModel):
    name: str
    age: int
    occupation: str


class Article(BaseModel):
    title: str = Field(description="The title of the article")
    summary: str = Field(description="A brief summary")
    key_points: List[str] = Field(description="Main points from the article")
    sentiment: str = Field(
        description="Overall sentiment: positive, negative, or neutral"
    )


def test_simple_extraction():
    print("Testing simple person extraction...")

    client = instructor.from_provider(
        "google/gemini-2.5-flash",
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    person = client.chat.completions.create(
        response_model=Person,
        messages=[
            {
                "role": "user",
                "content": "Extract: Sarah is a 28-year-old data scientist working at a tech company",
            }
        ],
    )

    print(f"Extracted Person: {person}")
    assert person.name == "Sarah"
    assert person.age == 28
    assert "data scientist" in person.occupation.lower()
    print("✓ Simple extraction test passed!\n")


def test_complex_extraction():
    print("Testing complex article extraction...")

    client = instructor.from_provider(
        "google/gemini-2.5-flash",
        vertexai=True,
        project=PROJECT_ID,
        location=LOCATION,
    )

    article_text = """
    The Rise of AI in Healthcare
    
    Artificial intelligence is revolutionizing healthcare by improving diagnostic accuracy 
    and patient outcomes. Recent studies show AI can detect diseases earlier than traditional 
    methods. Machine learning algorithms are being used to predict patient deterioration, 
    optimize treatment plans, and reduce healthcare costs. The technology is particularly 
    promising in radiology and pathology.
    """

    article = client.chat.completions.create(
        response_model=Article,
        messages=[
            {
                "role": "user",
                "content": f"Analyze this article and extract key information:\n\n{article_text}",
            }
        ],
    )

    print(f"Title: {article.title}")
    print(f"Summary: {article.summary}")
    print(f"Key Points: {article.key_points}")
    print(f"Sentiment: {article.sentiment}")

    assert len(article.key_points) > 0
    assert article.sentiment.lower() in ["positive", "negative", "neutral"]
    print("✓ Complex extraction test passed!\n")


if __name__ == "__main__":
    print("=" * 60)
    print("Gemini + Instructor Test Script (VertexAI)")
    print("=" * 60)
    print(f"Project ID: {PROJECT_ID}")
    print(f"Location: {LOCATION}")
    print("=" * 60 + "\n")

    if PROJECT_ID == "your-project-id":
        print("⚠️  Warning: Please set GOOGLE_CLOUD_PROJECT environment variable")
        print("   Example: export GOOGLE_CLOUD_PROJECT=my-project-id\n")

    try:
        test_simple_extraction()
        test_complex_extraction()
        print("=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        raise
