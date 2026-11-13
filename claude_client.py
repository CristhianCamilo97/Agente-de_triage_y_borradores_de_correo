# Cliente Claude: Anthropic API key local o Bedrock en el Cloud Workspace.
# No hardcodear secretos. Lee solo variables de entorno / .env local (gitignored).

from __future__ import annotations

import os
from functools import lru_cache

DEFAULT_MODEL = os.environ.get("CLAUDE_MODEL", "claude-haiku-4-5")


def _cargar_dotenv() -> None:
    ruta = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.isfile(ruta):
        return
    with open(ruta, encoding="utf-8") as f:
        for linea in f:
            linea = linea.strip()
            if not linea or linea.startswith("#") or "=" not in linea:
                continue
            k, _, v = linea.partition("=")
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k and k not in os.environ:
                os.environ[k] = v


@lru_cache(maxsize=1)
def get_client():
    _cargar_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        from anthropic import Anthropic

        return Anthropic(api_key=api_key)

    # Bedrock (workspace del bootcamp): sin API key de Anthropic
    try:
        from anthropic import AnthropicBedrock

        region = os.environ.get("AWS_REGION", "us-east-1")
        return AnthropicBedrock(aws_region=region)
    except Exception as e:
        raise RuntimeError(
            "No hay ANTHROPIC_API_KEY ni cliente Bedrock disponible. "
            "Copia .env.example a .env o usa el Cloud Workspace del curso."
        ) from e


def model_id(alias: str | None = None) -> str:
    # En API directa el alias corto suele bastar; en Bedrock el workspace ya resuelve el id.
    return alias or DEFAULT_MODEL
