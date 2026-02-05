import streamlit as st

from utils_ui import hide_streamlit_sidebar_pages
import os

# =========================
# Config
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
)

hide_streamlit_sidebar_pages()


APP_PASSWORD = st.secrets["APP_PASSWORD"]


# =========================
# Helpers
# =========================
def ensure_session_defaults():
    if "auth_ok" not in st.session_state:
        st.session_state.auth_ok = False
    if "route" not in st.session_state:
        # "home" = tablero / "inicio" = landing opcional
        st.session_state.route = "home"


def logout():
    st.session_state.auth_ok = False
    st.session_state.route = "home"
    st.rerun()


def sidebar_nav():
    """Sidebar único (sin lista automática de páginas)."""
    with st.sidebar:
        st.markdown("### Navegación")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧰 Tablero", use_container_width=True):
                st.session_state.route = "home"
                st.rerun()
        with c2:
            if st.button("🏠 Inicio", use_container_width=True):
                st.session_state.route = "home"
                st.rerun()

        st.markdown("---")
        st.button("Cerrar sesión", on_click=logout, use_container_width=True)


def require_auth():
    ensure_session_defaults()
    if st.session_state.auth_ok:
        return True

    # Pantalla de acceso
    st.markdown("## 🔒 Acceso al Portal IMEMSA")
    st.caption("Ingresa la contraseña para continuar.")

    col1, col2 = st.columns([2, 3])
    with col1:
        pwd = st.text_input("Contraseña", type="password")
        if st.button("Entrar"):
            if pwd == APP_PASSWORD:
                st.session_state.auth_ok = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    with col2:
        st.info("Si no cuentas con acceso, contacta al administrador del portal.")

    st.stop()




def card(title, icon, desc, tags, page_path):
    with st.container(border=True):
        st.markdown(f"### {icon} {title}")
        st.write(desc)
        if tags:
            st.caption(" · ".join(tags))

        # Validación del archivo (para que no “parezca que no hace nada”)
        if not os.path.exists(page_path):
            st.warning(f"No encuentro el archivo: `{page_path}`")
            st.caption("Revisa el nombre exacto en la carpeta /pages")
            return



# =========================
# App
# =========================
ensure_session_defaults()
require_auth()
sidebar_nav()

# --- Header principal
col_logo, col_title = st.columns([1, 5], vertical_alignment="center")
with col_logo:
    try:
        st.image("imemsa_logo.png", width=180)
    except Exception:
        pass

with col_title:
    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.write(
        "👋 **¡Bienvenido!** Este portal reúne herramientas de IA diseñadas para ayudarte a **trabajar más rápido**, "
        "**reducir tareas repetitivas** y **mejorar la calidad de tus entregables**.\n\n"
        "Explora las herramientas del tablero y elige la que necesites."
    )

st.markdown("---")

st.markdown("## 🧰 Herramientas de IA")
st.caption("Selecciona una herramienta para comenzar. También puedes volver aquí desde el menú lateral.")

# --- GRID de tarjetas
# Ajusta los paths según tus nombres exactos en /pages
# Tip: en Streamlit, los paths se escriben así: "pages/1_Transcripcion.py"
c1, c2, c3 = st.columns(3)
with c1:
    card(
        title="Transcripción",
        icon="🎧",
        desc="Convierte audio en español a texto listo para copiar o exportar.",
        tags=["Operación", "Administrativo"],
        page_path="pages/1_🎧_Transcripcion.py",
    )

with c2:
    card(
        title="Traducción",
        icon="🌐",
        desc="Traduce texto Inglés ↔ Español con formato claro y profesional.",
        tags=["Administrativo", "Comercial"],
        page_path="pages/2_🌐_Traduccion.py",
    )

with c3:
    card(
        title="Minutas y acciones",
        icon="📝",
        desc="Genera minuta estructurada y lista de acciones con responsables y fechas.",
        tags=["Administrativo", "Dirección"],
        page_path="pages/3_📝_Minutas_y_acciones.py",
    )

c4, c5, c6 = st.columns(3)
with c4:
    card(
        title="Documentos",
        icon="📄",
        desc="Extrae información clave de documentos (PDF/imagen) para revisión y exportables.",
        tags=["Finanzas", "Tesorería"],
        page_path="pages/4_📄_Documentos.py",
    )

with c5:
    card(
        title="Forecast y anomalías",
        icon="📈",
        desc="Genera pronóstico y detecta anomalías en series de tiempo a partir de un archivo.",
        tags=["Planeación", "Dirección"],
        page_path="pages/5_📈_Forecast_y_Anomalias.py",
    )

with c6:
    card(
        title="NLP Operación",
        icon="🧠",
        desc="Clasifica solicitudes (correo/ticket), estima prioridad y extrae datos clave (ej. Factura + OC).",
        tags=["Tesorería", "Comercial"],
        page_path="pages/6_🧠_NLP_Operacion.py",
    )

st.markdown("---")
st.caption("IMEMSA · Portal interno · v1")

