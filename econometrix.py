import pandas as pd
import os

def get_historical_data():
    """
    Capa de Datos Stratum v41.
    Carga optimizada del dataset 1900-2026 para el War Room.
    Coordina la ingesta con main.py y engine/logic.py.
    """
    # RUTA COORDINADA CON CAPTURA DE LAS 15:19
    path = "data/econometric.csv" 
    
    if not os.path.exists(path):
        # Log de error para diagnóstico en Google Cloud
        print(f"ERROR SISTÉMICO: No se halló {path}. Verifique estructura de carpetas.")
        return None
        
    try:
        # Carga optimizada para series temporales de largo plazo
        df = pd.read_csv(path, low_memory=False)
        
        # Sincronización de formatos
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            
        # Protocolo de Seguridad: Asegurar columnas para Proposición 2
        # Si faltan métricas en datos antiguos (ej. 1900), inicializa señales neutras
        if 'ISI' not in df.columns:
            df['ISI'] = 0.0
        if 'CP' not in df.columns:
            df['CP'] = 0.5  # Neutralidad estructural
        if 'SG' not in df.columns:
            df['SG'] = 0.0
                
        return df
    except Exception as e:
        print(f"FALLA DE INGESTA EN ECONOMETRIX: {e}")
        return None
