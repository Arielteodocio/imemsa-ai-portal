import io
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from utils_ui import render_title

import pandas as pd
import requests
import streamlit as st

# ==========================================================
# PÁGINA: 🧠 NLP Operación
# Clasifica solicitudes internas (correo/ticket) y sugiere acciones
#
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
st.markdown("# 🧠 NLP Operación")
st.caption(
    "Pega un correo/solicitud interna y obtén: **área destino**, **tipo**, **prioridad**, "
    "**datos clave**, **faltantes** y **acciones sugeridas**."
)

if hasattr(st, "page_link"):
    st.page_link("app.py", label="⬅️ Volver al Portafolio", icon="🏠", use_container_width=True)

st.divider()

with st.expander("📌 Qué hace y qué no hace", expanded=False):
    st.write(
        "- No inventa datos: si faltan factura/OC/proveedor/fecha, lo marca como **faltante**.\n"
        "- Mantiene números, folios, montos y nombres propios.\n"
        "- Puedes editar acciones antes de exportar."
    )

# ==========================================================
# OpenAI Chat Completions via HTTP (sin SDK)
# ==========================================================
MODEL = "gpt-4o-mini"

def _get_openai_api_key() -> Optional[str]:
    return (
        st.secrets.get("OPENAI_API_KEY") if hasattr(st, "secrets") else None
    ) or os.getenv("OPENAI_API_KEY")


def _extract_json(text: str) -> Dict[str, Any]:
    """
    El modelo debe devolver JSON. Si viene con texto extra,
    intentamos extraer el primer objeto JSON.
    """
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            raise ValueError("No se encontró JSON en la respuesta del modelo.")
        return json.loads(m.group(0))


@dataclass
class TicketResult:
    area: str
    tipo_solicitud: str
    prioridad: str
    motivo_prioridad: str
    resumen: str
    datos_clave: Dict[str, Any]
    faltantes: List[str]
    acciones: List[Dict[str, Any]]


def analyze_ticket(texto: str, contexto: str = "") -> TicketResult:
    api_key = _get_openai_api_key()
    if not api_key:
        st.error("Falta la API Key.")
        st.info(
            "En Streamlit Cloud agrega un Secret llamado **OPENAI_API_KEY** "
            "o define la variable de entorno `OPENAI_API_KEY`."
        )
        st.stop()

    schema = {
        "area": "Tesorería | Compras | Producción | Calidad | Almacén | Logística | Ventas | Sistemas | RH | Dirección | Otro | ''",
        "tipo_solicitud": "Pago | Cotización | Compra | Reclamo | Soporte TI | Envío | Producción | Calidad | Reporte | Otro | ''",
        "prioridad": "alta | media | baja | ''",
        "motivo_prioridad": "string o '' (por qué es alta/media/baja, basado en el texto)",
        "resumen": "string (3-6 líneas)",
        "datos_clave": {
            "proveedor": "string o ''",
            "cliente": "string o ''",
            "monto": "string o ''",
            "moneda": "string o ''",
            "factura": "string o ''",
            "oc": "string o ''",
            "fecha_limite": "string o ''",
            "proyecto": "string o ''",
            "impacto": "string o ''",
        },
        "faltantes": ["string (dato faltante crítico)"],
        "acciones": [
            {
                "accion": "string",
                "responsable_sugerido": "string o ''",
                "prioridad": "alta|media|baja o ''",
                "plazo_sugerido": "string o ''",
            }
        ],
    }

    system = (
        "Eres un analista de operaciones. Clasificas solicitudes internas y extraes información clave. "
        "Devuelve SOLO un JSON válido (sin markdown, sin explicación). "
        "Reglas: no inventes datos. Si no aparece, usa '' o lista vacía."
    )

    user = (
        "Analiza el siguiente texto (correo/ticket) y devuelve el JSON con el esquema EXACTO.\n\n"
        "Criterios de prioridad:\n"
        "- alta: riesgo de paro/embarque, cliente crítico, fecha hoy/mañana, seguridad, impacto financiero fuerte.\n"
        "- media: afecta operación pero no es urgente hoy.\n"
        "- baja: informativo, mejora, sin fechas cercanas.\n\n"
        "Regla Tesorería: si es pago, marca como faltantes si no hay proveedor, monto, factura/OC o fecha límite.\n\n"
        f"Contexto adicional (si existe): {contexto}\n\n"
        f"ESQUEMA:\n{json.dumps(schema, ensure_ascii=False)}\n\n"
        f"TEXTO:\n{texto}"
    )

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.2,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    if resp.status_code >= 400:
        st.error(f"Error al analizar (HTTP {resp.status_code}).")
        try:
            st.code(resp.json())
        except Exception:
            st.code(resp.text[:2000])
        st.stop()

    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    obj = _extract_json(content)

    # Normalización defensiva
    area = (obj.get("area") or "").strip()
    tipo = (obj.get("tipo_solicitud") or "").strip()
    prioridad = (obj.get("prioridad") or "").strip()
    motivo = (obj.get("motivo_prioridad") or "").strip()
    resumen = (obj.get("resumen") or "").strip()

    datos = obj.get("datos_clave") or {}
    if not isinstance(datos, dict):
        datos = {}

    falt = obj.get("faltantes") or []
    if not isinstance(falt, list):
        falt = []
    falt = [str(x).strip() for x in falt if str(x).strip()]

    acciones = obj.get("acciones") or []
    if not isinstance(acciones, list):
        acciones = []

    cleaned_actions: List[Dict[str, Any]] = []
    for a in acciones:
        if not isinstance(a, dict):
            continue
        act = (a.get("accion") or "").strip()
        if not act:
            continue
        cleaned_actions.append(
            {
                "accion": act,
                "responsable_sugerido": (a.get("responsable_sugerido") or "").strip(),
                "prioridad": (a.get("prioridad") or "").strip(),
                "plazo_sugerido": (a.get("plazo_sugerido") or "").strip(),
            }
        )

    return TicketResult(
        area=area,
        tipo_solicitud=tipo,
        prioridad=prioridad,
        motivo_prioridad=motivo,
        resumen=resumen,
        datos_clave=datos,
        faltantes=falt,
        acciones=cleaned_actions,
    )


# ==========================================================
# Export helper (Excel multi-hojas, opcional)
# ==========================================================
def to_xlsx_multiple_sheets(sheets: Dict[str, pd.DataFrame]) -> Optional[bytes]:
    try:
        import openpyxl  # noqa: F401
    except Exception:
        return None

    bio = io.BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        for name, df in sheets.items():
            df.to_excel(writer, index=False, sheet_name=str(name)[:31])
    return bio.getvalue()


# ==========================================================
# UI
# ==========================================================
contexto = st.text_input(
    "Contexto adicional (opcional)",
    placeholder="Ej: 'Solicitud de Tesorería / proveedor frecuente / embarque mañana'…",
)

texto = st.text_area(
    "Pega aquí el correo o solicitud",
    height=280,
    placeholder="Ej: 'Necesito pagar hoy al proveedor X, factura 1234, OC 456... impacta embarque...' ",
)

btn = st.button("Analizar", type="primary", disabled=(not texto.strip()), use_container_width=True)

if btn:
    if len(texto) > 25000:
        st.warning("El texto es muy largo. Divide en partes (recomendado: < 25,000 caracteres).")
        st.stop()

    with st.spinner("Analizando…"):
        r = analyze_ticket(texto.strip(), contexto=contexto.strip())

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
    df_actions = st.data_editor(df_actions, use_container_width=True, num_rows="dynamic", key="actions_editor")

    # Export
    st.divider()
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

    sheets = {
        "Resumen": pd.DataFrame(
            [{
                "area": r.area,
                "tipo_solicitud": r.tipo_solicitud,
                "prioridad": r.prioridad,
                "motivo_prioridad": r.motivo_prioridad,
                "resumen": r.resumen,
            }]
        ),
        "Datos_clave": pd.DataFrame([r.datos_clave]),
        "Faltantes": pd.DataFrame([{"faltante": x} for x in (r.faltantes or [])]),
        "Acciones": df_actions,
    }

    xlsx_bytes = to_xlsx_multiple_sheets(sheets)

    cA, cB = st.columns(2)
    with cA:
        st.download_button(
            "Descargar JSON",
            data=json_out.encode("utf-8"),
            file_name="nlp_operacion.json",
            mime="application/json",
            use_container_width=True,
        )
    with cB:
        if xlsx_bytes is None:
            st.info("Excel: agrega `openpyxl` a requirements.txt.")
        else:
            st.download_button(
                "Descargar Excel",
                data=xlsx_bytes,
                file_name="nlp_operacion.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )

