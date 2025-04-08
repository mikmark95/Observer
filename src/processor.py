import os
import zipfile
import pandas as pd
import geopandas as gpd
import tempfile
import re
from datetime import datetime

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

def process_zip_to_csv(zip_path: str, output_dir: str, mode: str, export_format: str = "csv"):
    mode = mode.strip().lower()
    export_format = export_format.strip().lower()

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_file = next((f for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
        if not shp_file:
            raise FileNotFoundError("File .shp non trovato nello zip")

        shp_path = os.path.join(temp_dir, shp_file)
        gdf = gpd.read_file(shp_path)

        def save_output(df, path, export_format):
            if export_format == "csv":
                df.drop(columns="geometry", errors='ignore').to_csv(path, index=False)
            elif export_format == "shp":
                if "Data e Ora" in df.columns:
                    df["Data"] = df["Data e Ora"].dt.strftime("%Y-%m-%d")
                    df["Ora"] = df["Data e Ora"].dt.strftime("%H:%M:%S")
                    df = df.drop(columns=["Data e Ora"])
                df.to_file(path, driver="ESRI Shapefile")

        if mode == "emlid":
            df = gdf.copy()
            df['Data e Ora'] = pd.to_datetime(df['Avg start'], errors='coerce')
            df = df.sort_values(by='Data e Ora').reset_index(drop=True)
            df['Data'] = df['Data e Ora'].dt.date.astype(str)
            grouped = df.groupby('Data')

            for day, group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(lambda x: int(x.total_seconds() / 60))
                group['geometry'] = gpd.points_from_xy(group['Longitude'], group['Latitude'])
                geo_df = gpd.GeoDataFrame(group[['ID', 'Desc', 'Longitude', 'Latitude', 'Data e Ora', 'Differenza', 'geometry']], crs='EPSG:4326')
                output_file = os.path.join(output_dir, f"dati_{day}.{export_format}")
                save_output(geo_df, output_file, export_format)

        elif mode == "ricerca perdite":
            df = gdf.copy()
            df['Squadra'] = df['lastUser'].astype(str).apply(lambda x: x.split('@')[0] if '@' in x else x)
            df['Data e Ora'] = df['Foto'].astype(str).apply(lambda val: extract_datetime_from_filename_RicercaPerdite(val.split(',')[0].strip()))
            df = df.dropna(subset=['Data e Ora']).sort_values(by='Data e Ora')
            df['Data'] = df['Data e Ora'].dt.date.astype(str)
            grouped = df.groupby(['Squadra', 'Data'])

            for (squadra, day), group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(lambda x: int(x.total_seconds() / 60))
                group['geometry'] = gpd.points_from_xy(group['long'], group['lat'])
                geo_df = gpd.GeoDataFrame(group[['ID', 'lat', 'long', 'Squadra', 'Data e Ora', 'Differenza', 'geometry']], crs='EPSG:4326')

                safe_squadra = re.sub(r'[\\/:*?"<>|]', '_', squadra)
                squadra_dir = os.path.join(output_dir, safe_squadra)
                os.makedirs(squadra_dir, exist_ok=True)
                output_file = os.path.join(squadra_dir, f"dati_{day}.{export_format}")
                save_output(geo_df, output_file, export_format)

        elif mode == "padania e chiampo":
            df = gdf.copy()
            df['Squadra'] = df['note_ge31'].astype(str).str[0].str.upper()
            df['Data e Ora'] = df['nomi foto'].astype(str).apply(extract_datetime_from_filename)
            df = df.dropna(subset=['Data e Ora']).sort_values(by='Data e Ora')
            df['Data'] = df['Data e Ora'].dt.date.astype(str)
            grouped = df.groupby(['Squadra', 'Data'])

            for (squadra, day), group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(lambda x: int(x.total_seconds() / 60))
                group['geometry'] = gpd.points_from_xy(group['coord_x16'], group['coord_y43'])
                geo_df = gpd.GeoDataFrame(group[['ID', 'coord_x16', 'coord_y43', 'Squadra', 'Data e Ora', 'Differenza', 'geometry']], crs='EPSG:4326')

                safe_squadra = re.sub(r'[\\/:*?"<>|]', '_', squadra)
                squadra_dir = os.path.join(output_dir, safe_squadra)
                os.makedirs(squadra_dir, exist_ok=True)
                output_file = os.path.join(squadra_dir, f"dati_{day}.{export_format}")
                save_output(geo_df, output_file, export_format)

        else:
            raise ValueError(f"Modalità non supportata: {mode}")
