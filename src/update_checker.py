import requests
import webbrowser
from PyQt6.QtWidgets import QMessageBox
from config import versione  # Assicurati che 'versione' sia definita in config.py


def up_to_date(remote_version, parent=None):
    """Mostra una finestra di dialogo se l'applicazione è già aggiornata."""
    QMessageBox.information(
        parent,  # Usa la finestra principale come parent
        "Aggiornamento software",
        f"L'ultima versione ({remote_version}) è già installata.",
        QMessageBox.StandardButton.Ok
    )


def ask_update(remote_version, parent=None):
    """Mostra una finestra di dialogo per l'aggiornamento disponibile."""
    reply = QMessageBox.question(
        parent,  # Usa la finestra principale come parent
        "Nuova versione disponibile",
        f"Una nuova versione ({remote_version}) è disponibile. Vuoi aggiornare?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No  # Imposta "No" come predefinito
    )

    if reply == QMessageBox.StandardButton.Yes:
        download_url = "https://github.com/mikmark95/file-scanner/releases/latest"
        print(f"Visita questa pagina per scaricare l'ultima versione: {download_url}")
        webbrowser.open(download_url)  # Apre il browser con l'URL di download
    else:
        print("L'aggiornamento è stato annullato.")


def check_version(parent=None):
    """Controlla la versione e avvisa l'utente se è disponibile un aggiornamento."""
    current_version = versione
    repo_url = "https://raw.githubusercontent.com/mikmark95/file-scanner/main/src/config.py"

    response = requests.get(repo_url)

    if response.status_code == 200:
        remote_config = response.text
        start_index = remote_config.find('versione = "') + len('versione = "')
        end_index = remote_config.find('"', start_index)
        remote_version = remote_config[start_index:end_index]

        if current_version != remote_version:
            print(f"⚠️ Attenzione! Una nuova versione ({remote_version}) è disponibile.")
            ask_update(remote_version, parent)
        else:
            print(f"✅ Il programma è aggiornato alla versione {remote_version}.")
            up_to_date(remote_version, parent)
    else:
        print("❌ Errore nel recuperare il file di configurazione da GitHub.")
