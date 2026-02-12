import streamlit as st
from pathlib import Path

# =========================
# CONFIG (debe ir primero)
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PORTAL_PASSWORD = "imemsa26"

# Rutas reales de tus páginas (según tu repo/capturas)
PAGES = {
    "Transcripción": "pages/1_🎧_Transcripcion.py",
    "Traducción": "pages/2_🌐_Traduccion.py",
    "Minutas y acciones": "pages/3_📝_Minutas_y_acciones.py",
    "Documentos": "pages/4_📄_Documentos.py",
    "Forecast y Anomalías": "pages/5_📈_Forecast_y_Anomalias.py",
    "NLP Operación": "pages/6_🧠_NLP_Operacion.py",
}

LABELS = {
    "Transcripción": "🎧 Transcripción",
    "Traducción": "🌐 Traducción",
    "Minutas y acciones": "📝 Minutas y acciones",
    "Documentos": "📄 Documentos",
    "Forecast y Anomalías": "📈 Forecast y anomalías",
    "NLP Operación": "🧠 NLP Operación",
}

# =========================
# SESSION + NAV
# =========================
def _init_session():
    st.session_state.setdefault("auth", False)
    st.session_state.setdefault("view", "login")  # login | home | tools

def _queue_page(page_key: str):
    """Programa el cambio de página y deja que ocurra al inicio del siguiente rerun."""
    st.session_state["_go_to_page"] = page_key
    st.rerun()

def _handle_pending_navigation():
    target = st.session_state.pop("_go_to_page", None)
    if target:
        st.switch_page(PAGES[target])
        st.stop()  # evita que se siga renderizando esta página

def _logout():
    st.session_state["auth"] = False
    st.session_state["view"] = "login"
    st.session_state.pop("_go_to_page", None)
    st.rerun()

def _go(view_name: str):
    st.session_state["view"] = view_name
    st.rerun()

def hide_native_pages_sidebar():
    """Oculta el menú nativo de multipage (la lista automática de pages en el sidebar)."""
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )

def render_sidebar():
    with st.sidebar:
        st.markdown("### Navegación")
        st.button("🏠 Home", use_container_width=True, on_click=_go, args=("home",), key="sb_home")
        st.button("🧰 Herramientas", use_container_width=True, on_click=_go, args=("tools",), key="sb_tools")

        st.divider()
        st.markdown("### Abrir herramienta")

        # Si tu versión de Streamlit tiene st.page_link, úsalo (es súper estable).
        if hasattr(st, "page_link"):
            for k, path in PAGES.items():
                st.page_link(path, label=LABELS.get(k, k), use_container_width=True)
        else:
            for k in PAGES.keys():
                st.button(
                    LABELS.get(k, k),
                    use_container_width=True,
                    on_click=_queue_page,
                    args=(k,),
                    key=f"sb_open_{k}",
                )

        st.divider()
        st.button("Cerrar sesión", use_container_width=True, on_click=_logout, key="sb_logout")

# =========================
# UI: LOGIN
# =========================
def render_login():
    hide_native_pages_sidebar()

    col1, col2, col3 = st.columns([1.2, 2.2, 1.2])
    with col2:
        st.markdown("## 🔒 Acceso al Portal IMEMSA")
        st.caption("Ingresa la contraseña para continuar.")

        pw = st.text_input("Contraseña", type="password", placeholder="••••••••")

        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("Entrar", use_container_width=True):
                if (pw or "").strip() == PORTAL_PASSWORD:
                    st.session_state["auth"] = True
                    st.session_state["view"] = "home"
                    st.session_state.pop("_go_to_page", None)
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
        with c2:
            st.info("Si no cuentas con acceso, contacta al administrador del portal.")

# =========================
# UI: HOME
# =========================
def render_home():
    hide_native_pages_sidebar()
    render_sidebar()

    logo = Path("assets/imemsa_logo.png")
    if logo.exists():
        st.image(str(logo), width=220)

    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.markdown(
        """
        **¡Bienvenido!**  
        Este portal reúne herramientas de Inteligencia Artificial para ayudarte a **trabajar más rápido**,  
        **reducir tareas repetitivas** y **mejorar la calidad** de tus entregables.
        """
    )

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(
            """
            <div style="border:1px solid rgba(150,150,150,0.25); border-radius:18px; padding:18px;">
              <h3 style="margin:0;">🧰 Herramientas de IA</h3>
              <p style="opacity:0.85; margin-top:10px;">
                Módulos listos para usar: transcripción, traducción, minutas, documentos, forecast y más.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Entrar a Herramientas", use_container_width=True, on_click=_go, args=("tools",), key="go_tools")

    with c2:
        st.markdown(
            """
            <div style="border:1px solid rgba(150,150,150,0.25); border-radius:18px; padding:18px;">
              <h3 style="margin:0;">🧠 Agentes de IA (próximamente)</h3>
              <p style="opacity:0.85; margin-top:10px;">
                Sección reservada para automatizaciones avanzadas y agentes por área (futuro).
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.button("Próximamente", use_container_width=True, disabled=True, key="agents_disabled")

# =========================
# UI: TOOLS DASHBOARD
# =========================
def tool_card(title, icon, desc, tags, page_key, key):
    st.markdown(
        f"""
        <div style="border:1px solid rgba(150,150,150,0.25); border-radius:18px; padding:18px; height: 260px;">
          <h3 style="margin:0;">{icon} {title}</h3>
          <p style="opacity:0.9; margin-top:10px; min-height: 95px;">{desc}</p>
          <p style="opacity:0.7; margin-top:6px; font-size: 0.9rem;">{' · '.join(tags)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # En vez de switch_page aquí (a veces se siente “sin acción”), programamos la navegación
    st.button("➡️ Abrir", use_container_width=True, on_click=_queue_page, args=(page_key,), key=f"open_{key}")

def render_tools():
    hide_native_pages_sidebar()
    render_sidebar()

    st.markdown("# 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar.")

    r1 = st.columns(3, gap="large")
    with r1[0]:
        tool_card(
            "Transcripción",
            "🎧",
            "Convierte audio en español a texto listo para copiar o exportar.",
            ["Operación", "Administrativo"],
            "Transcripción",
            "t1",
        )
    with r1[1]:
        tool_card(
            "Traducción",
            "🌐",
            "Traduce texto Inglés ↔ Español con formato claro y profesional.",
            ["Administrativo", "Comercial"],
            "Traducción",
            "t2",
        )
    with r1[2]:
        tool_card(
            "Minutas y acciones",
            "📝",
            "Genera minuta estructurada y acciones con responsables y fechas; exporta a Excel.",
            ["Administrativo", "Dirección"],
            "Minutas y acciones",
            "t3",
        )

    st.write("")  # separador

    r2 = st.columns(3, gap="large")
    with r2[0]:
        tool_card(
            "Documentos",
            "📄",
            "Lee PDFs/imagenes y extrae información estructurada.",
            ["Tesorería", "Administrativo"],
            "Documentos",
            "t4",
        )
    with r2[1]:
        tool_card(
            "Forecast y anomalías",
            "📈",
            "Pronostica series de tiempo y detecta anomalías para identificar cambios relevantes.",
            ["Planeación", "Dirección"],
            "Forecast y Anomalías",
            "t5",
        )
    with r2[2]:
        tool_card(
            "NLP Operación",
            "🧠",
            "Clasifica solicitudes internas y extrae datos clave (ej. Factura + OC).",
            ["Tesorería", "Comercial"],
            "NLP Operación",
            "t6",
        )

# =========================
# ROUTER
# =========================
_init_session()
_handle_pending_navigation()  # <- se ejecuta muy temprano para que el cambio de página sea estable

if not st.session_state["auth"]:
    st.session_state["view"] = "login"
    render_login()
else:
    if st.session_state["view"] == "login":
        st.session_state["view"] = "home"

    if st.session_state["view"] == "home":
        render_home()
    elif st.session_state["view"] == "tools":
        render_tools()
    else:
        render_home()

