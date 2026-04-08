from PySide6.QtGui import QIcon
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
from PySide6.QtCore import Qt

from littlehelper.config import settings
from littlehelper.llm.ollama_client import OllamaClient

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("LittleHelper >.<")
        self.resize(420, 700)

        self.client = OllamaClient(settings.ollama_host, settings.timeout_s)
        self.expanded = False

        central = QWidget()
        self.setCentralWidget(central)

        self.main_layout = QVBoxLayout()
        central.setLayout(self.main_layout)

        self.title_label = QLabel("LittleHelper >.<")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        self.screenshot_list = QListWidget()
        self.screenshot_list.addItem("No screenshot yet. Please take a screenshot.")
        self.main_layout.addWidget(self.screenshot_list)

        self.chat_output = QTextEdit()
        self.chat_output.setReadOnly(True)
        self.chat_output.setPlaceholderText("Model responses will appear here...")
        self.main_layout.addWidget(self.chat_output)

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Type your prompt here...")
        self.prompt_input.setFixedHeight(100)
        self.main_layout.addWidget(self.prompt_input)

        button_row = QHBoxLayout()

        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send_prompt)
        button_row.addWidget(self.send_button)

        self.expand_button = QPushButton("Expand")
        self.expand_button.clicked.connect(self.toggle_expand)
        button_row.addWidget(self.expand_button)

        self.main_layout.addLayout(button_row)

        #self.setWindowIcon(QIcon(settings.ICON_PATH))

    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.chat_output.append(f"You: {prompt}\n")
        print("HOST:", settings.ollama_host)
        print("MODEL:", settings.model)
        try:
            response = self.client.generate(
                model=settings.model,
                prompt=prompt,
                system="You are LittleHelper. Be concise, accurate, and practical."
            )
            self.chat_output.append(f"LittleHelper: {response}\n")
        except Exception as e:
            self.chat_output.append(f"Error: {str(e)}\n")

        self.prompt_input.clear()

    def toggle_expand(self):
        if self.expanded:
            self.resize(420, 700)
            self.expand_button.setText("Expand")
            self.expanded = False
        else:
            self.resize(800, 800)
            self.expand_button.setText("Compact")
            self.expanded = True


