import os
import runpy
import time
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

# =========================
# LOOP GUARD (ANTI-BUCLES)
# Evita el error del navegador:
# "history.pushState() more than 100 times per 10 seconds"
# =========================
def loop_guard(max_runs: int = 40, window_sec: int = 10):
    now = time.time()
    t0 = st.session_state.get("_lg_t0", now)
    n = st.session_state.get("_lg_n", 0)

    if now - t0 > window_sec:
        st.session_state["_lg_t0"] = now
        st.session_state["_lg_n"] = 1
        return

    n += 1
    st.session_state["_lg_n"] = n
    if n > max_runs:
        st.error("⚠️ Detecté un ciclo de recarga (rerun) demasiado rápido y lo detuve para proteger el navegador.")
        st.info(
            "Esto casi siempre pasa cuando **alguna herramienta** (archivo dentro de `pages/`) "
            "llama `st.rerun()`, `st.switch_page()` o cambia query params en **cada ejecución**."
        )
        with st.expander("Ver detalle técnico"):
            st.code(
                "Solución recomendada:\n"
                "1) Elimina cualquier `st.set_page_config()` dentro de páginas.\n"
                "2) Quita/ajusta guards que hagan `st.switch_page()` si no detectan login.\n"
                "3) Evita `st.experimental_set_query_params()` en loops.\n"
            )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🧹 Limpiar sesión y reiniciar", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        with c2:
            if st.button("🏠 Volver a Home", use_container_width=True):
                st.session_state["view"] = "home"
                st.rerun()

        st.stop()

loop_guard()


# =========================
# AUTH
# =========================
PORTAL_PASSWORD = "imemsa26"


# =========================
# AUTO-DETECCIÓN DE HERRAMIENTAS
# Lee todos los .py dentro de /pages y construye el menú solo con esos.
# =========================
def discover_tools(pages_dir: str = "pages"):
    tools = {}
    if not os.path.isdir(pages_dir):
        return tools

    files = [f for f in os.listdir(pages_dir) if f.endswith(".py")]
    # Ordena por prefijo numérico si existe (ej. 1_xxx.py)
    def _sort_key(fn: str):
        try:
            prefix = fn.split("_", 1)[0]
            return (0, int(prefix), fn)
        except Exception:
            return (1, 9999, fn)

    for fn in sorted(files, key=_sort_key):
        # Título bonito desde el nombre del archivo (sin .py)
        stem = fn[:-3]
        title = stem
        # quita prefijo "N_" si existe
        parts = stem.split("_", 1)
        if len(parts) == 2 and parts[0].isdigit():
            title = parts[1].replace("_", " ")
        else:
            title = stem.replace("_", " ")

        tools[title] = {
            "script": os.path.join(pages_dir, fn),
            "desc": "Herramienta disponible.",
            "tags": [],
        }
    return tools


TOOLS = discover_tools("pages")

# Si quieres fijar descripciones/tags, puedes sobrescribir aquí por nombre (opcional)
# EJEMPLO:
# TOOLS["🎧 Transcripcion"] = {**TOOLS["🎧 Transcripcion"], "desc": "...", "tags": ["Operación"]}


# =========================
# HELPERS
# =========================
def _init_session():
    st.session_state.setdefault("auth", False)
    st.session_state.setdefault("view", "login")  # login | home | tools
    st.session_state.setdefault("tool_filter", "")
    # selecciona primera herramienta disponible
    if "tool" not in st.session_state:
        st.session_state["tool"] = next(iter(TOOLS.keys()), None)


def hide_native_pages_sidebar():
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
    st.session_state.clear()
    st.rerun()


def _safe_switch_page(page_like):
    """
    Si alguna herramienta intenta hacer st.switch_page(), lo convertimos
    en “cambiar herramienta” sin tocar el historial del navegador.
    """
    # intenta mapear por ruta
    page_str = str(page_like)
    for name, meta in TOOLS.items():
        if meta["script"] in page_str or os.path.basename(meta["script"]) in page_str:
            st.session_state["view"] = "tools"
            st.session_state["tool"] = name
            st.rerun()
    # si no mapea, solo vuelve a home
    st.session_state["view"] = "home"
    st.rerun()


def _run_tool_script(script_path: str):
    """
    Ejecuta el archivo de herramienta dentro del mismo app.
    - Parchea st.set_page_config (no-op) dentro de tools.
    - Parchea st.switch_page para evitar loops/pushState.
    """
    if not script_path or not os.path.exists(script_path):
        st.error("❌ No encuentro el archivo de la herramienta.")
        st.code(script_path or "(vacío)")
        st.stop()

    # Compatibilidad para tools que usan otras keys de login
    st.session_state.setdefault("authenticated", st.session_state.get("auth", False))
    st.session_state.setdefault("logged_in", st.session_state.get("auth", False))

    # Monkey patches seguros durante la ejecución del tool
    _orig_set_page_config = getattr(st, "set_page_config", None)
    _orig_switch_page = getattr(st, "switch_page", None)

    try:
        # Evita excepción "set_page_config can only be called once"
        st.set_page_config = lambda *args, **kwargs: None  # type: ignore
        # Evita navegación multipage real (causa pushState)
        if _orig_switch_page is not None:
            st.switch_page = _safe_switch_page  # type: ignore

        runpy.run_path(script_path, run_name="__main__")
    except Exception:
        st.error("⚠️ La herramienta lanzó un error. Detalle:")
        st.code(traceback.format_exc())
    finally:
        # Restaura funciones originales
        if _orig_set_page_config is not None:
            st.set_page_config = _orig_set_page_config  # type: ignore
        if _orig_switch_page is not None:
            st.switch_page = _orig_switch_page  # type: ignore


# =========================
# UI
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
                st.session_state["auth"] = True
                st.session_state["view"] = "home"
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")


def render_sidebar(show_tools: bool = True):
    with st.sidebar:
        st.markdown("## Menú")
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

        if show_tools:
            st.markdown("### Herramientas")
            if not TOOLS:
                st.warning("No detecté carpeta `pages/` o no hay archivos .py adentro.")
            else:
                st.session_state["tool_filter"] = st.text_input(
                    "Buscar", value=st.session_state["tool_filter"], placeholder="Ej. traducción"
                )

                filtro = (st.session_state["tool_filter"] or "").strip().lower()
                opciones = list(TOOLS.keys())
                if filtro:
                    opciones = [k for k in opciones if filtro in k.lower()]

                if not opciones:
                    st.warning("No hay herramientas que coincidan con tu búsqueda.")
                else:
                    # clave fija para evitar recreación de widget
                    st.session_state["tool"] = st.radio(
                        "Selecciona una herramienta",
                        options=opciones,
                        index=opciones.index(st.session_state["tool"]) if st.session_state["tool"] in opciones else 0,
                        label_visibility="collapsed",
                        key="tool_radio",
                    )

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            logout()


def render_home():
    hide_native_pages_sidebar()
    render_sidebar(show_tools=False)

    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.write("Abre una herramienta desde la barra izquierda.")
    st.divider()
    if st.button("🧰 Ir a Herramientas", use_container_width=True):
        st.session_state["view"] = "tools"
        st.rerun()


def render_tools():
    hide_native_pages_sidebar()
    render_sidebar(show_tools=True)

    if not TOOLS:
        st.stop()

    tool_name = st.session_state.get("tool")
    meta = TOOLS.get(tool_name)

    if not meta:
        st.warning("Selecciona una herramienta en la barra izquierda.")
        st.stop()

    st.markdown(f"# {tool_name}")
    if meta.get("desc"):
        st.caption(meta["desc"])
    st.divider()

    _run_tool_script(meta["script"])


# =========================
# ROUTER
# =========================
_init_session()

if not st.session_state.get("auth", False):
    st.session_state["view"] = "login"
    render_login()
else:
    if st.session_state.get("view") == "login":
        st.session_state["view"] = "home"

    if st.session_state.get("view") == "home":
        render_home()
    else:
        render_tools()

