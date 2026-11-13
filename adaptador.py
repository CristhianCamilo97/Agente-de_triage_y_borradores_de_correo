# Punto de entrada CLI: una pregunta al agente con guardrails + costo.

from __future__ import annotations

import json
import sys
import time

import costing
import guardrails
from agente import opciones
from claude_client import DEFAULT_MODEL, get_client, model_id


def correr(pregunta: str) -> dict:
    bloqueo = guardrails.entrada_bloqueada(pregunta)
    if bloqueo:
        return {"ok": False, "error": bloqueo, "respuesta": bloqueo}

    opts = opciones()
    client = get_client()
    t0 = time.monotonic()

    # Camino preferido: Claude Agent SDK (Cloud Workspace / entorno del curso).
    try:
        from claude_agent_sdk import query

        texto = ""
        usage = None
        for evento in query(pregunta, **{k: v for k, v in opts.items() if k != "system"}):
            # La forma exacta del evento depende de la version del SDK del workspace.
            if hasattr(evento, "text"):
                texto += evento.text or ""
            if hasattr(evento, "usage"):
                usage = evento.usage
        if not texto:
            texto = str(evento)
        lat = (time.monotonic() - t0) * 1000
        if usage is not None:
            costing.log_usage(feature="adaptador_sdk", model=DEFAULT_MODEL, usage=usage, latency_ms=lat)
        riesgos = guardrails.salida_riesgosa(texto)
        return {
            "ok": True,
            "respuesta": guardrails.enmascarar_pii(texto),
            "riesgos": riesgos,
            "modo": "agent_sdk",
        }
    except Exception:
        pass

    # Fallback demo: una sola llamada Messages API con system cacheado (sin tools MCP).
    # Sirve para probar API key / costo cuando el SDK no esta instalado.
    r = client.messages.create(
        model=model_id(DEFAULT_MODEL),
        max_tokens=500,
        system=opts["system"],
        messages=[
            {
                "role": "user",
                "content": (
                    "Modo demo sin MCP: explica en 4 frases como triarias este pedido "
                    f"usando herramientas MCP (listar/obtener/politicas/guardar) y auditor:\n{pregunta}"
                ),
            }
        ],
    )
    lat = (time.monotonic() - t0) * 1000
    entry = costing.log_usage(feature="adaptador_demo", model=DEFAULT_MODEL, usage=r.usage, latency_ms=lat)
    texto = "".join(b.text for b in r.content if getattr(b, "type", "") == "text")
    return {
        "ok": True,
        "respuesta": guardrails.enmascarar_pii(texto),
        "riesgos": guardrails.salida_riesgosa(texto),
        "costo_usd": entry["cost_usd"],
        "tokens": {
            "input": entry["input_tokens"],
            "cache_read": entry["cache_read"],
            "cache_write": entry["cache_write"],
            "output": entry["output_tokens"],
        },
        "modo": "messages_demo",
    }


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python adaptador.py "Triagia el mensaje MSG-101"')
        raise SystemExit(1)
    out = correr(sys.argv[1])
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
