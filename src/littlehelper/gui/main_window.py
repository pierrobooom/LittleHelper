from PySide6.QtGui import (QIcon, QTextCursor)
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QListWidget,
    QHBoxLayout, QAbstractItemView,
)
from PySide6.QtCore import (Qt, QThread, QObject)

from littlehelper.config import settings
from littlehelper.llm.ollama_client import OllamaClient
from littlehelper.workers.inference_worker import InferenceWorker

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.system_prompt = "You are LittleHelper. Be concise, accurate, and practical."
        self.chat_turns = []
        self.rolling_summary = ""
        self.recent_turn_limit = 5
        self.summarized_turn_count = 0
        self.current_user_prompt = ""
        self.waiting_for_response = False

        self.client = OllamaClient(settings.ollama_host, settings.timeout_s)
        self.expanded = False

        self.setup_window()
        self.setup_central_widget()
        self.setup_title()
        self.setup_screenshot_list()
        self.setup_chat_output()
        self.setup_prompt_input()
        self.setup_buttons()

    def get_recent_turns(self):
        if len(self.chat_turns) > self.recent_turn_limit:
            return self.chat_turns[-self.recent_turn_limit:]
        else:
            return self.chat_turns

    def build_prompt_with_memory(self, current_user_prompt):
        sections = []
        recent_lines = []

        sections.append("System:\n" + self.system_prompt)

        if self.rolling_summary != "":
            sections.append("Conversation summary:\n" + self.rolling_summary)

        for turn in self.get_recent_turns():
            recent_lines.append("User: " + turn["user"])
            recent_lines.append("Assistant: " + turn["assistant"])

        if recent_lines:
            recent_chat = "\n".join(recent_lines)
            sections.append("Recent Conversation:\n" + recent_chat)

        sections.append("Current user message:\n" + current_user_prompt)
        sections.append("Assistant: ")

        return "\n\n".join(sections)

    def get_newly_displaced_turns(self):
        turns_that_should_be_summarized = max(0, len(self.chat_turns) - self.recent_turn_limit)

        if turns_that_should_be_summarized <= self.summarized_turn_count:
            return []

        return self.chat_turns[self.summarized_turn_count:turns_that_should_be_summarized]


    def update_rolling_summary_if_needed(self):
        newly_displaced_turns = self.get_newly_displaced_turns()
        if not newly_displaced_turns:
            return

        older_lines = []
        for turn in newly_displaced_turns:
            older_lines.append("User: " + turn["user"])
            older_lines.append("Assistant: " + turn["assistant"])

        older_text = "\n".join(older_lines)

        summary_prompt = (
            "You are maintaining a rolling conversation summary for a desktop assistant.\n\n"
            "Current summary:\n"
            f"{self.rolling_summary if self.rolling_summary else 'No previous summary.'}\n\n"
            "Newly displaced conversation turns to merge into the summary:\n"
            f"{older_text}\n\n"
            "Write an updated summary that preserves:\n"
            "- important facts\n"
            "- user preferences\n"
            "- decisions already made\n"
            "- unresolved questions or tasks\n"
            "- relevant constraints\n\n"
            "Be concise but informative."
        )

        try:
            summary = self.client.generate(
                model=settings.model,
                prompt=summary_prompt,
                system="You summarize conversations accurately, detailed and compactly."
            )
            self.rolling_summary = summary.strip()
            self.summarized_turn_count += len(newly_displaced_turns)

            print("UPDATED SUMMARY:")
            print(self.rolling_summary)
            print("SUMMARIZED TURN COUNT:", self.summarized_turn_count)
            print("-" * 40)
        except Exception as e:
            print("Summary update failed:", str(e))


    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.current_user_prompt = prompt
        full_prompt = self.build_prompt_with_memory(prompt)

        self.chat_output.append(f"You: {prompt}\n")
        self.chat_output.append("LittleHelper: Thinking...\n")
        self.waiting_for_response = True

        self.send_button.setDisabled(True)
        self.prompt_input.clear()

        self.thread = QThread()
        self.worker = InferenceWorker(
            self.client,
            settings.model,
            full_prompt,
            self.system_prompt
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)

        self.worker.finished.connect(self.on_response)
        self.worker.error.connect(self.on_error)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.error.connect(self.thread.quit)
        self.worker.error.connect(self.worker.deleteLater)

        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_response(self, response):
        self.remove_last_chat_block()

        self.chat_output.append(f"LittleHelper: {response}\n")

        self.send_button.setDisabled(False)
        self.waiting_for_response = False

        self.chat_turns.append({"user": self.current_user_prompt, "assistant": response})

        self.update_rolling_summary_if_needed()

    def on_error(self, error):
        self.remove_last_chat_block()

        self.chat_output.append(f"LittleHelper: Error -> {error}\n")

        self.send_button.setDisabled(False)
        self.waiting_for_response = False

    def remove_last_chat_block(self):
        cursor = self.chat_output.textCursor()
        cursor.movePosition(QTextCursor.End)

        # Move to the actual last text block, not the empty trailing position
        cursor.movePosition(QTextCursor.PreviousBlock)

        cursor.select(QTextCursor.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.deleteChar()  # removes the remaining block separator/newline

        self.chat_output.setTextCursor(cursor)

    def toggle_expand(self):
        if self.expanded:
            self.resize(420, 700)
            self.expand_button.setText("Expand")
            self.expanded = False
        else:
            self.resize(800, 800)
            self.expand_button.setText("Compact")
            self.expanded = True

    def setup_window(self):
        self.setWindowTitle("LittleHelper >.<")
        self.resize(420, 700)

    def setup_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

    def setup_title(self):
        self.title_label = QLabel("LittleHelper >.<")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

    def setup_screenshot_list(self):
        self.screenshot_list = QListWidget()
        self.screenshot_list.addItem("No screenshot yet. Please take a screenshot.")
        self.main_layout.addWidget(self.screenshot_list)

    def setup_chat_output(self):
        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setPlaceholderText("Model responses will appear here...")
        self.main_layout.addWidget(self.chat_output)

    def setup_prompt_input(self):
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Type your prompt here...")
        self.prompt_input.setFixedHeight(100)
        self.main_layout.addWidget(self.prompt_input)

    def setup_buttons(self):
        button_row = QHBoxLayout()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_prompt)
        button_row.addWidget(self.send_button)

        self.expand_button = QPushButton("Expand")
        self.expand_button.clicked.connect(self.toggle_expand)
        button_row.addWidget(self.expand_button)

        self.main_layout.addLayout(button_row)


