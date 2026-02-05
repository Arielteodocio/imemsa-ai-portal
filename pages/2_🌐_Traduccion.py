import streamlit as st
from utils_auth import require_password


from utils_nav import require_tools_mode, tools_sidebar_controls

require_password()
require_tools_mode()
tools_sidebar_controls()




from services.translate_openai import translate_en_es
from utils_export import to_docx_bytes, to_pdf_bytes
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

st.set_page_config(page_title="Traducción", page_icon="🌐", layout="wide")

st.title("🌐 Traducción (Texto → Texto)")
st.caption(
    "Pega el texto y obtén su traducción entre Inglés y Español. "
    "Entrega el resultado listo para copiar o exportar."
)

direction = st.radio(
    "Dirección de traducción",
    ["EN->ES", "ES->EN"],
    horizontal=True,
)

text = st.text_area(
    "Texto a traducir",
    height=260,
    placeholder="Pega aquí el texto…",
)

btn = st.button("Traducir", type="primary", disabled=(not text.strip()))

if btn:
    try:
        with st.spinner("Traduciendo…"):
            result = translate_en_es(text, direction=direction)

        st.success("Listo ✅")
        st.text_area("Resultado", value=result.text, height=320)

        st.subheader("Exportar")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.download_button(
                "TXT",
                data=result.text.encode("utf-8"),
                file_name="traduccion.txt",
                mime="text/plain",
            )

        with c2:
            st.download_button(
                "DOCX",
                data=to_docx_bytes("Traducción", result.text),
                file_name="traduccion.docx",
            )

        with c3:
            st.download_button(
                "PDF",
                data=to_pdf_bytes("Traducción", result.text),
                file_name="traduccion.pdf",
                mime="application/pdf",
            )

    except Exception as e:
        if show_maintenance_instead_of_api_error(e):
            st.warning(MAINTENANCE_MSG)
        else:
            st.error("Ocurrió un error inesperado. Contacta al administrador del portal.")

