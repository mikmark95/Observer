import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog,
    QLabel, QMessageBox, QComboBox
)
from processor import process_zip_to_csv

class ShpToCsvApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shapefile to CSV Converter")
        self.setGeometry(100, 100, 400, 200)

        self.layout = QVBoxLayout()

        self.label = QLabel("Seleziona un file .zip contenente uno shapefile")
        self.layout.addWidget(self.label)

        self.mode_label = QLabel("Seleziona la modalità di esportazione:")
        self.layout.addWidget(self.mode_label)

        self.mode_selector = QComboBox()
        self.mode_selector.addItems(["EMLID", "Ricerca Perdite", "Padania e Chiampo"])
        self.layout.addWidget(self.mode_selector)

        self.button = QPushButton("Carica .zip e Converti")
        self.button.clicked.connect(self.run_process)
        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

    def run_process(self):
        zip_path, _ = QFileDialog.getOpenFileName(self, "Seleziona file ZIP", "", "ZIP Files (*.zip)")
        if not zip_path:
            return

        output_path, _ = QFileDialog.getSaveFileName(self, "Salva CSV come", "output_punti.csv", "CSV Files (*.csv)")
        if not output_path:
            return

        mode = self.mode_selector.currentText()

        try:
            process_zip_to_csv(zip_path, output_path, mode)
            QMessageBox.information(self, "Successo", f"CSV salvato in: {output_path}")
        except Exception as e:
            QMessageBox.critical(self, "Errore", str(e))

def run_app():
    app = QApplication(sys.argv)
    window = ShpToCsvApp()
    window.show()
    sys.exit(app.exec())
