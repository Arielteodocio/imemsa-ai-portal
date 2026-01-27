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
        raise RuntimeError("Falta OPENAI_API_KEY. Configuralo en Streamlit Secrets.")
    return key


def _to_data_url(img_bytes: bytes, mime: str) -> str:
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def ocr_and_extract_from_images(
    images: List[Dict[str, Any]],
    document_type_hint: Optional[str] = None,
) -> DocExtractResult:
    client = OpenAI(api_key=_get_api_key())

    hint = document_type_hint or "documento"

    instructions = (
        "Eres un asistente para OCR y extraccion estructurada.\n"
        "Devuelve SOLO JSON valido con este formato:\n"
        "{\n"
        '  "full_text": "...",\n'
        '  "fields": {\n'
        '    "tipo_documento": "...",\n'
        '    "folio": "...",\n'
        '    "fecha": "...",\n'
        '    "cliente_proveedor": "...",\n'
        '    "total": "...",\n'
        '    "moneda": "...",\n'
        '    "notas": "...",\n'
        '    "items": [\n'
        '      {"descripcion":"...","cantidad":"...","unidad":"...","precio_unitario":"...","importe":"..."}\n'
        "    ]\n"
        "  }\n"
        "}\n"
        "Reglas:\n"
        "- No inventes datos. Si no existe, usa null o cadena vacia.\n"
        "- Conserva numeros, unidades, fechas y nombres.\n"
        f"Contexto: el documento es un {hint}."
    )

    # ✅ Formato correcto para Responses API
    content = [{"type": "input_text", "text": "Realiza OCR y devuelve SOLO JSON."}]
    for im in images:
        data_url = _to_data_url(im["bytes"], im["mime"])
        content.append({"type": "input_image", "image_url": data_url})

    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=[{"role": "user", "content": content}],
        # ✅ obliga salida JSON válida
        text={"format": {"type": "json_object"}},
    )

    raw = (resp.output_text or "").strip()
    if not raw:
        raise RuntimeError("Respuesta vacia del modelo (output_text).")

    try:
        data = json.loads(raw)
    except Exception as ex:
        raise RuntimeError(f"JSON invalido devuelto por el modelo: {raw[:300]}") from ex

    return DocExtractResult(
        full_text=str(data.get("full_text", "") or ""),
        fields=dict(data.get("fields", {}) or {}),
        model="gpt-4o-mini",
    )

