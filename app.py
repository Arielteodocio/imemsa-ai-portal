import streamlit as st
from utils_auth import require_password
from utils_ui import hide_streamlit_sidebar_pages

hide_streamlit_sidebar_pages()

# ----------------------------
# Config general
# ----------------------------
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
)

# ----------------------------
# Auth (password gate)
# ----------------------------
require_password()

# ----------------------------
# Post-login normalization
# ----------------------------
# Si acaba de loguearse: SIEMPRE aterriza en HOME
if st.session_state.get("just_logged_in", False):
    st.session_state.section = "home"
    st.session_state.just_logged_in = False

# Normaliza section
if "section" not in st.session_state or st.session_state.section not in ["home", "tools", "agents"]:
    st.session_state.section = "home"


# ----------------------------
# UI helpers
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
    """
    Sidebar para cuando estamos en Tools:
    - Tablero (tools home)
    - Inicio (home)
    - Cerrar sesión
    """
    with st.sidebar:
        st.markdown("### Navegación")
        if st.button("🧰 Tablero", use_container_width=True):
            st.session_state.section = "tools"
            st.rerun()

        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.section = "home"
            st.rerun()

        st.divider()

        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.section = "home"
            st.rerun()


def pill(text: str):
    st.markdown(
        f"""
        <span style="
          display:inline-block;
          padding: 4px 10px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.18);
          background: rgba(255,255,255,0.06);
          font-size: 0.78rem;
          opacity: 0.95;
          margin-right: 6px;
          margin-bottom: 6px;
        ">{text}</span>
        """,
        unsafe_allow_html=True,
    )


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

        Te invitamos a probar los módulos disponibles.  
        Si tienes sugerencias o detectas oportunidades de mejora, compártelas para seguir evolucionando el portafolio.
        """
    )

    st.write("")
    st.write("")

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown("### 🧰 Herramientas de IA")
        st.caption("Accede a los módulos disponibles para uso diario.")
        if st.button("Entrar a Herramientas", type="primary", use_container_width=True):
            st.session_state.section = "tools"
            st.rerun()

    with c2:
        st.markdown("### 🧠 Agentes de IA")
        st.caption("Automatizaciones y asistentes inteligentes (próximamente).")
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


def tools_dashboard():
    tools_sidebar_controls()

    top_brand()

    st.markdown("## 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar. También puedes navegar desde el menú lateral.")
    st.write("")

    # ---- Cards style ----
    st.markdown(
        """
        <style>
        .card {
            border: 1px solid rgba(255,255,255,0.12);
            border-radius: 18px;
            padding: 18px 18px 14px 18px;
            background: rgba(255,255,255,0.04);
            min-height: 190px;
        }
        .card h3 {
            margin: 0 0 6px 0;
            font-size: 1.25rem;
        }
        .card p {
            margin: 0;
            opacity: 0.86;
            line-height: 1.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Ajusta estos paths EXACTOS a tus archivos en /pages ----
    modules = [
        {
            "title": "Transcripción",
            "emoji": "🎧",
            "desc": "Convierte audio en español a texto listo para copiar o exportar.",
            "chips": ["Operación", "Administrativo"],
            "page": "pages/1_🎧_Transcripcion.py",
        },
        {
            "title": "Traducción",
            "emoji": "🌐",
            "desc": "Traduce texto Inglés ↔ Español con formato claro y profesional.",
            "chips": ["Administrativo", "Comercial"],
            "page": "pages/2_🌐_Traduccion.py",
        },
        {
            "title": "Minutas y acciones",
            "emoji": "📝",
            "desc": "Genera minuta estructurada y acciones con responsables y fechas.",
            "chips": ["Administrativo", "Dirección"],
            "page": "pages/3_📝_Minutas_y_acciones.py",
        },
        {
            "title": "Documentos",
            "emoji": "📄",
            "desc": "Extrae información de PDFs/escaneos (OCR) y crea exportables.",
            "chips": ["Finanzas", "Contabilidad", "Administrativo"],
            "page": "pages/4_📄_Documentos.py",
        },
        {
            "title": "Forecast y anomalías",
            "emoji": "📈",
            "desc": "Pronóstico + detección de desviaciones para análisis rápido.",
            "chips": ["Finanzas", "Comercial", "Dirección"],
            "page": "pages/5_📈_Forecast_y_Anomalias.py",
        },
        {
            "title": "NLP Corporativo",
            "emoji": "🧠",
            "desc": "Clasifica solicitudes internas, prioridad, área destino y datos clave.",
            "chips": ["Tesorería", "Comercial", "RRHH"],
            "page": "pages/6_🧠_NLP_Operacion.py",
        },
    ]

    # ---- Grid 3 columnas ----
    cols = st.columns(3, gap="large")

    for i, m in enumerate(modules):
        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="card">
                  <h3>{m["emoji"]} {m["title"]}</h3>
                  <p>{m["desc"]}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Chips debajo de la card
            st.write("")
            for ch in m.get("chips", []):
                pill(ch)

            st.write("")
            if st.button("Abrir", key=f"open_{i}", type="primary", use_container_width=True):
                st.switch_page(m["page"])


# ----------------------------
# Router
# ----------------------------
if st.session_state.section == "home":
    home_screen()
    st.stop()

if st.session_state.section == "agents":
    agents_screen()
    st.stop()

# Tools
tools_dashboard()

