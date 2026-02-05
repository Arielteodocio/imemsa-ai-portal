import streamlit as st

# =========================
# CONFIG
# =========================
st.set_page_config(
    page_title="IMEMSA | Portafolio de IA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

PORTAL_PASSWORD = "imemsa26"

# Rutas reales de tus páginas (según tu captura)
PAGES = {
    "Transcripción": "pages/1_🎧_Transcripcion.py",
    "Traducción": "pages/2_🌐_Traduccion.py",
    "Minutas y acciones": "pages/3_📝_Minutas_y_acciones.py",
    "Documentos": "pages/4_📄_Documentos.py",
    "Forecast y Anomalías": "pages/5_📈_Forecast_y_Anomalias.py",
    "NLP Operación": "pages/6_🧠_NLP_Operacion.py",
}




# =========================
# HELPERS
# =========================
def _init_session():
    if "auth" not in st.session_state:
        st.session_state.auth = False
    if "view" not in st.session_state:
        # views: "login" | "home" | "tools"
        st.session_state.view = "login"


def hide_native_pages_sidebar():
    """
    Oculta el menú nativo de multipage (la lista automática de pages en el sidebar).
    Ojo: Streamlit no ofrece un 'switch' oficial; esto es CSS.
    """
    st.markdown(
        """
        <style>
        /* Oculta el selector de páginas nativo */
        [data-testid="stSidebarNav"] { display: none !important; }
        /* Opcional: reduce el espacio arriba del sidebar */
        section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def require_auth_or_stop():
    """
    Úsalo en app.py para decidir qué renderizar.
    En las páginas (modules) haremos un equivalente para bloquear sin login.
    """
    if not st.session_state.auth:
        st.session_state.view = "login"
        st.stop()


def go(view_name: str):
    st.session_state.view = view_name
    st.rerun()


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
                    st.session_state.auth = True
                    st.session_state.view = "home"
                    st.rerun()
                else:
                    st.error("Contraseña incorrecta.")
        with c2:
            st.info("Si no cuentas con acceso, contacta al administrador del portal.")


# =========================
# UI: HOME (Herramientas / Agentes)
# =========================
def render_home():
    hide_native_pages_sidebar()

    # Sidebar propio (solo navegación)
    with st.sidebar:
        st.markdown("### Navegación")
        if st.button("🏠 Home", use_container_width=True):
            go("home")
        if st.button("🧰 Herramientas", use_container_width=True):
            go("tools")

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.auth = False
            st.session_state.view = "login"
            st.rerun()

    # Contenido
    st.image("assets/imemsa_logo.png", width=220) if False else None  # si tienes logo local, cambia a True y ajusta ruta
    st.markdown("# 🤖 Portafolio de Herramientas de IA")
    st.markdown(
        """
        **¡Bienvenido!**  
        Este portal reúne herramientas de Inteligencia Artificial diseñadas para ayudarte a **trabajar más rápido**,  
        **reducir tareas repetitivas** y **mejorar la calidad** de tus entregables.

        Selecciona una opción para comenzar:
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
        if st.button("Entrar a Herramientas", use_container_width=True, key="go_tools"):
            go("tools")

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
def tool_card(title, icon, desc, tags, page_path, key):
    st.markdown(
        f"""
        <div style="border:1px solid rgba(150,150,150,0.25); border-radius:18px; padding:18px; height: 240px;">
          <h3 style="margin:0;">{icon} {title}</h3>
          <p style="opacity:0.9; margin-top:10px; min-height: 90px;">{desc}</p>
          <p style="opacity:0.7; margin-top:6px; font-size: 0.9rem;">{' · '.join(tags)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Botón real (estable) -> navega a pages/...
    if st.button("➡️ Abrir", use_container_width=True, key=f"open_{key}"):
        st.switch_page(page_path)


def render_tools():
    hide_native_pages_sidebar()

    # Sidebar propio (solo navegación)
    with st.sidebar:
        st.markdown("### Navegación")
        if st.button("🏠 Home", use_container_width=True):
            go("home")
        if st.button("🧰 Herramientas", use_container_width=True):
            go("tools")

        st.divider()
        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.auth = False
            st.session_state.view = "login"
            st.rerun()

    st.markdown("# 🧰 Herramientas de IA")
    st.caption("Selecciona una herramienta para comenzar.")

    # Tablero
    r1 = st.columns(3, gap="large")
    with r1[0]:
        tool_card(
            "Transcripción",
            "🎧",
            "Convierte audio en español a texto listo para copiar o exportar.",
            ["Operación", "Administrativo"],
            PAGES["Transcripción"],
            "t1",
        )
    with r1[1]:
        tool_card(
            "Traducción",
            "🌐",
            "Traduce texto Inglés ↔ Español con formato claro y profesional.",
            ["Administrativo", "Comercial"],
            PAGES["Traducción"],
            "t2",
        )
    with r1[2]:
        tool_card(
            "Minutas y acciones",
            "📝",
            "Genera minuta estructurada y acciones con responsables y fechas; exporta a Excel.",
            ["Administrativo", "Dirección"],
            PAGES["Minutas y acciones"],
            "t3",
        )

    st.write("")
    r2 = st.columns(3, gap="large")
    with r2[0]:
        tool_card(
            "Documentos",
            "📄",
            "Lee PDFs/imagenes, aplica OCR (lectura de texto en imágenes) y extrae información estructurada.",
            ["Tesorería", "Administrativo"],
            PAGES["Documentos"],
            "t4",
        )
    with r2[1]:
        tool_card(
            "Forecast y anomalías",
            "📈",
            "Pronostica series de tiempo y detecta anomalías para identificar cambios relevantes.",
            ["Planeación", "Dirección"],
            PAGES["Forecast y Anomalías"],
            "t5",
        )
    with r2[2]:
        tool_card(
            "NLP Operación",
            "🧠",
            "Clasifica solicitudes internas, estima prioridad y extrae datos clave (ej. Factura + OC).",
            ["Tesorería", "Comercial"],
            PAGES["NLP Operación"],
            "t6",
        )


# =========================
# ROUTER
# =========================
_init_session()

# Si no está autenticado, solo login.
if not st.session_state.auth:
    st.session_state.view = "login"
    render_login()
else:
    # Ya autenticado -> router
    if st.session_state.view == "login":
        st.session_state.view = "home"

    if st.session_state.view == "home":
        render_home()
    elif st.session_state.view == "tools":
        render_tools()
    else:
        # fallback
        render_home()

