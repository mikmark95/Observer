import os
import zipfile
import pandas as pd
import geopandas as gpd
import tempfile
import re
from datetime import datetime
import fiona

def extract_datetime_from_filename(filename: str) -> datetime:
    match = re.search(r'(\d{4}-\d{2}-\d{2})-(\d{6})', filename)
    if match:
        date_part, time_part = match.groups()
        try:
            return datetime.strptime(f"{date_part} {time_part}", "%Y-%m-%d %H%M%S")
        except:
            return pd.NaT
    return pd.NaT

def extract_datetime_from_filename_RicercaPerdite(filename: str) -> datetime:
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})_(\d{2})_(\d{2})', filename)
    if match:
        try:
            return datetime.strptime('_'.join(match.groups()), "%Y_%m_%d_%H_%M")
        except:
            return pd.NaT
    match = re.search(r'(\d{4}-\d{2}-\d{2})-(\d{6})', filename)
    if match:
        try:
            return datetime.strptime(f"{match.group(1)} {match.group(2)}", "%Y-%m-%d %H%M%S")
        except:
            return pd.NaT
    return pd.NaT

def process_zip_to_csv(zip_path: str, output_dir: str, mode: str):
    mode = mode.strip().lower()
    print(f"Modalità selezionata: {mode}")
    print(f"Percorso file ZIP: {zip_path}")
    print(f"Cartella di output: {output_dir}")

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_file = next((f for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
        if not shp_file:
            raise FileNotFoundError("File .shp non trovato nello zip")

        shp_path = os.path.join(temp_dir, shp_file)
        gdf = gpd.read_file(shp_path)

        if mode == "emlid":
            df = gdf.copy()
            df['Data e Ora'] = pd.to_datetime(df['Avg start'], errors='coerce')
            df = df.sort_values(by='Data e Ora').reset_index(drop=True)
            df['Data'] = df['Data e Ora'].dt.date.astype(str)

            grouped = df.groupby('Data')
            for day, group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                    lambda x: int(x.total_seconds() / 60))
                output_df = group[['ID', 'Desc', 'Longitude', 'Latitude', 'Data e Ora', 'Differenza']]
                safe_day = re.sub(r'[\\/:*?"<>|]', '_', str(day))
                output_file = os.path.join(output_dir, f"dati_{safe_day}.csv")
                output_df.to_csv(output_file, index=False)
                print(f"File CSV creato: {output_file}")

        elif mode == "ricerca perdite":
            df = gdf.copy()
            df['Squadra'] = df['lastUser'].astype(str).apply(lambda x: x.split('@')[0] if '@' in x else x)
            df['Data e Ora'] = df['Foto'].astype(str).apply(
                lambda val: extract_datetime_from_filename_RicercaPerdite(val.split(',')[0].strip()))
            print("Esempi di valori in 'lastUser':", df['lastUser'].dropna().unique()[:5])
            print("Esempi di valori in 'Foto':", df['Foto'].dropna().unique()[:5])
            print("Numero righe con Data e Ora valida:", df['Data e Ora'].notna().sum())
            print("Numero righe con Squadra valida:", df['Squadra'].notna().sum())
            df = df.dropna(subset=['Data e Ora'])
            df = df.sort_values(by='Data e Ora')
            df['Data'] = df['Data e Ora'].dt.date.astype(str)
            grouped = df.groupby(['Squadra', 'Data'])
            for (squadra, day), group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                    lambda x: int(x.total_seconds() / 60))
                output_df = group[['ID', 'lat', 'long', 'Squadra', 'Data e Ora', 'Differenza']].copy()
                output_df.columns = ['ID', 'Lat', 'Long', 'Squadra', 'Data e Ora', 'Differenza']
                safe_squadra = re.sub(r'[\\/:*?"<>|]', '_', squadra)
                safe_day = re.sub(r'[\\/:*?"<>|]', '_', str(day))
                squadra_dir = os.path.join(output_dir, safe_squadra)
                os.makedirs(squadra_dir, exist_ok=True)
                print(f"Cartella creata o esistente: {squadra_dir}")
                output_file = os.path.join(squadra_dir, f"dati_{safe_day}.csv")
                output_df.to_csv(output_file, index=False)
                print(f"File CSV creato: {output_file}")

        elif mode == "padania e chiampo":
            df = gdf.copy()
            df['Squadra'] = df['note_ge31'].astype(str).str[0].str.upper()
            df['Data e Ora'] = df['nomi foto'].astype(str).apply(extract_datetime_from_filename)

            print("Esempi di valori in 'note_ge31':", df['note_ge31'].dropna().unique()[:5])
            print("Esempi di valori in 'nomi foto':", df['nomi foto'].dropna().unique()[:5])
            print("Numero righe con Data e Ora valida:", df['Data e Ora'].notna().sum())
            print("Numero righe con Squadra valida:", df['Squadra'].notna().sum())

            df = df.dropna(subset=['Data e Ora'])
            df = df.sort_values(by='Data e Ora')
            df['Data'] = df['Data e Ora'].dt.date.astype(str)

            grouped = df.groupby(['Squadra', 'Data'])
            for (squadra, day), group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                    lambda x: int(x.total_seconds() / 60))

                output_df = group[['ID', 'coord_x16', 'coord_y43', 'Squadra', 'Data e Ora', 'Differenza']].copy()
                output_df.columns = ['ID', 'X', 'Y', 'Squadra', 'Data e Ora', 'Differenza']

                safe_squadra = re.sub(r'[\\/:*?"<>|]', '_', squadra)
                safe_day = re.sub(r'[\\/:*?"<>|]', '_', str(day))
                squadra_dir = os.path.join(output_dir, safe_squadra)
                os.makedirs(squadra_dir, exist_ok=True)
                print(f"Cartella creata o esistente: {squadra_dir}")

                output_file = os.path.join(squadra_dir, f"dati_{safe_day}.csv")
                output_df.to_csv(output_file, index=False)
                print(f"File CSV creato: {output_file}")

        else:
            raise ValueError(f"Modalità non supportata: {mode}")
