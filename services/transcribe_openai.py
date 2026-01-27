from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from typing import Optional

from openai import OpenAI


@dataclass
class TranscriptionResult:
    text: str
    model: str


def _get_api_key() -> str:
    # Streamlit Cloud: puedes ponerlo en Secrets como OPENAI_API_KEY
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        raise RuntimeError("Falta OPENAI_API_KEY. Configúralo en Streamlit Secrets o variables de entorno.")
    return key


def transcribe_audio_bytes(
    audio_bytes: bytes,
    original_filename: str,
    model: str = "gpt-4o-mini-transcribe",
    language_hint: Optional[str] = None,
    prompt: Optional[str] = None,
) -> TranscriptionResult:
    """
    Transcribe audio -> text (cloud).
    No guarda audio: usa archivo temporal y lo borra al terminar.
    """

    client = OpenAI(api_key=_get_api_key())

    # Conserva extensión para que el endpoint identifique el formato.
    suffix = ""
    if "." in original_filename:
        suffix = "." + original_filename.split(".")[-1].lower()

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio_bytes)
        tmp.flush()

        with open(tmp.name, "rb") as f:
            params = {
                "model": model,
                "file": f,
                # Para estos modelos puedes pedir "text" o json; aquí usamos "text"
                "response_format": "text",
            }

            # Hint de idioma (opcional). Si no lo pasas, el modelo detecta.
            if language_hint and language_hint.lower() != "auto":
                params["language"] = language_hint

            # Prompt (opcional) para mejorar términos propios (IMEMSA, modelos, etc.)
            if prompt:
                params["prompt"] = prompt

            transcription = client.audio.transcriptions.create(**params)

    # En response_format="text", el SDK devuelve un string o un objeto; normalizamos:
    text = transcription if isinstance(transcription, str) else getattr(transcription, "text", "")
    return TranscriptionResult(text=text or "", model=model)
