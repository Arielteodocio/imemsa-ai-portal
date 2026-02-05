import json
import pandas as pd
import streamlit as st
from utils_auth import require_password
from utils_nav import require_tools_mode, tools_sidebar_controls
from utils_ui import hide_streamlit_sidebar_pages

require_password()
require_tools_mode()
tools_sidebar_controls()
hide_streamlit_sidebar_pages()




from services.nlp_ops_openai import analyze_ticket
from utils_excel_multi import to_xlsx_multiple_sheets
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

st.set_page_config(page_title="NLP Corporativo", page_icon="🧠", layout="wide")

st.title("🧠 NLP Corporativo (Clasificación y priorización)")
st.caption(
    "Clasifica solicitudes internas correo, asigna área destino, estima prioridad y extrae datos clave. "
    "  "
)

texto = st.text_area(
    "Pega aquí el correo o solicitud",
    height=260,
    placeholder="Ej: 'Necesito pagar hoy al proveedor X, factura 1234, OC 456... impacta embarque...'",
)

btn = st.button("Analizar", type="primary", disabled=(not texto.strip()))

if btn:
    try:
        with st.spinner("Analizando…"):
            r = analyze_ticket(texto.strip())

        st.success("Listo ✅")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Área destino", r.area or "—")
        with c2:
            st.metric("Tipo", r.tipo_solicitud or "—")
        with c3:
            st.metric("Prioridad", r.prioridad or "—")

        if r.motivo_prioridad:
            st.caption(f"Motivo prioridad: {r.motivo_prioridad}")

        # Faltantes (regla Tesorería)
        if r.faltantes:
            st.warning("Faltantes para poder atender la solicitud:")
            st.write("- " + "\n- ".join(r.faltantes))

        st.subheader("Resumen")
        st.write(r.resumen or "—")

        st.subheader("Datos clave")
        st.json(r.datos_clave)

        st.subheader("Acciones sugeridas")
        df_actions = pd.DataFrame(r.acciones) if r.acciones else pd.DataFrame(
            columns=["accion", "responsable_sugerido", "prioridad", "plazo_sugerido"]
        )
        df_actions = st.data_editor(df_actions, use_container_width=True, num_rows="dynamic")

        st.subheader("Exportar")

        json_out = json.dumps(
            {
                "area": r.area,
                "tipo_solicitud": r.tipo_solicitud,
                "prioridad": r.prioridad,
                "motivo_prioridad": r.motivo_prioridad,
                "resumen": r.resumen,
                "datos_clave": r.datos_clave,
                "faltantes": r.faltantes,
                "acciones": df_actions.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        )

        xlsx_bytes = to_xlsx_multiple_sheets(
            {
                "Resumen": pd.DataFrame([{
                    "area": r.area,
                    "tipo_solicitud": r.tipo_solicitud,
                    "prioridad": r.prioridad,
                    "motivo_prioridad": r.motivo_prioridad,
                    "resumen": r.resumen
                }]),
                "Datos_clave": pd.DataFrame([r.datos_clave]),
                "Faltantes": pd.DataFrame([{"faltante": x} for x in (r.faltantes or [])]),
                "Acciones": df_actions,
            }
        )

        c1, c2 = st.columns(2)
        with c1:
            st.download_button("Descargar JSON", json_out.encode("utf-8"), "nlp_corporativo.json", "application/json")
        with c2:
            st.download_button(
                "Descargar Excel",
                xlsx_bytes,
                "nlp_corporativo.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    except Exception as e:
        print("NLP_CORP_ERROR:", repr(e))

        if show_maintenance_instead_of_api_error(e):
            st.warning(MAINTENANCE_MSG)
        else:
            st.error("Ocurrió un error inesperado. Contacta al administrador del portal.")

            if str(st.secrets.get("DEBUG", "false")).lower() == "true":
                with st.expander("🛠️ Detalle técnico (solo admin)", expanded=False):
                    st.exception(e)

