import os
import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
)

PASSWORD = "imemsa26"

# Rutas reales (exactas) según tu captura
PAGES = {
    "Transcripción": "pages/1_💡_Transcripcion.py",
    "Traducción": "pages/2_🌐_Traduccion.py",
    "Minutas y acciones": "pages/3_📝_Minutas_y_acciones.py",
    "Documentos": "pages/4_📄_Documentos.py",
    "Forecast y Anomalías": "pages/5_📈_Forecast_y_Anomalias.py",
    "NLP Operación": "pages/6_🧠_NLP_Operacion.py",
}

TOOLS = [
    {
        "title": "Transcripción",
        "icon": "🎧",
        "desc": "Convierte audio en español a texto listo para copiar o exportar.",
        "tags": ["Operación", "Administrativo"],
        "page_key": "Transcripción",
    },
    {
        "title": "Traducción",
        "icon": "🌐",
        "desc": "Traduce texto Inglés ↔ Español con formato claro y profesional.",
        "tags": ["Administrativo", "Comercial"],
        "page_key": "Traducción",
    },
    {
        "title": "Minutas y acciones",
        "icon": "📝",
        "desc": "Genera minuta estructurada y acciones con responsables y fechas.",
        "tags": ["Administrativo", "Dirección"],
        "page_key": "Minutas y acciones",
    },
    {
        "title": "Documentos",
        "icon": "📄",
        "desc": "Extrae información de documentos (facturas, PDFs, imágenes) y exporta resultados.",
        "tags": ["Finanzas", "Tesorería"],
        "page_key": "Documentos",
    },
    {
        "title": "Forecast y Anomalías",
        "icon": "📈",
        "desc": "Crea pronósticos y detecta anomalías a partir de históricos (series de tiempo).",
        "tags": ["Planeación", "Operación"],
        "page_key": "Forecast y Anomalías",
    },
    {
        "title": "NLP Operación",
        "icon": "🧠",
        "desc": "Clasifica solicitudes internas, estima prioridad y extrae datos clave.",
        "tags": ["Corporativo", "Operación"],
        "page_key": "NLP Operación",
    },
]


# =========================
# STATE
# =========================
if "auth_ok" not in st.session_state:
    st.session_state.auth_ok = False

if "route" not in st.session_state:
    # route: "home" | "tools" | "agents"
    st.session_state.route = "home"


# =========================
# UI HELPERS
# =========================
def sidebar_nav():
    """Sidebar minimal (sin lista automática de pages)."""
    with st.sidebar:
        st.markdown("### Navegación")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state.route = "home"
                st.rerun()
        with c2:
            if st.button("🧰 Herramientas", use_container_width=True):
                st.session_state.route = "tools"
                st.rerun()

        st.divider()
        if st.button("🚪 Cerrar sesión", use_container_width=True):
            st.session_state.auth_ok = False
            st.session_state.route = "home"
            st.rerun()


def go_to_page(page_path: str):
    """Navega a un módulo de /pages, validando que exista."""
    if not os.path.exists(page_path):
        st.error(f"No encuentro este archivo en el repo: `{page_path}`")
        st.stop()
    st.switch_page(page_path)


def tool_card(tool):
    """Tarjeta con botón Abrir (siempre visible)."""
    page_path = PAGES.get(tool["page_key"])
    with st.container(border=True):
        st.markdown(f"### {tool['icon']} {tool['title']}")
        st.write(tool["desc"])
        if tool.get("tags"):
            st.caption(" · ".join(tool["tags"]))

        # Botón siempre visible
        if st.button("Abrir", key=f"open_{tool['page_key']}", use_container_width=True):
            go_to_page(page_path)


# =========================
# LOGIN
# =========================
def login_screen():
    st.markdown("## 🔒 Acceso al Portal IMEMSA")
    st.caption("Ingresa la contraseña para continuar.")
    pwd = st.text_input("Contraseña", type="password")

    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("Entrar", use_container_width=True):
            if pwd == PASSWORD:
                st.session_state.auth_ok = True
                st.session_state.route = "home"  # SIEMPRE Home al entrar
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    with col2:
        st.info("Si no cuentas con acceso, contacta al administrador del portal.")


# =========================
# HOME (Herramientas vs Agentes)
# =========================
def home_screen():
    sidebar_nav()

    st.markdown("## 🤖 Portafolio de Herramientas de IA")
    st.write(
        "👋 **¡Bienvenido!** Este portal reúne herramientas de IA diseñadas para ayudarte a **trabajar más rápido**, "
        "reducir tareas repetitivas y mejorar la calidad de tus entregables.\n\n"
        "Selecciona una opción para comenzar:"
    )

    st.divider()

    colA, colB = st.columns(2, gap="large")

    with colA:
        with st.container(border=True):
            st.markdown("### 🧰 Herramientas de IA")
            st.write("Accede a Transcripción, Traducción, Minutas, Documentos, Forecast y NLP.")
            if st.button("Entrar a Herramientas", use_container_width=True):
                st.session_state.route = "tools"
                st.rerun()

    with colB:
        with st.container(border=True):
            st.markdown("### 🤖 Agentes de IA (próximamente)")
            st.write("Espacio reservado para agentes automatizados. Se habilitará en una siguiente fase.")
            st.button("Ver Agentes", use_container_width=True, disabled=True)


# =========================
# TOOLS DASHBOARD
# =========================
def tools_screen():
    sidebar_nav()

    st.markdown("## 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar.")

    # Grid de tarjetas
    cols = st.columns(3, gap="large")
    for i, tool in enumerate(TOOLS):
        with cols[i % 3]:
            tool_card(tool)


# =========================
# MAIN
# =========================
if not st.session_state.auth_ok:
    login_screen()
else:
    # Asegura rutas válidas
    if st.session_state.route not in {"home", "tools", "agents"}:
        st.session_state.route = "home"

    if st.session_state.route == "home":
        home_screen()
    elif st.session_state.route == "tools":
        tools_screen()
    else:
        # agents (placeholder)
        sidebar_nav()
        st.markdown("## 🤖 Agentes de IA (próximamente)")
        st.info("Esta sección se habilitará en una siguiente fase.")

