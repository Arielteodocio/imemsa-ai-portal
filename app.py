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

PORTAL_PASSWORD = "imemsa26"

# =========================
# ANTI-BUCLE (protege el navegador)
# =========================
def loop_guard(max_runs: int = 50, window_sec: int = 10):
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
        st.error("⚠️ Detecté un ciclo de recarga (rerun) demasiado rápido y lo detuve.")
        st.info(
            "Alguna herramienta (archivo dentro de `pages/`) probablemente está llamando "
            "`st.rerun()`, `st.switch_page()` o cambiando query params en cada ejecución."
        )
        if st.button("🧹 Limpiar sesión y reiniciar", key="btn_clear_session", use_container_width=True):
            st.session_state.clear()
            st.rerun()
        st.stop()

loop_guard()


# =========================
# UTILIDADES
# =========================
def discover_tools(pages_dir: str = "pages"):
    tools = {}
    if not os.path.isdir(pages_dir):
        return tools

    files = [f for f in os.listdir(pages_dir) if f.endswith(".py")]

    def _sort_key(fn: str):
        # ordena por prefijo numérico si existe: 1_xxx.py
        try:
            prefix = fn.split("_", 1)[0]
            return (0, int(prefix), fn)
        except Exception:
            return (1, 9999, fn)

    for fn in sorted(files, key=_sort_key):
        stem = fn[:-3]
        parts = stem.split("_", 1)
        if len(parts) == 2 and parts[0].isdigit():
            title = parts[1].replace("_", " ")
        else:
            title = stem.replace("_", " ")
        tools[title] = {"script": os.path.join(pages_dir, fn)}
    return tools


TOOLS = discover_tools("pages")


def do_login():
    pw = (st.session_state.get("pw_input") or "").strip()
    if pw == PORTAL_PASSWORD:
        st.session_state["auth"] = True
    else:
        st.session_state["auth"] = False
        st.session_state["login_error"] = "Contraseña incorrecta."


def do_logout():
    # conserva la detección de tools, limpia lo demás
    keep = {"_lg_t0": st.session_state.get("_lg_t0"), "_lg_n": st.session_state.get("_lg_n")}
    st.session_state.clear()
    st.session_state.update(keep)


def _safe_switch_page(page_like):
    # Evita navegación multipage real (causa pushState). Regresa al selector.
    st.warning("🔁 Esta herramienta intentó navegar a otra página; lo bloqueé para evitar el bug de navegación.")
    st.stop()


def _run_tool_script(script_path: str):
    if not os.path.exists(script_path):
        st.error(f"❌ No encuentro el archivo: `{script_path}`")
        st.stop()

    # Compatibilidad para tools que usan otros flags
    st.session_state.setdefault("authenticated", st.session_state.get("auth", False))
    st.session_state.setdefault("logged_in", st.session_state.get("auth", False))

    # Monkey patches seguros durante ejecución del tool
    _orig_set_page_config = getattr(st, "set_page_config", None)
    _orig_switch_page = getattr(st, "switch_page", None)
    _orig_set_qp = getattr(st, "experimental_set_query_params", None)

    try:
        # Evita excepción: set_page_config solo una vez
        st.set_page_config = lambda *args, **kwargs: None  # type: ignore
        # Bloquea switch_page para no usar history.pushState
        if _orig_switch_page is not None:
            st.switch_page = _safe_switch_page  # type: ignore
        # Bloquea set_query_params (también empuja history)
        if _orig_set_qp is not None:
            st.experimental_set_query_params = lambda **kwargs: None  # type: ignore

        runpy.run_path(script_path, run_name="__main__")
    except Exception:
        st.error("⚠️ Error dentro de la herramienta:")
        st.code(traceback.format_exc())
    finally:
        if _orig_set_page_config is not None:
            st.set_page_config = _orig_set_page_config  # type: ignore
        if _orig_switch_page is not None:
            st.switch_page = _orig_switch_page  # type: ignore
        if _orig_set_qp is not None:
            st.experimental_set_query_params = _orig_set_qp  # type: ignore


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


# =========================
# UI
# =========================
hide_native_pages_sidebar()
st.session_state.setdefault("auth", False)

with st.sidebar:
    st.markdown("## Menú")

    # Debug mini para saber si la app está recibiendo clicks/cambios
    with st.expander("🧪 Diagnóstico rápido", expanded=False):
        st.session_state["dbg_counter"] = st.session_state.get("dbg_counter", 0) + 1
        st.caption(f"Reruns detectados: **{st.session_state['dbg_counter']}**")
        st.toggle("Toggle de prueba", key="dbg_toggle")
        st.text_input("Input de prueba", key="dbg_input")

    st.divider()

    if not st.session_state["auth"]:
        st.markdown("### 🔒 Login")
        st.text_input("Contraseña", type="password", key="pw_input", placeholder="••••••••")
        st.button("Entrar", key="btn_login", on_click=do_login, use_container_width=True)
        if st.session_state.get("login_error"):
            st.error(st.session_state["login_error"])
    else:
        st.success("Sesión activa")
        st.button("Cerrar sesión", key="btn_logout", on_click=do_logout, use_container_width=True)

        st.divider()
        st.markdown("### Herramientas")

        if not TOOLS:
            st.warning("No detecté carpeta `pages/` o no hay archivos .py dentro.")
        else:
            # Selector estable (sin navegación)
            options = list(TOOLS.keys())
            current = st.session_state.get("tool_selected")
            if current not in options:
                st.session_state["tool_selected"] = options[0]

            st.selectbox(
                "Selecciona una herramienta",
                options=options,
                key="tool_selected",
                label_visibility="collapsed",
            )

# MAIN
if not st.session_state["auth"]:
    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.caption("Inicia sesión en la barra izquierda para ver el catálogo.")
else:
    tool_name = st.session_state.get("tool_selected")
    script_path = TOOLS.get(tool_name, {}).get("script")

    st.markdown(f"# {tool_name}")
    st.caption("Seleccionada desde el menú lateral. (Sin navegación multipage)")
    st.divider()

    _run_tool_script(script_path)

