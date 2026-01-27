from __future__ import annotations

from openai import APIStatusError, RateLimitError


MAINTENANCE_MSG = (
    "⚠️ Estamos en mantenimiento.\n\n"
    "Por favor intenta más tarde o contacta al administrador del portal."
)


def show_maintenance_instead_of_api_error(e: Exception) -> bool:
    """
    Devuelve True si el error es de cuota/billing/rate limit y ya fue manejado
    como "mantenimiento". False si conviene mostrar otro error.
    """
    # RateLimitError suele mapearse a 429 también
    if isinstance(e, RateLimitError):
        return True

    # Errores con status code (429, 402, etc.)
    if isinstance(e, APIStatusError):
        status = getattr(e, "status_code", None)

        # Mensaje de OpenAI puede incluir "insufficient_quota", "billing", "quota", etc.
        msg = str(e).lower()

        if status in (402, 429) and any(
            k in msg for k in ["insufficient_quota", "quota", "billing", "exceeded your current quota"]
        ):
            return True

        # A veces 429 no es cuota, sino rate limit.
        if status == 429:
            return True

    return False
