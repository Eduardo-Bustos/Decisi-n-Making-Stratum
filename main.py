import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from engine.logic import StratumEngine
import os

# Configuración de página de alto impacto (War Room)
st.set_page_config(
    page_title="Stratum Decision | War Room v41",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado para el "War Room"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_stratum_data():
    # Ruta optimizada para el nuevo repositorio
    path = "data/stratum_econometrico.csv"
    if not os.path.exists(path):
        st.error(f"Falta el 'State Core': No se encontró {path}")
        return None
    df = pd.read_csv(path)
    df['date'] = pd.to_datetime(df['date'])
    return df

def main():
    st.sidebar.title("🛡️ Stratum v41 Control")
    tau = st.sidebar.slider("Umbral Crítico (τ)", 0.2000, 0.5000, 0.3492, format="%.4f")
    
    # Instanciar el motor analítico
    engine = StratumEngine(tau=tau)
    
    df_raw = load_stratum_data()
    if df_raw is None: return

    # Procesamiento dinámico
    df = engine.process_system_state(df_raw)
    current_state = engine.get_current_risk_assessment(df)

    # Cabecera Operativa (KPIs)
    st.title("Stratum Decision: Centro de Mando Sistémico")
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        color = "inverse" if current_state["is_breached"] else "normal"
        st.metric("Régimen Actual", current_state["regime"], delta="CRÍTICO" if current_state["is_breached"] else "ESTABLE", delta_color=color)
    
    with kpi2:
        st.metric("Sync Gap (SG)", f"{current_state['sg_value']:.4f}")
    
    with kpi3:
        st.metric("Saturación (ISI)", f"{current_state['isi_saturation']:.4f}")
    
    with kpi4:
        st.metric("Umbral τ", f"{tau:.4f}")

    # Visualización Principal: Mapa de Fase
    st.subheader("Dinámica de Coordinación Sistémica (SG vs ISI)")
    fig_phase = px.scatter(
        df, x='ISI', y='SG', color='Regime_economic',
        color_discrete_map={"Stable": "#10b981", "Transitional": "#f59e0b", "Acute Stress": "#ef4444"},
        hover_data=['date'], template="plotly_dark"
    )
    # Líneas de umbral tau
    fig_phase.add_hline(y=tau, line_dash="dash", line_color="red", annotation_text="+τ Breach")
    fig_phase.add_hline(y=-tau, line_dash="dash", line_color="red", annotation_text="-τ Breach")
    
    st.plotly_chart(fig_phase, use_container_width=True)

    # Simulación de Proyecciones Locales (LP)
    st.divider()
    st.subheader("Simulación de Respuesta al Impulso (Local Projections)")
    
    col_sim1, col_sim2 = st.columns([1, 3])
    
    with col_sim1:
        st.info("Simula un shock en un nodo de relevancia sistémica (SRF) para observar la velocidad de recuperación del sistema.")
        horizon = st.number_input("Horizonte (días)", 5, 30, 15)
        if st.button("Ejecutar Proyección"):
            with st.spinner("Calculando respuesta Jordà (LP)..."):
                irf_results = engine.run_local_projection(df, horizon=horizon)
                st.session_state['irf'] = irf_results

    with col_sim2:
        if 'irf' in st.session_state:
            irf = st.session_state['irf']
            fig_irf = go.Figure([
                go.Scatter(x=irf['horizon'], y=irf['beta'], name='Respuesta SG', line=dict(color='#3b82f6', width=3)),
                go.Scatter(x=irf['horizon'], y=irf['ci_upper'], fill=None, mode='lines', line_color='rgba(59, 130, 246, 0.2)', showlegend=False),
                go.Scatter(x=irf['horizon'], y=irf['ci_lower'], fill='tonexty', mode='lines', line_color='rgba(59, 130, 246, 0.2)', name='IC 95% (HAC)')
            ])
            fig_irf.update_layout(title="Impulse Response Function: SG vs Shock", template="plotly_dark")
            st.plotly_chart(fig_irf, use_container_width=True)

if __name__ == "__main__":
    main()
