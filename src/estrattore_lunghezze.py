import os.path

import fiona
import geopandas as gpd

'''
Script che serve per fare il controllo in itinere dell avanzamento del rilievo condotte
'''

def calcola_lunghezze(percorso_file):
    '''
    Funzione che prende in input un file .gpkg e ritorna  le lunghezze delle tratte rosse
    :param percorso_file:
    :return: lunghezza -> String
    '''
    # Leggi il file .gpkg
    gdf = gpd.read_file(percorso_file)

    # Mostra i campi disponibili
    print(gdf.head(0))

    # Fase 1: Rimuovi elementi che contengono "_ALL_" nel campo 'unid'
    indici_da_rimuovere = []
    eliminare = 0

    for idx, row in gdf.iterrows():
        if row['unid'] and '_ALL_' in row['unid']:
            indici_da_rimuovere.append(idx)
            eliminare += 1

    print(f'Elementi Totali: {len(gdf)}')
    print(f'Elementi con "_ALL_": {eliminare}')

    # Rimuovi
    gdf.drop(indici_da_rimuovere, inplace=True)
    print(f'Elementi rimasti: {len(gdf)}')

    #Nome file filtrato
    new_name = os.path.join(os.path.dirname(percorso_file), f'{os.path.basename(percorso_file)}_filtrato.csv')


    # Esporta shapefile "pulito" senza "_ALL_"
    output_path = new_name
    if not os.path.exists(output_path):
        gdf.to_file(output_path, driver='ESRI Shapefile')
        print(f'Shapefile salvato in: {output_path}')
    else:
        print(f'Shapefile già presente in: {output_path}')

    # Fase 2: Individua elementi con valori sospetti in 'diametro_n' e 'materiale'
    valori_sospetti_diametro = ['non class', 'non classi', 'scon']
    valori_sospetti_materiale = ['non class']


    elementi_sospetti = 0
    lunghezza_elementi_sospetti = float(0.0)

    print("\n--- RECORD SOSPETTI ---")
    for idx, row in gdf.iterrows():
        diametro_n = str(row['diametro_n']).lower() if row['diametro_n'] else None
        materiale = str(row['materiale']).lower() if row['materiale'] else None

        if (
            diametro_n is None or diametro_n in valori_sospetti_diametro
            or materiale is None or materiale in valori_sospetti_materiale
        ):
            elementi_sospetti += 1
            print(f"Indice: {idx}")
            print(gdf.loc[idx, ['gid','unid', 'diametro_n', 'materiale', 'lunghezza']])
            lunghezza_elementi_sospetti += float(row['lunghezza'])
            print('------------------------------------------------------------------')

    print(f'Elementi sospetti: {elementi_sospetti}')
    print(f'Lunghezza sospetti: {lunghezza_elementi_sospetti}')
    return lunghezza_elementi_sospetti

if __name__ == '__main__':

    # Percorso del file GeoPackage
    percorso_file = r"C:\Users\mmarchetti\Downloads\__TEST VERIFICHE CONDOTTE\Arzignano 17-04-25_ArzignanoCondotte.gpkg"
    percorso_file2 = r"C:\Users\mmarchetti\Downloads\__TEST VERIFICHE CONDOTTE\Arzignano 16-04-25_ArzignanoCondotte.gpkg"
    file1 = calcola_lunghezze(percorso_file)
    file2 = calcola_lunghezze(percorso_file2)
    print('----------------------------------------------------------')
    print(f'Lunghezza file 1: {file1}')
    print(f'Lunghezza file 2: {file2}')