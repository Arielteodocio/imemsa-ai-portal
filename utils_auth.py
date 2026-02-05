import hmac
import streamlit as st


def require_password() -> None:
    """
    Gate simple por contraseña usando st.session_state.

    - Password en st.secrets["APP_PASSWORD"] (recomendado)
    - Si no existe, fallback "imemsa26"
    """

    if st.session_state.get("authenticated", False):
        return

    correct = str(st.secrets.get("APP_PASSWORD", "imemsa26"))

    # Oculta sidebar en login
    st.markdown(
        """
        <style>
          [data-testid="stSidebar"] {display: none;}
          [data-testid="stSidebarNav"] {display: none;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("🔒 Acceso al Portal IMEMSA")
    st.caption("Ingresa la contraseña para continuar.")

    pwd = st.text_input("Contraseña", type="password")

    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Entrar", type="primary"):
            if hmac.compare_digest(pwd, correct):
                st.session_state["authenticated"] = True

                # 🔥 Siempre manda a HOME después de loguear
                st.session_state["section"] = "home"
                st.session_state["just_logged_in"] = True

                st.switch_page("app.py")
            else:
                st.error("Contraseña incorrecta. Intenta de nuevo.")

    with c2:
        st.info("Si no cuentas con acceso, contacta al administrador del portal.")

    st.stop()


