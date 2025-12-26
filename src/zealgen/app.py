import sys
import anyio
import os
import platform
import subprocess
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QListWidget, QFileDialog, QCheckBox,
    QLabel, QTextEdit, QMessageBox, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal, QStandardPaths
from .core import generate

class Worker(QThread):
    finished = Signal()
    error = Signal(str)
    log = Signal(str)
    progress = Signal(int, int)

    def __init__(self, urls, output, js):
        super().__init__()
        self.urls = urls
        self.output = output
        self.js = js

    def run(self):
        try:
            def report_progress(current, total):
                self.progress.emit(current, total)

            anyio.run(generate, self.urls, self.output, self.js, 100, report_progress)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zeal Docset Generator")
        self.setMinimumSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # URL list
        layout.addWidget(QLabel("URLs to fetch:"))
        self.url_list = QListWidget()
        layout.addWidget(self.url_list)

        url_input_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter documentation URL...")
        self.url_input.returnPressed.connect(self.add_url)
        url_input_layout.addWidget(self.url_input)
        
        add_btn = QPushButton("Add")
        add_btn.clicked.connect(self.add_url)
        url_input_layout.addWidget(add_btn)
        
        remove_btn = QPushButton("Remove Selected")
        remove_btn.clicked.connect(self.remove_url)
        url_input_layout.addWidget(remove_btn)
        layout.addLayout(url_input_layout)

        # Output directory
        layout.addWidget(QLabel("Output Docset Path:"))
        out_layout = QHBoxLayout()
        self.out_input = QLineEdit()
        out_layout.addWidget(self.out_input)
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.browse_output)
        out_layout.addWidget(browse_btn)
        layout.addLayout(out_layout)

        # Options
        self.js_checkbox = QCheckBox("Enable JavaScript (Playwright)")
        layout.addWidget(self.js_checkbox)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Logs
        layout.addWidget(QLabel("Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        # Generate button
        self.generate_btn = QPushButton("Generate Docset")
        self.generate_btn.clicked.connect(self.start_generation)
        layout.addWidget(self.generate_btn)

        # Open Zeal Folder button
        self.open_zeal_btn = QPushButton("Open Zeal Docsets Folder")
        self.open_zeal_btn.clicked.connect(self.open_zeal_folder)
        layout.addWidget(self.open_zeal_btn)

    def open_zeal_folder(self):
        system = platform.system()
        path = None
        
        if system == "Windows":
            path = os.path.join(os.environ.get("LOCALAPPDATA", ""), "Zeal", "Zeal", "docsets")
        elif system == "Darwin":  # macOS
            path = os.path.expanduser("~/Library/Application Support/Zeal/Zeal/docsets")
        elif system == "Linux":
            path = os.path.expanduser("~/.local/share/Zeal/Zeal/docsets")

        if path and os.path.exists(path):
            if system == "Windows":
                os.startfile(path)
            elif system == "Darwin":
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])
        else:
            QMessageBox.warning(self, "Folder Not Found", f"Could not find Zeal docsets folder at:\n{path}\n\nPlease make sure Zeal is installed and has been run at least once.")

    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            self.url_list.addItem(url)
            self.url_input.clear()

    def remove_url(self):
        for item in self.url_list.selectedItems():
            self.url_list.takeItem(self.url_list.row(item))

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if path:
            self.out_input.setText(path)

    def start_generation(self):
        urls = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        output = self.out_input.text().strip()
        js = self.js_checkbox.isChecked()

        if not urls:
            QMessageBox.warning(self, "Error", "Please add at least one URL.")
            return
        if not output:
            QMessageBox.warning(self, "Error", "Please specify an output path.")
            return

        self.generate_btn.setEnabled(False)
        self.log_output.append("Starting generation...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        self.worker = Worker(urls, output, js)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()

    def update_progress(self, current, total):
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def on_finished(self):
        self.progress_bar.setValue(self.progress_bar.maximum())
        self.log_output.append("Generation completed successfully!")
        self.generate_btn.setEnabled(True)
        QMessageBox.information(self, "Done", "Docset generated successfully.")

    def on_error(self, message):
        self.log_output.append(f"Error: {message}")
        self.generate_btn.setEnabled(True)
        QMessageBox.critical(self, "Error", f"An error occurred: {message}")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
