import streamlit as st

st.set_page_config(page_title="IMEMSA AI Portal", page_icon="🤖", layout="wide")


import streamlit as st

st.set_page_config(page_title="IMEMSA AI Portal", page_icon="🤖", layout="wide")

st.image("imemsa_logo.png", width=220)
st.title("IMEMSA AI Portal")

st.title("🤖 IMEMSA AI Portal")
st.caption("Portal interno: Transcripción | Traducción | Minutas | Documentos | Forecast | NLP Operación")

st.markdown("## Módulos")
c1, c2, c3 = st.columns(3)

with c1:
    st.page_link("pages/1_🎧_Transcripcion.py", label="🎧 Transcripción", icon="🎧")
    st.page_link("pages/2_🌐_Traduccion.py", label="🌐 Traducción", icon="🌐")

with c2:
    st.page_link("pages/3_📝_Minutas_y_acciones.py", label="📝 Minutas y acciones", icon="📝")
    st.page_link("pages/4_📄_Documentos.py", label="📄 Documentos", icon="📄")

with c3:
    st.page_link("pages/5_📈_Forecast_y_Anomalias.py", label="📈 Forecast y anomalías", icon="📈")
    st.page_link("pages/6_🧠_NLP_Operacion.py", label="🧠 NLP para operación", icon="🧠")
