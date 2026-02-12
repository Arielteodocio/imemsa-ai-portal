import os
import runpy
import traceback
import streamlit as st

# =========================
# CONFIG (DEBE IR PRIMERO)
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

PORTAL_PASSWORD = "imemsa26"

# Tus herramientas (NO navega a páginas: ejecuta el script dentro del mismo app.py)
TOOLS = {
    "🎧 Transcripción": {
        "script": "pages/1_🎧_Transcripcion.py",
        "desc": "Convierte audio en español a texto listo para copiar o exportar.",
        "tags": ["Operación", "Administrativo"],
    },
    "🌐 Traducción": {
        "script": "pages/2_🌐_Traduccion.py",
        "desc": "Traduce texto Inglés ↔ Español con formato claro y profesional.",
        "tags": ["Administrativo", "Comercial"],
    },
    "📝 Minutas y acciones": {
        "script": "pages/3_📝_Minutas_y_acciones.py",
        "desc": "Genera minuta estructurada y acciones con responsables y fechas.",
        "tags": ["Administrativo", "Dirección"],
    },
    "📄 Documentos": {
        "script": "pages/4_📄_Documentos.py",
        "desc": "Lee PDFs/imagenes, extrae información estructurada.",
        "tags": ["Tesorería", "Administrativo"],
    },
    "📈 Forecast y anomalías": {
        "script": "pages/5_📈_Forecast_y_Anomalias.py",
        "desc": "Pronostica series de tiempo y detecta anomalías.",
        "tags": ["Planeación", "Dirección"],
    },
    "🧠 NLP Operación": {
        "script": "pages/6_🧠_NLP_Operacion.py",
        "desc": "Clasifica solicitudes internas y extrae datos clave.",
        "tags": ["Tesorería", "Comercial"],
    },
}


# =========================
# HELPERS
# =========================
def _init_session():
    st.session_state.setdefault("auth", False)
    st.session_state.setdefault("view", "login")        # login | home | tools
    st.session_state.setdefault("tool", list(TOOLS.keys())[0])
    st.session_state.setdefault("tool_filter", "")


def hide_native_pages_sidebar():
    # Oculta el selector nativo de multipage (si existe carpeta pages/)
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        header, footer { visibility: hidden; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def logout():
    # Limpia lo esencial para que no quede nada raro en sesión
    for k in ["auth", "view", "tool", "tool_filter"]:
        if k in st.session_state:
            del st.session_state[k]
    st.rerun()


def _run_tool_script(script_path: str):
    """
    Ejecuta el archivo de herramienta dentro del mismo app.
    Ventaja: no depende de st.switch_page(), ni de navegación multipage.
    """
    if not os.path.exists(script_path):
        st.error(f"❌ No encuentro el archivo: `{script_path}`")
        st.info("Revisa que exista la carpeta `pages/` y que el nombre del archivo sea idéntico (incluyendo emojis).")
        return

    try:
        # OJO: si el script tiene st.set_page_config(), hay que quitarlo de ese script,
        # porque Streamlit solo permite set_page_config una vez (en el main).
        runpy.run_path(script_path, run_name="__main__")
    except Exception:
        st.error("⚠️ La herramienta lanzó un error. Te dejo el detalle para debug:")
        st.code(traceback.format_exc())


# =========================
# VIEWS
# =========================
def render_login():
    hide_native_pages_sidebar()

    col1, col2, col3 = st.columns([1.2, 2.2, 1.2])
    with col2:
        st.markdown("## 🔒 Acceso al Portal IMEMSA")
        st.caption("Ingresa la contraseña para continuar.")

        pw = st.text_input("Contraseña", type="password", placeholder="••••••••", key="pw_input")
        if st.button("Entrar", use_container_width=True):
            if (pw or "").strip() == PORTAL_PASSWORD:
                st.session_state.auth = True
                st.session_state.view = "home"
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")


def render_home():
    hide_native_pages_sidebar()
    render_sidebar(show_tools=False)

    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.write(
        "Desde la barra izquierda puedes abrir una herramienta. "
        "Esta versión ya **no navega entre páginas**, así evitamos el problema de botones sin acción."
    )
    st.divider()
    if st.button("🧰 Ir a Herramientas", use_container_width=True):
        st.session_state.view = "tools"
        st.rerun()


def render_sidebar(show_tools: bool = True):
    with st.sidebar:
        st.markdown("## Menú")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.view = "home"
                st.rerun()
        with c2:
            if st.button("🧰 Herr.", use_container_width=True):
                st.session_state.view = "tools"
                st.rerun()

        st.divider()

        if show_tools:
            st.markdown("### Herramientas")
            st.session_state.tool_filter = st.text_input(
                "Buscar", value=st.session_state.tool_filter, placeholder="Ej. traducción"
            )

            # Filtrado simple
            filtro = (st.session_state.tool_filter or "").strip().lower()
            opciones = list(TOOLS.keys())
            if filtro:
                opciones = [k for k in opciones if filtro in k.lower() or filtro in TOOLS[k]["desc"].lower()]

            if not opciones:
                st.warning("No hay herramientas que coincidan con tu búsqueda.")
            else:
                st.session_state.tool = st.radio(
                    "Selecciona una herramienta",
                    options=opciones,
                    index=opciones.index(st.session_state.tool) if st.session_state.tool in opciones else 0,
                    label_visibility="collapsed",
                )

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            logout()


def render_tools():
    hide_native_pages_sidebar()
    render_sidebar(show_tools=True)

    tool_name = st.session_state.tool
    meta = TOOLS[tool_name]

    # Header “pro”
    st.markdown(f"# {tool_name}")
    st.caption(meta["desc"])
    st.write("**Áreas:** " + " · ".join(meta["tags"]))
    st.divider()

    # Ejecuta el script de la herramienta dentro del mismo app
    _run_tool_script(meta["script"])


# =========================
# APP ROUTER
# =========================
_init_session()

if not st.session_state.auth:
    st.session_state.view = "login"
    render_login()
else:
    if st.session_state.view == "login":
        st.session_state.view = "home"

    if st.session_state.view == "home":
        render_home()
    else:
        render_tools()

