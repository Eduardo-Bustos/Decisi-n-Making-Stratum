import streamlit as st
import pandas as pd
import plotly.express as px
from engine.logic import StratumEngine
import econometrix as ex  # COORDINACIÓN: Nombre exacto de tu archivo en la raíz
import os

# 1. CONFIGURACIÓN DE ESCENARIO
st.set_page_config(
    page_title="Stratum War Room v41",
    page_icon="🛡️",
    layout="wide"
)

# Estilo Erudito (Modo Oscuro)
st.markdown("""
    <style>
    .stMetric { background-color: #1f2937; padding: 20px; border-radius: 12px; border: 1px solid #374151; }
    div[data-testid="stMetricValue"] { color: #60a5fa; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data_coordinated():
    """
    Llama a econometrix.py para obtener el dataset 1900-2026.
    """
    # Usamos la función optimizada que definimos en econometrix.py
    df = ex.get_historical_data()
    return df

def main():
    # --- SIDEBAR: CONTROL DE HORIZONTE ---
    st.sidebar.title("🛡️ Stratum Control")
    st.sidebar.markdown("### Configuración Histórica")
    
    # Rango para el dataset 1900-2026
    years = st.sidebar.slider("Ventana de Análisis", 1900, 2026, (2000, 2026))
    tau_base = st.sidebar.slider("τ Referencia", 0.20, 0.50, 0.3492, format="%.4f")

    # --- CARGA Y SINCRONIZACIÓN ---
    df_full = load_data_coordinated()
    
    if df_full is None:
        st.error("⚠️ Error Crítico: No se pudo sincronizar con econometrix.py o falta data/econometric.csv")
        return

    # Filtrado por el rango seleccionado en el slider
    df = df_full[(df_full['date'].dt.year >= years[0]) & (df_full['date'].dt.year <= years[1])].copy()

    # --- MOTOR ANALÍTICO (PROPOSICIÓN 2) ---
    engine = StratumEngine(tau_base=tau_base)
    df, results = engine.process_system_state(df)

    # --- INTERFAZ: WAR ROOM ---
    st.title("Stratum Decision: Centro de Mando")
    
    # KPIs de la Proposición 2 (Dinámicos)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Estatus Prop. 2", results["regime"], 
                  delta="CRÍTICO" if results["trigger_active"] else "ESTABLE",
                  delta_color="inverse" if results["trigger_active"] else "normal")
    with c2:
        st.metric("Nivel (ISI)", f"{results['lambda_stat']:.4f}", f"P85: {results['lambda_threshold']:.2f}")
    with c3:
        st.metric("Momentum (Δλ)", f"{results['momentum']:.4f}", delta="Acelerando" if results['momentum'] > 0 else "Estable")
    with c4:
        st.metric("Concentración (CP)", f"{results['structural_concentration']:.4f}")

    # Visualización del Mapa de Fase
    st.divider()
    fig = px.scatter(df, x='ISI', y='SG', color='threshold_breach',
                     color_discrete_map={True: "#ef4444", False: "#10b981"},
                     hover_data=['date'], template="plotly_dark",
                     title=f"Geometría de Riesgo Sistémico ({years[0]}-{years[1]})")
    
    # Línea de saturación dinámica
    fig.add_vline(x=results['lambda_threshold'], line_dash="dot", line_color="yellow", 
                  annotation_text="Límite de Saturación")
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
