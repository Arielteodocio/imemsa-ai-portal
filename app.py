import streamlit as st

# =========================
# CONFIG (SIEMPRE PRIMERO)
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# AJUSTES
# =========================
PORTAL_PASSWORD = "imemsa26"   # <- cambia aquí si quieres
APP_TITLE = "🤖 Portafolio de Herramientas de IA"

TOOLS = [
    {
        "title": "🎧 Transcripción",
        "desc": "Convierte audio a texto.",
        "page": "pages/1_transcripcion.py",
    },
    {
        "title": "🌐 Traducción",
        "desc": "Traduce texto Inglés ↔ Español.",
        "page": "pages/2_traduccion.py",
    },
    {
        "title": "📝 Minutas y acciones",
        "desc": "Minutas estructuradas y lista de acciones.",
        "page": "pages/3_minutas_y_acciones.py",
    },
    {
        "title": "📄 Documentos",
        "desc": "Lectura/extracción de PDFs e imágenes.",
        "page": "pages/4_documentos.py",
    },
    {
        "title": "📈 Forecast y anomalías",
        "desc": "Pronósticos y detección de anomalías.",
        "page": "pages/5_forecast_y_anomalias.py",
    },
    {
        "title": "🧠 NLP Operación",
        "desc": "Clasificación y extracción de información.",
        "page": "pages/6_nlp_operacion.py",
    },
]

# =========================
# CSS (cards pro)
# =========================
st.markdown(
    """
<style>
/* Oculta el nav nativo de multipage (evita confusión) */
[data-testid="stSidebarNav"] { display: none !important; }

.card {
  border: 1px solid rgba(49,51,63,0.15);
  border-radius: 18px;
  padding: 16px 16px 12px 16px;
  background: rgba(255,255,255,0.6);
}
.card h3 { margin: 0 0 6px 0; font-size: 1.05rem; }
.card p { margin: 0 0 12px 0; opacity: 0.85; }
.smallcap { opacity: 0.75; font-size: 0.9rem; }
</style>
""",
    unsafe_allow_html=True,
)

# =========================
# SESSION STATE
# =========================
st.session_state.setdefault("auth", False)
st.session_state.setdefault("view", "login")  # login | home | tools

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("## Menú")

    if st.session_state["auth"]:
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🏠 Home", use_container_width=True):
                st.session_state["view"] = "home"
                st.rerun()
        with c2:
            if st.button("🧰 Herr.", use_container_width=True):
                st.session_state["view"] = "tools"
                st.rerun()

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.clear()
            st.rerun()
    else:
        st.caption("Inicia sesión para continuar.")

# =========================
# VIEWS
# =========================
def render_login():
    st.markdown(f"# {APP_TITLE}")
    st.caption("Acceso al portal")

    col1, col2, col3 = st.columns([1.1, 1.2, 1.1])
    with col2:
        with st.form("login_form", clear_on_submit=False):
            st.markdown("### 🔒 Login")
            pw = st.text_input("Contraseña", type="password", placeholder="••••••••", key="pw_input")
            submit = st.form_submit_button("Entrar", use_container_width=True)

        if submit:
            if (pw or "").strip() == PORTAL_PASSWORD:
                st.session_state["auth"] = True
                st.session_state["view"] = "home"
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")


def render_home():
    st.markdown(f"# {APP_TITLE}")
    st.caption("Selecciona una opción")

    colA, colB = st.columns(2)
    with colA:
        st.markdown(
            """
<div class="card">
  <h3>🧰 Herramientas de IA</h3>
  <p>Transcripción, traducción, minutas, documentos y más.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("Abrir Herramientas", use_container_width=True):
            st.session_state["view"] = "tools"
            st.rerun()

    with colB:
        st.markdown(
            """
<div class="card">
  <h3>🧑‍💻 Agentes</h3>
  <p class="smallcap">Deshabilitado por el momento.</p>
</div>
""",
            unsafe_allow_html=True,
        )
        st.button("Agentes (próximamente)", disabled=True, use_container_width=True)


def render_tools():
    st.markdown("# 🧰 Herramientas de IA")
    st.caption("Da click y te manda directo a la página de la herramienta.")

    # Grid 3 columnas
    cols = st.columns(3)
    for i, t in enumerate(TOOLS):
        with cols[i % 3]:
            st.markdown(
                f"""
<div class="card">
  <h3>{t["title"]}</h3>
  <p>{t["desc"]}</p>
</div>
""",
                unsafe_allow_html=True,
            )

            # Navegación robusta: page_link (sin switch_page)
            if hasattr(st, "page_link"):
                st.page_link(t["page"], label="Abrir", icon="➡️", use_container_width=True)
            else:
                # Fallback si tu Streamlit es muy viejo
                if st.button("➡️ Abrir", key=f"open_{i}", use_container_width=True):
                    st.switch_page(t["page"])

    st.divider()
    if st.button("⬅️ Volver a Home", use_container_width=True):
        st.session_state["view"] = "home"
        st.rerun()


# =========================
# ROUTER
# =========================
if not st.session_state["auth"]:
    st.session_state["view"] = "login"
    render_login()
else:
    # si vienes ya logueado, default a home
    if st.session_state["view"] == "login":
        st.session_state["view"] = "home"

    if st.session_state["view"] == "home":
        render_home()
    else:
        render_tools()
