import time
import streamlit as st

from services.transcribe_openai import transcribe_audio_bytes
from utils_export import to_docx_bytes, to_pdf_bytes
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

st.set_page_config(page_title="Transcripción", page_icon="🎧", layout="wide")

st.title("🎧 Transcripción (Audio → Texto)")
st.caption(
    "Carga un audio en español y obtén la transcripción en texto (español). "
    "Entrega el contenido transcrito listo para copiar o exportar."
)

with st.expander("🔒 Privacidad (cómo funciona)", expanded=False):
    st.write(
        "- El audio se procesa en la nube y se devuelve el texto.\n"
        "- No guardamos el archivo ni la transcripción.\n"
        "- Solo se utiliza un archivo temporal durante la transcripción."
    )

# ✅ Configuración fija (sin opciones al usuario)
MODEL = "gpt-4o-mini-transcribe"
LANGUAGE_HINT = "es"_
