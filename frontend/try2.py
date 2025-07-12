import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Configuración Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ----- FUNCIONES -----
def fetch_data():
    try:
        response = supabase.table("producto").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"❌ Error al obtener datos: {e}")
        return None

# ----- ESTILOS CUSTOM -----
def local_css():
    st.markdown("""
        <style>
            /* Fondo degradado */
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #f0f2f6;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            /* Título principal */
            .main-title {
                font-size: 3rem;
                font-weight: 800;
                color: #ffb347;
                text-align: center;
                margin-top: 1rem;
                text-shadow: 1px 1px 4px #00000088;
                font-family: 'Poppins', sans-serif;
            }
            /* Subtítulo */
            .subtitle {
                text-align: center;
                font-size: 1.3rem;
                margin-bottom: 2rem;
                color: #e0e0e0cc;
                font-weight: 500;
            }
            /* Cards para los productos */
            .card {
                background: #ffffff10;
                border-radius: 12px;
                padding: 20px 25px;
                margin: 10px 0;
                box-shadow: 0 8px 24px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, background 0.3s ease;
                cursor: pointer;
            }
            .card:hover {
                transform: scale(1.03);
                background: #ffb34733;
            }
            /* Tabla estilizada */
            .dataframe thead th {
                background-color: #764ba2;
                color: white;
            }
            .dataframe tbody tr:nth-child(even) {
                background-color: #e0e0e033;
            }
            /* Footer */
            footer {
                text-align: center;
                padding: 15px;
                font-size: 0.9rem;
                color: #ddd;
            }
        </style>
    """, unsafe_allow_html=True)

# ----- APP -----
def main():
    local_css()

    st.markdown('<h1 class="main-title">🔥 Productos en Supabase</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Conectando tu base de datos con estilo y performance</p>', unsafe_allow_html=True)

    data = fetch_data()

    if data:
        st.markdown(f"<h3 style='text-align:center; margin-bottom: 0.5rem;'>Total productos: {len(data)}</h3>", unsafe_allow_html=True)
        
        # Mostrar cada producto como una card
        for producto in data:
            st.markdown(
                f"""
                <div class="card">
                    <h4>🛒 <b>{producto.get('nombre', 'Sin nombre')}</b></h4>
                    <p>Descripción: {producto.get('unidad', 'N/A')}</p>
                    <p><b>Precio:</b> ${producto.get('usd', 'No definido')}</p>
                    <p><b>Categoría:</b> {producto.get('categoria', 'General')}</p>
                </div>
                """, unsafe_allow_html=True
            )
    else:
        st.warning("⚠️ No se pudieron obtener datos o no hay productos disponibles.")

    st.markdown("<footer>© 2025 Tu App con Supabase + Streamlit 💜</footer>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
