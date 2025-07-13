import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os
import threading

# Cargar variables de entorno
load_dotenv()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Función para obtener productos
def fetch_data():
    try:
        response = supabase.table("producto").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error al obtener productos: {e}")
        return []

# Función para obtener precios de un producto y un año
def fetch_precios(producto, anio):
    try:
        producto_id = fetch_producto_id(producto)
        if producto_id:
            response = supabase.table("precio_productor").select("*").eq("producto_id", producto_id["id"]).eq("anio", anio).execute()
            return response.data
    except Exception as e:
        st.error(f"❌ Error al obtener precios: {e}")
        return []

# Función para obtener el ID del producto por nombre
def fetch_producto_id(nombre_producto):
    try:
        response = supabase.table("producto").select("id").eq("nombre", nombre_producto).single()
        if response.data:
            return response.data['id']
        else:
            st.error(f"Producto no encontrado: {nombre_producto}")
            return None
    except Exception as e:
        st.error(f"Error al obtener producto: {e}")
        return None


# Función para insertar precio en la base de datos
def insertar_precio_productor(anio, mes, producto_id, precio_usd, precio_kg, usuario_simulado):
    try:
        response = supabase.rpc("insertar_precio_productor", 
                                {"p_anio": anio, 
                                 "p_mes": mes, 
                                 "p_nombre_producto": producto_id, 
                                 "p_ponderado_usd": precio_usd, 
                                 "p_ponderado_usd_kg": precio_kg, 
                                 "p_usuario_simulado": usuario_simulado}).execute()
        
        # Si la respuesta tiene éxito, se ha insertado el precio correctamente
        if response.status_code == 200:
            return True
        else:
            st.error(f"Error al insertar precio: {response.message}")
            return False
    except Exception as e:
        st.error(f"Error al insertar precio: {e}")
        return False

# Formulario para insertar/actualizar precios
def insertar_precio():
    st.header("Insertar o Actualizar Precio del Productor")
    
    # Selección de producto
    productos = fetch_data()  # Llamamos la función fetch_data() que ya tienes
    if productos:
        producto_names = [producto['nombre'] for producto in productos]
        producto_seleccionado = st.selectbox("Selecciona un Producto", producto_names)
    else:
        st.warning("No hay productos disponibles.")
        return

    # Año, mes, y precios
    anio = st.number_input("Año", min_value=2013, max_value=2025, value=2024)
    mes = st.selectbox("Mes", ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"])
    precio_usd = st.number_input("Precio Ponderado en USD", min_value=0.0, format="%.2f")
    precio_kg = st.number_input("Precio Ponderado en USD/KG", min_value=0.0, format="%.2f")

    # Usuario simulado
    usuario_simulado = st.text_input("Nombre de Usuario Simulado")

    if st.button("Insertar/Actualizar Precio"):
        if usuario_simulado and precio_usd and precio_kg:
            producto_id = next(producto['id'] for producto in productos if producto['nombre'] == producto_seleccionado)
            # Llamar a la función de insertar/actualizar precio
            try:
                insertar_precio_productor(anio, mes, producto_id, precio_usd, precio_kg, usuario_simulado)
                st.success(f"Precio de {producto_seleccionado} insertado/actualizado exitosamente.")
            except Exception as e:
                st.error(f"Error al insertar el precio: {e}")
        else:
            st.error("Por favor, complete todos los campos.")

# Consultar precios existentes
def consultar_precios():
    st.header("Consultar Precios del Productor")

    # Obtener productos
    productos = fetch_data()
    if productos:
        producto_names = [producto['nombre'] for producto in productos]
        producto_seleccionado = st.selectbox("Selecciona un Producto", producto_names)
    else:
        st.warning("No hay productos disponibles.")
        return

    # Filtro de año
    anio = st.number_input("Año", min_value=2013, max_value=2025, value=2024)

    # Consultar precios para el producto seleccionado y el año elegido
    precios = fetch_precios(producto_seleccionado, anio)
    
    if precios:
        st.write("Datos de Precios:")
        for precio in precios:
            st.write(f"Año: {precio['anio']}, Mes: {precio['mes']}, Precio USD: {precio['ponderado_usd']}, Precio USD/KG: {precio['ponderado_usd_kg']}")
    else:
        st.warning("No hay precios disponibles para el producto o año seleccionado.")

def simular_concurrencia():
    st.header("Simular Concurrencia de Usuarios")
    
    def insertar_concurrente():
        # Simulación de inserción concurrente
        # Por ejemplo, inserta el precio de un producto (puedes hacer esto de forma más avanzada)
        st.write("Simulando inserción...")
        insertar_precio()

    if st.button("Iniciar Simulación"):
        # Crear varios hilos para simular múltiples usuarios
        threads = []
        for _ in range(5):  # 5 usuarios simulados
            thread = threading.Thread(target=insertar_concurrente)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        st.success("Simulación de concurrencia completada.")

# Mostrar el menú y las diferentes opciones
menu = st.sidebar.selectbox("Menú", [
    "Insertar/Actualizar Precio",
    "Consultar Precios",
    "Consultas Avanzadas",
    "Auditoría",
    "Simular Concurrencia"
])

if menu == "Insertar/Actualizar Precio":
    insertar_precio()
elif menu == "Consultar Precios":
    consultar_precios()
elif menu == "Simular Concurrencia":
    simular_concurrencia()
