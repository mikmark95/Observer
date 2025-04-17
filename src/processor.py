import os
import zipfile
import pandas as pd
import geopandas as gpd
import tempfile
import re
from datetime import datetime
import folium
import webbrowser
from pathlib import Path
from folium.plugins import Fullscreen
from bs4 import BeautifulSoup

from bs4 import BeautifulSoup
import re

def aggiungi_popup_a_html(percorso_input: str):
    with open(percorso_input, "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # Trova l'ID della mappa dinamicamente
    match = re.search(r"var (map_[a-f0-9]+) = L\.map", html)
    if not match:
        print(f"⚠️ ID mappa non trovato in: {percorso_input}")
        return
    map_id = match.group(1)

    script_js = f"""
    <script>
      const markerById = {{}};

      {map_id}.eachLayer(layer => {{
        if (layer instanceof L.Marker && layer.getTooltip()) {{
          const tooltipContent = layer.getTooltip().getContent();
          const match = tooltipContent.match(/ID:\\s*(\\d+)/);
          if (match) {{
            const id = match[1];
            markerById[id] = layer;
          }}
        }}
      }});

      document.querySelectorAll("#data-table tbody tr").forEach(row => {{
        row.addEventListener("click", () => {{
          const idCell = row.querySelector("td");
          if (!idCell) return;
          const id = idCell.textContent.trim();

          const marker = markerById[id];
          if (marker) {{
            marker.openPopup();
            document.querySelectorAll("#data-table tbody tr").forEach(r => r.classList.remove("table-selected"));
            row.classList.add("table-selected");
          }}
        }});
      }});
    </script>
    """

    if soup.body:
        soup.body.append(BeautifulSoup(script_js, "html.parser"))

    with open(percorso_input, "w", encoding="utf-8") as f:
        f.write(str(soup))

    print(f"✅ Popup integrato in: {percorso_input}")



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


def show_shp_on_map(geo_df: gpd.GeoDataFrame, output_path: Path):
    if geo_df.empty:
        print("Shapefile vuoto.")
        return

    geo_df = geo_df.sort_values(by="ID").reset_index(drop=True)

    # Riproiettiamo per calcolare il centroide correttamente
    geo_df_projected = geo_df.to_crs(epsg=3857)
    centroid_projected = geo_df_projected.geometry.centroid
    centroid_geo = gpd.GeoDataFrame(geometry=centroid_projected, crs=3857).to_crs(4326)
    center = [centroid_geo.geometry.y.mean(), centroid_geo.geometry.x.mean()]

    m = folium.Map(location=center, zoom_start=15)
    Fullscreen().add_to(m)

    coords = [(point.y, point.x) for point in geo_df.geometry]
    folium.PolyLine(locations=coords, color="gray", weight=3, tooltip="Percorso").add_to(m)

    # Creiamo un dizionario per memorizzare le coordinate di ogni punto
    markers_dict = {}

    for i, row in geo_df.iterrows():
        lat = row.geometry.y
        lng = row.geometry.x
        color = "blue" if i == len(geo_df) - 1 else "green" if i == 0 else "red"

        # Salviamo le coordinate nel dizionario usando l'ID come chiave
        markers_dict[str(row['ID'])] = [lat, lng]

        folium.Marker(
            location=[lat, lng],
            popup=folium.Popup(row.drop("geometry").to_frame().to_html(), max_width=300),
            tooltip=f"ID: {row.get('ID', '')}",
            icon=folium.Icon(color=color)
        ).add_to(m)

    # Prepariamo la tabella
    display_df = geo_df.copy()
    display_df['table_id'] = display_df.index.astype(str)

    table_html = display_df.drop(columns="geometry", errors="ignore").to_html(
        classes="table table-striped table-hover table-sm",
        index=False,
        table_id="data-table"
    )

    # Template HTML con JavaScript migliorato per il centramento sulla mappa
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Mappa e dati</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/css/bootstrap.min.css">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: Arial, sans-serif;
                overflow-x: hidden;
            }
            .main-container {
                display: flex;
                flex-direction: row;
                width: 100%;
                height: 100vh;
                margin: 0;
                padding: 0;
            }
            .map-container {
                flex: 1;
                height: 100vh;
                position: sticky;
                top: 0;
            }
            .table-container {
                flex: 1;
                height: 100vh;
                overflow-y: auto;
                padding: 20px;
                background-color: #f8f9fa;
                box-shadow: -2px 0 10px rgba(0,0,0,0.1);
            }
            #map {
                height: 100%;
                width: 100%;
            }
            .table {
                width: 100%;
                font-size: 14px;
                margin-top: 0;
                table-layout: fixed;
                white-space: nowrap;
            }
            .table th, .table td {
                overflow: hidden;
                text-overflow: ellipsis;
                padding: 8px;
                border: 1px solid #dee2e6;
                white-space: nowrap;
            }
            #data-table tbody tr {
                cursor: pointer;
            }
            #data-table tbody tr:hover {
                background-color: #e9ecef !important;
            }
            .table-selected {
                background-color: #cfe2ff !important;
            }
            h2 {
                margin-bottom: 20px;
                border-bottom: 1px solid #dee2e6;
                padding-bottom: 10px;
            }

            /* Stile per dispositivi mobili */
            @media (max-width: 768px) {
                .main-container {
                    flex-direction: column;
                }
                .map-container, .table-container {
                    flex: none;
                    width: 100%;
                    height: 50vh;
                }
            }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="map-container">
                <div id="map">{{map_html}}</div>
            </div>
            <div class="table-container">
                <h2>Dati degli elementi</h2>
                <div class="table-responsive">
                    {{table_html}}
                </div>
            </div>
        </div>

        <script src="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/5.2.3/js/bootstrap.bundle.min.js"></script>
        <script>
            // Dizionario delle coordinate dei marker
            const markers = {{markers_dict}};

            // Funzione per trovare l'oggetto mappa nell'iframe
            function findMapObject() {
                const iframe = document.querySelector('.map-container iframe');
                if (!iframe || !iframe.contentWindow) return null;

                try {
                    // Cerca tutte le variabili globali nell'iframe che potrebbero essere la mappa
                    for (const key in iframe.contentWindow) {
                        if (key.startsWith('map_') && 
                            typeof iframe.contentWindow[key] === 'object' && 
                            iframe.contentWindow[key].setView) {
                            return iframe.contentWindow[key];
                        }
                    }
                } catch (e) {
                    console.error('Errore nella ricerca dell\'oggetto mappa:', e);
                }
                return null;
            }

            document.addEventListener('DOMContentLoaded', function() {
                // Attendiamo che l'iframe sia caricato
                let attempts = 0;
                const maxAttempts = 20;

                const checkInterval = setInterval(function() {
                    attempts++;
                    const mapObject = findMapObject();

                    if (mapObject || attempts >= maxAttempts) {
                        clearInterval(checkInterval);
                        if (mapObject) {
                            console.log('Mappa trovata, configurazione eventi tabella');

                            // Configurazione degli eventi click sulla tabella
                            document.querySelectorAll('#data-table tbody tr').forEach(row => {
                                row.addEventListener('click', function() {
                                    const id = this.cells[0].textContent.trim();
                                    if (markers[id]) {
                                        const [lat, lng] = markers[id];
                                        mapObject.setView([lat, lng], 17);

                                        // Evidenziazione riga selezionata
                                        document.querySelectorAll('#data-table tbody tr').forEach(r => 
                                            r.classList.remove('table-selected'));
                                        this.classList.add('table-selected');
                                    }
                                });
                            });
                        } else {
                            console.error('Non è stato possibile trovare l\'oggetto mappa dopo', attempts, 'tentativi');

                            // Piano B: prova un approccio alternativo per trovare la mappa
                            const iframe = document.querySelector('.map-container iframe');
                            if (iframe && iframe.contentDocument) {
                                try {
                                    // Inietta uno script nell'iframe che renderà l'oggetto mappa accessibile
                                    const script = document.createElement('script');
                                    script.textContent = `
                                        // Trova tutte le istanze di mappa
                                        window.mapObjects = [];
                                        for (const key in window) {
                                            if (typeof window[key] === 'object' && window[key] && window[key].setView) {
                                                window.mapObjects.push(window[key]);
                                            }
                                        }
                                        // Esponi una funzione per centrare la mappa
                                        window.centerMap = function(lat, lng, zoom) {
                                            if (window.mapObjects && window.mapObjects.length > 0) {
                                                window.mapObjects[0].setView([lat, lng], zoom || 17);
                                                return true;
                                            }
                                            return false;
                                        };
                                    `;
                                    iframe.contentDocument.body.appendChild(script);

                                    // Configura gli eventi della tabella per utilizzare questa funzione
                                    document.querySelectorAll('#data-table tbody tr').forEach(row => {
                                        row.addEventListener('click', function() {
                                            const id = this.cells[0].textContent.trim();
                                            if (markers[id] && iframe.contentWindow.centerMap) {
                                                const [lat, lng] = markers[id];
                                                iframe.contentWindow.centerMap(lat, lng, 17);

                                                // Evidenziazione riga selezionata
                                                document.querySelectorAll('#data-table tbody tr').forEach(r => 
                                                    r.classList.remove('table-selected'));
                                                this.classList.add('table-selected');
                                            }
                                        });
                                    });
                                } catch (e) {
                                    console.error('Anche il piano B è fallito:', e);
                                }
                            }
                        }
                    }
                }, 500); // Controlla ogni 500ms
            });
        </script>
    </body>
    </html>
    """

    # Convertiamo il dizionario dei marker in formato JSON per JavaScript
    import json
    markers_json = json.dumps(markers_dict)

    html_content = (
        html_template
        .replace("{{map_html}}", m.get_root().render())
        .replace("{{table_html}}", table_html)
        .replace("{{markers_dict}}", markers_json)
    )

    html_output_path = output_path.with_suffix(".html")
    with open(html_output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    aggiungi_popup_a_html(str(html_output_path))
    print(f"✅ HTML modificato con popup: {html_output_path}")


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
                # Per CSV esportiamo tutti i campi tranne la geometria
                df.drop(columns="geometry", errors='ignore').to_csv(path, index=False)
            elif export_format == "shp":
                if "Data e Ora" in df.columns:
                    df["Data e Ora"] = pd.to_datetime(df["Data e Ora"])
                    df["Data"] = df["Data e Ora"].dt.strftime("%Y-%m-%d")
                    df["Ora"] = df["Data e Ora"].dt.strftime("%H:%M:%S")
                    df = df.drop(columns=["Data e Ora"])

                # Se siamo in modalità "ricerca perdite", ordiniamo i campi come richiesto
                mode_lower = mode.strip().lower()
                if mode_lower == "ricerca perdite":
                    # Assicuriamoci che tutti i campi necessari esistano
                    for field in ["Note"]:
                        if field not in df.columns:
                            df[field] = ""  # Aggiungiamo campi mancanti con valore vuoto

                    # Selezioniamo e ordiniamo i campi come richiesto
                    fields = ["ID", "long", "lat", "Squadra", "Data", "Ora", "Differenza", "Note", "geometry"]
                    keep_fields = [f for f in fields if f in df.columns]
                    df = df[keep_fields]

                df.to_file(path, driver="ESRI Shapefile")
                show_shp_on_map(df, Path(path))

        if mode == "emlid":
            df = gdf.copy()

            # Conversione campo data
            df['Data e Ora'] = pd.to_datetime(df['Avg start'], errors='coerce')
            df = df.dropna(subset=['Data e Ora']).sort_values(by='Data e Ora').reset_index(drop=True)

            # Aggiunta campi
            df['ID'] = df.index + 1
            df['Differenza'] = df['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                lambda x: int(x.total_seconds() / 60)
            )

            # Crea GeoDataFrame solo con i campi richiesti
            df['geometry'] = gpd.points_from_xy(df['Longitude'], df['Latitude'])
            fields = ['ID', 'Longitude', 'Latitude', 'Desc', 'Data e Ora', 'Differenza', 'geometry']
            geo_df = gpd.GeoDataFrame(df[fields], crs='EPSG:4326')

            # Campo "Data" per raggruppare
            geo_df['Data'] = geo_df['Data e Ora'].dt.date.astype(str)
            grouped = geo_df.groupby('Data')

            for day, group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                    lambda x: int(x.total_seconds() / 60)
                )

                output_file = os.path.join(output_dir, f"dati_{day}.{export_format}")
                save_output(group, output_file, export_format)




        elif mode == "ricerca perdite":
            df = gdf.copy()
            df['Squadra'] = df['lastUser'].astype(str).apply(lambda x: x.split('@')[0] if '@' in x else x)
            df['Data e Ora'] = df['Foto'].astype(str).apply(
                lambda val: extract_datetime_from_filename_RicercaPerdite(val.split(',')[0].strip()))
            df = df.dropna(subset=['Data e Ora']).sort_values(by='Data e Ora')
            df['Data'] = df['Data e Ora'].dt.date.astype(str)
            df['Ora'] = df['Data e Ora'].dt.strftime('%H:%M:%S')
            if 'note' in df.columns:
                df['Note'] = df['note']
            else:
                df['Note'] = ""

            grouped = df.groupby(['Squadra', 'Data'])
            for (squadra, day), group in grouped:
                group = group.sort_values(by='Data e Ora').reset_index(drop=True)
                group['ID'] = group.index + 1
                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(
                    lambda x: int(x.total_seconds() / 60))
                group['lat'] = group['lat']  # Assicuriamoci che esistano queste colonne
                group['long'] = group['long']
                group['geometry'] = gpd.points_from_xy(group['long'], group['lat'])

                # Ordiniamo i campi come richiesto per "Ricerca Perdite"
                fields = ["ID", "long", "lat", "Squadra", "Data", "Ora", "Differenza", "Note", "geometry"]
                keep_fields = [f for f in fields if f in group.columns]
                geo_df = gpd.GeoDataFrame(group[keep_fields], crs='EPSG:4326')

                safe_squadra = re.sub(r'[\/:*?"<>|]', '_', squadra)
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

                group['Differenza'] = group['Data e Ora'].diff().fillna(pd.Timedelta(seconds=0)).apply(

                    lambda x: int(x.total_seconds() / 60)

                )

                group['geometry'] = gpd.points_from_xy(group['coord_x16'], group['coord_y43'])

                group = group.rename(columns={'coord_x16': 'Longitude', 'coord_y43': 'Latitude'})

                fields = ['ID', 'Longitude', 'Latitude', 'Squadra', 'Data e Ora', 'Differenza', 'geometry']

                group = group[fields]

                geo_df = gpd.GeoDataFrame(group, geometry='geometry', crs='EPSG:4326')

                safe_squadra = re.sub(r'[\/:*?"<>|]', '_', squadra)

                squadra_dir = os.path.join(output_dir, safe_squadra)

                os.makedirs(squadra_dir, exist_ok=True)

                output_file = os.path.join(squadra_dir, f"dati_{day}.{export_format}")

                save_output(geo_df, output_file, export_format)

        else:

            raise ValueError(f"Modalità non supportata:")