import sys
import os
import re
import webbrowser
from pathlib import Path
import tempfile


import markdown
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QComboBox, QMainWindow, QMenuBar, QMenu,
    QSpacerItem, QSizePolicy, QHBoxLayout, QLineEdit, QFrame
)
from PyQt6.QtGui import QFont, QAction
from PyQt6.QtCore import Qt
# from aiofiles import tempfile

from processor import process_zip_to_csv
from config import versione, autore
from update_checker import check_version


class ShpToCsvApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Observer 👁️👁️")
        self.setGeometry(100, 100, 640, 360)
        self.setStyleSheet("""
            QWidget {
                background-color: #2b2f35;
                color: #f0f0f0;
                font-size: 13px;
            }

            QPushButton {
                background-color: #5c7cfa;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
            }

            QPushButton:hover {
                background-color: #4c6ef5;
            }

            QLineEdit {
                background-color: white;
                color: #2b2f35;
                padding: 5px;
                border-radius: 4px;
            }

            QComboBox {
                background-color: white;
                color: #2b2f35;
                padding: 5px;
                border-radius: 4px;
            }

            QLabel {
                font-weight: bold;
            }

            QMenuBar {
                background-color: #3b4252;
                font-size: 13px;
            }

            QMenu::item {
                background-color: #3b4252;
                color: white;
                padding: 5px;
            }
        """)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setSpacing(12)

        title = QLabel("Convertitore Shapefile in CSV / SHP")
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self._add_line_separator()

        self.input_line = self._add_browsable_row("1. File .zip dello shapefile:", True, self.select_input_file)
        self.mode_selector = self._add_combo_row("2. Seleziona la modalità di esportazione", ["Ricerca Perdite", "Padania e Chiampo", "EMLID"], self.toggle_team_field)
        self.team_line = self._add_input_row("3. Nome squadra (solo EMLID):", hide=True)
        self.output_line = self._add_browsable_row("4. Cartella di salvataggio:", True, self.select_output_folder)
        self.format_selector = self._add_combo_row("5. Formato di esportazione", ["CSV", "Shapefile (.shp)"])

        self._add_line_separator()

        action_layout = QHBoxLayout()
        self.convert_button = QPushButton("Converti")
        self.convert_button.clicked.connect(self.run_process)
        self.clear_button = QPushButton("Pulisci campi")
        self.clear_button.clicked.connect(self.clear_fields)
        action_layout.addStretch()
        action_layout.addWidget(self.convert_button)
        action_layout.addWidget(self.clear_button)
        self.layout.addLayout(action_layout)

        self._create_menu_bar()

        self.output_folder = ""
        self.input_file = ""

    def _add_line_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

    def _add_input_row(self, label_text, hide=False):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        layout.addWidget(label)
        layout.addWidget(line_edit)
        self.layout.addLayout(layout)
        label.setVisible(not hide)
        line_edit.setVisible(not hide)
        return line_edit

    def _add_combo_row(self, label_text, items, callback=None):
        label = QLabel(label_text)
        combo = QComboBox()
        combo.addItems(items)
        if callback:
            combo.currentTextChanged.connect(callback)
        self.layout.addWidget(label)
        self.layout.addWidget(combo)
        return combo

    def _add_browsable_row(self, label_text, readonly, browse_action):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        line_edit = QLineEdit()
        line_edit.setReadOnly(readonly)
        button = QPushButton("Sfoglia")
        button.clicked.connect(browse_action)
        layout.addWidget(label)
        layout.addWidget(line_edit)
        layout.addWidget(button)
        self.layout.addLayout(layout)
        return line_edit

    def toggle_team_field(self, text):
        is_emlid = text == "EMLID"
        self.team_line.setVisible(is_emlid)
        self.layout.itemAt(5).layout().itemAt(0).widget().setVisible(is_emlid)  # Mostra/Nasconde etichetta

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
        self.format_selector.setCurrentIndex(0)

    def _create_menu_bar(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)
        help_menu = QMenu("Info", self)
        about_action = QAction("Sviluppatore", self)

        support_menu = QMenu("Supporto", self)
        guida_action = support_menu.addAction("Guida")
        guida_action.triggered.connect(self.guida_function)

        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        menu_bar.addMenu(help_menu)
        menu_bar.addMenu(support_menu)

    def show_about(self):
        QMessageBox.information(self, "Informazioni",
            f"Sviluppato da: {autore}\nVersione: {versione}")

    def check_update(self):
        """Chiama il controllo aggiornamenti con il contesto della finestra principale."""
        check_version(self)

    import webbrowser
    import tempfile
    import requests
    import markdown

    def guida_function(self):
        url_raw = "https://raw.githubusercontent.com/mikmark95/Observer/main/README.md"

        try:
            response = requests.get(url_raw)
            response.raise_for_status()
            markdown_content = response.text
        except requests.RequestException as e:
            print(f"Errore nel download: {e}")
            return

        html_content = markdown.markdown(markdown_content)
        html_full = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <title>Guida - README</title>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """

        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.html', encoding='utf-8') as f:
            f.write(html_full)
            temp_file_path = f.name

        webbrowser.open_new(temp_file_path)

    def run_process(self):
        if not self.input_file or not self.output_folder:
            QMessageBox.warning(self, "Attenzione", "Completa tutti i campi prima di procedere.")
            return

        mode = self.mode_selector.currentText()
        export_format = self.format_selector.currentText().lower().strip()
        if export_format == "shapefile (.shp)":
            export_format = "shp"
        else:
            export_format = "csv"

        base_filename = os.path.splitext(os.path.basename(self.input_file))[0]

        if mode == "EMLID":
            team_name = self.team_line.text().strip()
            if not team_name:
                QMessageBox.warning(self, "Attenzione", "Inserisci il nome della squadra per la modalità EMLID.")
                return
            safe_team_name = re.sub(r'[\\/\\:*?"<>|]', '_', team_name)
            output_path = Path(self.output_folder) / safe_team_name
        else:
            output_path = Path(self.output_folder)

        try:
            output_path = output_path.resolve()
            os.makedirs(output_path, exist_ok=True)
            process_zip_to_csv(self.input_file, str(output_path), mode, export_format)
            QMessageBox.information(self, "Successo", f"File esportati in: {output_path}")
            if os.name == 'nt':
                os.startfile(output_path)
        except PermissionError as pe:
            QMessageBox.critical(self, "Errore di permesso", str(pe))
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

def run_app():
    app = QApplication(sys.argv)
    window = ShpToCsvApp()
    check_version()
    window.show()
    sys.exit(app.exec())
