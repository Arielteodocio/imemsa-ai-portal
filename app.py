import os
import re
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
PAGES_DIR = "pages"

# =========================
# CSS
# =========================
st.markdown(
    """
<style>
/* Oculta el nav nativo de multipage (evita confusión) */
[data-testid="stSidebarNav"] { display: none !important; }
header, footer { visibility: hidden; }

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
# Helpers
# =========================
def _sort_key(fn: str):
    """Ordena por prefijo numérico si existe: 1_xxx.py"""
    stem = fn[:-3]
    m = re.match(r"^(\d+)[_\- ].*", stem)
    if m:
        return (0, int(m.group(1)), fn.lower())
    return (1, 9999, fn.lower())


def _title_from_filename(fn: str) -> str:
    """Convierte nombre archivo a título bonito."""
    name = fn[:-3].lower()

    if "transcrip" in name:
        return "🎧 Transcripción"
    if "tradu" in name:
        return "🌐 Traducción"
    if "minut" in name or "accion" in name:
        return "📝 Minutas y acciones"
    if "doc" in name or "pdf" in name:
        return "📄 Documentos"
    if "forecast" in name or "anom" in name:
        return "📈 Forecast y anomalías"
    if "nlp" in name or "oper" in name:
        return "🧠 NLP Operación"

    # fallback: limpia prefijo numérico
    stem = fn[:-3]
    stem = re.sub(r"^\d+[_\- ]*", "", stem)
    stem = stem.replace("_", " ").replace("-", " ").strip()
    return stem[:1].upper() + stem[1:]


def discover_pages():
    """Auto-detecta archivos .py dentro de /pages para evitar PageNotFoundError."""
    if not os.path.isdir(PAGES_DIR):
        return []

    files = [f for f in os.listdir(PAGES_DIR) if f.endswith(".py")]
    files = sorted(files, key=_sort_key)

    tools = []
    for f in files:
        tools.append(
            {
                "title": _title_from_filename(f),
                "desc": "Abrir herramienta.",
                "page": f"{PAGES_DIR}/{f}",
            }
        )
    return tools


TOOLS = discover_pages()


def do_logout():
    st.session_state.clear()
    st.rerun()


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
            do_logout()
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

    if not TOOLS:
        st.error("No encontré páginas en la carpeta `pages/`.")
        st.info("Verifica que exista la carpeta `pages` y que contenga tus archivos .py.")
        st.stop()

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

            # ✅ Navegación por click (no valida la página al renderizar, evita PageNotFoundError)
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
    if st.session_state["view"] == "login":
        st.session_state["view"] = "home"

    if st.session_state["view"] == "home":
        render_home()
    else:
        render_tools()
