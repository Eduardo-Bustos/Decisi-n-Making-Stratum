import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from engine.logic import StratumEngine
import os

# 1. CONFIGURACIÓN DE ESCENARIO (WAR ROOM)
st.set_page_config(
    page_title="Stratum Decision | War Room v41",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Erudito (Modo Oscuro Institucional)
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_stratum_data():
    path = "data/stratum_econometrico.csv"
    if not os.path.exists(path):
        st.error(f"Error Crítico: No se encontró el State Core en {path}")
        return None
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def main():
    # --- SIDEBAR: CONTROL DE SENSIBILIDAD ---
    st.sidebar.title("🛡️ Stratum v41 Control")
    st.sidebar.markdown("### Configuración de Referencia")
    tau_slider = st.sidebar.slider("Umbral τ (Histórico)", 0.20, 0.50, 0.3492, format="%.4f")
    st.sidebar.info("La Proposición 2 calibra automáticamente el riesgo por encima de este valor base.")

    # --- CARGA Y PROCESAMIENTO (El orden resuelve el NameError) ---
    df_raw = load_stratum_data()
    if df_raw is None: return

    # Inicializar el motor con la Proposición 2 integrada
    engine = StratumEngine(tau_base=tau_slider)
    
    # El motor ahora devuelve el DataFrame y el diccionario de activación dinámica
    df, results = engine.process_system_state(df_raw)

    # --- CABECERA: CENTRO DE MANDO ---
    st.title("Stratum Decision: War Room v41")
    st.markdown(f"**Estado del Sistema:** Prop. 2 {'🔴 ACTIVADA' if results['trigger_active'] else '🟢 OPERATIVA'}")

    # Fila 1: KPIs de la Proposición 2 (El "Fríjol" Dinámico)
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        # El régimen ya no es fijo, depende de la alineación de factores
        st.metric("Régimen Institucional", results["regime"], 
                  delta="ALERTA" if results["trigger_active"] else "NORMAL",
                  delta_color="inverse" if results["trigger_active"] else "normal")

    with c2:
        # Nivel de saturación comparado con el percentil 85 dinámico
        st.metric("Carga Sistémica (ISI)", f"{results['lambda_stat']:.4f}", 
                  f"Ref: {results['lambda_threshold']:.2f}")

    with c3:
        # Momentum: Indica si el riesgo está creciendo o disipándose
        st.metric("Momentum (Δλ)", f"{results['momentum']:.4f}", 
                  delta="Acelerando" if results['momentum'] > 0 else "Disipando")

    with c4:
        # Concentración estructural de nodos críticos
        st.metric("Fragilidad (CP)", f"{results['structural_concentration']:.4f}")

    # Fila 2: Barra de Proximidad a la Fractura
    st.markdown("### Proximidad a Transición de Fase")
    proximity = 1.0 - results['fracture_proximity']
    bar_color = "red" if results["trigger_active"] else "orange" if proximity > 0.7 else "green"
    st.progress(max(0.0, min(1.0, proximity)))
    st.caption(f"Capacidad de disipación remanente: {(results['fracture_proximity']*100):.1f}%")

    # --- VISUALIZACIÓN DE MAPA DE FASE ---
    st.divider()
    col_graph, col_info = st.columns([3, 1])

    with col_graph:
        fig_phase = px.scatter(
            df, x='ISI', y='SG', color='Regime_economic',
            color_discrete_map={"Stable": "#10b981", "Transitional": "#f59e0b", "Acute Stress": "#ef4444"},
            hover_data=['date'], template="plotly_dark", title="Dinámica SG vs ISI (Geometría de Riesgo)"
        )
        # Dibujamos el área de saturación dinámica (Percentil 85)
        fig_phase.add_vline(x=results['lambda_threshold'], line_dash="dot", line_color="yellow", 
                            annotation_text="Límite de Saturación")
        st.plotly_chart(fig_phase, use_container_width=True)

    with col_info:
        st.markdown("#### Análisis de la Proposición 2")
        st.write(f"- **Nivel crítico:** {'Superado' if results['lambda_stat'] > results['lambda_threshold'] else 'Bajo Control'}")
        st.write(f"- **Dirección del Riesgo:** {'Acumulando' if results['momentum'] > 0 else 'Liberando'}")
        st.write(f"- **Estado de Chokepoints:** {'Concentrado' if results['structural_concentration'] > 0.6 else 'Disperso'}")

    # --- SIMULACIÓN DE PROYECCIONES LOCALES ---
    st.divider()
    st.subheader("Simulación de Respuesta al Impulso (Local Projections)")
    # ... (Aquí sigue tu bloque de LP que ya tenías, usando df)

if __name__ == "__main__":
    main()
