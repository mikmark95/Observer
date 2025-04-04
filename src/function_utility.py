import shapefile
import csv
import os
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog, messagebox

'''
Scrpit che serve per convertire il file shp delle fognature  caricato da 3eye e crea una gerarchia di sottocartelle divise giornata e csv divisi per squadra
'''


def process_shapefile(shp_path, csv_path):
    try:
        # Creazione directory di output se non esiste
        os.makedirs(csv_path, exist_ok=True)

        # Lettura del file Shapefile
        sf = shapefile.Reader(shp_path)

        # Lettura dei campi (escludendo "DeletionFlag")
        fields = [field[0] for field in sf.fields if field[0] != "DeletionFlag"]
        fields += ["Orario", "Squadra"]  # Aggiunta dei campi "Orario" e "Squadra"

        # Lettura dei record
        records = sf.records()

        # Creazione del dizionario per gruppi di record in base a 'lastDate' e 'Squadra'
        diz = {}
        foto_index = fields.index('Foto')  # Trova l'indice del campo 'Foto'
        id_index = fields.index('id')  # Trova l'indice del campo 'id'

        def is_valid_time_format(value):
            try:
                datetime.strptime(value, "%H_%M")
                return True
            except (ValueError, TypeError):
                return False

        for record in records:
            squad = (record[id_index][0].upper() + '_' + record[fields.index('lastUser')][:-3].split('@')[0])

            # Converte il campo 'Foto' in una lista
            if isinstance(record[foto_index], str):
                record[foto_index] = record[foto_index].split(',')
            elif not isinstance(record[foto_index], list):
                record[foto_index] = [record[foto_index]]

            last_date = record[foto_index][0][:10]
            orario = (record[foto_index][0][-11:-6]) if len(record[foto_index][0]) >= 11 else ""
            if not is_valid_time_format(orario):
                orario = ""

            record += [orario, squad]

            if last_date not in diz:
                diz[last_date] = {}
            if squad not in diz[last_date]:
                diz[last_date][squad] = []
            diz[last_date][squad].append(record)

        # Esportazione dei file CSV
        for last_date, squadre in diz.items():
            dir_giornata = os.path.join(csv_path, last_date if last_date else "Foto_non_presenti")
            os.makedirs(dir_giornata, exist_ok=True)

            for squad, valori in squadre.items():
                dest_csv = os.path.join(dir_giornata, f"{last_date}_Squadra_{squad}.csv")

                # Scrittura iniziale dei record senza Delta tempo
                with open(dest_csv, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(fields)
                    for valore in valori:
                        valore[foto_index] = "; ".join(map(str, valore[foto_index]))
                        writer.writerow(valore)

                # Rileggi, ordina per Orario e calcola Delta tempo
                csv_data = []
                with open(dest_csv, 'r', encoding='utf-8') as csvfile:
                    reader = csv.reader(csvfile)
                    header = next(reader)
                    for row in reader:
                        csv_data.append(row)

                # Ordina i dati
                csv_data.sort(key=lambda x: datetime.strptime(x[-2], "%H_%M") if is_valid_time_format(x[-2]) else datetime.min)

                # Calcolo del Delta tempo e riscrittura
                previous_time = None
                for row in csv_data:
                    if is_valid_time_format(row[-2]):
                        current_time = datetime.strptime(row[-2], "%H_%M")
                        delta_time = int((current_time - previous_time).total_seconds() // 60) if previous_time else 0
                        previous_time = current_time
                    else:
                        delta_time = 0
                    row.append(delta_time)

                # Riscrittura nel CSV ordinato
                with open(dest_csv, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(header + ["Delta_tempo"])
                    writer.writerows(csv_data)

                print(f"CSV aggiornato: {dest_csv}")

    except Exception as e:
        print(f"Errore: {e}")

    messagebox.showinfo("Completato", f"Processo completato con successo.\nFile salvati in: {csv_path}")


def select_shapefile():
    """Seleziona il file Shapefile."""
    file_path = filedialog.askopenfilename(title="Seleziona Shapefile", filetypes=[("Shapefile", "*.shp")])
    shapefile_entry.delete(0, 'end')
    shapefile_entry.insert(0, file_path)


def select_output_folder():
    """Seleziona la cartella di output."""
    folder_path = filedialog.askdirectory(title="Seleziona Cartella di Output")
    output_entry.delete(0, 'end')
    output_entry.insert(0, folder_path)


def run_process():
    """Esegue il processo."""
    shp_path = shapefile_entry.get()
    csv_path = output_entry.get()

    if not shp_path or not csv_path:
        messagebox.showwarning("Attenzione", "Inserire entrambi i percorsi!")
    else:
        process_shapefile(shp_path, csv_path)


def clear_inputs():
    """Pulisce le caselle di input."""
    shapefile_entry.delete(0, 'end')
    output_entry.delete(0, 'end')


def show_info():
    """Mostra informazioni sull'autore e la versione."""
    messagebox.showinfo("Info", "Autore: M. Marchetti\nVersione: 1.2")


# Creazione della finestra principale
root = Tk()
root.title("Processa Shapefile")

# Interfaccia grafica
Label(root, text="Percorso Shapefile:").grid(row=0, column=0, padx=10, pady=5, sticky="e")
shapefile_entry = Entry(root, width=50)
shapefile_entry.grid(row=0, column=1, padx=10, pady=5)
Button(root, text="Sfoglia...", command=select_shapefile).grid(row=0, column=2, padx=10, pady=5)

Label(root, text="Cartella di Output:").grid(row=1, column=0, padx=10, pady=5, sticky="e")
output_entry = Entry(root, width=50)
output_entry.grid(row=1, column=1, padx=10, pady=5)
Button(root, text="Sfoglia...", command=select_output_folder).grid(row=1, column=2, padx=10, pady=5)

# Pulsanti sulla stessa riga
Button(root, text="Esegui", command=run_process, bg="green", fg="white", width=10, height=2).grid(row=2, column=1, padx=5, pady=10, )
Button(root, text="Cancella", command=clear_inputs, bg="orange", width=10, height=2).grid(row=2, column=0, padx=5, pady=10, )
Button(root, text="Info", command=show_info, bg="blue", fg="white", width=10, height=2).grid(row=2, column=2, padx=5, pady=10, )

# Avvio della finestra
root.mainloop()
