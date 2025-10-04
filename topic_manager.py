from typing import Dict, List
from dataclasses import dataclass, field
import threading


@dataclass
class Topic:
    description: str
    chunk_stack: List[str] = field(default_factory=list)


class TopicManager:
    def __init__(self):
        self._topics: Dict[str, Topic] = {}
        self._lock = threading.Lock()

    def add_chunk(self, topic_id: str, chunk: str, description: str = "") -> None:
        with self._lock:
            if topic_id not in self._topics:
                self._topics[topic_id] = Topic(description=description)
            self._topics[topic_id].chunk_stack.append(chunk)

    def update_description(self, topic_id: str, description: str) -> None:
        with self._lock:
            if topic_id not in self._topics:
                self._topics[topic_id] = Topic(description=description)
            else:
                self._topics[topic_id].description = description

    def get_topic_summaries(self) -> Dict[str, str]:
        with self._lock:
            return {
                topic_id: topic.description for topic_id, topic in self._topics.items()
            }

    def get_topic_summaries_formatted(self) -> str:
        with self._lock:
            if not self._topics:
                return "No topics yet."

            formatted = ""
            for topic_id, topic in self._topics.items():
                formatted += f"- {topic_id}: {topic.description}\n"
            return formatted.strip()

    def get_all_topics(self) -> Dict[str, Topic]:
        with self._lock:
            return {topic_id: topic for topic_id, topic in self._topics.items()}

    def get_chunks_for_topic(self, topic_id: str) -> List[str]:
        with self._lock:
            if topic_id in self._topics:
                return list(self._topics[topic_id].chunk_stack)
            return []

    def get_all_chunks(self) -> Dict[str, List[str]]:
        with self._lock:
            return {
                topic_id: list(topic.chunk_stack)
                for topic_id, topic in self._topics.items()
            }

    def clear(self) -> None:
        with self._lock:
            self._topics.clear()
