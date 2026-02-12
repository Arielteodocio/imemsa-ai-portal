import streamlit as st

def _hide_native_pages_sidebar():
    st.markdown(
        """
        <style>
        [data-testid="stSidebarNav"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

_hide_native_pages_sidebar()

if "auth" not in st.session_state or not st.session_state.auth:
    st.warning("Sesión no iniciada. Regresa al inicio para ingresar contraseña.")
    st.stop()

import streamlit as st

# ✅ NO pongas st.set_page_config() aquí (solo en app.py)

def require_login():
    if not st.session_state.get("auth", False):
        st.error("🔒 Inicia sesión para usar esta herramienta.")
        if hasattr(st, "page_link"):
            st.page_link("app.py", label="Ir al Login", icon="🔐", use_container_width=True)
        else:
            st.info("Vuelve a app.py para iniciar sesión.")
        st.stop()

require_login()

# Header
st.markdown("# 📄 Documentos")
if hasattr(st, "page_link"):
    st.page_link("app.py", label="⬅️ Volver al Portafolio", icon="🏠", use_container_width=True)

st.divider()

st.info("Pega aquí el código de tu herramienta (la app que ya programaste).")








import json
from io import BytesIO
from utils_auth import require_password
import streamlit as st
from utils_ui import hide_streamlit_sidebar_pages
from utils_nav import require_tools_mode, tools_sidebar_controls

require_password()
require_tools_mode()
tools_sidebar_controls()
hide_streamlit_sidebar_pages()



import pandas as pd
import streamlit as st
from PIL import Image
import fitz  # pymupd

from services.docs_ocr_openai import ocr_and_extract_from_images
from utils_export import to_docx_bytes, to_pdf_bytes
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

import streamlit as st
from utils_ui import hide_streamlit_sidebar_pages

hide_streamlit_sidebar_pages()

# --- Requiere login
if "auth_ok" not in st.session_state or not st.session_state.auth_ok:
    st.switch_page("app.py")

# --- Sidebar navegación (mismo look en todos)
def logout():
    st.session_state.auth_ok = False
    st.switch_page("app.py")

with st.sidebar:
    st.markdown("### Navegación")
    if st.button("🧰 Tablero", use_container_width=True):
        st.switch_page("app.py")
    st.markdown("---")
    st.button("Cerrar sesión", on_click=logout, use_container_width=True)






#st.set_page_config(page_title="Documentos", page_icon="📄", layout="wide")

#st.title("📄 Documentos (OCR + extracción)")
#st.caption(
#    "Sube un documento (PDF o imagen) y conviértelo a texto con OCR (Reconocimiento Óptico de Caracteres). "
#    "Después, extrae información clave y la entrega organizada para revisión y exportación."
#)

with st.expander("🔒 Privacidad (cómo funciona)", expanded=False):
    st.write(
        "- El documento se procesa y se devuelve el texto y campos.\n"
        "- No guardamos el archivo.\n"
        "- Puedes exportar el resultado."
    )

doc_type = st.selectbox(
    "Tipo de documento (opcional)",
    ["Auto", "Factura", "Orden de compra", "Reporte", "Checklist", "Otro"],
    index=0,
)

uploaded = st.file_uploader("Sube PDF o imagen", type=["pdf", "png", "jpg", "jpeg"])

btn = st.button("Procesar documento", type="primary", disabled=(uploaded is None))

def pdf_to_images(pdf_bytes: bytes, dpi: int = 150):
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    for i in range(len(doc)):
        page = doc[i]
        pix = page.get_pixmap(dpi=dpi)
        img_bytes = pix.tobytes("png")
        images.append({"bytes": img_bytes, "mime": "image/png", "name": f"page_{i+1}.png"})
    return images

def image_file_to_bytes(file) -> dict:
    # Normaliza a PNG para mejor OCR
    img = Image.open(file).convert("RGB")
    bio = BytesIO()
    img.save(bio, format="PNG")
    return {"bytes": bio.getvalue(), "mime": "image/png", "name": file.name}

if btn and uploaded is not None:
    try:
        file_bytes = uploaded.getvalue()
        ext = uploaded.name.lower().split(".")[-1]

        with st.spinner("Procesando…"):
            if ext == "pdf":
                images = pdf_to_images(file_bytes)
            else:
                images = [image_file_to_bytes(uploaded)]

            hint = None if doc_type == "Auto" else doc_type
            result = ocr_and_extract_from_images(images, document_type_hint=hint)

        st.success("Listo ✅")

        st.subheader("Texto (OCR)")
        st.text_area("Texto extraído", value=result.full_text, height=300)

        st.subheader("Extracción estructurada")
        st.json(result.fields)

        # Intento de tabla de items si existe
        items = result.fields.get("items", [])
        df_items = pd.DataFrame(items) if isinstance(items, list) else pd.DataFrame()

        if not df_items.empty:
            st.subheader("Items detectados")
            st.dataframe(df_items, use_container_width=True)

        # Exportables
        st.subheader("Exportar")
        txt_out = result.full_text.strip()

        json_out = json.dumps(result.fields, ensure_ascii=False, indent=2)

        c1, c2, c3, c4, c5 = st.columns(5)
        with c1:
            st.download_button("TXT", txt_out.encode("utf-8"), "documento_ocr.txt", "text/plain")
        with c2:
            st.download_button("DOCX", to_docx_bytes("Documento (OCR)", txt_out), "documento_ocr.docx")
        with c3:
            st.download_button("PDF", to_pdf_bytes("Documento (OCR)", txt_out), "documento_ocr.pdf", "application/pdf")
        with c4:
            st.download_button("JSON (campos)", json_out.encode("utf-8"), "campos.json", "application/json")
        with c5:
            # CSV de items si existe, si no, CSV de campos (key/value)
            if not df_items.empty:
                csv = df_items.to_csv(index=False).encode("utf-8")
                st.download_button("CSV (items)", csv, "items.csv", "text/csv")
            else:
                kv = pd.DataFrame([{"campo": k, "valor": v} for k, v in result.fields.items()])
                st.download_button("CSV (campos)", kv.to_csv(index=False).encode("utf-8"), "campos.csv", "text/csv")

    except Exception as e:
        # Esto imprime el error REAL en los logs de Streamlit (Manage app -> Logs)
        print("DOCS_MODULE_ERROR:", repr(e))

        if show_maintenance_instead_of_api_error(e):
            st.warning(MAINTENANCE_MSG)
        else:
            st.error("Ocurrió un error inesperado. Contacta al administrador del portal.")

            # Solo si DEBUG=true en Secrets, muestra detalles para ti
            if str(st.secrets.get("DEBUG", "false")).lower() == "true":
                with st.expander("🛠️ Detalle técnico (solo admin)", expanded=False):
                    st.exception(e)
