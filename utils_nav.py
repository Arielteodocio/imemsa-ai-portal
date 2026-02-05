import streamlit as st


def go_home():
    st.session_state.section = "home"
    st.switch_page("app.py")


def require_tools_mode():
    """
    Si el usuario no ha elegido 'Herramientas', lo regresa al Home.
    Esto evita que entren directo a /pages/*.
    """
    if st.session_state.get("section") != "tools":
        go_home()
