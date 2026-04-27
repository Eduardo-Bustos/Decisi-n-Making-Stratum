import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from engine.logic import StratumEngine
import Data_econometrix as de  # Coordinación con el nuevo módulo de datos
import os

# 1. CONFIGURACIÓN DE ESCENARIO INSTITUCIONAL
st.set_page_config(
    page_title="Stratum Decision | War Room v41",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Erudito: Interfaz de Mando en Modo Oscuro
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #374151; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #60a5fa; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_and_sync_data():
    """Coordina con Data_econometrix para obtener el dataset 1900-2026"""
    try:
        # Llamada al nuevo módulo optimizado
        df = de.get_historical_data() 
        if df is not None:
            df['date'] = pd.to_datetime(df['date'])
        return df
    except Exception as e:
        st.error(f"Falla de Coordinación con Data_econometrix: {e}")
        return None

def main():
    # --- CONTROL LATERAL (SENSITIVITY & SCOPE) ---
    st.sidebar.title("🛡️ Stratum Control v41")
    
    # Filtro temporal vital para procesar 126 años de historia
    st.sidebar.subheader("Horizonte Temporal")
    years = st.sidebar.slider("Rango de Análisis", 1900, 2026, (2000, 2026))
    
    st.sidebar.subheader("Sensibilidad Institucional")
    tau_base = st.sidebar.slider("τ Referencia (Histórico)", 0.20, 0.50, 0.3492, format="%.4f")
    st.sidebar.info("La Prop. 2 opera como un vector de activación dinámico sobre este umbral.")

    # --- NÚCLEO DE PROCESAMIENTO ---
    df_full = load_and_sync_data()
    if df_full is None:
        st.warning("Aguardando flujo de datos de Data_econometrix...")
        return

    # Filtrado dinámico por fecha para optimizar memoria
    mask = (df_full['date'].dt.year >= years[0]) & (df_full['date'].dt.year <= years[1])
    df = df_full.loc[mask].copy()

    # Instanciación del Motor (Engine)
    engine = StratumEngine(tau_base=tau_base)
    
    # Ejecución de la Lógica y Proposición 2
    df, results = engine.process_system_state(df)

    # --- INTERFAZ DE MANDO (WAR ROOM) ---
    st.title("Stratum Decision: Centro de Mando Sistémico")
    
    # PANEL DE KPIs: Geometría de Riesgo (Prop. 2)
    k1, k2, k3, k4 = st.columns(4)
    
    with k1:
        st.metric("Estatus Prop. 2", results["regime"], 
                  delta="CRÍTICO" if results["trigger_active"] else "ESTABLE",
                  delta_color="inverse" if results["trigger_active"] else "normal")
    
    with k2:
        st.metric("Carga ISI (Nivel)", f"{results['lambda_stat']:.4f}", 
                  f"Ref. 85%: {results['lambda_threshold']:.2f}")
    
    with k3:
        st.metric("Momentum (Δλ)", f"{results['momentum']:.4f}", 
                  delta="Acumulando" if results['momentum'] > 0 else "Disipando")
    
    with k4:
        st.metric("Fragilidad (CP)", f"{results['structural_concentration']:.4f}")

    # BARRA DE PROXIMIDAD A LA FRACTURA
    st.divider()
    prox_val = 1.0 - results['fracture_proximity']
    st.markdown(f"### Proximidad a Transición de Fase: **{prox_val*100:.1f}%**")
    st.progress(max(0.0, min(1.0, prox_val)))
    
    # --- VISUALIZACIÓN ANALÍTICA ---
    col_map, col_details = st.columns([3, 1])
    
    with col_map:
        # Mapa de Fase (Geometría del Riesgo)
        fig = px.scatter(
            df, x='ISI', y='SG', color='threshold_breach',
            color_discrete_map={True: "#ef4444", False: "#10b981"},
            hover_data=['date'], template="plotly_dark",
            title=f"Dinámica Sistémica ({years[0]}-{years[1]})"
        )
        # Línea de saturación dinámica
        fig.add_vline(x=results['lambda_threshold'], line_dash="dot", line_color="#fbbf24", 
                      annotation_text="Límite de Saturación (P85)")
        st.plotly_chart(fig, use_container_width=True)

    with col_details:
        st.subheader("Diagnóstico")
        if results["trigger_active"]:
            st.error("ALINEACIÓN DETECTADA: Ruptura de coordinación inminente por saturación y momentum positivo.")
        else:
            st.success("SISTEMA ACUÑADO: La capacidad de disipación es suficiente para el nivel de carga actual.")
        
        st.write("**Resumen Operativo:**")
        st.write(f"- Puntos analizados: {len(df)}")
        st.write(f"- Umbral τ base: {tau_base}")

if __name__ == "__main__":
    main()
