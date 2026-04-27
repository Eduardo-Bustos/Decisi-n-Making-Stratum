import numpy as np
import pandas as pd

class StratumEngine:
    def __init__(self, tau_base: float = 0.3492):
        """
        Inicializa el motor con el umbral histórico de referencia.
        """
        self.tau_base = tau_base

    def get_dynamic_trigger(self, df: pd.DataFrame):
        """
        Implementación de la Proposition 2: Geometría de Riesgo Dinámica.
        Evalúa la alineación de Nivel, Momentum y Concentración.
        """
        # Validar existencia de datos mínimos
        if df.empty:
            return self._empty_results()

        # 1. Capa de Nivel (Lambda Norm): Percentil 85 histórico
        # Representa la carga actual vs. la fatiga histórica del sistema
        lambda_norm = df['ISI'].iloc[-1]
        lambda_threshold = df['ISI'].quantile(0.85)
        
        # 2. Capa de Dinámica (Momentum): Dirección del flujo de riesgo
        # Un delta positivo indica que el sistema está acumulando presión (carga activa)
        delta_lambda = df['ISI'].diff().iloc[-1] if len(df) > 1 else 0
        
        # 3. Capa de Contexto (Concentración / CP): Fragilidad estructural
        # Mide si los chokepoints están saturados (baja biodiversidad de respuesta)
        cp_level = df['CP'].iloc[-1] if 'CP' in df.columns else 0.5
        cp_median = df['CP'].median() if 'CP' in df.columns else 0.5
        
        # LÓGICA DE ACTIVACIÓN (Trigger Geométrico)
        # La ruptura ocurre por ALINEACIÓN, no solo por nivel.
        is_trigger = (lambda_norm > lambda_threshold) and (delta_lambda > 0) and (cp_level > cp_median)
        
        # Métrica de proximidad para el dashboard (1.0 = Fractura inminente)
        # Se normaliza la proximidad basándose en el nivel de carga
        proximity = lambda_norm / 1.0  # Asumiendo 1.0 como saturación total teórica
        
        return {
            "trigger_active": is_trigger,
            "lambda_stat": lambda_norm,
            "lambda_threshold": lambda_threshold,
            "momentum": delta_lambda,
            "structural_concentration": cp_level,
            "fracture_proximity": 1.0 - proximity, # Inverso para la barra de progreso
            "regime": "ACUTE STRESS" if is_trigger else "STABLE/OPERATIVE"
        }

    def process_system_state(self, df: pd.DataFrame):
        """
        Orquesta la limpieza base y la ejecución de la Prop. 2.
        Coordina con el DataFrame filtrado por el Main (1900-2026).
        """
        # Validación de brecha clásica (SG vs Tau Histórico)
        df['threshold_breach'] = df['SG'].abs() > self.tau_base
        
        # Ejecución del Cerebro de Prop. 2
        results = self.get_dynamic_trigger(df)
        
        return df, results

    def _empty_results(self):
        """Devuelve un estado neutro en caso de falta de datos"""
        return {
            "trigger_active": False,
            "lambda_stat": 0,
            "lambda_threshold": 0,
            "momentum": 0,
            "structural_concentration": 0,
            "fracture_proximity": 1.0,
            "regime": "INSUFFICIENT DATA"
        }
