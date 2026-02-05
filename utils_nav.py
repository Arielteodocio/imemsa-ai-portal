import streamlit as st


def go_home():
    st.session_state.section = "home"
    st.switch_page("app.py")


def require_tools_mode():
    """
    Evita que entren directo a /pages sin pasar por HOME -> Herramientas.
    """
    if st.session_state.get("section") != "tools":
        go_home()


def tools_sidebar_controls():
    """
    Menú lateral que debe aparecer EN app.py y en CADA módulo dentro de /pages
    """
    with st.sidebar:
        st.markdown("### Navegación")

        if st.button("🧰 Tablero", use_container_width=True):
            st.session_state.section = "tools"
            st.switch_page("app.py")

        if st.button("🏠 Inicio", use_container_width=True):
            st.session_state.section = "home"
            st.switch_page("app.py")

        st.divider()

        if st.button("Cerrar sesión", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.section = "home"
            st.switch_page("app.py")
