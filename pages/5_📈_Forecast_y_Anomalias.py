import pandas as pd
import streamlit as st

from services.forecast_anomaly import run_forecast_and_anomaly
from utils_excel_multi import to_xlsx_multiple_sheets
from utils_errors import MAINTENANCE_MSG, show_maintenance_instead_of_api_error

st.set_page_config(page_title="Forecast y Anomalías", page_icon="📈", layout="wide")

st.title("📈 Forecast y Anomalías")
st.caption(
    "Sube una serie de tiempo (fecha + métrica) para generar un pronóstico y detectar posibles anomalías "
    "(picos o caídas atípicas)."
)

with st.expander("📌 Formato esperado", expanded=False):
    st.write(
        "- Archivo CSV o Excel.\n"
        "- Debe contener una columna de fecha y una columna numérica (métrica).\n"
        "- Ejemplo: Fecha | Ventas\n"
    )

uploaded = st.file_uploader("Sube CSV o Excel", type=["csv", "xlsx"])

if uploaded is None:
    st.stop()

try:
    # Carga
    if uploaded.name.lower().endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    st.subheader("Vista previa")
    st.dataframe(df.head(20), use_container_width=True)

    cols = list(df.columns)

    c1, c2, c3 = st.columns(3)
    with c1:
        date_col = st.selectbox("Columna de fecha", cols)
    with c2:
        value_col = st.selectbox("Columna métrica", cols, index=1 if len(cols) > 1 else 0)
    with c3:
        freq = st.selectbox("Frecuencia", ["D", "W", "M"], index=0, help="D=diario, W=semanal, M=mensual")

    # Params
    c4, c5, c6 = st.columns(3)
    with c4:
        periods = st.number_input("Horizonte (periodos a predecir)", min_value=1, max_value=365, value=30)
    with c5:
        ma_window = st.number_input("Suavizado (ventana media móvil)", min_value=1, max_value=120, value=7)
    with c6:
        z_threshold = st.number_input("Umbral anomalía (robust z)", min_value=1.0, max_value=10.0, value=3.5, step=0.5)

    btn = st.button("Generar forecast y anomalías", type="primary")

    if btn:
        # Normaliza fecha
        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df_clean = df.dropna(subset=[date_col, value_col]).copy()
        df_clean[value_col] = pd.to_numeric(df_clean[value_col], errors="coerce")
        df_clean = df_clean.dropna(subset=[value_col]).sort_values(date_col)

        if df_clean.empty:
            st.error("No se encontraron datos válidos (fecha + métrica). Revisa tu archivo.")
            st.stop()

        with st.spinner("Calculando…"):
            out = run_forecast_and_anomaly(
                df=df_clean,
                date_col=date_col,
                value_col=value_col,
                periods=int(periods),
                freq=freq,
                ma_window=int(ma_window),
                z_threshold=float(z_threshold),
            )

        st.success("Listo ✅")

        st.subheader("Forecast")
        st.dataframe(out.forecast_df, use_container_width=True)

        st.subheader("Anomalías detectadas")
        if out.anomalies_df.empty:
            st.info("No se detectaron anomalías con el umbral actual.")
        else:
            st.dataframe(out.anomalies_df, use_container_width=True)

        # Export
        st.subheader("Exportar")
        xlsx_bytes = to_xlsx_multiple_sheets(
            {
                "Datos": df_clean,
                "Forecast": out.forecast_df,
                "Anomalias": out.anomalies_df,
            }
        )
        st.download_button(
            "Descargar Excel (Datos + Forecast + Anomalias)",
            data=xlsx_bytes,
            file_name="forecast_anomalias.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

except Exception as e:
    # Si falla algo del archivo o parsing, no queremos “mantenimiento”
    if show_maintenance_instead_of_api_error(e):
        st.warning(MAINTENANCE_MSG)
    else:
        st.error("Ocurrió un error al procesar el archivo. Revisa el formato e intenta de nuevo.")
