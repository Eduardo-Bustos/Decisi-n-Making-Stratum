import numpy as np
import pandas as pd
import statsmodels.api as sm

class StratumEngine:
    def __init__(self, tau_base: float = 0.3492):
        self.tau_base = tau_base
        self.regime_labels = {0: "Laminar", 1: "Latente/Tensión", 2: "Acute Stress"}

    def get_dynamic_trigger(self, df: pd.DataFrame):
        """
        Implementación de la Proposition 2: Threshold Dinámico Multi-capa.
        Sustituye el valor fijo por una condición de alineación estructural.
        """
        # 1. Capa de Nivel (Lambda Norm): Percentil histórico para adaptabilidad
        # Usamos el ISI como proxy de la carga del sistema
        lambda_norm = df['ISI'].iloc[-1]
        lambda_threshold = df['ISI'].quantile(0.85) # Umbral de cola dinámica
        
        # 2. Capa de Dinámica (Momentum): ¿El riesgo se está cargando o disipando?
        # Captura la histéresis: delta positivo implica acumulación de presión
        delta_lambda = df['ISI'].diff().iloc[-1]
        
        # 3. Capa de Contexto (Concentración / CP): Capacidad de absorción
        # Si no existe CP, usamos un valor neutro (0.5)
        cp_level = df['CP'].iloc[-1] if 'CP' in df.columns else 0.5
        cp_median = df['CP'].median() if 'CP' in df.columns else 0.5
        
        # Condición Compuesta: El Trigger Geométrico
        # Se activa si: Nivel Alto + Aceleración Positiva + Baja Disipación (CP alto)
        is_trigger = (lambda_norm > lambda_threshold) and (delta_lambda > 0) and (cp_level > cp_median)
        
        # Cálculo de la "Distancia a la Fractura" (Métrica para el dashboard)
        distance = 1.0 - lambda_norm
        
        return {
            "trigger_active": is_trigger,
            "lambda_stat": lambda_norm,
            "lambda_threshold": lambda_threshold,
            "momentum": delta_lambda,
            "structural_concentration": cp_level,
            "fracture_proximity": distance,
            "regime": "CRÍTICO" if is_trigger else "OPERATIVO"
        }

    def process_system_state(self, df: pd.DataFrame):
        # Mantenemos compatibilidad con el CSV para visualización de fondo
        df['threshold_breach'] = df['SG'].abs() > self.tau_base
        return df
