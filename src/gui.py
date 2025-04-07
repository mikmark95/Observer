import sys
import os
import re
from pathlib import Path
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QComboBox, QMainWindow, QMenuBar, QMenu,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit
)
from PyQt6.QtGui import QFont, QAction, QCursor
from PyQt6.QtCore import Qt
from processor import process_zip_to_csv
from config import APP_VERSION, DEVELOPER_NAME

class ShpToCsvApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Observer 👁️👁️")
        self.setGeometry(100, 100, 500, 250)
        self.setStyleSheet("""
                           QWidget {
                               background-color: #374048;
                               color: white;
                               font-size: 14px;
                           }

                           QPushButton {
                               background-color: #B7BFC8;
                               color: white;
                               border-radius: 5px;
                               padding: 5px;
                           }

                           QPushButton:hover {
                               background-color: #81A1C1;
                           }

                           QLineEdit {
                               background-color: white;
                               font-size: 14px;
                               color: #374048;
                           }

                           QMenuBar {
                               background-color: #6F7F90;
                               font-size: 14px;
                           }
                           QMenu::item {
                               background-color: #6F7F90;  
                               color: white;  
                               padding: 5px;  
                           }

                       """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        title = QLabel("Convertitore Shapefile in CSV")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.layout.addSpacerItem(QSpacerItem(10, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

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
        self.mode_selector.addItems(["Ricerca Perdite", "Padania e Chiampo", "EMLID"])
        self.mode_selector.currentTextChanged.connect(self.toggle_team_field)
        self.layout.addWidget(self.mode_selector)

        # Team name field (only for EMLID)
        self.team_layout = QHBoxLayout()
        self.team_label = QLabel("Nome squadra:")
        self.team_line = QLineEdit()
        self.team_layout.addWidget(self.team_label)
        self.team_layout.addWidget(self.team_line)
        self.layout.addLayout(self.team_layout)
        self.team_label.setVisible(False)
        self.team_line.setVisible(False)

        # Output folder selection
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel("3. Cartella di salvataggio:")
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

    def toggle_team_field(self, text):
        is_emlid = text == "EMLID"
        self.team_label.setVisible(is_emlid)
        self.team_line.setVisible(is_emlid)

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
        self.team_line.clear()
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

        if mode == "EMLID":
            team_name = self.team_line.text().strip()
            if not team_name:
                QMessageBox.warning(self, "Attenzione", "Inserisci il nome della squadra per la modalità EMLID.")
                return
            safe_team_name = re.sub(r'[\/\:*?"<>|]', '_', team_name)
            output_path = Path(self.output_folder) / safe_team_name
        else:
            output_path = Path(self.output_folder)

        try:
            output_path = output_path.resolve()
            print(f"Percorso destinazione: {output_path}")

            if output_path.exists() and not output_path.is_dir():
                raise PermissionError(f"Esiste un file con lo stesso nome della cartella: {output_path}")

            os.makedirs(output_path, exist_ok=True)

            if not os.access(output_path, os.W_OK):
                raise PermissionError(f"Non hai i permessi per scrivere in: {output_path}")

            process_zip_to_csv(self.input_file, str(output_path), mode)
            QMessageBox.information(self, "Successo", f"File CSV salvati in: {output_path}")
            if os.name == 'nt':
                os.startfile(output_path)

        except PermissionError as pe:
            QMessageBox.critical(self, "Errore di permesso", str(pe))
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

def run_app():
    app = QApplication(sys.argv)
    window = ShpToCsvApp()
    window.show()
    sys.exit(app.exec())