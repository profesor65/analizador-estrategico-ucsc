# -*- coding: utf-8 -*-
"""
SISTEMA DE ANÁLISIS ESTRATÉGICO INTEGRADO (PORTER + PESTEL + FODA + ISHIKAWA)
Autor: Dr.(c) José Rodríguez López - FACEA UCSC
Año: 2026

© Todos los derechos reservados. Prohibida la reproducción total o parcial sin autorización expresa.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# ============================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Analizador Estratégico - José Rodríguez López",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# VERIFICACIÓN DE ACCESO CON CONTRASEÑA (desde Secrets)
# ============================================================
try:
    PASSWORD = st.secrets["PASSWORD"]
except:
    PASSWORD = "UCSC2026"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Acceso restringido")
    st.markdown("### Facultad de Ciencias Económicas y Administrativas - FACEA UCSC")
    password_input = st.text_input("Ingrese la contraseña para acceder a la herramienta:", type="password")
    if st.button("Ingresar"):
        if password_input == PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta. Acceso denegado.")
    st.stop()
# ============================================================

# ============================================================
# ESTILO PERSONALIZADO (ocultar opciones de Streamlit)
# ============================================================
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { margin-top: -50px; }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ============================================================
# ENCABEZADO INSTITUCIONAL
# ============================================================
st.markdown(
    """
    <div style="text-align: center; background-color: #1e3a5f; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
        <h1 style="color: white;">📊 Analizador Estratégico Integrado</h1>
        <h3 style="color: #ffd966;">PORTER · PESTEL · FODA · ISHIKAWA (Escala Likert 1-5)</h3>
        <p style="color: #d9e2ef; font-size: 0.9rem;">
            <strong>Sistema creado por:</strong> Dr.(c) José Rodríguez López | FACEA UCSC - 2026<br>
            <strong>© Todos los derechos reservados. Prohibida la copia o modificación sin autorización.</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Barra lateral
with st.sidebar:
    st.header("📋 Identificación del trabajo")
    nombre_estudiante = st.text_input("Nombre del estudiante", value="", placeholder="Ej. María Pérez González")
    nombre_profesor = st.text_input("Nombre del profesor de la asignatura *", value="", placeholder="Obligatorio")
    nombre_proyecto = st.text_input("Nombre del proyecto / empresa", value="Mi Empresa")
    
    if not nombre_profesor:
        st.warning("⚠️ Por favor ingrese el nombre del profesor para continuar.")
    
    st.markdown("---")
    st.subheader("📐 Escala Likert utilizada")
    st.markdown("""
    | Valor | Significado                          |
    |-------|--------------------------------------|
    | 1     | Muy en desacuerdo / Muy negativo     |
    | 2     | En desacuerdo / Negativo              |
    | 3     | Neutral / Ni positivo ni negativo     |
    | 4     | De acuerdo / Positivo                 |
    | 5     | Muy de acuerdo / Muy positivo         |
    """)
    st.caption("Responda cada afirmación según su percepción del sector o empresa.")

# ============================================================
# DICCIONARIOS (PORTER, PESTEL, etc.) - se mantienen igual
# ============================================================
PORTER_FACTORES = { ... }  # (aquí va el mismo contenido que tenías, no lo repito por brevedad)
PESTEL_FACTORES = { ... }  # (si decides mantenerlo, pero ya no se usa realmente)

# ============================================================
# FUNCIÓN AUXILIAR PARA EJEMPLOS EN FODA
# ============================================================
def obtener_ejemplo(cuadrante, i):
    ejemplos = {
        "Fortalezas": ["Marca reconocida", "Equipo calificado", "Tecnología propia", "Bajos costos", "Lealtad de clientes"],
        "Debilidades": ["Falta de capital", "Tecnología obsoleta", "Poca presencia digital", "Alta rotación", "Dependencia de pocos clientes"],
        "Oportunidades": ["Nuevos mercados", "Cambios regulatorios", "Tendencias verdes", "Alianzas estratégicas", "Subsidios"],
        "Amenazas": ["Nuevos competidores", "Crisis económica", "Cambios de gustos", "Aumento de costos", "Regulaciones estrictas"]
    }
    lista = ejemplos.get(cuadrante, [""] * 5)
    return lista[i-1] if i-1 < len(lista) else ""

# ============================================================
# FUNCIONES PARA MOSTRAR SECCIONES (Porter, PESTEL, FODA, Ishikawa)
# ============================================================
# (Aquí deben ir tus funciones mostrar_seccion_porter, mostrar_seccion_pestel, mostrar_seccion_foda, mostrar_seccion_ishikawa)
# Ya las tienes definidas previamente, solo asegúrate de incluirlas tal cual estaban.
# Voy a poner un marcador, pero en la práctica copia las que funcionaban.

# ... (copia aquí tus funciones: mostrar_seccion_porter, mostrar_seccion_pestel, mostrar_seccion_foda, mostrar_seccion_ishikawa)

# ============================================================
# FUNCIÓN PARA GENERAR EXCEL (con Ishikawa)
# ============================================================
def generar_excel(respuestas_porter, respuestas_pestel, respuestas_foda, respuestas_ishikawa, nombre_est, nombre_prof, proyecto):
    data = []
    for k, v in respuestas_porter.items():
        data.append({"Sección": "Porter", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in respuestas_pestel.items():
        data.append({"Sección": "PESTEL", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in respuestas_foda.items():
        data.append({"Sección": "FODA", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in respuestas_ishikawa.items():
        data.append({"Sección": "Ishikawa", "Factor/Enunciado": k, "Puntuación": v})
    df = pd.DataFrame(data)
    
    metadata = pd.DataFrame([
        ["Estudiante", nombre_est if nombre_est else "No especificado"],
        ["Profesor", nombre_prof],
        ["Proyecto", proyecto],
        ["Fecha", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Sistema creado por", "Dr.(c) José Rodríguez López - FACEA UCSC"]
    ], columns=["Campo", "Valor"])
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        metadata.to_excel(writer, sheet_name="Metadatos", index=False)
        df.to_excel(writer, sheet_name="Respuestas Likert", index=False)
        stats = df.groupby("Sección")["Puntuación"].agg(["mean", "median", "std"]).round(2)
        stats.to_excel(writer, sheet_name="Estadísticas")
    return output.getvalue()

# ============================================================
# APLICACIÓN PRINCIPAL CON PESTAÑAS (CORREGIDO)
# ============================================================
st.markdown("---")
st.header("🧪 Seleccione el análisis a realizar")

tabs = st.tabs(["🏛️ PORTER", "🌍 PESTEL", "⚡ FODA", "🐟 ISHIKAWA", "📊 Resultados globales"])

# Inicializar variables de sesión
if 'resp_porter' not in st.session_state:
    st.session_state.resp_porter = {}
if 'resp_pestel' not in st.session_state:
    st.session_state.resp_pestel = {}
if 'resp_foda' not in st.session_state:
    st.session_state.resp_foda = {}
if 'resp_ishikawa' not in st.session_state:
    st.session_state.resp_ishikawa = {}

# Pestaña PORTER
with tabs[0]:
    st.session_state.resp_porter = mostrar_seccion_porter()

# Pestaña PESTEL
with tabs[1]:
    st.session_state.resp_pestel = mostrar_seccion_pestel()

# Pestaña FODA
with tabs[2]:
    st.session_state.resp_foda = mostrar_seccion_foda()

# Pestaña ISHIKAWA
with tabs[3]:
    st.session_state.resp_ishikawa = mostrar_seccion_ishikawa()
    
    # Resultados dentro de la misma pestaña
    if st.session_state.resp_ishikawa:
        st.markdown("---")
        st.subheader("📊 Resultados del análisis Ishikawa")
        
        # Promedio por espina
        espina_promedios = {}
        for clave, valor in st.session_state.resp_ishikawa.items():
            espina = clave.split(":")[0]
            if espina not in espina_promedios:
                espina_promedios[espina] = []
            espina_promedios[espina].append(valor)
        
        promedios = {e: sum(v)/len(v) for e, v in espina_promedios.items()}
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Problema analizado", st.session_state.get("ishikawa_problema_final", "No definido"))
        with col2:
            espina_critica = max(promedios, key=promedios.get) if promedios else "Ninguna"
            st.metric("Espina más crítica", espina_critica)
        
        df_espinas = pd.DataFrame([{"Espina": e, "Importancia promedio": f"{p:.2f}/5"} for e, p in promedios.items()])
        st.dataframe(df_espinas, use_container_width=True, hide_index=True)
        
        top_causas = sorted(st.session_state.resp_ishikawa.items(), key=lambda x: x[1], reverse=True)[:10]
        df_top = pd.DataFrame([{"Causa": c, "Importancia": v} for c, v in top_causas])
        st.subheader("🏆 Top 10 causas más importantes")
        st.dataframe(df_top, use_container_width=True, hide_index=True)
        
        if top_causas:
            fig, ax = plt.subplots(figsize=(8, 5))
            causas = [c[:60] for c, _ in top_causas]
            importancias = [v for _, v in top_causas]
            ax.barh(causas, importancias, color="darkorange")
            ax.set_xlim(0, 5.5)
            ax.set_xlabel("Importancia (1-5)")
            ax.set_title("Priorización de causas (Ishikawa)")
            for i, (bar, val) in enumerate(zip(ax.patches, importancias)):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f"{val}", va='center')
            st.pyplot(fig)
    else:
        st.info("Complete las causas y asigne importancia para ver resultados.")

# Pestaña RESULTADOS GLOBALES
with tabs[4]:
    if not nombre_profesor:
        st.error("⚠️ Debe ingresar el nombre del profesor en la barra lateral para generar resultados.")
    else:
        st.header("📈 Resultados consolidados")
        st.markdown(f"**Proyecto:** {nombre_proyecto}")
        st.markdown(f"**Estudiante:** {nombre_estudiante if nombre_estudiante else 'No especificado'}")
        st.markdown(f"**Profesor:** {nombre_profesor}")
        st.markdown(f"**Sistema creado por:** Dr.(c) José Rodríguez López - FACEA UCSC")
        st.markdown("---")
        
        def promediar_por_grupo(respuestas):
            return sum(respuestas.values()) / len(respuestas) if respuestas else 0
        
        prom_porter = promediar_por_grupo(st.session_state.resp_porter)
        prom_pestel = promediar_por_grupo(st.session_state.resp_pestel)
        prom_foda = promediar_por_grupo(st.session_state.resp_foda)
        prom_ishikawa = promediar_por_grupo(st.session_state.resp_ishikawa)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Porter", f"{prom_porter:.2f}/5", help="Intensidad competitiva")
        col2.metric("PESTEL", f"{prom_pestel:.2f}/5", help="Favorabilidad del entorno")
        col3.metric("FODA", f"{prom_foda:.2f}/5", help="Importancia media de factores")
        col4.metric("Ishikawa", f"{prom_ishikawa:.2f}/5", help="Prioridad media de causas")
        
        fig, ax = plt.subplots()
        categorias = ["Porter", "PESTEL", "FODA", "Ishikawa"]
        valores = [prom_porter, prom_pestel, prom_foda, prom_ishikawa]
        colores = ["#2c3e50", "#27ae60", "#e67e22", "#8e44ad"]
        bars = ax.bar(categorias, valores, color=colores)
        ax.set_ylim(0, 5.5)
        ax.set_ylabel("Puntuación promedio (1-5)")
        ax.set_title("Resumen del análisis estratégico")
        for bar, val in zip(bars, valores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f"{val:.2f}", ha='center')
        st.pyplot(fig)
        
        st.subheader("Interpretación")
        # (Mantén tus interpretaciones, solo añade una para Ishikawa)
        st.info("🐟 **Ishikawa:** Los promedios altos indican causas críticas que requieren atención prioritaria.")
        
        st.markdown("---")
        st.subheader("Exportar resultados")
        excel_data = generar_excel(
            st.session_state.resp_porter,
            st.session_state.resp_pestel,
            st.session_state.resp_foda,
            st.session_state.resp_ishikawa,
            nombre_estudiante,
            nombre_profesor,
            nombre_proyecto
        )
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="analisis_estrategico_{nombre_proyecto}.xlsx">📥 Descargar análisis completo en Excel</a>'
        st.markdown(href, unsafe_allow_html=True)

# ============================================================
# PIE DE PÁGINA
# ============================================================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: gray; font-size: 0.8rem;">
        <strong>© 2026 Dr.(c) José Rodríguez López - Facultad de Ciencias Económicas y Administrativas, UCSC</strong><br>
        Este software es de uso exclusivo para fines académicos. Prohibida su reproducción, modificación o distribución sin autorización expresa del autor.
    </div>
    """,
    unsafe_allow_html=True
)
