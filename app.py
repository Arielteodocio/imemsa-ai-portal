import streamlit as st
from utils_auth import require_password


# ----------------------------
# Config general
# ----------------------------
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
)


# ----------------------------
# Auth
# ----------------------------
require_password()


# ----------------------------
# Estado de navegación
# home | tools | agents
# ----------------------------
if "section" not in st.session_state:
    st.session_state.section = "home"


# ----------------------------
# Helpers UI
# ----------------------------
def hide_sidebar():
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] {display: none;}
          [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def top_brand():
    # Logo (si existe)
    try:
        st.image("imemsa_logo.png", width=180)
    except Exception:
        st.markdown("### IMEMSA")


def tools_sidebar_controls():
    # Controles extra cuando ya estamos en Tools
    with st.sidebar:
        st.divider()
        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.section = "home"
            st.rerun()

        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.section = "home"
            st.rerun()


# ----------------------------
# Screens
# ----------------------------
def home_screen():
    hide_sidebar()

    top_brand()

    st.markdown("## 🤖 Portafolio de Herramientas de IA")
    st.markdown(
        """
        👋 **¡Bienvenido!**  
        Este portal reúne herramientas de Inteligencia Artificial diseñadas para ayudarte a **trabajar más rápido**,  
        **reducir tareas repetitivas** y **mejorar la calidad** de tus entregables.

        Te invitamos a probar las herramientas disponibles.  
        Si tienes sugerencias o detectas oportunidades de mejora, compártelas para seguir evolucionando el portafolio.
        """
    )

    st.write("")
    st.write("")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### 🧰 Herramientas de IA")
        st.caption("Accede a los módulos disponibles (Transcripción, Traducción, Minutas, Documentos, Forecast, NLP).")

        # Imagen opcional: si la tienes en el repo (si no existe, no truena)
        try:
            st.image("assets/herramientas.png", use_container_width=True)
        except Exception:
            pass

        if st.button("Entrar a Herramientas", type="primary", use_container_width=True):
            st.session_state.section = "tools"
            st.rerun()

    with c2:
        st.markdown("### 🧠 Agentes de IA")
        st.caption("Sección reservada para agentes/automatizaciones inteligentes (próximamente).")

        try:
            st.image("assets/agentes.png", use_container_width=True)
        except Exception:
            pass

        if st.button("Ver Agentes (próximamente)", use_container_width=True):
            st.session_state.section = "agents"
            st.rerun()


def agents_screen():
    hide_sidebar()

    top_brand()
    st.markdown("## 🧠 Agentes de IA")

    st.info(
        "Esta sección se habilitará en una fase futura. "
        "Por ahora, utiliza **Herramientas de IA** para acceder a los módulos."
    )

    st.write("")
    if st.button("⬅️ Volver al inicio", use_container_width=True):
        st.session_state.section = "home"
        st.rerun()


def tools_landing_screen():
    # Aquí ya se muestran tus páginas en el sidebar
    tools_sidebar_controls()

    top_brand()
    st.markdown("## 🧰 Herramientas de IA")
    st.caption("Usa el menú lateral para elegir un módulo.")

    st.write("")
    st.info("Tip: Si quieres volver al Home, usa el botón **🏠 Inicio** en el menú lateral.")


# ----------------------------
# Router
# ----------------------------
if st.session_state.section == "home":
    home_screen()
    st.stop()

if st.session_state.section == "agents":
    agents_screen()
    st.stop()

# Si no es home/agents, caemos en tools
tools_landing_screen()

