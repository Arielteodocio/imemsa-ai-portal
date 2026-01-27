import time
import streamlit as st

from services.transcribe_openai import transcribe_audio_bytes
from utils_export import to_docx_bytes, to_pdf_bytes

st.set_page_config(page_title="Transcripción", page_icon="🎧", layout="wide")

st.title("🎧 Transcripción de Audio a Texto")
st.caption(
    "Carga un archivo de audio y obtén la transcripción en texto. "
    "Entrega el contenido transcrito listo para copiar o exportar."
)

with st.expander("🔒 Privacidad (cómo funciona)", expanded=False):
    st.write(
        "- El audio se procesa en la nube y se devuelve el texto.\n"
        "- No se guarda el archivo ni la transcripción.\n"
        "- Solo se utiliza un archivo temporal durante la transcripción."
    )

# ✅ Configuración fija (sin opciones al usuario)
MODEL = "gpt-4o-mini-transcribe"
LANGUAGE_HINT = "es"
PROMPT = (
    "El audio es de un contexto industrial/operativo. "
    "Conserva siglas y términos técnicos. "
    "Términos: IMEMSA, gel coat, fibra de vidrio, infusión al vacío, T-top, quilla, patín, borda, consola."
)

audio_file = st.file_uploader(
    "Sube audio (mp3, m4a, wav, webm, mp4)",
    type=["mp3", "m4a", "wav", "webm", "mp4", "mpeg", "mpga"],
)

if audio_file:
    st.audio(audio_file)

btn = st.button("Transcribir", type="primary", disabled=(audio_file is None))

if btn and audio_file:
    t0 = time.time()
    try:
        audio_bytes = audio_file.read()

        # Límite práctico para evitar fallos típicos con archivos grandes
        if len(audio_bytes) > 25 * 1024 * 1024:
            st.error("El archivo supera 25 MB. Divide el audio o usa un formato más comprimido (m4a/mp3).")
            st.stop()

        with st.spinner("Transcribiendo…"):
            result = transcribe_audio_bytes(
                audio_bytes=audio_bytes,
                original_filename=audio_file.name,
                model=MODEL,
                language_hint=LANGUAGE_HINT,
                prompt=PROMPT,
            )

        st.success("Listo ✅")

        st.subheader("Transcripción")
        st.text_area("Resultado", value=result.text, height=360)

        st.subheader("Exportar")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button(
                "TXT",
                data=result.text.encode("utf-8"),
                file_name="transcripcion.txt",
                mime="text/plain",
            )
        with c2:
            st.download_button(
                "DOCX",
                data=to_docx_bytes("Transcripción", result.text),
                file_name="transcripcion.docx",
            )
        with c3:
            st.download_button(
                "PDF",
                data=to_pdf_bytes("Transcripción", result.text),
                file_name="transcripcion.pdf",
                mime="application/pdf",
            )

        st.caption(f"Tiempo: {round(time.time() - t0, 2)} s")

    except Exception as e:
        st.error(f"Error: {e}")

