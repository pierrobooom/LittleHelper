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
        self.screenshot_list.addItems("No screenshot yet. Please take a screenshot.")
        self.main_layout.addWidget(self.screenshot_list)



        #self.setWindowIcon(QIcon(settings.ICON_PATH))
