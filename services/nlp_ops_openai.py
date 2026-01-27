import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI


@dataclass
class NlpOpsResult:
    area: str
    tipo_solicitud: str
    prioridad: str
    motivo_prioridad: str
    resumen: str
    acciones: List[Dict[str, Any]]
    datos_clave: Dict[str, Any]
    faltantes: List[str]
    modelo: str


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configúralo en Streamlit Secrets.")
    return key


def analyze_ticket(texto: str) -> NlpOpsResult:
    client = OpenAI(api_key=_get_api_key())

    instructions = (
    "Eres un asistente NLP para corporativo.\n"
    "Analiza solicitudes (correo/ticket) y devuelve SOLO JSON valido (formato json).\n"
    "IMPORTANTE: responde en JSON (json) estricto, sin texto extra.\n\n"
    "REGLAS CLAVE:\n"
    "- Prioridad 'Critica' cuando el texto indique 'impacta' (operacion, embarque, cierre, cobranza, paro, penalizacion).\n"
    "- Tesoreria: para pagos, son obligatorios Factura y OC. Si falta alguno, listalo en 'faltantes'.\n"
    "- Comercial: el caso mas comun es 'Cotizacion'.\n"
    "- No inventes datos. Si no existe, usa null o ''.\n\n"
    "Devuelve este JSON:\n"
    "{\n"
    '  "area": "Comercial|Finanzas|Contabilidad|Tesoreria|RRHH|TI|Legal|Direccion|Otro",\n'
    '  "tipo_solicitud": "Cotizacion|Pago|Factura_CFDI|Nomina_Incidencia|Alta_Baja|Soporte_TI|Otro",\n'
    '  "prioridad": "Baja|Media|Alta|Critica",\n'
    '  "motivo_prioridad": "...",\n'
    '  "resumen": "...",\n'
    '  "datos_clave": {\n'
    '     "cliente": "...",\n'
    '     "proveedor": "...",\n'
    '     "factura": "...",\n'
    '     "oc": "...",\n'
    '     "monto": "...",\n'
    '     "moneda": "...",\n'
    '     "fecha_limite": "...",\n'
    '     "contacto": "..."\n'
    "  },\n"
    '  "faltantes": ["..."],\n'
    '  "acciones": [\n'
    '     {"accion":"...", "responsable_sugerido":"...", "prioridad":"Alta|Media|Baja", "plazo_sugerido":"..."}\n'
    "  ]\n"
    "}\n"
    )


    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=[{"role": "user", "content": [{"type": "input_text", "text": f"Solicitud:\n{texto}"}]}],
        text={"format": {"type": "json_object"}},
    )

    raw = (resp.output_text or "").strip()
    if not raw:
        raise RuntimeError("Respuesta vacía del modelo (output_text).")

    try:
        data = json.loads(raw)
    except Exception as ex:
        raise RuntimeError(f"JSON inválido devuelto por el modelo: {raw[:300]}") from ex

    # ✅ Normalizaciones defensivas
    area = str(data.get("area", "") or "")
    tipo = str(data.get("tipo_solicitud", "") or "")
    prioridad = str(data.get("prioridad", "") or "")
    motivo = str(data.get("motivo_prioridad", "") or "")
    resumen = str(data.get("resumen", "") or "")

    datos = data.get("datos_clave", {}) or {}
    if not isinstance(datos, dict):
        datos = {}

    faltantes = data.get("faltantes", []) or []
    if not isinstance(faltantes, list):
        faltantes = [str(faltantes)]
    faltantes = [str(x) for x in faltantes]

    acciones = data.get("acciones", []) or []
    if not isinstance(acciones, list):
        acciones = []
    acciones = [a for a in acciones if isinstance(a, dict)]

    return NlpOpsResult(
        area=area,
        tipo_solicitud=tipo,
        prioridad=prioridad,
        motivo_prioridad=motivo,
        resumen=resumen,
        datos_clave=datos,
        faltantes=faltantes,
        acciones=acciones,
        modelo="gpt-4o-mini",
    )

