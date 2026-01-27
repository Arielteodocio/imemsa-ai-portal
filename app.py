import streamlit as st
from utils_auth import require_password
require_password()

st.set_page_config(page_title="IMEMSA AI Portal", page_icon="🤖", layout="wide")

# Logo (está en la raíz del repo)
st.image("imemsa_logo.png", width=220)

# ✅ Único título visible (con ícono)
st.title("🤖 Portafolio de Herramientas de IA")
st.markdown(
    """
    <div style="margin-top: 10px; font-size: 1.05rem; opacity: 0.9;">
      👋 <b>¡Bienvenido!</b><br>
      Este portal reúne herramientas de Inteligencia Artificial diseñadas para ayudarte a
      <b>trabajar más rápido</b>, <b>reducir tareas repetitivas</b> y <b>mejorar la calidad</b> de tus entregables.
      <br><br>
      Te invitamos a probar los módulos del menú lateral. Si tienes sugerencias o detectas oportunidades de mejora,
      compártelas para seguir evolucionando el portafolio.
    </div>
    """,
    unsafe_allow_html=True,
)

# (Opcional) Mantener una línea descriptiva corta
st.caption("Portal interno: Transcripción | Traducción | Minutas | Documentos | Forecast | NLP Operación")
