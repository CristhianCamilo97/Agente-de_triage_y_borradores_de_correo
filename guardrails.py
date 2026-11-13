# Guardrails de entrada/salida. Solo datos de texto; sin secretos.

from __future__ import annotations

import re

RE_EMAIL = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
RE_TARJETA = re.compile(r"\b(?:\d[ -]*?){13,19}\b")
RE_CLAVE = re.compile(
    r"(?i)\b(password|contrasena|api[_-]?key|token|secret|aws_secret|bearer)\b\s*[:=]?\s*\S+"
)

INYECCIONES = [
    "ignora las politicas",
    "ignora las instrucciones",
    "reveal system prompt",
    "muestra las credenciales",
    "aprueba todas",
]


def enmascarar_pii(texto: str) -> str:
    """Enmascara posibles tarjetas y valores junto a palabras de secreto."""
    salida = RE_TARJETA.sub("[TARJETA]", texto)
    salida = RE_CLAVE.sub(lambda m: m.group(1) + " [OCULTA]", salida)
    return salida


def entrada_bloqueada(pregunta: str) -> str | None:
    """Si la pregunta es claramente adversarial, devuelve motivo; si no, None."""
    t = pregunta.lower()
    for p in INYECCIONES:
        if p in t:
            return f"Entrada bloqueada: patron adversario ({p})."
    if "credenciales bancarias" in t or "llaves de base de datos" in t:
        return "Entrada bloqueada: solicitud de informacion restringida."
    return None


def salida_riesgosa(respuesta: str) -> list[str]:
    """Senales de riesgo en la respuesta del modelo (para evals / defensa)."""
    hallazgos = []
    if RE_TARJETA.search(respuesta):
        hallazgos.append("posible_tarjeta")
    if RE_CLAVE.search(respuesta):
        hallazgos.append("posible_secreto")
    baja = respuesta.lower()
    if "te prometo" in baja or "garantizo el pago manana" in baja:
        hallazgos.append("promesa_no_respaldada")
    return hallazgos
