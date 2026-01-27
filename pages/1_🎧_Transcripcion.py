
import time
import streamlit as st

from services.transcribe_openai import transcribe_audio_bytes
from utils_export import to_docx_bytes, to_pdf_bytes  # archivo que creamos en el paso 4

st.set_page_config(page_title="Transcripción", page_icon="🎧", layout="wide")

st.title("🎧 Transcripción (Audio → Texto)")
st.caption(
    "Carga un archivo de audio y obtén la transcripción en texto. "
    "Entrega el contenido transcrito listo para copiar o exportar."
)

with st.expander("🔒 Privacidad (cómo funciona)", expanded=False):
    st.write(
        "- El audio se procesa en la nube y se devuelve el texto.\n"
        "- No guardamos el archivo ni la transcripción.\n"
        "- Solo se utiliza un archivo temporal durante la transcripción."
    )

colL, colR = st.columns([2, 1])

with colR:
    st.subheader("Configuración")
    model = st.selectbox(
        "Modelo",
        ["gpt-4o-mini-transcribe", "gpt-4o-transcribe"],
        index=0,
        help="mini = más económico; 4o = mayor calidad/costo.",
    )
    language_hint = st.selectbox("Idioma (opcional)", ["auto", "es", "en"], index=0)
    technical_mode = st.toggle("Modo Técnico (prompt)", value=True)
    prompt_default = (
        "El audio es de un contexto industrial/operativo. "
        "Conserva siglas y términos técnicos. "
        "Términos: IMEMSA, gel coat, fibra de vidrio, infusión al vacío, T-top, quilla, patín, borda, consola."
    )
    prompt = st.text_area("Contexto / glosario (opcional)", value=prompt_default if technical_mode else "", height=120)

with colL:
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

        # Recomendación práctica: Streamlit Cloud + OpenAI tiene límite de tamaño por request.
        if len(audio_bytes) > 25 * 1024 * 1024:
            st.error("El archivo supera 25 MB. Divide el audio o usa un formato más comprimido (m4a/mp3).")
            st.stop()

        with st.spinner("Transcribiendo…"):
            result = transcribe_audio_bytes(
                audio_bytes=audio_bytes,
                original_filename=audio_file.name,
                model=model,
                language_hint=language_hint,
                prompt=prompt.strip() or None,
            )

        st.success(f"Listo ✅ (modelo: {result.model})")

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
