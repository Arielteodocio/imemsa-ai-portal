from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI


@dataclass
class MinutesResult:
    title: str
    summary: str
    agreements: List[str]
    actions: List[Dict[str, Any]]
    model: str


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configúralo en Streamlit Secrets.")
    return key


def generate_minutes(transcript: str) -> MinutesResult:
    client = OpenAI(api_key=_get_api_key())

    system = (
        "Eres un asistente corporativo para generar minutas.\n"
        "A partir de una transcripción de reunión (texto), debes producir una salida en JSON ESTRICTO.\n"
        "Reglas:\n"
        "- No inventes datos. Si no está claro, usa null o 'No especificado'.\n"
        "- Respeta nombres propios y siglas.\n"
        "- Si no hay fecha compromiso, pon null.\n"
        "- Prioridad: 'Alta', 'Media' o 'Baja'.\n"
        "- Área: una de: 'Operación', 'Producción', 'Calidad', 'Compras', 'Ventas', 'Ingeniería', 'Finanzas', 'RH', 'Otro'.\n"
        "- Devuelve SOLO JSON (sin texto adicional).\n"
        "Formato JSON:\n"
        "{\n"
        "  \"title\": \"...\",\n"
        "  \"summary\": \"...\",\n"
        "  \"agreements\": [\"...\"],\n"
        "  \"actions\": [\n"
        "    {\n"
        "      \"accion\": \"...\",\n"
        "      \"responsable\": \"...\",\n"
        "      \"fecha_compromiso\": \"YYYY-MM-DD\" | null,\n"
        "      \"prioridad\": \"Alta\"|\"Media\"|\"Baja\",\n"
        "      \"area\": \"Operación\"|\"Producción\"|\"Calidad\"|\"Compras\"|\"Ventas\"|\"Ingeniería\"|\"Finanzas\"|\"RH\"|\"Otro\",\n"
        "      \"notas\": \"...\"\n"
        "    }\n"
        "  ]\n"
        "}\n"
    )

    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": transcript},
        ],
    )

    raw = response.output_text.strip()

    # Limpieza defensiva por si el modelo mete fences (raro, pero pasa)
    raw = raw.replace("```json", "").replace("```", "").strip()

    data: Dict[str, Any] = json.loads(raw)

    return MinutesResult(
        title=str(data.get("title", "Minuta de reunión") or "Minuta de reunión"),
        summary=str(data.get("summary", "") or ""),
        agreements=list(data.get("agreements", []) or []),
        actions=list(data.get("actions", []) or []),
        model="gpt-4o-mini",
    )
