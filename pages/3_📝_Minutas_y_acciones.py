import pandas as pd
import streamlit as st
from utils_auth import require_password
from utils_ui import hide_streamlit_sidebar_pages
from utils_nav import require_tools_mode, tools_sidebar_controls

require_password()
require_tools_mode()
tools_sidebar_controls()


hide_streamlit_sidebar_pages()


from services.minutes_openai import generate_minutes
from utils_export import to_docx_bytes, to_pdf_bytes
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error
from utils_excel import actions_to_xlsx_bytes


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





st.set_page_config(page_title="Minutas y acciones", page_icon="📝", layout="wide")

st.title("📝 Minutas y acciones")
st.caption(
    "Pega la transcripción de una reunión y genera una minuta con acuerdos y acciones. "
    "Entrega un resumen estructurado con responsables y fechas (cuando estén disponibles en el texto)."
)

with st.expander("🔒 Privacidad (cómo funciona)", expanded=False):
    st.write(
        "- El texto se procesa y se devuelven resultados estructurados.\n"
        "- No guardamos la transcripción ni la minuta.\n"
        "- Puedes exportar la información a tus formatos."
    )

transcript = st.text_area(
    "Transcripción",
    height=300,
    placeholder="Pega aquí la transcripción completa de la reunión…",
)

btn = st.button("Generar minuta", type="primary", disabled=(not transcript.strip()))

if btn:
    try:
        with st.spinner("Generando minuta…"):
            result = generate_minutes(transcript.strip())

        st.success("Listo ✅")

        # ---- Presentación
        st.subheader(result.title)
        st.write(result.summary if result.summary else "_(Sin resumen)_")

        st.subheader("Acuerdos")
        if result.agreements:
            for i, a in enumerate(result.agreements, start=1):
                st.write(f"{i}. {a}")
        else:
            st.info("No se detectaron acuerdos explícitos.")

        st.subheader("Acciones")
        actions = result.actions or []

        if actions:
            df = pd.DataFrame(actions)

            expected_cols = ["accion", "responsable", "fecha_compromiso", "prioridad", "area", "notas"]
            for c in expected_cols:
                if c not in df.columns:
                    df[c] = None
            df = df[expected_cols]

            edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic")
        else:
            st.info("No se detectaron acciones explícitas.")
            edited_df = pd.DataFrame(columns=["accion", "responsable", "fecha_compromiso", "prioridad", "area", "notas"])

        # ---- Exportables
        st.subheader("Exportar")

        lines = []
        lines.append(result.title)
        lines.append("")
        lines.append("RESUMEN")
        lines.append(result.summary or "")
        lines.append("")
        lines.append("ACUERDOS")
        if result.agreements:
            for i, a in enumerate(result.agreements, start=1):
                lines.append(f"{i}. {a}")
        else:
            lines.append("No se detectaron acuerdos.")
        lines.append("")
        lines.append("ACCIONES")
        if not edited_df.empty:
            for _, row in edited_df.iterrows():
                lines.append(
                    f"- Acción: {row.get('accion','')}\n"
                    f"  Responsable: {row.get('responsable','')}\n"
                    f"  Fecha compromiso: {row.get('fecha_compromiso','')}\n"
                    f"  Prioridad: {row.get('prioridad','')}\n"
                    f"  Área: {row.get('area','')}\n"
                    f"  Notas: {row.get('notas','')}"
                )
        else:
            lines.append("No se detectaron acciones.")
        txt_out = "\n".join(lines).strip()

        c1, c2, c3, c4, c5 = st.columns(5)

        with c1:
            st.download_button(
                "TXT",
                data=txt_out.encode("utf-8"),
                file_name="minuta.txt",
                mime="text/plain",
            )

        with c2:
            st.download_button(
                "DOCX",
                data=to_docx_bytes(result.title, txt_out),
                file_name="minuta.docx",
            )

        with c3:
            st.download_button(
                "PDF",
                data=to_pdf_bytes(result.title, txt_out),
                file_name="minuta.pdf",
                mime="application/pdf",
            )

        with c4:
            st.download_button(
                "CSV (acciones)",
                data=edited_df.to_csv(index=False).encode("utf-8"),
                file_name="acciones.csv",
                mime="text/csv",
            )

        with c5:
            st.download_button(
                "Excel (acciones)",
                data=actions_to_xlsx_bytes(edited_df),
                file_name="acciones.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        if show_maintenance_instead_of_api_error(e):
            st.warning(MAINTENANCE_MSG)
        else:
            st.error("Ocurrió un error inesperado. Contacta al administrador del portal.")

