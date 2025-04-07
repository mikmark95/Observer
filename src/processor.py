import os
import zipfile
import pandas as pd
import geopandas as gpd
import tempfile
import re

def process_zip_to_csv(zip_path: str, output_dir: str, mode: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_file = next((f for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
        if not shp_file:
            raise FileNotFoundError("File .shp non trovato nello zip")

        shp_path = os.path.join(temp_dir, shp_file)
        gdf = gpd.read_file(shp_path)

        if mode == "EMLID":
            df = gdf.copy()
            df['Data e Ora'] = pd.to_datetime(df['Avg start'], errors='coerce')
            df = df.sort_values(by='Data e Ora').reset_index(drop=True)
            df['Data'] = df['Data e Ora'].dt.date.astype(str)

            grouped = df.groupby('Data')
            for day, group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(lambda x: int(x.total_seconds() / 60))
                output_df = group[['ID', 'Desc', 'Longitude', 'Latitude', 'Data e Ora', 'Differenza']]
                safe_day = re.sub(r'[\\/:*?"<>|]', '_', str(day))
                output_file = os.path.join(output_dir, f"dati_{safe_day}.csv")
                output_df.to_csv(output_file, index=False)

        elif mode == "Ricerca Perdite":
            output_df = gdf[['Desc', 'Longitude', 'Latitude']].copy()
            output_df.insert(0, 'ID', range(1, len(output_df) + 1))
            output_file = os.path.join(output_dir, "ricerca_perdite.csv")
            output_df.to_csv(output_file, index=False)

        elif mode == "Padania e Chiampo":
            output_df = gdf[['Name', 'Longitude', 'Latitude']].copy()
            output_df.insert(0, 'ID', range(1, len(output_df) + 1))
            output_file = os.path.join(output_dir, "padania_chiampo.csv")
            output_df.to_csv(output_file, index=False)

        else:
            raise ValueError(f"Modalità non supportata: {mode}")
