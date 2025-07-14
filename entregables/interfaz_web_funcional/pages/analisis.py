import streamlit as st
import os
import pandas as pd
import altair as alt
from supabase import create_client, Client
from dotenv import load_dotenv
from PIL import Image

# ======== CARGA DE VARIABLES .ENV ========
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ======== CSS PARA FONDO DE IMAGEN ========
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://wallpapers.com/images/hd/agriculture-background-zb06jbplfqoilptw.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# ======== FUNCIONES DE CONSULTA ========
def get_productos():
    res = supabase.rpc("obtener_productos").execute()
    if res.data is None:
        st.error("Error cargando productos")
        return []
    return res.data

def get_precios_historicos(producto_id):
    res = supabase.rpc("obtener_precios_historicos_completos", {"prod_id": producto_id}).execute()
    if res.data is None:
        st.error("Error cargando datos históricos")
        return pd.DataFrame()
    return pd.DataFrame(res.data)

# ======== MAIN ========
def main():
    set_background()

    # ===================== BOTÓN DE REGRESO =======================
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <a href="http://localhost:8501" style="
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                font-weight: bold;
                border-radius: 10px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                position: absolute;
                top: 0px;
                left: 10px;
            ">🔙 Volver al Inicio</a>
        </div>
    """, unsafe_allow_html=True)


    st.title("📈 Comparador de Precios Históricos de Productos")

    productos = get_productos()
    if not productos:
        return

    opciones = {p["nombre"]: p["id"] for p in productos}
    
    seleccionados = st.multiselect(
        "Selecciona uno o más productos para comparar",
        options=list(opciones.keys())
    )

    if not seleccionados:
        st.info("Selecciona al menos un producto para visualizar datos.")
        return

    # Mapeo para los nombres de los meses con primera letra mayúscula
    meses_map = {
        'Enero': 1, 'Febrero': 2, 'Marzo': 3, 'Abril': 4, 'Mayo': 5, 'Junio': 6,
        'Julio': 7, 'Agosto': 8, 'Septiembre': 9, 'Octubre': 10, 'Noviembre': 11, 'Diciembre': 12
    }

    df_total = pd.DataFrame()

    for nombre in seleccionados:
        producto_id = opciones[nombre]
        df = get_precios_historicos(producto_id)

        if df.empty:
            continue

        # Normaliza meses y crea fecha
        df["mes"] = df["mes"].str.capitalize()  # 'enero' -> 'Enero'
        df["mes_num"] = df["mes"].map(meses_map)
        df["fecha"] = pd.to_datetime(dict(year=df["anio"], month=df["mes_num"], day=1), errors='coerce')
        df["producto"] = nombre
        df_total = pd.concat([df_total, df], ignore_index=True)

    if df_total.empty or df_total["fecha"].isna().all():
        st.warning("No se pudieron construir las fechas para graficar.")
        return
    
    # Crear filtro por año
    # Crear filtro por año con opción "Todos"
    anios_disponibles = sorted(df_total["anio"].dropna().unique())
    anios_opciones = ["Todos"] + [str(a) for a in anios_disponibles]

    anio_seleccionado = st.selectbox("📅 Filtrar por año", anios_opciones)

    if anio_seleccionado != "Todos":
        anio_num = int(anio_seleccionado)
        df_total = df_total[df_total["anio"] == anio_num]



    # ====================== GRÁFICAS =========================
    st.subheader("📊 Precio Ponderado Total (USD)")
    chart_usd = alt.Chart(df_total.dropna(subset=["fecha"])).mark_line(
        point=True,
        opacity=0.5
    ).encode(
        x="fecha:T",
        y=alt.Y("ponderado_usd:Q", title="Precio USD"),
        color="producto:N",
        tooltip=["producto", "fecha:T", "ponderado_usd"]
    ).properties(
        width=800,
        height=400,
        background='rgba(0, 0, 0, 0.6)'  # <- fondo totalmente transparente
    )

    st.altair_chart(chart_usd, use_container_width=True)


    st.subheader("📊 Precio Ponderado por KG (USD/kg)")
    chart_kg = alt.Chart(df_total.dropna(subset=["fecha"])).mark_line(point=True).encode(
        x="fecha:T",
        y=alt.Y("ponderado_usd_kg:Q", title="Precio USD/kg"),
        color="producto:N",
        tooltip=["producto", "fecha:T", "ponderado_usd_kg"]
    ).properties(width=800, height=400,background='rgba(0, 0, 0, 0.6)')
    st.altair_chart(chart_kg, use_container_width=True)



    #Consultas avanzadas

    st.subheader("📊 Promedio de Precios por Producto y Año")
    promedio_res = supabase.rpc("obtener_promedio_usd_por_anio").execute()
    if promedio_res.data:
        df_promedio = pd.DataFrame(promedio_res.data)
        chart1 = alt.Chart(df_promedio).mark_line(point=True).encode(
            x="anio:O",
            y="promedio_usd:Q",
            color="nombre:N",
            tooltip=["nombre", "anio", "promedio_usd"]
        ).properties(
            width=750,
            height=400,
            title="Promedio USD por producto y año"
        )
        st.altair_chart(chart1, use_container_width=True)
    else:
        st.info("No hay datos disponibles para promedio.")

    st.subheader("📉 Variación Máxima de Precio por Producto")
    variacion_res = supabase.rpc("obtener_variacion_maxima_usd").execute()
    if variacion_res.data:
        df_var = pd.DataFrame(variacion_res.data)
        chart2 = alt.Chart(df_var).mark_bar().encode(
            x=alt.X("variacion:Q", title="Variación USD"),
            y=alt.Y("nombre:N", sort='-x'),
            tooltip=["nombre", "variacion"]
        ).properties(
            width=750,
            height=400,
            title="Rango Máximo de Variación de Precio por Producto"
        )
        st.altair_chart(chart2, use_container_width=True)
    else:
        st.info("No hay datos disponibles para variación.")

    #obtener planes explain...

    def obtener_explain_promedio():
        res = supabase.rpc("explain_promedio").execute()
        if res.data is None:
            st.error("No se pudo obtener el plan de ejecución.")
            return []
        return [line['plan'] for line in res.data]

    def obtener_explain_variacion():
        res = supabase.rpc("explain_variacion").execute()
        if res.data is None:
            st.error("No se pudo obtener el plan de ejecución.")
            return []
        return [line['plan'] for line in res.data]



    




# En tu función principal o página
    with st.expander("📊 Ver plan de ejecución para variación de precios"):
        
            
        if st.button("Mostrar EXPLAIN variación"):
            plan = obtener_explain_variacion()
            
            plan2= obtener_explain_promedio()
            if plan and plan2:
                st.write("consulta de promedio:")
                st.code("\n".join(plan2), language="sql")
                st.image(Image.open("pages/figs/variacion.png"))

                st.write("consulta de variacion:")
                st.code("\n".join(plan), language="sql")
                st.image(Image.open("pages/figs/promedio.png"))
            else:
                st.warning("No se recibió ningún plan.")




        # ===================== BOTÓN DE REGRESO =======================
    st.markdown("""
        <div style="text-align: center; margin-top: 2rem;">
            <a href="http://localhost:8501/?page=home" style="
                background-color: #4CAF50;
                color: white;
                padding: 12px 24px;
                text-decoration: none;
                font-weight: bold;
                border-radius: 10px;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.3);
                aligment: right;
            ">🔙 Volver al Inicio</a>
        </div>
    """, unsafe_allow_html=True)



if __name__ == "__main__":
    main()
