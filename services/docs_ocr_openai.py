from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI


@dataclass
class DocExtractResult:
    full_text: str
    fields: Dict[str, Any]
    model: str


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configúralo en Streamlit Secrets.")
    return key


def _img_to_data_url(img_bytes: bytes, mime: str) -> str:
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def ocr_and_extract_from_images(
    images: List[Dict[str, Any]],
    document_type_hint: Optional[str] = None,
) -> DocExtractResult:
    """
    images: list of {"bytes": ..., "mime": "image/png"|"image/jpeg", "name": "page_1.png"}
    """
    client = OpenAI(api_key=_get_api_key())

    hint = document_type_hint or "documento"
    system = (
        "Eres un asistente para OCR y extracción estructurada.\n"
        "Objetivo:\n"
        "1) Extraer TODO el texto visible (OCR).\n"
        "2) Detectar campos clave en formato JSON.\n"
        "Reglas:\n"
        "- No inventes datos. Si no existe, deja null.\n"
        "- Conserva números, unidades, fechas y nombres.\n"
        "- Devuelve SOLO JSON con este formato:\n"
        "{\n"
        "  \"full_text\": \"...\",\n"
        "  \"fields\": {\n"
        "     \"tipo_documento\": \"...\",\n"
        "     \"folio\": \"...\",\n"
        "     \"fecha\": \"...\",\n"
        "     \"cliente_proveedor\": \"...\",\n"
        "     \"total\": \"...\",\n"
        "     \"moneda\": \"...\",\n"
        "     \"notas\": \"...\",\n"
        "     \"items\": [ {\"descripcion\":\"...\",\"cantidad\":\"...\",\"unidad\":\"...\",\"precio_unitario\":\"...\",\"importe\":\"...\"} ]\n"
        "  }\n"
        "}\n"
        f"Contexto: el documento es un {hint} (puede ser factura, orden de compra, reporte, checklist, etc.)."
    )

    content = [{"type": "text", "text": "Realiza OCR y extrae campos. Devuelve SOLO JSON."}]
    for im in images:
        content.append(
            {"type": "image_url", "image_url": {"url": _img_to_data_url(im["bytes"], im["mime"])}}
        )

    resp = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": content},
        ],
    )

    raw = resp.output_text.strip().replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)

    return DocExtractResult(
        full_text=str(data.get("full_text", "") or ""),
        fields=dict(data.get("fields", {}) or {}),
        model="gpt-4o-mini",
    )
