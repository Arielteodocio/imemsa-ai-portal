import io
import os
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import pandas as pd
import requests
import streamlit as st

# ==========================================================
# PÁGINA: 📈 Forecast y anomalías
# - Compatible con el proyecto base (login en app.py)
# - SIN st.set_page_config() (solo en app.py)
# - SIN st.switch_page() / st.rerun() (evita loops)
# ==========================================================

# --------- Login guard (misma llave que app.py del proyecto base)
def require_login() -> None:
    if not st.session_state.get("auth", False):
        st.error("🔒 Inicia sesión para usar esta herramienta.")
        if hasattr(st, "page_link"):
            st.page_link("app.py", label="Ir al Login", icon="🔐", use_container_width=True)
        st.stop()


require_login()

# --------- UI Header
st.markdown("# 📈 Forecast y anomalías")
st.caption(
    "Sube una serie de tiempo (fecha + métrica) para generar un **pronóstico** y detectar "
    "**anomalías** (picos/caídas atípicas) con un método robusto."
)

if hasattr(st, "page_link"):
    st.page_link("app.py", label="⬅️ Volver al Portafolio", icon="🏠", use_container_width=True)

st.divider()

with st.expander("📌 Formato esperado", expanded=False):
    st.write(
        "- Archivo CSV o Excel.\n"
        "- Debe contener una columna de **fecha** y una columna **numérica** (métrica).\n"
        "- Ejemplo: `Fecha | Ventas`."
    )

# ==========================================================
# Core: forecast (Holt simple) + anomalías (robust z-score)
# ==========================================================
@dataclass
class ForecastAnomalyOutput:
    forecast_df: pd.DataFrame
    anomalies_df: pd.DataFrame
    series_df: pd.DataFrame


def _make_regular_series(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    freq: str,
    agg: str,
    fill_method: str,
) -> pd.Series:
    d = df[[date_col, value_col]].copy()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d[value_col] = pd.to_numeric(d[value_col], errors="coerce")
    d = d.dropna(subset=[date_col, value_col]).sort_values(date_col)
    if d.empty:
        raise ValueError("No se encontraron datos válidos (fecha + métrica).")

    d = d.set_index(date_col)

    if agg == "sum":
        s = d[value_col].resample(freq).sum()
    else:
        s = d[value_col].resample(freq).mean()

    if fill_method == "interpolate":
        s = s.interpolate(limit_direction="both")
    elif fill_method == "ffill":
        s = s.ffill().bfill()
    else:
        s = s.fillna(0)

    return s


def _holt_forecast(series: pd.Series, periods: int, alpha: float, beta: float) -> Tuple[pd.Series, pd.Series]:
    """
    Holt (double exponential smoothing) sin dependencias externas.
    Retorna:
      - fitted (in-sample one-step forecast)
      - forecast (out-of-sample)
    """
    y = series.astype(float).values
    if len(y) < 2:
        raise ValueError("Se requieren al menos 2 puntos para pronosticar.")

    level = y[0]
    trend = y[1] - y[0]
    fitted = []

    for i in range(len(y)):
        if i == 0:
            fitted.append(y[0])
            continue
        prev_level = level
        level = alpha * y[i] + (1 - alpha) * (level + trend)
        trend = beta * (level - prev_level) + (1 - beta) * trend
        fitted.append(level + trend)

    fitted_s = pd.Series(fitted, index=series.index)

    # forecast future
    last_level = level
    last_trend = trend
    future = [last_level + (i + 1) * last_trend for i in range(periods)]
    return fitted_s, pd.Series(future)


def _robust_z(residual: pd.Series) -> pd.Series:
    """
    Robust z-score usando MAD.
    z = 0.6745 * (x - median) / MAD
    """
    med = residual.median()
    mad = (residual - med).abs().median()
    if mad == 0 or pd.isna(mad):
        # si MAD=0, devuelve 0's para evitar división por cero
        return pd.Series([0.0] * len(residual), index=residual.index)
    z = 0.6745 * (residual - med) / mad
    return z


def run_forecast_and_anomaly(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    freq: str,
    agg: str,
    periods: int,
    ma_window: int,
    z_threshold: float,
    alpha: float,
    beta: float,
    fill_method: str,
) -> ForecastAnomalyOutput:
    s = _make_regular_series(df, date_col, value_col, freq=freq, agg=agg, fill_method=fill_method)

    # Smoothing base (rolling mean) para residuales
    smooth = s.rolling(window=max(2, int(ma_window)), min_periods=1).mean()
    residual = s - smooth
    z = _robust_z(residual)

    anomalies = s[abs(z) >= z_threshold].copy()
    anomalies_df = pd.DataFrame(
        {
            date_col: anomalies.index,
            value_col: anomalies.values,
            "z_robusto": z.loc[anomalies.index].values,
            "residual": residual.loc[anomalies.index].values,
        }
    )

    fitted, future_vals = _holt_forecast(s, periods=int(periods), alpha=float(alpha), beta=float(beta))

    # future index
    last_ts = s.index.max()
    future_index = pd.date_range(start=last_ts, periods=int(periods) + 1, freq=freq, inclusive="right")
    forecast = pd.Series(future_vals.values, index=future_index)

    forecast_df = pd.DataFrame({date_col: forecast.index, "forecast": forecast.values})

    series_df = pd.DataFrame(
        {
            date_col: s.index,
            value_col: s.values,
            "suavizado": smooth.values,
            "residual": residual.values,
            "z_robusto": z.values,
            "fitted_holt": fitted.values,
        }
    )

    return ForecastAnomalyOutput(forecast_df=forecast_df, anomalies_df=anomalies_df, series_df=series_df)


# ==========================================================
# Export helper (opcional Excel multi-hojas)
# ==========================================================
def to_xlsx_multiple_sheets(sheets: Dict[str, pd.DataFrame]) -> Optional[bytes]:
    try:
        import openpyxl  # noqa: F401
    except Exception:
        return None

    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in sheets.items():
            safe = str(name)[:31]  # limit Excel sheet name
            df.to_excel(writer, index=False, sheet_name=safe)
    return bio.getvalue()


# ==========================================================
# UI
# ==========================================================
uploaded = st.file_uploader("Sube CSV o Excel", type=["csv", "xlsx"])

if uploaded is None:
    st.stop()

# Carga
if uploaded.name.lower().endswith(".csv"):
    df = pd.read_csv(uploaded)
else:
    df = pd.read_excel(uploaded)

st.subheader("Vista previa")
st.dataframe(df.head(25), use_container_width=True)

cols = list(df.columns)
if len(cols) < 2:
    st.error("El archivo debe tener al menos 2 columnas (fecha y métrica).")
    st.stop()

c1, c2, c3 = st.columns(3)
with c1:
    date_col = st.selectbox("Columna de fecha", cols, index=0)
with c2:
    value_col = st.selectbox("Columna métrica", cols, index=1 if len(cols) > 1 else 0)
with c3:
    freq = st.selectbox("Frecuencia", ["D", "W", "M"], index=0, help="D=diario, W=semanal, M=mensual")

c4, c5, c6 = st.columns(3)
with c4:
    agg = st.selectbox("Agregación al reagrupar", ["sum", "mean"], index=0, help="sum recomendado para ventas/volumen")
with c5:
    periods = st.number_input("Horizonte (periodos a predecir)", min_value=1, max_value=365, value=30)
with c6:
    ma_window = st.number_input("Suavizado (ventana media móvil)", min_value=2, max_value=180, value=7)

c7, c8, c9 = st.columns(3)
with c7:
    z_threshold = st.number_input("Umbral anomalía (z robusto)", min_value=1.5, max_value=10.0, value=3.5, step=0.5)
with c8:
    fill_method = st.selectbox("Relleno de faltantes", ["interpolate", "ffill", "zero"], index=0)
with c9:
    st.caption("Holt smoothing (avanzado)")
    alpha = st.slider("alpha", 0.05, 0.95, 0.35, 0.05)
    beta = st.slider("beta", 0.01, 0.95, 0.15, 0.02)

btn = st.button("Generar forecast y anomalías", type="primary", use_container_width=True)

if btn:
    try:
        # Normaliza datos base sin modificar df original
        df_clean = df.copy()

        with st.spinner("Calculando…"):
            out = run_forecast_and_anomaly(
                df=df_clean,
                date_col=date_col,
                value_col=value_col,
                freq=freq,
                agg=agg,
                periods=int(periods),
                ma_window=int(ma_window),
                z_threshold=float(z_threshold),
                alpha=float(alpha),
                beta=float(beta),
                fill_method=fill_method,
            )

        st.success("Listo ✅")

        # ----- Plots (matplotlib)
        try:
            import matplotlib.pyplot as plt
        except Exception:
            st.warning("No pude importar matplotlib. Se mostrarán solo tablas.")
            plt = None  # type: ignore

        if plt is not None:
            # Gráfica: serie + suavizado + forecast
            st.subheader("Histórico + suavizado + forecast")
            fig1 = plt.figure()
            plt.plot(out.series_df[date_col], out.series_df[value_col], label="Histórico")
            plt.plot(out.series_df[date_col], out.series_df["suavizado"], label="Suavizado")
            plt.plot(out.forecast_df[date_col], out.forecast_df["forecast"], label="Forecast")
            plt.xlabel("Fecha")
            plt.ylabel(value_col)
            plt.legend()
            st.pyplot(fig1)
            plt.close(fig1)

            # Gráfica: anomalías
            st.subheader("Anomalías detectadas")
            fig2 = plt.figure()
            plt.plot(out.series_df[date_col], out.series_df[value_col], label="Histórico")
            if not out.anomalies_df.empty:
                plt.scatter(out.anomalies_df[date_col], out.anomalies_df[value_col], label="Anomalías")
            plt.xlabel("Fecha")
            plt.ylabel(value_col)
            plt.legend()
            st.pyplot(fig2)
            plt.close(fig2)

        # ----- Tablas
        st.subheader("Serie preparada")
        st.dataframe(out.series_df, use_container_width=True)

        st.subheader("Forecast")
        st.dataframe(out.forecast_df, use_container_width=True)

        st.subheader("Anomalías")
        if out.anomalies_df.empty:
            st.info("No se detectaron anomalías con el umbral actual.")
        else:
            st.dataframe(out.anomalies_df, use_container_width=True)

        # ----- Exportar
        st.divider()
        st.subheader("Exportar")

        cA, cB, cC = st.columns(3)

        with cA:
            st.download_button(
                "CSV (serie preparada)",
                out.series_df.to_csv(index=False).encode("utf-8"),
                file_name="serie_preparada.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "CSV (forecast)",
                out.forecast_df.to_csv(index=False).encode("utf-8"),
                file_name="forecast.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with cB:
            st.download_button(
                "CSV (anomalías)",
                out.anomalies_df.to_csv(index=False).encode("utf-8"),
                file_name="anomalias.csv",
                mime="text/csv",
                use_container_width=True,
            )

        with cC:
            xlsx_bytes = to_xlsx_multiple_sheets(
                {
                    "Serie": out.series_df,
                    "Forecast": out.forecast_df,
                    "Anomalias": out.anomalies_df,
                }
            )
            if xlsx_bytes is None:
                st.info("Excel: agrega `openpyxl` a requirements.txt.")
            else:
                st.download_button(
                    "Excel (3 hojas)",
                    data=xlsx_bytes,
                    file_name="forecast_anomalias.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                )

    except Exception as e:
        st.error("Ocurrió un error al procesar el archivo. Revisa el formato e intenta de nuevo.")
        with st.expander("🛠️ Detalle técnico (admin)", expanded=False):
            st.exception(e)

