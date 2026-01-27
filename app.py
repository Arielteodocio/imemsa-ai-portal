import streamlit as st
from utils_auth import require_password
require_password()

st.set_page_config(page_title="IMEMSA AI Portal", page_icon="🤖", layout="wide")

# Logo (está en la raíz del repo)
st.image("imemsa_logo.png", width=220)

# ✅ Único título visible (con ícono)
st.title("🤖 Portafolio de Herramientas de IA")

# (Opcional) Mantener una línea descriptiva corta
st.caption("Portal interno: Transcripción | Traducción | Minutas | Documentos | Forecast | NLP Operación")
