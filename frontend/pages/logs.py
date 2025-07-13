import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv
import pandas as pd
import json
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://cdn.pixabay.com/photo/2021/08/15/08/31/sunset-6547166_1280.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)



st.title("📋 Historial de Logs y Auditoría")
st.markdown("Consulta los cambios registrados en el sistema con filtros avanzados.")

# Parámetro de cantidad de registros
n = st.number_input("🔢 ¿Cuántos registros deseas ver?", min_value=1, max_value=500, value=10, step=1)

# Obtener los logs vía función
response = supabase.rpc("obtener_logs_auditoria", {"p_n_registros": n}).execute()
if not response.data:
    st.info("No se encontraron logs.")
  

df = pd.DataFrame(response.data)

# Procesamiento de campos
df["fecha"] = pd.to_datetime(df["fecha"]).dt.strftime("%Y-%m-%d %H:%M:%S")
df["datos_antes"] = df["datos_antes"].apply(lambda x: json.dumps(x, indent=2) if x else "")
df["datos_despues"] = df["datos_despues"].apply(lambda x: json.dumps(x, indent=2) if x else "")

# Filtros
operaciones = ["Todos"] + sorted(df["operacion"].unique())
tablas = ["Todas"] + sorted(df["tabla_afectada"].unique())

operacion_sel = st.selectbox("🔧 Filtrar por operación", operaciones)
tabla_sel = st.selectbox("🗂️ Filtrar por tabla afectada", tablas)

df_filtrado = df.copy()
if operacion_sel != "Todos":
    df_filtrado = df_filtrado[df_filtrado["operacion"] == operacion_sel]
if tabla_sel != "Todas":
    df_filtrado = df_filtrado[df_filtrado["tabla_afectada"] == tabla_sel]

# Mostrar resultados
st.markdown("### Resultados")


def colorear_filas_por_operacion(row):
    if row["operacion"] == "INSERT":
        color = "background-color: rgba(40, 167, 69, 0.15);"   # verde suave transparente
    elif row["operacion"] == "UPDATE":
        color = "background-color: rgba(255, 193, 7, 0.15);"    # amarillo suave transparente
    elif row["operacion"] == "DELETE":
        color = "background-color: rgba(220, 53, 69, 0.15);"    # rojo suave transparente
    else:
        color = ""
    return [color] * len(row)




styled_df = df_filtrado[["fecha", "usuario_simulado", "tabla_afectada", "operacion", "datos_antes", "datos_despues"]].style.apply(colorear_filas_por_operacion, axis=1)

st.dataframe(styled_df, use_container_width=True)
