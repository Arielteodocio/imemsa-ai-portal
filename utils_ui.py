import streamlit as st

def hide_streamlit_sidebar_pages():
    """
    Oculta el 'Pages navigation' automático (lista de apps) del sidebar,
    dejando tu sidebar personalizado.
    """
    st.markdown(
        """
        <style>
        /* Oculta el bloque de navegación de páginas automático */
        [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True
    )
