# 🛰️ Observer - Convertitore Shapefile in CSV / SHP

**Observer** è un'applicazione desktop con interfaccia grafica sviluppata in **Python + PyQt6** per convertire file shapefile compressi `.zip` in **file CSV** o **Shapefile**, generando automaticamente una struttura ordinata per **squadra** e **giorno di lavoro**, con mappe interattive integrate.

> ✅ Sviluppato da: **Michele Marchetti**  
> 🔖 Versione: `2.0`

---

## 🖥️ Funzionalità principali

- 🔍 Lettura automatica di shapefile da archivi `.zip`
- 📂 Creazione di cartelle suddivise per **squadra** e **giorno**
- 📊 Estrazione ed elaborazione avanzata di dati geospaziali
- 🧠 Calcolo differenza in minuti tra i record
- 🗺️ Generazione automatica di mappe HTML interattive sincronizzate con i dati
- 💡 GUI moderna con supporto a **3 modalità operative**:
  - **EMLID**
  - **Ricerca Perdite**
  - **Padania e Chiampo**
- 📈 Esportazione in `.csv` o `.shp`
- 🚀 Controllo aggiornamenti integrato da GitHub
- 🧭 Guida accessibile direttamente dall'app

---

## 📸 Modalità di esportazione

### 🔹 EMLID
- Richiede **nome squadra**
- Estrae e salva:
  - `ID`, `Desc`, `Longitude`, `Latitude`
  - `Data e Ora` (dal campo `Avg start`)
  - `Differenza` (tempo in minuti rispetto al record precedente)
- Crea un file per **ogni giornata**
- Mappa HTML generata con marker colorati e tabella interattiva

---

### 🔹 Ricerca Perdite
- Estrae e salva:
  - `ID`, `Lat`, `Long`
  - `Squadra` (dal campo `lastUser`, parte prima della `@`)
  - `Data e Ora` (dal nome PNG nel campo `Foto`)
  - `Differenza` (tra i record)
- Crea una **cartella per ogni squadra**, con file suddivisi per giorno
- Mappa HTML sincronizzata: cliccando su una riga, si apre il marker sulla mappa

---

### 🔹 Padania e Chiampo
- Estrae e salva:
  - `ID`, `Longitude`, `Latitude`
  - `Squadra` (dal primo carattere del campo `note_ge31`)
  - `Data e Ora` (dal nome JPG in `nomi foto`)
  - `Differenza` (tra i record)
- Dati esportati e organizzati per **squadra e giorno**
- Mappa HTML generata per ogni giorno

---

## 🚀 Avvio rapido

### ⚙️ Prerequisiti

Installa i pacchetti richiesti:

```bash
pip install -r requirements.txt
```

Se il file `requirements.txt` non è disponibile:

```bash
pip install PyQt6 geopandas pandas folium requests markdown beautifulsoup4
```

### ▶️ Avvio dell'app

Da terminale:

```bash
python src/main.py
```

---

## 📁 Struttura del progetto

```
Observer/
├── src/
│   ├── main.py              # Punto di avvio
│   ├── gui.py               # Interfaccia grafica PyQt6
│   ├── processor.py         # Logica per conversione e mappe
│   ├── config.py            # Info su autore e versione
│   └── update_checker.py    # Controllo aggiornamenti GitHub
```

---

## 🗺️ Output generato

Per ogni esportazione viene prodotto:

- 📄 File `.csv` o `.shp` con campi come:
  - `ID`, `Data`, `Ora`, `Lat`, `Long`, `Squadra`, `Differenza`, `Note`
- 🧭 Una **mappa HTML interattiva** con:
  - Visualizzazione sincrona tra tabella e marker
  - Evidenziazione selezione
  - Pop-up informativi per ogni punto

---

## ℹ️ Altre funzionalità

- ✅ Controllo versione integrato: confronta con la versione su GitHub
- 📖 Guida accessibile dal menu "Supporto"
- 📤 Supporta sia output semplice che avanzato

---

## 👨‍💻 Autore

**Michele Marchetti**

---

## 📃 Licenza

Consultare → [QUI](https://raw.githubusercontent.com/mikmark95/Observer/refs/heads/main/LICENSE
)


---

## 🔜 Idee per il futuro

- [ ] Esportazione diretta in PDF con layout elegante
- [ ] Visualizzazione guida integrata nella GUI (senza browser)
- [ ] Supporto drag & drop per i file `.zip`
