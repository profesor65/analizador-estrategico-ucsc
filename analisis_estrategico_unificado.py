# -*- coding: utf-8 -*-
"""
SISTEMA DE ANÁLISIS ESTRATÉGICO INTEGRADO (PORTER + PESTEL + FODA)
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
# Intenta leer la contraseña desde los secrets de Streamlit Cloud
# Si no existe, usa una contraseña por defecto (cámbiala)
try:
    PASSWORD = st.secrets["PASSWORD"]
except:
    PASSWORD = "UCSC2026"  # fallback si no está en secrets

# Inicializar estado de autenticación
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Si no está autenticado, mostrar pantalla de login
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
    st.stop()  # Detiene la ejecución del resto de la app
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
        <h3 style="color: #ffd966;">PORTER · PESTEL · FODA (Escala Likert 1-5)</h3>
        <p style="color: #d9e2ef; font-size: 0.9rem;">
            <strong>Sistema creado por:</strong> Dr.(c) José Rodríguez López | FACEA UCSC - 2026<br>
            <strong>© Todos los derechos reservados. Prohibida la copia o modificación sin autorización.</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Barra lateral para datos del usuario
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
# DICCIONARIOS DE FACTORES CON ENUNCIADOS
# ============================================================
PORTER_FACTORES = {
    "Amenaza de nuevos competidores": [
        "Las economías de escala representan una barrera de entrada importante en este sector.",
        "La lealtad de los clientes hacia las marcas existentes es alta.",
        "Los costos de cambio para que un cliente cambie de proveedor son elevados.",
        "Se requieren inversiones de capital muy altas para competir en este sector.",
        "El acceso a los canales de distribución es muy difícil para un nuevo competidor.",
        "La curva de aprendizaje y experiencia acumulada por las empresas actuales es una ventaja decisiva.",
        "La regulación gubernamental dificulta la entrada de nuevos competidores.",
        "Los productos o servicios actuales están altamente diferenciados.",
        "El acceso a la tecnología clave está restringido a pocas empresas.",
        "Las empresas establecidas tienen ventajas en costos no relacionadas con la escala (patentes, ubicación, etc.).",
        "Las políticas gubernamentales (subsidios, aranceles) favorecen a los incumbentes."
    ],
    "Rivalidad entre competidores": [
        "El número de competidores en el sector es muy elevado.",
        "Existen fuertes barreras emocionales o de lealtad que reducen la rivalidad.",
        "El crecimiento de la industria es muy bajo o nulo, lo que intensifica la lucha por participación.",
        "Las guerras de precios son frecuentes y agresivas.",
        "Las restricciones gubernamentales o sociales limitan las opciones competitivas.",
        "Los costos de salida del sector (despidos, activos especializados) son muy altos.",
        "Los márgenes de beneficio en la industria son muy ajustados."
    ],
    "Poder de negociación de proveedores": [
        "Los proveedores tienen un poder de negociación muy elevado frente a las empresas del sector.",
        "Los precios que fijan los proveedores son considerablemente altos.",
        "La cantidad de insumos disponibles es limitada (oferta concentrada).",
        "Los proveedores están ubicados en zonas lejanas, aumentando costos logísticos.",
        "Existe un bajo grado de confianza y relación con los proveedores.",
        "La relación con los proveedores es de confrontación o desfavorable.",
        "El peligro de que los proveedores se integren hacia adelante (compitan directamente) es alto.",
        "No existen insumos sustitutos viables para nuestra producción.",
        "El costo de cambiar de proveedor es muy alto.",
        "La calidad del producto del proveedor es difícilmente igualable."
    ],
    "Poder de negociación de compradores": [
        "El costo de cambio para que un cliente cambie de proveedor es muy bajo.",
        "El número de clientes importantes es reducido (alta concentración de compras).",
        "Los compradores podrían integrarse hacia atrás fácilmente (fabricar ellos mismos).",
        "Los compradores tienen gran facilidad para encontrar productos sustitutos.",
        "La implicación emocional o importancia del producto para el cliente es baja.",
        "El poder de negociación de los compradores es muy elevado."
    ],
    "Amenaza de productos sustitutos": [
        "Existe gran disponibilidad de productos sustitutos cercanos.",
        "El costo de cambio para el comprador hacia un sustituto es muy bajo.",
        "Los productos sustitutos son muy agresivos en precios y promoción.",
        "La relación valor-precio de los sustitutos es muy favorable comparada con nuestros productos."
    ]
}

PESTEL_FACTORES = {
    "Político": [
        "La estabilidad política del país es alta y predecible.",
        "Las políticas fiscales (impuestos) son favorables para el negocio.",
        "Las políticas de comercio exterior son abiertas y facilitan la importación/exportación.",
        "Las regulaciones laborales son flexibles y no encarecen excesivamente el empleo.",
        "La presión de grupos de interés o lobby es baja o favorable."
    ],
    "Económico": [
        "El crecimiento del PIB es alto y sostenido.",
        "La tasa de inflación es baja y controlada.",
        "El tipo de cambio es estable y competitivo para nuestras operaciones.",
        "La tasa de desempleo es baja, lo que indica una economía saludable.",
        "El acceso al crédito y financiamiento es amplio y con tasas razonables."
    ],
    "Social": [
        "Los cambios demográficos (envejecimiento, migración) benefician nuestro mercado.",
        "El nivel educativo de la población es alto y calificado.",
        "Los estilos de vida y preferencias del consumidor están alineados con nuestra oferta.",
        "La conciencia social y de salud es elevada y favorece nuestros productos.",
        "La desigualdad en la distribución de la renta es baja, existiendo una clase media amplia."
    ],
    "Tecnológico": [
        "La inversión en I+D e innovación en el sector es alta y constante.",
        "El nivel de digitalización y automatización del sector es avanzado (Industria 4.0).",
        "El acceso a internet y tecnologías de la información es universal y de alta velocidad.",
        "La transferencia tecnológica desde universidades o centros de investigación es fluida.",
        "La ciberseguridad y protección de datos están garantizadas por normas robustas."
    ],
    "Ecológico / Ambiental": [
        "Las regulaciones ambientales son claras y no excesivamente costosas.",
        "El cambio climático y eventos extremos tienen un impacto bajo en nuestras operaciones.",
        "Los consumidores tienen una alta conciencia ecológica que favorece nuestra propuesta verde.",
        "La disponibilidad de recursos naturales es abundante y a precios razonables.",
        "Los costos de la energía sostenible son bajos o están subvencionados."
    ],
    "Legal": [
        "La seguridad jurídica y cumplimiento de contratos son excelentes.",
        "La protección de la propiedad intelectual (patentes, marcas) es fuerte.",
        "Las leyes de competencia (antimonopolio) son efectivas y justas.",
        "La legislación laboral es equilibrada y no genera conflictos.",
        "Las leyes de protección al consumidor son rigurosas y nos benefician (generan confianza)."
    ]
}

# ============================================================
# FUNCIÓN AUXILIAR PARA EJEMPLOS EN FODA
# ============================================================
def obtener_ejemplo(cuadrante, i):
    """Devuelve un ejemplo según el cuadrante y el número (opcional)"""
    ejemplos = {
        "Fortalezas": ["Marca reconocida", "Equipo calificado", "Tecnología propia", "Bajos costos", "Lealtad de clientes"],
        "Debilidades": ["Falta de capital", "Tecnología obsoleta", "Poca presencia digital", "Alta rotación", "Dependencia de pocos clientes"],
        "Oportunidades": ["Nuevos mercados", "Cambios regulatorios", "Tendencias verdes", "Alianzas estratégicas", "Subsidios"],
        "Amenazas": ["Nuevos competidores", "Crisis económica", "Cambios de gustos", "Aumento de costos", "Regulaciones estrictas"]
    }
    lista = ejemplos.get(cuadrante, [""] * 5)
    if i-1 < len(lista):
        return lista[i-1]
    return ""

# ============================================================
# FUNCIONES PARA MOSTRAR SECCIONES
# ============================================================
def mostrar_seccion_porter():
    st.header("🏛️ Análisis de las 5 Fuerzas de Porter")
    st.markdown("Evalúe cada afirmación según la escala Likert (1 = Muy en desacuerdo, 5 = Muy de acuerdo).")
    
    respuestas = {}
    for fuerza, lista_enunciados in PORTER_FACTORES.items():
        st.subheader(f"🔹 {fuerza}")
        cols = st.columns(2)
        for idx, enunciado in enumerate(lista_enunciados):
            key = f"porter_{fuerza}_{idx}"
            if key not in st.session_state:
                st.session_state[key] = 3
            with cols[idx % 2]:
                respuesta = st.select_slider(
                    enunciado,
                    options=[1, 2, 3, 4, 5],
                    key=key,
                    format_func=lambda x: {1:"1 - Muy en desacuerdo", 2:"2 - En desacuerdo", 3:"3 - Neutral", 4:"4 - De acuerdo", 5:"5 - Muy de acuerdo"}[x]
                )
                respuestas[f"{fuerza}: {enunciado[:50]}..."] = respuesta
        st.markdown("---")
    return respuestas

def mostrar_seccion_pestel():
    st.header("🌍 Análisis PESTEL del Macroentorno")
    st.markdown("Evalúe cada afirmación (1 = Muy negativo/desfavorable, 5 = Muy positivo/favorable).")
    
    respuestas = {}
    for factor, lista_enunciados in PESTEL_FACTORES.items():
        st.subheader(f"📌 {factor}")
        cols = st.columns(2)
        for idx, enunciado in enumerate(lista_enunciados):
            key = f"pestel_{factor}_{idx}"
            if key not in st.session_state:
                st.session_state[key] = 3
            with cols[idx % 2]:
                respuesta = st.select_slider(
                    enunciado,
                    options=[1, 2, 3, 4, 5],
                    key=key,
                    format_func=lambda x: {1:"1 - Muy negativo", 2:"2 - Negativo", 3:"3 - Neutral", 4:"4 - Positivo", 5:"5 - Muy positivo"}[x]
                )
                respuestas[f"{factor}: {enunciado[:50]}..."] = respuesta
        st.markdown("---")
    return respuestas

def mostrar_seccion_foda():
    st.header("⚡ Análisis FODA (Personalizado)")
    st.markdown("""
    **Instrucciones:**  
    Escribe hasta **5 factores** para cada cuadrante (Fortalezas, Debilidades, Oportunidades, Amenazas).  
    Luego, en el slider, indica la **importancia** de ese factor para tu organización (1 = Nada importante, 5 = Muy importante).  
    *Deja los campos de texto vacíos si no necesitas usar los 5.*
    """)
    
    respuestas = {}
    cuadrantes = ["Fortalezas", "Debilidades", "Oportunidades", "Amenazas"]
    
    guias = {
        "Fortalezas": "🔍 **Pista:** Piensa en qué hace bien tu organización, qué recursos valiosos tienes, en qué eres mejor que la competencia. Ejemplo: *'Marca reconocida'*, *'Equipo con alta experiencia'*.",
        "Debilidades": "⚠️ **Pista:** Reflexiona sobre limitaciones internas, aspectos a mejorar, carencias de recursos o capacidades. Ejemplo: *'Falta de capital de trabajo'*, *'Tecnología obsoleta'*.",
        "Oportunidades": "🌱 **Pista:** Observa tendencias externas favorables, necesidades insatisfechas, cambios en el mercado o regulaciones que te beneficien. Ejemplo: *'Crecimiento del comercio electrónico'*, *'Nuevos nichos de mercado'*.",
        "Amenazas": "⚡ **Pista:** Identifica factores externos que puedan perjudicarte: nuevos competidores, crisis económicas, cambios regulatorios adversos. Ejemplo: *'Entrada de competidores internacionales'*, *'Aumento de costos de materias primas'*."
    }
    
    for cuadrante in cuadrantes:
        st.subheader(f"📌 {cuadrante}")
        st.info(guias[cuadrante])
        
        for i in range(1, 6):
            text_key = f"foda_text_{cuadrante}_{i}"
            slider_key = f"foda_slider_{cuadrante}_{i}"
            
            if text_key not in st.session_state:
                st.session_state[text_key] = ""
            if slider_key not in st.session_state:
                st.session_state[slider_key] = 3
            
            col1, col2 = st.columns([3, 1])
            with col1:
                factor_texto = st.text_input(
                    f"Factor {i}",
                    value=st.session_state[text_key],
                    key=text_key,
                    placeholder=f"Ej. {obtener_ejemplo(cuadrante, i)}"
                )
            with col2:
                importancia = st.select_slider(
                    "Importancia",
                    options=[1, 2, 3, 4, 5],
                    value=st.session_state[slider_key],
                    key=slider_key,
                    label_visibility="collapsed"
                )
            
            if factor_texto.strip():
                clave_respuesta = f"{cuadrante}: {factor_texto.strip()}"
                respuestas[clave_respuesta] = importancia
        
        st.markdown("---")
    
    return respuestas

# ============================================================
# FUNCIÓN PARA GENERAR EXCEL
# ============================================================
def generar_excel(respuestas_porter, respuestas_pestel, respuestas_foda, nombre_est, nombre_prof, proyecto):
    data = []
    for k, v in respuestas_porter.items():
        data.append({"Sección": "Porter", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in respuestas_pestel.items():
        data.append({"Sección": "PESTEL", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in respuestas_foda.items():
        data.append({"Sección": "FODA", "Factor/Enunciado": k, "Puntuación": v})
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
# APLICACIÓN PRINCIPAL CON PESTAÑAS
# ============================================================
st.markdown("---")
st.header("🧪 Seleccione el análisis a realizar")

tabs = st.tabs(["🏛️ PORTER", "🌍 PESTEL", "⚡ FODA", "📊 Resultados globales"])

# Inicializar variables de sesión para almacenar respuestas
if 'resp_porter' not in st.session_state:
    st.session_state.resp_porter = {}
if 'resp_pestel' not in st.session_state:
    st.session_state.resp_pestel = {}
if 'resp_foda' not in st.session_state:
    st.session_state.resp_foda = {}

with tabs[0]:
    st.session_state.resp_porter = mostrar_seccion_porter()
with tabs[1]:
    st.session_state.resp_pestel = mostrar_seccion_pestel()
with tabs[2]:
    st.session_state.resp_foda = mostrar_seccion_foda()

with tabs[3]:
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
            if not respuestas:
                return 0
            return sum(respuestas.values()) / len(respuestas)
        
        prom_porter = promediar_por_grupo(st.session_state.resp_porter)
        prom_pestel = promediar_por_grupo(st.session_state.resp_pestel)
        prom_foda = promediar_por_grupo(st.session_state.resp_foda)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Porter (intensidad competitiva)", f"{prom_porter:.2f}/5", 
                    help="Promedio > 4 indica alta intensidad; < 2 indica baja")
        col2.metric("PESTEL (favorabilidad del entorno)", f"{prom_pestel:.2f}/5",
                    help="> 4 entorno muy favorable; < 2 muy desfavorable")
        col3.metric("FODA (importancia media de factores)", f"{prom_foda:.2f}/5",
                    help="Valor alto significa que los factores listados son muy relevantes para el negocio")
        
        fig, ax = plt.subplots()
        categorias = ["Porter", "PESTEL", "FODA"]
        valores = [prom_porter, prom_pestel, prom_foda]
        colores = ["#2c3e50", "#27ae60", "#e67e22"]
        bars = ax.bar(categorias, valores, color=colores)
        ax.set_ylim(0, 5.5)
        ax.set_ylabel("Puntuación promedio (1-5)")
        ax.set_title("Resumen del análisis estratégico")
        for bar, val in zip(bars, valores):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, f"{val:.2f}", ha='center')
        st.pyplot(fig)
        
        st.subheader("Interpretación")
        if prom_porter >= 4:
            st.warning("⚠️ **Porter:** Alta intensidad competitiva. El sector es muy disputado.")
        elif prom_porter <= 2:
            st.success("✅ **Porter:** Baja intensidad competitiva. Entorno favorable para crecer.")
        else:
            st.info("ℹ️ **Porter:** Intensidad competitiva moderada.")
        
        if prom_pestel >= 4:
            st.success("🌱 **PESTEL:** Entorno muy favorable. Aproveche las oportunidades.")
        elif prom_pestel <= 2:
            st.error("⚠️ **PESTEL:** Entorno hostil. Desarrolle planes de contingencia.")
        else:
            st.info("📊 **PESTEL:** Entorno neutral. Monitoree cambios.")
        
        if prom_foda >= 4:
            st.info("📌 **FODA:** Los factores evaluados son muy relevantes. Preste atención especial a las debilidades y amenazas.")
        else:
            st.info("📌 **FODA:** Los factores evaluados tienen importancia moderada o baja.")
        
        st.markdown("---")
        st.subheader("Exportar resultados")
        excel_data = generar_excel(
            st.session_state.resp_porter,
            st.session_state.resp_pestel,
            st.session_state.resp_foda,
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
