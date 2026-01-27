import json
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from openai import OpenAI


@dataclass
class NlpOpsResult:
    categoria: str
    severidad: str
    resumen: str
    acciones: List[Dict[str, Any]]
    datos_clave: Dict[str, Any]
    modelo: str


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configuralo en Streamlit Secrets.")
    return key


def analyze_ticket(texto: str) -> NlpOpsResult:
    client = OpenAI(api_key=_get_api_key())

    instructions = (
        "Eres un asistente NLP para operaciones industriales.\n"
        "Tu tarea es analizar un ticket/reporte y devolver SOLO JSON valido.\n"
        "Reglas:\n"
        "- No inventes. Si no hay dato, usa null o ''.\n"
        "- Mantén tono profesional.\n"
        "Devuelve este JSON:\n"
        "{\n"
        '  "categoria": "Calidad|Mantenimiento|Produccion|Compras|Logistica|Seguridad|TI|Otro",\n'
        '  "severidad": "Baja|Media|Alta|Critica",\n'
        '  "resumen": "...",\n'
        '  "acciones": [\n'
        '     {"accion":"...", "responsable_sugerido":"...", "prioridad":"Alta|Media|Baja", "plazo_sugerido":"..."}\n'
        "  ],\n"
        '  "datos_clave": {\n'
        '     "area": "...",\n'
        '     "equipo": "...",\n'
        '     "turno": "...",\n'
        '     "fecha": "...",\n'
        '     "impacto": "...",\n'
        '     "palabras_clave": ["..."]\n'
        "  }\n"
        "}\n"
    )

    resp = client.responses.create(
        model="gpt-4o-mini",
        instructions=instructions,
        input=[
            {
                "role": "user",
                "content": [{"type": "input_text", "text": f"Ticket:\n{texto}"}],
            }
        ],
        text={"format": {"type": "json_object"}},
    )

    raw = (resp.output_text or "").strip()
    data = json.loads(raw)

    return NlpOpsResult(
        categoria=str(data.get("categoria", "") or ""),
        severidad=str(data.get("severidad", "") or ""),
        resumen=str(data.get("resumen", "") or ""),
        acciones=list(data.get("acciones", []) or []),
        datos_clave=dict(data.get("datos_clave", {}) or {}),
        modelo="gpt-4o-mini",
    )
