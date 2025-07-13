import streamlit as st

# CONFIGURACIÓN GENERAL
st.set_page_config(page_title="App Agrícola", layout="wide")

# ===== CSS PERSONALIZADO =====
def inject_css():
    st.markdown("""
        <style>
            /* Fondo con imagen */
            .stApp {
                background-image: url("https://wallpapers.com/images/hd/agriculture-background-zb06jbplfqoilptw.jpg");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
            }

            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

            html, body, [class*="css"] {
                font-family: 'Roboto', sans-serif;
            }

            .main-title {
            text-align: center;
            font-size: 3.4rem;
            font-weight: 800;
            color: rgba(240, 240, 0, 1);
            background: rgba(0, 0, 30, 0.3);
            padding: 1rem 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
            text-shadow: 2px 2px 8px rgba(0,0,0,0.6);
            backdrop-filter: blur(1px);
            margin-top: 2rem;
            margin-bottom: 3rem;
            transition: all 0.3s ease-in-out;
        }

        


            .card-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 2.5rem 2rem;
                width: 100%;
                padding: 0 4rem 3rem;
            }

            .card {
                background: linear-gradient(145deg, rgba(90, 120, 90, 0.8), rgba(40, 60, 50, 0.25));
                border-radius: 18px;
                padding: 28px;
                box-shadow:
                    0 1px 3px rgba(0,0,0,0.25),
                    0 4px 12px rgba(0,0,0,0.3),
                    inset 0 0 1px rgba(255,255,255,0.05);
                transition: all 0.35s ease-in-out;
                color: #e2f1ea;
                cursor: pointer;
                text-decoration: none;
                backdrop-filter: blur(4px);
                position: relative;
                overflow: hidden;
                margin-bottom: 4.5rem;
                margin-left: 4rem;
                margin-right: 4rem;
            }

            .card::before {
                content: "";
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: radial-gradient(circle at top left, rgba(255,255,255,0.1), transparent 70%);
                z-index: 0;
                opacity: 0.2;
                pointer-events: none;
            }

            .card:hover {
                transform: scale(1.05);
                box-shadow:
                    0 6px 25px rgba(0, 100, 0, 0.3),
                    0 10px 40px rgba(0,0,0,0.35);
                background: linear-gradient(145deg, rgba(100, 130, 100, 0.8), rgba(40, 70, 50, 0.25));
            }

            .card-icon, .card-title, .card-desc {
                position: relative;
                z-index: 1;
                text-align: center;
            }

            .card-icon {
                font-size: 2.5rem;
                margin-bottom: 0.6rem;
            }

            .card-title {
                font-size: 1.4rem;
                font-weight: bold;
                margin-bottom: 0.5rem;
            }

            .card-desc {
                font-size: 1rem;
                opacity: 0.9;
            }

            footer {
                text-align: center;
                padding: 2rem;
                color: #fff;
                text-shadow: 1px 1px 2px #000;
            }
        </style>
    """, unsafe_allow_html=True)






# ===== FUNCIÓN PARA TARJETAS =====
def render_card(title, description, icon, route):
    # Detectar si el ícono es una URL de imagen
    if isinstance(icon, str) and icon.startswith("http"):
        icon_html = f'<img src="{icon}" alt="icon" style="width:60px; height:60px; margin-bottom:10px;" />'
    else:
        icon_html = f"{icon}"

    card_html = f"""
        <a href="/{route}" target="_self" style="text-decoration: none;">
            <div class="card">
                <div class="card-icon">{icon_html}</div>
                <div class="card-title">{title}</div>
                <div class="card-desc">{description}</div>
            </div>
        </a>
    """
    st.markdown(card_html, unsafe_allow_html=True)


# ===== MAIN PAGE =====
def render_home():
    inject_css()
    st.markdown('<h1 class="main-title"> Plataforma Agrícola Inteligente</h1>', unsafe_allow_html=True)

    st.markdown('<div class="card-grid">', unsafe_allow_html=True)

    

    render_card(
        title="Registrar Nuevos Productos",
        description="Añadir nuevos productos agrícolas, con su precio y fecha de registro.",
        icon="https://cdn-icons-png.flaticon.com/512/748/748916.png",
        route="registro"
    )

    render_card(
        title="Análisis de Precios Históricos",
        description="Consulta los precios históricos de productos agrícolas y compara su evolución.",
        icon="https://cdn-icons-png.flaticon.com/512/6012/6012178.png",
        route="analisis"
    )

    render_card(
        title="Consultar Logs y Actividades",
        description="Ver el historial de actividades y eventos del sistema.",
        icon="https://cdn-icons-png.flaticon.com/512/4303/4303996.png",
        route="logs"
    )


    render_card(
            title="Simular concurrencia",
            description="Simula la interaccion de usuarios con el sistema al hacer algunos inserts o updates",
            icon="https://cdn-icons-png.flaticon.com/512/3598/3598209.png",
            route="concurrencia"
        )


    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<footer>© 2025 Plataforma Agrícola · Todos los derechos reservados</footer>', unsafe_allow_html=True)

# ===== ENRUTAMIENTO BÁSICO =====
query_params = st.query_params
page = query_params.get("page", ["home"])[0]

if page == "home":
    render_home()
elif page == "gestion":
    st.title("📦 Gestión de Productos")
    st.write("Aquí irá la interfaz para consultar y gestionar productos.")
    if st.button("🔙 Volver al inicio"):
        st.experimental_set_query_params(page="home")
elif page == "registro":
    st.title("📝 Registro de Nuevos Productos")
    st.write("Aquí irá el formulario para registrar nuevos productos.")
    if st.button("🔙 Volver al inicio"):
        st.experimental_set_query_params(page="home")
elif page == "analisis":
    st.title("📈 Análisis de Precios Históricos")
    st.write("Aquí se mostrarán gráficos comparativos y visualizaciones.")
    if st.button("🔙 Volver al inicio"):
        st.experimental_set_query_params(page="home")
elif page == "logs":
    st.title("📋 Historial de Logs y Actividades")
    st.write("Aquí se mostrará el historial de acciones del sistema.")
    if st.button("🔙 Volver al inicio"):
        st.experimental_set_query_params(page="home")
