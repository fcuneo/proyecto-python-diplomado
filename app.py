# TODO: Aquí debes escribir tu código

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import date
import plotly.express as px

st.set_page_config(
    page_title="Gestión de recursos hídricos - DINAGUA",
    layout="wide"
)

@st.cache_data
def cargar_datos():
    df = pd.read_csv("data/processed/tramites_procesados.csv")
    df["Fecha de Solicitud"] = pd.to_datetime(df["Fecha de Solicitud"], errors="coerce")
    return df

df = cargar_datos()

st.title("💧 Gestión de trámites de derechos de uso de aguas - DINAGUA")



#FILTROS SIDEBAR

st.sidebar.header("Filtros")

# FECHA PRIMERO
fecha_min = df["Fecha de Solicitud"].min().date()
fecha_max = df["Fecha de Solicitud"].max().date()

fecha_inicio_default = date(2025, 4, 1)
fecha_fin_default = min(date(2026, 4, 1), fecha_max)

rango_fechas = st.sidebar.date_input(
    "Fecha de Solicitud",
    value=(fecha_inicio_default, fecha_fin_default),
    min_value=fecha_min,
    max_value=fecha_max,
    format="DD/MM/YYYY"
)

# DESPUÉS LOS DEMÁS FILTROS
regional = st.sidebar.multiselect(
    "Regional",
    options=sorted(df["Regional"].dropna().unique()),
    default=sorted(df["Regional"].dropna().unique())
)

uso = st.sidebar.multiselect(
    "Uso",
    options=sorted(df["Uso"].dropna().unique()),
    default=sorted(df["Uso"].dropna().unique())
)

estado = st.sidebar.multiselect(
    "Estado",
    options=sorted(df["Estado Agrupado"].dropna().unique()),
    default=sorted(df["Estado Agrupado"].dropna().unique())
)

df_filtrado = df[
    (df["Fecha de Solicitud"].dt.date >= rango_fechas[0]) &
    (df["Fecha de Solicitud"].dt.date <= rango_fechas[1]) &
    (df["Regional"].isin(regional)) &
    (df["Uso"].isin(uso)) &
    (df["Estado Agrupado"].isin(estado))
]


#FILTROS ACTIVOS
st.markdown("###### Filtros activos")

st.markdown(
    f"""
    <div style="
        background-color:#f2f2f2;
        padding:8px;
        border-radius:5px;
        color:black;
        font-size:12px;
    ">
        📅 {rango_fechas[0].strftime('%d/%m/%Y')} - {rango_fechas[1].strftime('%d/%m/%Y')}
        &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;
        🌎 {len(regional)} regionales
        &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;
        💧 {len(uso)} usos
        &nbsp;&nbsp;&nbsp;•&nbsp;&nbsp;&nbsp;
        📋 {len(estado)} estados
    </div>
    """,
    unsafe_allow_html=True
)

st.divider()
#INDICADORES GENERALES

st.subheader("📊 Indicadores generales")

col1, col2, col3, col4 = st.columns(4)

total = len(df_filtrado)
registrados = (df_filtrado["Estado Agrupado"] == "Registrada").sum()
pendientes = (df_filtrado["Estado Agrupado"] == "Pendiente").sum()
porcentaje_pendientes = pendientes / total * 100 if total > 0 else 0

col1.metric("Total expedientes", total)
col2.metric("Registrados", registrados)
col3.metric("Pendientes", pendientes)
col4.metric("% pendientes", f"{porcentaje_pendientes:.1f}%")

st.divider()

st.subheader("⏱️ Tiempo de tramitación")

df_resueltos = df_filtrado[
    df_filtrado["Tiempo de Tramitación"].notna()
]

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Tiempo mediano",
        f"{df_resueltos['Tiempo de Tramitación'].median():.1f} meses"
    )

with col2:
    st.metric(
        "Tiempo promedio",
        f"{df_resueltos['Tiempo de Tramitación'].mean():.1f} meses"
    )

with col3:
    st.metric(
        "Tiempo máximo",
        f"{df_resueltos['Tiempo de Tramitación'].max():.1f} meses"
    )

st.divider()

#HISTOGRAMA TIEMPO TRAMITACIÓN
st.markdown("###### Histograma tiempo de tramitación")

fig, ax = plt.subplots(figsize=(8,4))

sns.histplot(
    data=df_resueltos,
    x="Tiempo de Tramitación",
    bins=30,
    kde=True,
    color="#0B5CAD",   # azul oscuro
    ax=ax
)

# Media y mediana
media = df_resueltos["Tiempo de Tramitación"].mean()
mediana = df_resueltos["Tiempo de Tramitación"].median()

# Línea de la media
ax.axvline(
    media,
    linestyle="--",
    linewidth=2,
    color="dimgray",
    label=f"Media: {media:.1f} meses"
)

# Línea de la mediana
ax.axvline(
    mediana,
    linestyle=":",
    linewidth=2,
    color="dimgray",
    label=f"Mediana: {mediana:.1f} meses"
)

# Cuadrícula horizontal tenue
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.3
)



ax.set_xlabel(
    "Tiempo de Tramitación (meses)",
    fontsize=9
)

ax.set_ylabel(
    "Cantidad de expedientes",
    fontsize=9
)

# Tamaño de los números de los ejes
ax.tick_params(
    axis="both",
    labelsize=7
)

# Leyenda
ax.legend(
    fontsize=7
)

st.pyplot(fig)
#BOXPLOT TIEMPO RESOLUCIÓN POR REGIONAL
st.markdown("###### Tiempo de Tramitación por Regional")
fig, ax = plt.subplots(figsize=(10,5))

sns.boxplot(
    data=df_resueltos,
    x="Regional",
    y="Tiempo de Tramitación",
    color="#0B5CAD",
    ax=ax
)

ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.3
)

ax.set_xlabel(
    "Regional",
    fontsize=9
)

ax.set_ylabel(
    "Tiempo de Tramitación (meses)",
    fontsize=9
)

# Tamaño de las categorías y números
ax.tick_params(
    axis="both",
    labelsize=7
)

plt.xticks(rotation=45)

st.pyplot(fig)


#TABLA TIEMPO POR USO
st.markdown("###### Tiempo de Tramitación por Uso")

tabla_uso = (
    df_resueltos
    .groupby("Uso")["Tiempo de Tramitación"]
    .agg(
        Cantidad="count",
        Q1=lambda x: x.quantile(0.25),
        Mediana="median",
        Q3=lambda x: x.quantile(0.75),
        Q4="max"
    )
    .round(2)
    .sort_values("Mediana", ascending=False)
)

st.dataframe(tabla_uso)



#BOXPLOT POR USO

fig, ax = plt.subplots(figsize=(12,5))

sns.boxplot(
    data=df_resueltos,
    x="Uso",
    y="Tiempo de Tramitación",
    color="#0B5CAD",   # Power BI oscuro
    ax=ax
)

# Cuadrícula horizontal tenue
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.3
)



ax.set_xlabel(
    "Uso",
    fontsize=9
)

ax.set_ylabel(
    "Tiempo de Tramitación (meses)",
    fontsize=9
)

# Tamaño de letras de categorías y números
ax.tick_params(
    axis="both",
    labelsize=9
)

# Rotar etiquetas de categorías
plt.xticks(rotation=45, ha="right")

st.pyplot(fig)

st.divider()
#TRAMITES PENDINTES
st.subheader("⏳ Trámites Pendientes")

#INDICADORES PRINCIPALES PENDIENTES
df_pendientes = df_filtrado[
    df_filtrado["Estado Agrupado"] == "Pendiente"
]

col1, col2, col3 = st.columns(3)

col1.metric(
    "Pendientes",
    len(df_pendientes)
)

col2.metric(
    "Antigüedad mediana",
    f"{df_pendientes['Antigüedad Pendiente'].median():.1f} meses"
)

col3.metric(
    "Antigüedad máxima",
    f"{df_pendientes['Antigüedad Pendiente'].max():.1f} meses"
)

st.divider()

#HISTOGRAMA ANTIGUEDAD PENDIENTES
st.markdown("###### Histograma antigüedad pendientes")

from matplotlib.patches import Patch

datos_antiguedad = df_pendientes["Antigüedad Pendiente"].dropna()

fig, ax = plt.subplots(figsize=(8,4))

n, bins, patches = ax.hist(
    datos_antiguedad,
    bins=20,
    edgecolor="black",
    linewidth=0.8
)

# Cuartiles calculados sobre los datos filtrados
q1 = datos_antiguedad.quantile(0.25)
q2 = datos_antiguedad.quantile(0.50)
q3 = datos_antiguedad.quantile(0.75)

# Coloreado dinámico según cuartiles
for patch, bin_left in zip(patches, bins[:-1]):

    if bin_left <= q1:
        patch.set_facecolor("green")

    elif bin_left <= q2:
        patch.set_facecolor("yellow")

    elif bin_left <= q3:
        patch.set_facecolor("orange")

    else:
        patch.set_facecolor("red")

# Leyenda
legend_elements = [
    Patch(facecolor="green", edgecolor="black", label="Menor antigüedad"),
    Patch(facecolor="yellow", edgecolor="black", label="Antigüedad baja-media"),
    Patch(facecolor="orange", edgecolor="black", label="Antigüedad media-alta"),
    Patch(facecolor="red", edgecolor="black", label="Mayor antigüedad")
]

ax.legend(
    handles=legend_elements,
    fontsize=7
)

# Cuadrícula horizontal tenue
ax.grid(
    axis="y",
    linestyle="--",
    linewidth=0.5,
    alpha=0.3
)

ax.set_xlabel(
    "Antigüedad (meses)",
    fontsize=8
)

ax.set_ylabel(
    "Cantidad de expedientes",
    fontsize=8
)

# Tamaño de los números de los ejes
ax.tick_params(
    axis="both",
    labelsize=7
)

st.pyplot(fig)

#DETALLE EXPEDIENTES PENDIENTES
st.markdown("###### Detalle de Expedientes Pendientes")

st.caption(
    "La tabla permite identificar y analizar los casos con mayor antigüedad dentro del período seleccionado. Utilice el desplazamiento y ordenamiento para explorar las columnas."
)

columnas_pendientes = [
    "Regional",
    "Departamento",
    "Uso",
    "Fecha de Solicitud",
    "Antigüedad Pendiente",
    "Nro. GEX"
]

st.dataframe(
    df_pendientes[columnas_pendientes]
    .sort_values("Antigüedad Pendiente", ascending=False),
    use_container_width=True,
    height=250

)

st.divider()

#MAPA

st.subheader("🗺️ Distribución Geográfica de los Expedientes")
st.caption(
    "Distribución geográfica de los expedientes con coordenadas disponibles. El color de cada punto representa el uso declarado del agua."
)
df_mapa = df_filtrado.dropna(
    subset=["Latitud", "Longitud"]
).copy()

fig = px.scatter_mapbox(
    df_mapa,
    lat="Latitud",
    lon="Longitud",
    color="Uso",
    hover_name="Nro. GEX",
    hover_data=[
        "Regional",
        "Departamento",
        "Uso"
    ],
    zoom=5,
    height=500
)

fig.update_layout(
    mapbox_style="open-street-map",
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.divider()

#TABLA COMPLETA
st.markdown("### 📄 Detalle de expedientes")

st.caption(
    "Listado completo de los expedientes filtrados. Utilice el desplazamiento y el ordenamiento de columnas para explorar los registros."
)

st.caption(
    f"Base completa: {df.shape[0]:,} registros × {df.shape[1]} variables | "
    f"Tabla filtrada: {df_filtrado.shape[0]:,} registros × {df_filtrado.shape[1]} variables"
    .replace(",", ".")
)

st.dataframe(
    df_filtrado,
    use_container_width=True,
    height=350
)
