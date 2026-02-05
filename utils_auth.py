import streamlit as st
import hmac

def require_password() -> None:
    # 🔒 Si NO está autenticado, ocultamos sidebar + navegación
    if not st.session_state.get("authenticated", False):
        st.markdown(
            """
            <style>
              [data-testid="stSidebar"] {display: none;}
              [data-testid="stSidebarNav"] {display: none;}
              header {visibility: hidden;}
            </style>
            """,
            unsafe_allow_html=True,
        )

    if st.session_state.get("authenticated", False):
        return

    correct = str(st.secrets.get("APP_PASSWORD", "imemsa26"))

    st.title("🔒 Acceso al Portafolio de Herramientas Imemsa")
    st.caption("Ingresa la contraseña para continuar.")

    pwd = st.text_input("Contraseña", type="password")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Entrar", type="primary"):
            if hmac.compare_digest(pwd, correct):
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Contraseña incorrecta. Intenta de nuevo.")

    with c2:
        st.info("Si no cuentas con acceso, contacta a un integrante del Comite de IA.")

    st.stop()

