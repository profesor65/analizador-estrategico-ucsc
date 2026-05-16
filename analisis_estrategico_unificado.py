# -*- coding: utf-8 -*-
"""
SISTEMA DE ANÁLISIS ESTRATÉGICO INTEGRADO (PORTER + PESTEL + FODA + ISHIKAWA)
Versión 2.0 - Con perfil del evaluador y escala de percepciones estratégicas
Autor: Dr.(c) José Rodríguez López - FACEA UCSC
Año: 2026

© Todos los derechos reservados. Prohibida la reproducción total o parcial sin autorización expresa.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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
        <h3 style="color: #ffd966;">PORTER · PESTEL · FODA · ISHIKAWA · PERFIL + ESCALA</h3>
        <p style="color: #d9e2ef; font-size: 0.9rem;">
            <strong>Sistema creado por:</strong> Dr.(c) José Rodríguez López | FACEA UCSC - 2026<br>
            <strong>© Todos los derechos reservados. Prohibida la copia o modificación sin autorización.</strong>
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ============================================================
# BARRA LATERAL: IDENTIFICACIÓN Y PERFIL
# ============================================================
with st.sidebar:
    st.header("📋 Identificación del trabajo")
    nombre_estudiante = st.text_input("Nombre del estudiante", value="", placeholder="Ej. María Pérez González")
    nombre_profesor = st.text_input("Nombre del profesor de la asignatura *", value="", placeholder="Obligatorio")
    nombre_proyecto = st.text_input("Nombre del proyecto / empresa", value="Mi Empresa")
    
    if not nombre_profesor:
        st.warning("⚠️ Por favor ingrese el nombre del profesor para continuar.")
    
    st.markdown("---")
    st.subheader("👤 Perfil del evaluador")
    edad = st.selectbox("Rango de edad", ["18-25", "26-35", "36-45", "46-55", "56+"])
    experiencia = st.selectbox("Años de experiencia en el sector", ["0-2", "3-5", "6-10", "11-20", "20+"])
    carrera = st.selectbox("Formación académica principal", ["Ingeniería", "Administración", "Marketing", "Finanzas", "Derecho", "Otra"])
    cargo = st.selectbox("Nivel de cargo actual", ["Directivo/Gerente", "Jefe de área", "Profesional especialista", "Analista/Operativo", "Otro"])
    
    # Almacenar perfil en session_state
    st.session_state.perfil = {
        "edad": edad,
        "experiencia": experiencia,
        "carrera": carrera,
        "cargo": cargo
    }
    
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
# FUNCIONES AUXILIARES
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

def cronbach_alpha(df_items):
    """Calcula el coeficiente Alfa de Cronbach para un DataFrame de ítems (filas = sujetos, columnas = ítems)"""
    n_sujetos, n_items = df_items.shape
    var_totales = df_items.var(axis=0, ddof=1)
    suma_var_items = var_totales.sum()
    var_total = df_items.sum(axis=1).var(ddof=1)
    if var_total == 0:
        return np.nan
    alpha = (n_items / (n_items - 1)) * (1 - suma_var_items / var_total)
    return alpha

# ============================================================
# FUNCIONES PARA CADA SECCIÓN
# ============================================================

def mostrar_perfil_y_escala():
    st.header("🧑‍💼 Perfil del evaluador y Escala de percepciones")
    
    # Mostrar perfil ingresado
    st.subheader("Datos del perfil")
    perfil_df = pd.DataFrame([st.session_state.perfil])
    st.dataframe(perfil_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    st.subheader("📏 Escala de percepciones estratégicas (basada en Hofstede)")
    st.markdown("Indique su grado de acuerdo con cada afirmación según la escala Likert (1=Muy en desacuerdo, 5=Muy de acuerdo).")
    
    escala_items = {
        "Aversión al riesgo": [
            "Ante una decisión incierta, prefiero opciones seguras aunque den menos beneficio.",
            "Me siento incómodo cuando no podemos predecir los resultados de una acción.",
            "Invertir en proyectos con alto riesgo no vale la pena."
        ],
        "Orientación a la innovación": [
            "La empresa debe adoptar nuevas tecnologías aunque no estén probadas.",
            "Fomentar la experimentación es clave para el éxito.",
            "Me gusta probar formas diferentes de hacer las cosas."
        ],
        "Distancia de poder (jerarquía)": [
            "Las decisiones importantes deben tomarlas los altos directivos sin consultar.",
            "Es mejor mantener la distancia entre jefes y subordinados.",
            "El poder debe concentrarse en pocas manos."
        ],
        "Individualismo vs Colectivismo": [
            "El éxito personal es más importante que el del equipo.",
            "Cada cual debe resolver sus propios problemas laborales.",
            "Prefiero trabajar individualmente que en equipo."
        ]
    }
    
    respuestas_escala = {}
    for dimension, preguntas in escala_items.items():
        st.subheader(f"🔹 {dimension}")
        for i, p in enumerate(preguntas):
            key = f"escala_{dimension}_{i}"
            if key not in st.session_state:
                st.session_state[key] = 3
            valor = st.select_slider(
                p, options=[1,2,3,4,5], key=key,
                format_func=lambda x: {1:"1",2:"2",3:"3",4:"4",5:"5"}[x]
            )
            respuestas_escala[f"{dimension}: {p}"] = valor
        st.markdown("---")
    
    # Guardar en session_state
    st.session_state.resp_escala = respuestas_escala
    
    # Mostrar estadísticas descriptivas de la escala (si hay respuestas)
    if respuestas_escala:
        df_escala_temp = pd.DataFrame([respuestas_escala]).T
        df_escala_temp.columns = ["Puntuación"]
        st.subheader("📊 Resumen de tus respuestas")
        st.dataframe(df_escala_temp, use_container_width=True)
        
        # Calcular promedios por dimensión
        promedios_dim = {}
        for dim in escala_items.keys():
            items = [v for k, v in respuestas_escala.items() if k.startswith(dim)]
            if items:
                promedios_dim[dim] = np.mean(items)
        if promedios_dim:
            st.subheader("Promedio por dimensión")
            st.bar_chart(promedios_dim)
    
    return respuestas_escala

def mostrar_seccion_porter():
    st.header("🏛️ Análisis de las 5 Fuerzas de Porter")
    st.markdown("Evalúe cada afirmación según la escala Likert (1 = Muy en desacuerdo, 5 = Muy de acuerdo).")
    
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
    st.header("🌍 Análisis PESTEL del Macroentorno (Personalizado)")
    st.markdown("""
    **Instrucciones:**  
    Para cada categoría, edita los factores (o escribe los tuyos propios) y asigna su importancia en la escala Likert.  
    Puedes dejar campos vacíos si no necesitas usar los 5.  
    La escala es:  
    1 = Muy negativo/desfavorable, 2 = Negativo, 3 = Neutral, 4 = Positivo, 5 = Muy positivo/favorable.
    """)
    
    respuestas = {}
    pestel_predefinido = {
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
    
    guias = {
        "Político": "🏛️ **Pista:** Analiza la estabilidad gubernamental, políticas fiscales, comercio exterior, regulaciones laborales y presión de grupos de interés.",
        "Económico": "📈 **Pista:** Considera crecimiento del PIB, inflación, tipo de cambio, desempleo y acceso al crédito.",
        "Social": "👥 **Pista:** Reflexiona sobre demografía, educación, estilos de vida, conciencia social y desigualdad.",
        "Tecnológico": "💻 **Pista:** Evalúa I+D, digitalización, acceso a internet, transferencia tecnológica y ciberseguridad.",
        "Ecológico / Ambiental": "🌿 **Pista:** Observa regulaciones ambientales, cambio climático, conciencia ecológica, disponibilidad de recursos y costos de energía sostenible.",
        "Legal": "⚖️ **Pista:** Examina seguridad jurídica, propiedad intelectual, leyes de competencia, legislación laboral y protección al consumidor."
    }
    
    for categoria, lista_factores in pestel_predefinido.items():
        st.subheader(f"📌 {categoria}")
        st.info(guias[categoria])
        for i in range(1, 6):
            text_key = f"pestel_text_{categoria}_{i}"
            slider_key = f"pestel_slider_{categoria}_{i}"
            if text_key not in st.session_state:
                st.session_state[text_key] = lista_factores[i-1] if i-1 < len(lista_factores) else ""
            if slider_key not in st.session_state:
                st.session_state[slider_key] = 3
            col1, col2 = st.columns([3, 1])
            with col1:
                factor_texto = st.text_input(f"Factor {i}", value=st.session_state[text_key], key=text_key, placeholder="Escribe o modifica el factor")
            with col2:
                importancia = st.select_slider("Importancia", options=[1,2,3,4,5], value=st.session_state[slider_key], key=slider_key, label_visibility="collapsed")
            if factor_texto.strip():
                respuestas[f"{categoria}: {factor_texto.strip()}"] = importancia
        st.markdown("---")
    return respuestas

def mostrar_seccion_foda():
    st.header("⚡ Análisis FODA (Personalizado)")
    st.markdown("""
    **Instrucciones:**  
    Escribe hasta **5 factores** para cada cuadrante (Fortalezas, Debilidades, Oportunidades, Amenazas).  
    Luego, en el slider, indica la **importancia** de ese factor (1 = Nada importante, 5 = Muy importante).  
    *Deja los campos de texto vacíos si no necesitas usar los 5.*
    """)
    respuestas = {}
    cuadrantes = ["Fortalezas", "Debilidades", "Oportunidades", "Amenazas"]
    guias = {
        "Fortalezas": "🔍 **Pista:** Piensa en qué hace bien tu organización, qué recursos valiosos tienes, en qué eres mejor que la competencia.",
        "Debilidades": "⚠️ **Pista:** Reflexiona sobre limitaciones internas, aspectos a mejorar, carencias de recursos o capacidades.",
        "Oportunidades": "🌱 **Pista:** Observa tendencias externas favorables, necesidades insatisfechas, cambios en el mercado o regulaciones que te beneficien.",
        "Amenazas": "⚡ **Pista:** Identifica factores externos que puedan perjudicarte: nuevos competidores, crisis económicas, cambios regulatorios adversos."
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
                factor_texto = st.text_input(f"Factor {i}", value=st.session_state[text_key], key=text_key, placeholder=f"Ej. {obtener_ejemplo(cuadrante, i)}")
            with col2:
                importancia = st.select_slider("Importancia", options=[1,2,3,4,5], value=st.session_state[slider_key], key=slider_key, label_visibility="collapsed")
            if factor_texto.strip():
                respuestas[f"{cuadrante}: {factor_texto.strip()}"] = importancia
        st.markdown("---")
    return respuestas

def mostrar_seccion_ishikawa():
    st.header("🐟 Diagrama de Ishikawa (Causa-Efecto)")
    st.markdown("""
    **Instrucciones:**  
    1. Define el **problema principal** (efecto) que deseas analizar.  
    2. Para cada espina, escribe hasta **5 causas** y asigna su **importancia** (1 = Nada importante, 5 = Muy importante).  
    3. Se mostrarán las causas más críticas.
    """)
    
    st.info("💡 **Nota:** Las preguntas que aparecen debajo de cada espina son **solo sugerencias** para guiar tu análisis. No es necesario responderlas todas; puedes adaptarlas o agregar otras que consideres relevantes.")
    
    problema_key = "ishikawa_problema"
    if problema_key not in st.session_state:
        st.session_state[problema_key] = ""
    problema = st.text_input("✏️ **Problema o efecto a analizar:**", value=st.session_state[problema_key], key=problema_key, placeholder="Ej. Baja productividad en el área de producción")
    
    espinas = {
        "👥 Mano de obra": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿El personal tiene las habilidades necesarias?  
            - ¿Hay problemas de motivación o clima laboral?  
            - ¿La carga de trabajo es equilibrada?  
            - ¿Se registran errores frecuentes?
            """,
            "factores": [
                "Falta de capacitación del personal",
                "Baja motivación / clima laboral negativo",
                "Alta rotación de personal",
                "Errores frecuentes en tareas manuales",
                "Insuficiente número de trabajadores"
            ]
        },
        "🛠️ Maquinaria": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿Los equipos actuales son modernos y tienen la capacidad para cumplir con los requisitos de producción?  
            - ¿Se realiza un mantenimiento preventivo y predictivo de forma sistemática y se documenta?  
            - ¿Cuáles son las causas principales de las paradas no planificadas o el tiempo de inactividad?
            """,
            "factores": [
                "Equipos obsoletos o lentos",
                "Falta de mantenimiento preventivo",
                "Paradas no planificadas frecuentes",
                "Herramientas inadecuadas para la tarea",
                "Capacidad insuficiente de maquinaria"
            ]
        },
        "📋 Método": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿Los procedimientos están estandarizados y documentados?  
            - ¿Existen cuellos de botella o pasos innecesarios?  
            - ¿La comunicación entre áreas es fluida?  
            - ¿Se siguen las buenas prácticas del sector?
            """,
            "factores": [
                "Procedimientos no estandarizados",
                "Instrucciones de trabajo poco claras",
                "Procesos excesivamente complejos",
                "Falta de control de calidad en procesos",
                "Mala distribución de flujo de trabajo"
            ]
        },
        "📦 Materiales": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿La materia prima o insumos cumplen con las especificaciones requeridas?  
            - ¿Hay problemas con proveedores (plazos, calidad)?  
            - ¿El inventario es suficiente o hay desabastecimiento?  
            - ¿Se generan muchos desperdicios?
            """,
            "factores": [
                "Materia prima de baja calidad",
                "Proveedores poco confiables",
                "Falta de inventario (desabastecimiento)",
                "Exceso de inventario (obsolescencia)",
                "Materiales no adecuados para el proceso"
            ]
        },
        "📏 Medición": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿Se miden los indicadores clave de desempeño (KPI)?  
            - ¿Los datos son confiables y oportunos?  
            - ¿Los instrumentos de medición están calibrados?  
            - ¿La retroalimentación llega a tiempo para tomar acciones?
            """,
            "factores": [
                "Indicadores de desempeño inadecuados",
                "Errores en la recolección de datos",
                "Falta de instrumentos de medición",
                "Mala calibración de equipos de medición",
                "Retraso en la retroalimentación de resultados"
            ]
        },
        "🌍 Medio ambiente": {
            "guia": """
            **Preguntas sugeridas:**  
            - ¿Las condiciones físicas del lugar de trabajo (iluminación, ruido, temperatura) son adecuadas?  
            - ¿Influyen factores externos (clima, normativas, situación económica)?  
            - ¿La cultura organizacional favorece o dificulta la solución del problema?
            """,
            "factores": [
                "Condiciones de trabajo inseguras",
                "Ruido, temperatura o iluminación inadecuados",
                "Regulaciones gubernamentales restrictivas",
                "Factores climáticos o geográficos",
                "Cultura organizacional negativa"
            ]
        }
    }
    
    respuestas = {}
    for espina, datos in espinas.items():
        st.subheader(f"📌 {espina}")
        st.info(datos["guia"])
        for i in range(1, 6):
            text_key = f"ishikawa_text_{espina}_{i}"
            slider_key = f"ishikawa_slider_{espina}_{i}"
            if text_key not in st.session_state:
                st.session_state[text_key] = datos["factores"][i-1] if i-1 < len(datos["factores"]) else ""
            if slider_key not in st.session_state:
                st.session_state[slider_key] = 3
            col1, col2 = st.columns([3, 1])
            with col1:
                causa_texto = st.text_input(f"Causa {i}", value=st.session_state[text_key], key=text_key, placeholder="Escribe o modifica la causa")
            with col2:
                importancia = st.select_slider("Importancia", options=[1,2,3,4,5], value=st.session_state[slider_key], key=slider_key, label_visibility="collapsed")
            if causa_texto.strip():
                respuestas[f"{espina}: {causa_texto.strip()}"] = importancia
        st.markdown("---")
    
    st.session_state.ishikawa_problema_final = problema
    st.session_state.resp_ishikawa = respuestas
    return respuestas

# ============================================================
# FUNCIÓN PARA GENERAR EXCEL (actualizada)
# ============================================================
def generar_excel(resp_porter, resp_pestel, resp_foda, resp_ishikawa, resp_escala, perfil, nombre_est, nombre_prof, proyecto):
    data = []
    for k, v in resp_porter.items():
        data.append({"Sección": "Porter", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in resp_pestel.items():
        data.append({"Sección": "PESTEL", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in resp_foda.items():
        data.append({"Sección": "FODA", "Factor/Enunciado": k, "Puntuación": v})
    for k, v in resp_ishikawa.items():
        data.append({"Sección": "Ishikawa", "Factor/Enunciado": k, "Puntuación": v})
    
    df_respuestas = pd.DataFrame(data)
    
    metadata = pd.DataFrame([
        ["Estudiante", nombre_est if nombre_est else "No especificado"],
        ["Profesor", nombre_prof],
        ["Proyecto", proyecto],
        ["Fecha", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["Sistema creado por", "Dr.(c) José Rodríguez López - FACEA UCSC"]
    ], columns=["Campo", "Valor"])
    
    df_perfil = pd.DataFrame([perfil])
    
    # Convertir respuestas de escala a DataFrame
    df_escala = pd.DataFrame([resp_escala]).T.reset_index()
    df_escala.columns = ["Ítem", "Puntuación"]
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        metadata.to_excel(writer, sheet_name="Metadatos", index=False)
        df_respuestas.to_excel(writer, sheet_name="Respuestas Likert", index=False)
        stats = df_respuestas.groupby("Sección")["Puntuación"].agg(["mean", "median", "std"]).round(2)
        stats.to_excel(writer, sheet_name="Estadísticas")
        df_perfil.to_excel(writer, sheet_name="Perfil evaluador", index=False)
        df_escala.to_excel(writer, sheet_name="Escala percepciones", index=False)
    
    return output.getvalue()

# ============================================================
# APLICACIÓN PRINCIPAL CON PESTAÑAS (nueva primera pestaña)
# ============================================================
st.markdown("---")
st.header("🧪 Seleccione el análisis a realizar")

tabs = st.tabs(["🧑‍💼 Perfil y Escala", "🏛️ PORTER", "🌍 PESTEL", "⚡ FODA", "🐟 ISHIKAWA", "📊 Resultados globales"])

# Inicializar variables de sesión
if 'resp_porter' not in st.session_state:
    st.session_state.resp_porter = {}
if 'resp_pestel' not in st.session_state:
    st.session_state.resp_pestel = {}
if 'resp_foda' not in st.session_state:
    st.session_state.resp_foda = {}
if 'resp_ishikawa' not in st.session_state:
    st.session_state.resp_ishikawa = {}
if 'resp_escala' not in st.session_state:
    st.session_state.resp_escala = {}

with tabs[0]:
    mostrar_perfil_y_escala()

with tabs[1]:
    st.session_state.resp_porter = mostrar_seccion_porter()

with tabs[2]:
    st.session_state.resp_pestel = mostrar_seccion_pestel()

with tabs[3]:
    st.session_state.resp_foda = mostrar_seccion_foda()

with tabs[4]:
    st.session_state.resp_ishikawa = mostrar_seccion_ishikawa()
    # Mostrar resultados de Ishikawa dentro de la misma pestaña
    if st.session_state.resp_ishikawa:
        st.markdown("---")
        st.subheader("📊 Resultados del análisis Ishikawa")
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
            for bar, val in zip(ax.patches, importancias):
                ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, f"{val}", va='center')
            st.pyplot(fig)
    else:
        st.info("Complete las causas y asigne importancia para ver resultados.")

with tabs[5]:
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
        st.info("🐟 **Ishikawa:** Los promedios altos indican causas críticas que requieren atención prioritaria.")
        
        # --- NUEVA SECCIÓN: ANÁLISIS SEGMENTADO (con datos simulados) ---
        st.markdown("---")
        st.subheader("📊 Análisis segmentado (simulación con datos agregados)")
        st.markdown("""
        En una versión con múltiples evaluadores, sería posible filtrar y correlacionar los resultados según el perfil.  
        A continuación se muestra un ejemplo interactivo con **datos simulados** de 100 evaluadores, para ilustrar el potencial.
        """)
        
        # Generar datos simulados para demostración
        np.random.seed(42)
        n_sim = 100
        cargos_sim = np.random.choice(["Directivo/Gerente", "Jefe de área", "Profesional especialista", "Analista/Operativo"], n_sim)
        edades_sim = np.random.choice(["18-35", "36-50", "51+"], n_sim)
        porter_sim = np.random.uniform(2, 5, n_sim)
        # Simular respuestas de escala (promedio por evaluador)
        aversion_riesgo_sim = np.random.uniform(1, 5, n_sim)
        
        df_sim = pd.DataFrame({
            "cargo": cargos_sim,
            "edad": edades_sim,
            "porter_promedio": porter_sim,
            "aversion_riesgo": aversion_riesgo_sim
        })
        
        # Filtros
        col_filt1, col_filt2 = st.columns(2)
        with col_filt1:
            cargos_sel = st.multiselect("Filtrar por cargo", options=df_sim["cargo"].unique(), default=df_sim["cargo"].unique())
        with col_filt2:
            edades_sel = st.multiselect("Filtrar por edad", options=df_sim["edad"].unique(), default=df_sim["edad"].unique())
        
        df_filt = df_sim[df_sim["cargo"].isin(cargos_sel) & df_sim["edad"].isin(edades_sel)]
        
        if len(df_filt) > 0:
            fig2, ax2 = plt.subplots()
            promedios_cargo = df_filt.groupby("cargo")["porter_promedio"].mean().sort_values()
            promedios_cargo.plot(kind="barh", ax=ax2, color="teal")
            ax2.set_xlabel("Porter promedio (1-5)")
            ax2.set_title("Percepción de competitividad según cargo")
            st.pyplot(fig2)
            
            fig3, ax3 = plt.subplots()
            ax3.scatter(df_filt["aversion_riesgo"], df_filt["porter_promedio"], alpha=0.6, c="darkred")
            ax3.set_xlabel("Aversión al riesgo (1-5)")
            ax3.set_ylabel("Porter promedio")
            ax3.set_title("Relación entre perfil de riesgo y evaluación Porter")
            # Línea de tendencia
            z = np.polyfit(df_filt["aversion_riesgo"], df_filt["porter_promedio"], 1)
            p = np.poly1d(z)
            ax3.plot(np.linspace(1,5,100), p(np.linspace(1,5,100)), "b--", alpha=0.8)
            st.pyplot(fig3)
        else:
            st.warning("No hay datos con los filtros seleccionados.")
        
        # Calcular Alfa de Cronbach para la escala (si hay suficientes respuestas)
        if st.session_state.resp_escala:
            # Reorganizar las respuestas de escala en un DataFrame de sujetos x items
            # Como solo tenemos un sujeto, no se puede calcular alfa; pero mostramos un aviso
            st.markdown("---")
            st.subheader("🔧 Consistencia interna de la escala (Alfa de Cronbach)")
            st.info("Con las respuestas de un solo evaluador no es posible calcular el alfa. En una recopilación de múltiples usuarios, esta estadística indicaría la fiabilidad de la escala.")
            # Si se tuvieran datos de varios usuarios, se calcularía así:
            # df_items = pd.DataFrame([respuestas_usuario1, respuestas_usuario2, ...])
            # alpha = cronbach_alpha(df_items)
            # st.metric("Alfa de Cronbach", f"{alpha:.3f}")
        
        st.markdown("---")
        st.subheader("Exportar resultados")
        excel_data = generar_excel(
            st.session_state.resp_porter,
            st.session_state.resp_pestel,
            st.session_state.resp_foda,
            st.session_state.resp_ishikawa,
            st.session_state.get("resp_escala", {}),
            st.session_state.get("perfil", {}),
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
