# 🛰️ Observer - Convertitore Shapefile in CSV

**Observer** è un'applicazione desktop con interfaccia grafica sviluppata in **Python + PyQt6** per convertire file shapefile compressi `.zip` in **file CSV**, generando automaticamente una struttura ordinata per squadra e giorno di lavoro.

> ✅ Sviluppato da: **Marchetti Michele**  
> 🔖 Versione: `1.0.0`

---

## 🖥️ Funzionalità principali

- 🔍 Lettura shapefile da file `.zip`
- 📂 Creazione automatica di cartelle per squadra e giornata
- 📊 Estrazione ed elaborazione avanzata dei dati geospaziali
- 💡 GUI moderna con supporto per 3 modalità:
  - **EMLID**
  - **Ricerca Perdite**
  - **Padania e Chiampo**

---

## 📸 Modalità di esportazione

### 🔹 EMLID
- Richiede **nome squadra**
- Estrae:
  - `ID`, `Desc`, `Longitude`, `Latitude`
  - `Data e Ora` (da campo `Avg start`)
  - `Differenza` (tempo in minuti rispetto al record precedente)
- Crea un CSV per ogni **giornata**.

---

### 🔹 Ricerca Perdite
- Estrae:
  - `ID`, `Lat`, `Long`
  - `Squadra` (da `lastUser`, prima della `@`)
  - `Data e Ora` (dal nome file PNG nel campo `Foto`)
  - `Differenza` (tra i record)
- Crea una cartella per ogni **squadra**, con un CSV per ogni **giorno**.

---

### 🔹 Padania e Chiampo
- Estrae:
  - `ID`, `X`, `Y`
  - `Squadra` (dal primo carattere del campo `note_ge31`)
  - `Data e Ora` (dal nome JPG in `nomi foto`)
  - `Differenza` (tra i record)
- Organizzazione per **squadra e giorno**.

---

## 🧑‍💻 Avvio

### ⚙️ Prerequisiti

Installa i pacchetti richiesti:

```bash
pip install -r requirements.txt
