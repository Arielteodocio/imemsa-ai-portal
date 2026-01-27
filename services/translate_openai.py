from __future__ import annotations

import os
from dataclasses import dataclass
from openai import OpenAI


@dataclass
class TranslationResult:
    text: str
    model: str


def _get_api_key() -> str:
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configúralo en Streamlit Secrets.")
    return key


def translate_en_es(text: str, direction: str) -> TranslationResult:
    """
    direction:
      - "EN->ES"
      - "ES->EN"
    """
    client = OpenAI(api_key=_get_api_key())

    if direction not in ("EN->ES", "ES->EN"):
        raise ValueError("direction debe ser 'EN->ES' o 'ES->EN'.")

    source = "inglés" if direction == "EN->ES" else "español"
    target = "español" if direction == "EN->ES" else "inglés"

    system = (
        f"Eres un traductor profesional. Traduce del {source} al {target}.\n"
        "- Mantén el significado exacto y el tono.\n"
        "- Conserva nombres propios, siglas y unidades.\n"
        "- No agregues explicaciones ni notas.\n"
        "- Devuelve únicamente la traducción."
    )

    # Responses API (recomendada para nuevos proyectos)
    response = client.responses.create(
        model="gpt-4o-mini",
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": text},
        ],
    )

    return TranslationResult(text=response.output_text.strip(), model="gpt-4o-mini")
