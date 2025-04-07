import os
import zipfile
import pandas as pd
import geopandas as gpd
import tempfile

def process_zip_to_csv(zip_path: str, output_csv_path: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        shp_file = next((f for f in os.listdir(temp_dir) if f.endswith(".shp")), None)
        if not shp_file:
            raise FileNotFoundError("File .shp non trovato nello zip")

        shp_path = os.path.join(temp_dir, shp_file)
        gdf = gpd.read_file(shp_path)

        df = gdf.copy()
        df['Data e Ora'] = pd.to_datetime(df['Avg start'], errors='coerce')
        df = df.sort_values(by='Data e Ora').reset_index(drop=True)
        df['ID'] = df.index + 1
        df['Differenza'] = df['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(lambda x: int(x.total_seconds() / 60))

        output_df = df[['ID', 'Desc', 'Longitude', 'Latitude', 'Data e Ora', 'Differenza']]
        output_df.to_csv(output_csv_path, index=False)