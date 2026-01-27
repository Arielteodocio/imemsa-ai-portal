import json
import pandas as pd
import streamlit as st

from services.nlp_ops_openai import analyze_ticket
from utils_excel_multi import to_xlsx_multiple_sheets
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

st.set_page_config(page_title="NLP Operación", page_icon="🧠", layout="wide")

st.title("🧠 NLP para Operación (Tickets y reportes)")
st.caption(
    "Analiza tickets/correos/reportes operativos para clasificar, estimar severidad, extraer datos clave "
    "y sugerir acciones."
)

with st.expander("💡 Ejemplos de uso", expanded=False):
    st.write(
        "- Ticket de mantenimiento: falla en bomba, ruido, vibración.\n"
        "- Reporte de calidad: defecto en gel coat, retrabajo, scrap.\n"
        "- Seguridad: incidente, casi accidente, EPP.\n"
    )

texto = st.text_area(
    "Pega el ticket / correo / reporte",
    height=260,
    placeholder="Ej: 'Se detectó fuga en la línea de resina...'",
)

btn = st.button("Analizar", type="primary", disabled=(not texto.strip()))

if btn:
    try:
        with st.spinner("Analizando…"):
            r = analyze_ticket(texto.strip())

        st.success("Listo ✅")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Categoría", r.categoria or "—")
        with c2:
            st.metric("Severidad", r.severidad or "—")
        with c3:
            st.caption(f"Modelo: {r.modelo}")

        st.subheader("Resumen")
        st.write(r.resumen or "—")

        st.subheader("Datos clave")
        st.json(r.datos_clave)

        st.subheader("Acciones sugeridas")
        df_actions = pd.DataFrame(r.acciones) if r.acciones else pd.DataFrame(
            columns=["accion", "responsable_sugerido", "prioridad", "plazo_sugerido"]
        )
        df_actions = st.data_editor(df_actions, use_container_width=True, num_rows="dynamic")

        # Exportables
        st.subheader("Exportar")

        json_out = json.dumps(
            {
                "categoria": r.categoria,
                "severidad": r.severidad,
                "resumen": r.resumen,
                "datos_clave": r.datos_clave,
                "acciones": df_actions.to_dict(orient="records"),
            },
            ensure_ascii=False,
            indent=2,
        )

        txt_out = (
            f"CATEGORIA: {r.categoria}\n"
            f"SEVERIDAD: {r.severidad}\n\n"
            f"RESUMEN:\n{r.resumen}\n\n"
            f"DATOS CLAVE:\n{json.dumps(r.datos_clave, ensure_ascii=False, indent=2)}\n\n"
            f"ACCIONES:\n{df_actions.to_csv(index=False)}"
        )

        xlsx_bytes = to_xlsx_multiple_sheets(
            {
                "Resumen": pd.DataFrame([{"categoria": r.categoria, "severidad": r.severidad, "resumen": r.resumen}]),
                "Datos_clave": pd.DataFrame([r.datos_clave]),
                "Acciones": df_actions,
            }
        )

        c1, c2, c3 = st.columns(3)
        with c1:
            st.download_button("JSON", json_out.encode("utf-8"), "nlp_operacion.json", "application/json")
        with c2:
            st.download_button(
                "Excel",
                xlsx_bytes,
                "nlp_operacion.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        with c3:
            st.download_button("TXT", txt_out.encode("utf-8"), "nlp_operacion.txt", "text/plain")

    except Exception as e:
        if show_maintenance_instead_of_api_error(e):
            st.warning(MAINTENANCE_MSG)
        else:
            st.error("Ocurrió un error inesperado. Contacta al administrador del portal.")

