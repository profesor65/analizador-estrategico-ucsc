# -*- coding: utf-8 -*-
"""
Dashboard para el profesor: análisis de datos acumulados
Acceso restringido con contraseña distinta (opcional)
Dr.(c) José Rodríguez López - FACEA UCSC
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from supabase import create_client, Client

# Configuración de página
st.set_page_config(page_title="Dashboard Profesor", layout="wide", page_icon="📈")

# Verificar que existe conexión a Supabase
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    supabase_available = True
except Exception as e:
    supabase_available = False
    st.error("No se pudo conectar a Supabase. Verifica los secrets.")
    st.stop()

# Contraseña específica para el dashboard (puede ser la misma o diferente)
DASHBOARD_PASSWORD = st.secrets.get("DASHBOARD_PASSWORD", "Admin2026")

if "dashboard_auth" not in st.session_state:
    st.session_state.dashboard_auth = False

if not st.session_state.dashboard_auth:
    st.title("🔒 Acceso al Dashboard del Profesor")
    pwd = st.text_input("Ingrese la contraseña del dashboard:", type="password")
    if st.button("Acceder"):
        if pwd == DASHBOARD_PASSWORD:
            st.session_state.dashboard_auth = True
            st.rerun()
        else:
            st.error("Contraseña incorrecta")
    st.stop()

# Cargar datos desde Supabase
@st.cache_data(ttl=300)
def cargar_evaluaciones():
    try:
        response = supabase.table("evaluaciones").select("*").execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error al cargar datos: {e}")
        return pd.DataFrame()

df = cargar_evaluaciones()

if df.empty:
    st.warning("Aún no hay evaluaciones guardadas. Los datos aparecerán aquí cuando los usuarios guarden sus respuestas.")
    st.stop()

st.title("📊 Dashboard de Análisis Estratégico - Datos Acumulados")
st.markdown(f"**Total de evaluaciones anonimizadas:** {len(df)}")
st.markdown("---")

# Función para extraer dimensiones de la escala desde el JSON
def extraer_promedio_dimension(resp_escala_dict, dimension_key):
    """Extrae el promedio de una dimensión de la escala (ej. 'Aversión al riesgo')"""
    items = [v for k, v in resp_escala_dict.items() if k.startswith(dimension_key)]
    return np.mean(items) if items else np.nan

# Procesar datos
perfiles = []
promedios_porter = []
promedios_pestel = []
promedios_foda = []
promedios_ishikawa = []
dim_aversion = []
dim_innovacion = []
dim_poder = []
dim_individualismo = []

for _, row in df.iterrows():
    perfil = row['perfil']
    perfiles.append(perfil)
    
    # Promedios de cada sección (si existen)
    resp_p = row.get('resp_porter', {})
    promedios_porter.append(np.mean(list(resp_p.values())) if resp_p else np.nan)
    
    resp_pe = row.get('resp_pestel', {})
    promedios_pestel.append(np.mean(list(resp_pe.values())) if resp_pe else np.nan)
    
    resp_f = row.get('resp_foda', {})
    promedios_foda.append(np.mean(list(resp_f.values())) if resp_f else np.nan)
    
    resp_i = row.get('resp_ishikawa', {})
    promedios_ishikawa.append(np.mean(list(resp_i.values())) if resp_i else np.nan)
    
    # Dimensiones de escala
    escala = row.get('resp_escala', {})
    dim_aversion.append(extraer_promedio_dimension(escala, "Aversión al riesgo"))
    dim_innovacion.append(extraer_promedio_dimension(escala, "Orientación a la innovación"))
    dim_poder.append(extraer_promedio_dimension(escala, "Distancia de poder"))
    dim_individualismo.append(extraer_promedio_dimension(escala, "Individualismo vs Colectivismo"))

df_perfiles = pd.DataFrame(perfiles)
df_perfiles['porter_promedio'] = promedios_porter
df_perfiles['pestel_promedio'] = promedios_pestel
df_perfiles['foda_promedio'] = promedios_foda
df_perfiles['ishikawa_promedio'] = promedios_ishikawa
df_perfiles['aversion_riesgo'] = dim_aversion
df_perfiles['innovacion'] = dim_innovacion
df_perfiles['distancia_poder'] = dim_poder
df_perfiles['individualismo'] = dim_individualismo

# Filtros laterales
st.sidebar.header("Filtros")
cargos_uniq = df_perfiles['cargo'].dropna().unique()
cargos_sel = st.sidebar.multiselect("Cargo", cargos_uniq, default=cargos_uniq)
edades_uniq = df_perfiles['edad'].dropna().unique()
edades_sel = st.sidebar.multiselect("Edad", edades_uniq, default=edades_uniq)
experiencia_uniq = df_perfiles['experiencia'].dropna().unique()
experiencia_sel = st.sidebar.multiselect("Experiencia", experiencia_uniq, default=experiencia_uniq)

df_filtrado = df_perfiles[
    df_perfiles['cargo'].isin(cargos_sel) &
    df_perfiles['edad'].isin(edades_sel) &
    df_perfiles['experiencia'].isin(experiencia_sel)
]

st.subheader("📈 Promedios generales por metodología")
prom_porter = df_filtrado['porter_promedio'].mean()
prom_pestel = df_filtrado['pestel_promedio'].mean()
prom_foda = df_filtrado['foda_promedio'].mean()
prom_ishikawa = df_filtrado['ishikawa_promedio'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Porter", f"{prom_porter:.2f}/5" if not np.isnan(prom_porter) else "N/D")
col2.metric("PESTEL", f"{prom_pestel:.2f}/5" if not np.isnan(prom_pestel) else "N/D")
col3.metric("FODA", f"{prom_foda:.2f}/5" if not np.isnan(prom_foda) else "N/D")
col4.metric("Ishikawa", f"{prom_ishikawa:.2f}/5" if not np.isnan(prom_ishikawa) else "N/D")

# Gráficos por cargo
st.subheader("📊 Análisis por cargo")
fig, ax = plt.subplots(figsize=(10, 5))
promedios_cargo = df_filtrado.groupby('cargo')[['porter_promedio', 'pestel_promedio']].mean()
promedios_cargo.plot(kind='bar', ax=ax, color=['#2c3e50', '#27ae60'])
ax.set_ylim(0, 5.5)
ax.set_ylabel("Puntuación promedio")
ax.set_title("Comparación Porter vs PESTEL según cargo")
st.pyplot(fig)

# Relación entre dimensiones de escala y Porter
st.subheader("🔍 Correlaciones entre perfil psicológico y análisis Porter")
if len(df_filtrado) > 1:
    corr_matrix = df_filtrado[['aversion_riesgo', 'innovacion', 'distancia_poder', 'individualismo', 'porter_promedio']].corr()
    st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'))
    
    # Gráfico de dispersión: aversión al riesgo vs Porter
    fig2, ax2 = plt.subplots()
    ax2.scatter(df_filtrado['aversion_riesgo'], df_filtrado['porter_promedio'], alpha=0.6)
    ax2.set_xlabel("Aversión al riesgo (1-5)")
    ax2.set_ylabel("Porter promedio")
    ax2.set_title("Relación entre aversión al riesgo y percepción competitiva")
    # Línea de tendencia
    x = df_filtrado['aversion_riesgo'].dropna()
    y = df_filtrado['porter_promedio'].dropna()
    if len(x) > 1:
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax2.plot(np.linspace(1,5,100), p(np.linspace(1,5,100)), "r--")
    st.pyplot(fig2)
else:
    st.info("Se necesitan al menos 2 evaluaciones para mostrar correlaciones.")

# Alfa de Cronbach (si hay al menos 3 evaluaciones y la escala tiene items consistentes)
st.subheader("🔧 Consistencia interna de la escala (Alfa de Cronbach)")
if len(df_filtrado) >= 3:
    # Reconstruir matriz de ítems (cada evaluador, cada ítem de la escala)
    # Vamos a extraer las 12 respuestas individuales como columnas
    items_scale = []
    for _, row in df_filtrado.iterrows():
        escala = row.get('resp_escala', {})
        if escala:
            # Ordenar por clave para tener consistencia
            valores = [v for k, v in sorted(escala.items())]
            items_scale.append(valores)
    if len(items_scale) >= 3 and len(items_scale[0]) > 1:
        df_items = pd.DataFrame(items_scale)
        # Calcular alfa usando la función de numpy (o podemos usar la misma función auxiliar)
        from cronbach_alpha import cronbach_alpha  # o definirla aquí directamente
        def cronbach_alpha_local(df_items):
            n_items = df_items.shape[1]
            var_items = df_items.var(axis=0, ddof=1)
            total_var = df_items.sum(axis=1).var(ddof=1)
            if total_var == 0:
                return np.nan
            return (n_items / (n_items - 1)) * (1 - var_items.sum() / total_var)
        alpha = cronbach_alpha_local(df_items)
        st.metric("Alfa de Cronbach", f"{alpha:.3f}" if not np.isnan(alpha) else "N/D")
        st.markdown("**Interpretación:** α > 0.7 indica buena consistencia interna.")
    else:
        st.info("No hay suficientes datos de la escala para calcular alfa.")
else:
    st.info("Se necesitan al menos 3 evaluaciones para calcular la consistencia de la escala.")

# Mostrar tabla de datos brutos (anonimizada)
with st.expander("Ver datos anonimizados (últimas 50 evaluaciones)"):
    st.dataframe(df_filtrado[['edad', 'experiencia', 'carrera', 'cargo', 'porter_promedio', 'aversion_riesgo']].head(50))