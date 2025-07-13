import streamlit as st
import asyncio
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import random




load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def insertar_o_actualizar_precio(p_anio, p_mes, p_nombre_producto, p_ponderado_usd, p_ponderado_usd_kg, p_usuario_simulado):
    params = {
        "p_anio": p_anio,
        "p_mes": p_mes,
        "p_nombre_producto": p_nombre_producto,
        "p_ponderado_usd": p_ponderado_usd,
        "p_ponderado_usd_kg": p_ponderado_usd_kg,
        "p_usuario_simulado": p_usuario_simulado
    }
    supabase.rpc('insertar_usuario_simulado',{"p_nombre":p_usuario_simulado , "p_correo": (p_usuario_simulado + "@gmail.com") }).execute()
    res = supabase.rpc("insertar_precio_productor", params).execute()
    return res

async def concurrent_update(p_anio, p_mes, p_nombre_producto, p_ponderado_usd, p_ponderado_usd_kg, p_usuario_simulado, iteracion, logs):
    await asyncio.sleep(random.uniform(0, 0.5))
    res = insertar_o_actualizar_precio(p_anio, p_mes, p_nombre_producto, p_ponderado_usd, p_ponderado_usd_kg, p_usuario_simulado)
    if res.data is None:
        logs.append(f"❌ [{datetime.now().strftime('%H:%M:%S')}] Usuario '{p_usuario_simulado}' Iter {iteracion}: ERROR - {res.error.message}")
    else:
        logs.append(f"✅ [{datetime.now().strftime('%H:%M:%S')}] Usuario '{p_usuario_simulado}' Iter {iteracion}: OK")

def main():
    st.title("🛠️ Simulación de Concurrencia en Actualizaciones")



    st.markdown(
        """
        <style>
        .stApp {
            background-image: url("https://www.nationalgeographic.com/foodfeatures/feeding-9-billion/images/carousel3/images_1536/steinmetzb7_1536.jpg");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


    productos_res = supabase.rpc("obtener_productos").execute()
    productos = productos_res.data or []
    opciones_productos = [p['nombre'] for p in productos]

    usar_datos_fijos = st.radio("Selecciona modo de datos para actualización:", 
                               ["Datos predefinidos (Año 2013, Enero, Aguacate fuerte, precio 0)", 
                                "Datos personalizados"])

    if usar_datos_fijos == "Datos predefinidos (Año 2013, Enero, Aguacate fuerte, precio 0)":
        p_anio = 2013
        p_mes = "Enero"
        p_nombre_producto = "Aguacate Fuerte"
        # Puedes variar precios ligeramente para simular concurrencia más real
        precio_base_usd = 0.0
        precio_base_usd_kg = 0.0
        mostrar_inputs = False
    else:
        p_anio = st.number_input("Año", min_value=2013, max_value=2025, value=2024)
        p_mes = st.selectbox("Mes", ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'])
        p_nombre_producto = st.selectbox("Selecciona producto para actualizar", opciones_productos)
        precio_base_usd = st.number_input("Precio ponderado USD", min_value=0.0, format="%.2f", value=100.0)
        precio_base_usd_kg = st.number_input("Precio ponderado USD por kg", min_value=0.0, format="%.2f", value=50.0)
        mostrar_inputs = True

    usuarios_simulados_txt = st.text_input("Nombres de usuarios simulados (separados por coma)", "usuario1,usuario2")
    usuarios_simulados = [u.strip() for u in usuarios_simulados_txt.split(",") if u.strip()]
    iteraciones = st.number_input("Número de iteraciones por usuario", min_value=1, max_value=100, value=5)

    if st.button("🚀 Ejecutar Actualizaciones Concurrentes"):
        logs = []
        st.info(f"Iniciando {iteraciones} iteraciones para cada uno de {len(usuarios_simulados)} usuarios simulados...")

        async def run_all():
            tasks = []
            for iteracion in range(1, iteraciones + 1):
                for usuario in usuarios_simulados:
                    # Si está en modo fijo, se puede variar un poco para simular concurrencia
                    if usar_datos_fijos == "Datos predefinidos (Año 2013, Enero, Aguacate fuerte, precio 0)":
                        usd_variacion = precio_base_usd + random.uniform(-0.5, 0.5)
                        usd_kg_variacion = precio_base_usd_kg + random.uniform(-0.3, 0.3)
                    else:
                        usd_variacion = precio_base_usd + random.uniform(-5, 5)
                        usd_kg_variacion = precio_base_usd_kg + random.uniform(-2, 2)

                    tasks.append(concurrent_update(
                        p_anio, p_mes, p_nombre_producto,
                        round(usd_variacion, 2), round(usd_kg_variacion, 2),
                        usuario, iteracion, logs
                    ))
            await asyncio.gather(*tasks)

        asyncio.run(run_all())

        st.subheader("📝 Logs de la Simulación")
        for log in logs:
            st.write(log)

if __name__ == "__main__":
    main()
