import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QComboBox, QMainWindow, QMenuBar, QMenu,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
from processor import process_zip_to_csv
from config import APP_VERSION, DEVELOPER_NAME

class ShpToCsvApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapefile to CSV Converter")
        self.setGeometry(100, 100, 600, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        title = QLabel("Convertitore Shapefile in CSV")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Input file selection
        self.input_layout = QHBoxLayout()
        self.input_label = QLabel("1. File .zip dello shapefile:")
        self.input_line = QLineEdit()
        self.input_line.setReadOnly(True)
        self.input_button = QPushButton("Sfoglia")
        self.input_button.clicked.connect(self.select_input_file)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_line)
        self.input_layout.addWidget(self.input_button)
        self.layout.addLayout(self.input_layout)

        self.mode_label = QLabel("2. Seleziona la modalità di esportazione")
        self.layout.addWidget(self.mode_label)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["EMLID", "Ricerca Perdite", "Padania e Chiampo"])
        self.layout.addWidget(self.mode_selector)

        # Output folder selection with button on the right
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel("3. Cartella di salvataggio del CSV:")
        self.output_line = QLineEdit()
        self.output_line.setReadOnly(True)
        self.output_button = QPushButton("Sfoglia")
        self.output_button.clicked.connect(self.select_output_folder)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_line)
        self.output_layout.addWidget(self.output_button)
        self.layout.addLayout(self.output_layout)

        # Action buttons
        self.action_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converti")
        self.convert_button.setStyleSheet("padding: 10px; font-weight: bold;")
        self.convert_button.clicked.connect(self.run_process)

        self.clear_button = QPushButton("Pulisci campi")
        self.clear_button.clicked.connect(self.clear_fields)

        self.action_layout.addStretch()
        self.action_layout.addWidget(self.convert_button)
        self.action_layout.addWidget(self.clear_button)
        self.layout.addLayout(self.action_layout)

        self.layout.addSpacerItem(QSpacerItem(10, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self._create_menu_bar()

        self.output_folder = ""
        self.input_file = ""

    def select_input_file(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Seleziona file ZIP", "", "ZIP Files (*.zip)")
        if zip_path:
            self.input_file = zip_path
            self.input_line.setText(zip_path)

    def select_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Seleziona cartella di output")
        if folder:
            self.output_folder = folder
            self.output_line.setText(folder)

    def clear_fields(self):
        self.input_file = ""
        self.output_folder = ""
        self.input_line.clear()
        self.output_line.clear()
        self.mode_selector.setCurrentIndex(0)

    def _create_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        help_menu = QMenu("Info", self)
        about_action = QAction("Sviluppatore", self)
        about_action.triggered.connect(self.show_about)

        help_menu.addAction(about_action)
        menu_bar.addMenu(help_menu)

    def show_about(self):
        QMessageBox.information(self, "Informazioni",
            f"Sviluppato da: {DEVELOPER_NAME}\nVersione: {APP_VERSION}")

    def run_process(self):
        if not self.input_file or not self.output_folder:
            QMessageBox.warning(self, "Attenzione", "Completa tutti i campi prima di procedere.")
            return

        mode = self.mode_selector.currentText()
        base_filename = os.path.splitext(os.path.basename(self.input_file))[0]
        output_path = os.path.join(self.output_folder, f"{base_filename}.csv")

        try:
            process_zip_to_csv(self.input_file, output_path, mode)
            QMessageBox.information(self, "Successo", f"CSV salvato in: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

def run_app():
    app = QApplication(sys.argv)
    window = ShpToCsvApp()
    window.show()
    sys.exit(app.exec())
