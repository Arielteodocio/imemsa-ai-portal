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
    # Sidebar con controles extra
    tools_sidebar_controls()

    top_brand()

    st.markdown("## 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar. También puedes navegar desde el menú lateral.")

    st.write("")

    # ---- Ajusta estos paths exactamente a tus archivos dentro de /pages ----
    modules = [
        {
            "title": "Transcripción",
            "emoji": "🎧",
            "desc": "Convierte audio en español a texto listo para copiar o exportar.",
            "page": "1_🎧_Transcripcion.py",
        },
        {
            "title": "Traducción",
            "emoji": "🌐",
            "desc": "Traduce texto Inglés ↔ Español con formato claro y profesional.",
            "page": "2_🌐_Traduccion.py",
        },
        {
            "title": "Minutas y acciones",
            "emoji": "📝",
            "desc": "Genera minuta estructurada y lista de acciones con responsables y fechas.",
            "page": "3_📝_Minutas_y_acciones.py",
        },
        {
            "title": "Documentos",
            "emoji": "📄",
            "desc": "Extrae información de PDFs/escaneos (OCR) y crea exportables.",
            "page": "4_📄_Documentos.py",
        },
        {
            "title": "Forecast y anomalías",
            "emoji": "📈",
            "desc": "Pronóstico + detección de desviaciones para análisis rápido.",
            "page": "5_📈_Forecast_y_Anomalias.py",
        },
        {
            "title": "NLP Operación",
            "emoji": "🧠",
            "desc": "Clasifica solicitudes internas, prioridad, área destino y datos clave.",
            "page": "6_🧠_NLP_Operacion.py",
        },
    ]

    # ---- Estilo cards (sutil y corporativo) ----
    st.markdown(
        """
        <style>
        .card {
            border: 1px solid rgba(255,255,255,0.10);
            border-radius: 16px;
            padding: 18px 18px 14px 18px;
            background: rgba(255,255,255,0.03);
            min-height: 170px;
        }
        .card h3 {
            margin: 0 0 6px 0;
            font-size: 1.25rem;
        }
        .card p {
            margin: 0;
            opacity: 0.85;
            line-height: 1.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- Grid 3 columnas ----
    cols = st.columns(3, gap="large")

    for i, m in enumerate(modules):
        with cols[i % 3]:
            with st.container():
                st.markdown(
                    f"""
                    <div class="card">
                      <h3>{m["emoji"]} {m["title"]}</h3>
                      <p>{m["desc"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c1, c2 = st.columns([1, 1])
                with c1:
                    if st.button("Abrir", key=f"open_{i}", use_container_width=True, type="primary"):
                        st.switch_page(m["page"])
                with c2:
                    st.button("Info", key=f"info_{i}", use_container_width=True)

                # Acción para "Info"
                if st.session_state.get(f"info_{i}", False):
                    st.toast(f'{m["title"]}: {m["desc"]}', icon="ℹ️")


