import streamlit as st
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



# === Obtener productos desde Supabase ===
def get_productos():
    res = supabase.rpc("obtener_productos").execute()
    if res.data is None:
        st.error("Error al obtener productos")
        return []
    return res.data

# === Llamar a la función insertar_precio_productor ===
def insertar_precio(anio, mes, nombre_producto, precio_usd, precio_kg, usuario):
    params = {
        "p_anio": anio,
        "p_mes": mes,
        "p_nombre_producto": nombre_producto,
        "p_ponderado_usd": precio_usd,
        "p_ponderado_usd_kg": precio_kg,
        "p_usuario_simulado": usuario
    }
    supabase.rpc('insertar_usuario_simulado',{"p_nombre":usuario , "p_correo": (usuario + "@gmail.com") }).execute()
    res = supabase.rpc("insertar_precio_productor", params).execute()
    return res

# === UI STREAMLIT ===
def render_registro():
    st.title("📝 Registro de Nuevos Precios de Producto")

    st.markdown(
    """
    <style>
    .stApp {
        background-image: url("https://www.fundssociety.com/wp-content/uploads/2021/05/field-213364_1920.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    </style>
    """,
    unsafe_allow_html=True
)


    productos = get_productos()
    if not productos:
        return

    producto_nombres = [p["nombre"] for p in productos]
    producto_seleccionado = st.selectbox("📦 Producto", producto_nombres)

    anio = st.selectbox("📅 Año", list(range(2013, 2026)))
    mes = st.selectbox("📆 Mes", [
        'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
        'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
    ])

    precio_usd = st.number_input("💰 Precio ponderado USD", min_value=0.0, step=0.01, format="%.2f")
    precio_usd_kg = st.number_input("⚖️ Precio ponderado USD/Kg", min_value=0.0, step=0.01, format="%.2f")
    usuario = st.text_input("👤 Nombre del agricultor o usuario")

    if st.button("💾 Insertar / Actualizar"):
        if not usuario.strip():
            st.warning("⚠️ Debes ingresar un nombre de usuario.")
            return
        resultado = insertar_precio(anio, mes, producto_seleccionado, precio_usd, precio_usd_kg, usuario)
        if resultado is None:
            st.error(f"❌ Error al insertar: {resultado.error.message}")
        else:
            st.success("✅ Precio registrado o actualizado correctamente.")

# === Ejecutar ===
if __name__ == "__main__":
    render_registro()
