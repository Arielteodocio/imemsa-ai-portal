from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class ForecastOutput:
    forecast_df: pd.DataFrame
    anomalies_df: pd.DataFrame


def _robust_zscore_mad(x: np.ndarray) -> np.ndarray:
    """
    Robust z-score usando Median Absolute Deviation (MAD).
    """
    x = x.astype(float)
    med = np.nanmedian(x)
    mad = np.nanmedian(np.abs(x - med))
    if mad == 0 or np.isnan(mad):
        return np.zeros_like(x, dtype=float)
    return 0.6745 * (x - med) / mad


def detect_anomalies(
    df: pd.DataFrame,
    value_col: str,
    z_threshold: float = 3.5,
) -> pd.DataFrame:
    """
    Detecta anomalías por robust z-score (MAD).
    """
    x = df[value_col].to_numpy(dtype=float)
    z = _robust_zscore_mad(x)

    out = df.copy()
    out["robust_z"] = z
    out["is_anomaly"] = np.abs(z) >= z_threshold
    out["anomaly_type"] = np.where(z > z_threshold, "alta", np.where(z < -z_threshold, "baja", "normal"))
    return out[out["is_anomaly"]].copy()


def forecast_moving_trend(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    periods: int,
    freq: str,
    ma_window: int = 7,
) -> pd.DataFrame:
    """
    Pronóstico rápido: suavizado por media móvil + tendencia lineal (OLS sobre el suavizado).
    Devuelve dataframe con fechas futuras y pronóstico.
    """
    d = df[[date_col, value_col]].copy()
    d = d.dropna()
    d = d.sort_values(date_col)

    y = d[value_col].astype(float).to_numpy()
    # Suavizado
    if ma_window < 2:
        y_smooth = y
    else:
        y_smooth = pd.Series(y).rolling(window=ma_window, min_periods=max(2, ma_window // 2)).mean().to_numpy()
        # rellena NaNs iniciales con valores reales
        mask = np.isnan(y_smooth)
        y_smooth[mask] = y[mask]

    # Trend lineal sobre índice temporal
    t = np.arange(len(y_smooth))
    a, b = np.polyfit(t, y_smooth, 1)  # y = a*t + b

    # fechas futuras
    last_date = pd.to_datetime(d[date_col].iloc[-1])
    future_dates = pd.date_range(start=last_date, periods=periods + 1, freq=freq)[1:]

    t_future = np.arange(len(y_smooth), len(y_smooth) + periods)
    yhat = a * t_future + b

    return pd.DataFrame({date_col: future_dates, "forecast": yhat})


def run_forecast_and_anomaly(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    periods: int,
    freq: str,
    ma_window: int,
    z_threshold: float,
) -> ForecastOutput:
    forecast_df = forecast_moving_trend(
        df=df, date_col=date_col, value_col=value_col, periods=periods, freq=freq, ma_window=ma_window
    )

    anomalies_df = detect_anomalies(df=df.sort_values(date_col), value_col=value_col, z_threshold=z_threshold)

    return ForecastOutput(forecast_df=forecast_df, anomalies_df=anomalies_df)
