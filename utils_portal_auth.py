import streamlit as st

def require_login_redirect() -> None:
    """
    Si no hay sesión, redirige directo al Login del portal (app.py) SIN pantalla intermedia.
    """
    if st.session_state.get("auth", False):
        return

    # fuerza al portal a mostrar login
    st.session_state["view"] = "login"

    # redirección directa
    st.switch_page("app.py")
