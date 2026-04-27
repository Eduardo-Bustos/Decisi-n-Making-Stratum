import numpy as np
import pandas as pd
import statsmodels.api as sm
from typing import Optional

class StratumEngine:
    def __init__(self, tau: float = 0.3492):
        self.tau = tau
        self.regime_labels = {
            0: "Estable",
            1: "Transicional",
            2: "Acute Stress"
        }

    def process_system_state(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula alertas basadas en el umbral tau y prepara el dataframe
        para la visualización en el War Room.
        """
        # Asegurar que SG sea absoluto para la detección de umbral
        df['threshold_breach'] = df['SG'].abs() > self.tau
        
        # Clasificación de criticidad basada en ISI y SG
        df['criticality_index'] = df['SG'].abs() * df['ISI']
        
        return df

    def run_local_projection(self, 
                             df: pd.DataFrame, 
                             horizon: int = 10, 
                             shock_col: str = 'shock_proxy') -> pd.DataFrame:
        """
        Ejecuta una Proyección Local simplificada para el War Room.
        Calcula la respuesta de SG ante un shock en t=0.
        """
        responses = []
        
        # Limpieza básica
        data = df.dropna(subset=['SG', shock_col])
        
        for h in range(horizon + 1):
            # Desplazar la variable dependiente h períodos hacia adelante
            y = data['SG'].shift(-h)
            x = data[shock_col]
            
            # Máscara para eliminar NaNs tras el shift
            mask = y.notna() & x.notna()
            
            if mask.sum() > 10:
                model = sm.OLS(y[mask], sm.add_constant(x[mask])).fit()
                # Coeficiente de respuesta
                responses.append({
                    'horizon': h,
                    'beta': model.params[shock_col],
                    'ci_lower': model.conf_int().loc[shock_col, 0],
                    'ci_upper': model.conf_int().loc[shock_col, 1]
                })
        
        return pd.DataFrame(responses)

    def get_current_risk_assessment(self, df: pd.DataFrame):
        """
        Devuelve un resumen ejecutivo del estado actual del sistema.
        """
        last_row = df.iloc[-1]
        state = {
            "regime": last_row.get('Regime_economic', 'N/A'),
            "sg_value": last_row['SG'],
            "is_breached": abs(last_row['SG']) > self.tau,
            "isi_saturation": last_row['ISI']
        }
        return state
