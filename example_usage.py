import logging
import sys
from typing import Dict
from asciimatics.widgets import Frame, Layout, Label, TextBox, Divider
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError, StopApplication
from audio_streams import LocalAudioStream
from transcriber import Transcriber, TranscriberConfig
from topic_manager import TopicManager


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="transcription.log",
    filemode="a",
)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.ERROR)
logging.getLogger().addHandler(console_handler)

logger = logging.getLogger(__name__)


class TranscriptionFrame(Frame):
    def __init__(self, screen, transcriber, topic_manager):
        super(TranscriptionFrame, self).__init__(
            screen,
            screen.height,
            screen.width,
            has_border=True,
            title="Real-Time Transcription",
        )
        self.transcriber = transcriber
        self.topic_manager = topic_manager

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)

        layout.add_widget(Label("=== FULL TRANSCRIPT ==="))
        self.full_buffer_text = TextBox(
            height=screen.height // 3 - 2,
            as_string=True,
            line_wrap=True,
            readonly=True,
        )
        layout.add_widget(self.full_buffer_text)

        layout.add_widget(Divider())
        layout.add_widget(Label("=== WORKING BUFFER ==="))
        self.working_buffer_text = TextBox(
            height=screen.height // 3 - 2,
            as_string=True,
            line_wrap=True,
            readonly=True,
        )
        layout.add_widget(self.working_buffer_text)

        layout.add_widget(Divider())
        layout.add_widget(Label("=== TOPICS & CHUNKS (Use ↑↓ to scroll) ==="))
        self.chunks_text = TextBox(
            height=screen.height // 3 - 3,
            as_string=True,
            line_wrap=True,
            readonly=False,
        )
        layout.add_widget(self.chunks_text)

        layout.add_widget(Label("Press 'Q' to quit | TAB to switch focus", height=1))

        self.fix()

    def _update(self, frame_no):
        full_transcript = self.transcriber.get_full_transcript()
        working_buffer = self.transcriber.get_working_buffer_text()
        all_topics = self.topic_manager.get_all_topics()

        self.full_buffer_text.value = full_transcript if full_transcript else "(empty)"
        self.working_buffer_text.value = working_buffer if working_buffer else "(empty)"

        if all_topics:
            chunks_display = ""
            for topic_id, topic in all_topics.items():
                chunks_display += f"━━━ {topic_id.upper()} ━━━\n"
                if topic.description:
                    chunks_display += f"📝 Topic: {topic.description}\n"
                chunks_display += f"({len(topic.chunk_stack)} chunk{'s' if len(topic.chunk_stack) != 1 else ''})\n\n"

                for i, chunk in enumerate(topic.chunk_stack, 1):
                    chunks_display += f"  Chunk #{i}:\n"
                    if chunk.blurb:
                        chunks_display += f"    📝 {chunk.blurb}\n"
                    chunks_display += f"    💬 {chunk.content}\n\n"
                chunks_display += "\n"
            self.chunks_text.value = chunks_display.strip()
        else:
            self.chunks_text.value = "(no topics yet)"

        super(TranscriptionFrame, self)._update(frame_no)

    def process_event(self, event):
        if event and hasattr(event, "key_code"):
            if event.key_code in [ord("q"), ord("Q")]:
                raise StopApplication("User quit")

        return super(TranscriptionFrame, self).process_event(event)


def demo(screen, scene, transcriber, topic_manager):
    frame = TranscriptionFrame(screen, transcriber, topic_manager)
    screen.play([Scene([frame], -1)], stop_on_resize=True)


def print_all_chunks(topic_manager):
    print("\n\n" + "=" * 70)
    print("ALL CHUNKS ORGANIZED BY TOPIC")
    print("=" * 70 + "\n")

    all_topics = topic_manager.get_all_topics()

    if not all_topics:
        print("No chunks were produced.\n")
        return

    for topic_id, topic in all_topics.items():
        print("━" * 70)
        print(f"TOPIC: {topic_id.upper()}")
        if topic.description:
            print(f"Description: {topic.description}")
        print(f"Chunks: {len(topic.chunk_stack)}")
        print("━" * 70 + "\n")

        for i, chunk in enumerate(topic.chunk_stack, 1):
            print(f"Chunk #{i}:")
            if chunk.blurb:
                print(f"  📝 Blurb: {chunk.blurb}")
            print(f"  💬 Content: {chunk.content}\n")

    print("=" * 70)
    print(f"Total topics: {len(all_topics)}")
    total_chunks = sum(len(topic.chunk_stack) for topic in all_topics.values())
    print(f"Total chunks: {total_chunks}")
    print("=" * 70 + "\n")


def main():
    logger.info("Starting Real-Time Transcription application")

    config = TranscriberConfig(
        language_code="en-US",
        sample_rate_hertz=16000,
        min_word_count=10,
        min_time_since_dump=5.0,
        enable_automatic_punctuation=True,
        restart_interval_seconds=300.0,
    )

    audio_stream = LocalAudioStream(rate=16000, channels=1, chunk_size=1024)
    topic_manager = TopicManager()

    def on_chunks_produced(chunks: Dict[str, str]):
        logger.info(f"Chunks produced: {list(chunks.keys())}")

    transcriber = Transcriber(
        audio_stream=audio_stream,
        topic_manager=topic_manager,
        config=config,
        on_chunks_produced=on_chunks_produced,
    )

    transcriber.start()
    logger.info("Transcriber started")

    last_scene = None
    try:
        while True:
            try:
                Screen.wrapper(
                    demo,
                    catch_interrupt=True,
                    arguments=[last_scene, transcriber, topic_manager],
                )
                break
            except ResizeScreenError as e:
                last_scene = e.scene
            except StopApplication:
                logger.info("User quit application")
                break
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break
    finally:
        transcriber.stop()
        logger.info("Transcriber stopped")
        print_all_chunks(topic_manager)


if __name__ == "__main__":
    main()
