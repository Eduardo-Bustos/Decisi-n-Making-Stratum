import pandas as pd
import os

def get_historical_data():
    """
    Carga optimizada del dataset histórico (1900-2026).
    Coordina la ingesta para el War Room.
    """
    # Buscamos el archivo en la carpeta data según tu estructura
    path = "data/econometric.csv" 
    
    if not os.path.exists(path):
        print(f"Error: No se encontró el archivo en {path}")
        return None
        
    try:
        # Cargamos con tipos de datos optimizados para series largas
        df = pd.read_csv(path, low_memory=False)
        
        # Aseguramos que la columna de fecha sea reconocida
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        # Validación de columnas críticas para la Proposición 2
        columns_needed = ['SG', 'ISI', 'CP']
        for col in columns_needed:
            if col not in df.columns:
                # Si falta CP, creamos una señal neutra para no romper el motor
                df[col] = 0.5 if col == 'CP' else 0.0
                
        return df
    except Exception as e:
        print(f"Error en la carga de econometrix: {e}")
        return None
