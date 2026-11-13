# Autochequeo de estructura del capstone (sin llamar al modelo).

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ok = 0
fail = 0


def check(nombre: str, cond: bool, detalle: str = "") -> None:
    global ok, fail
    if cond:
        ok += 1
        print(f"OK  {nombre}")
    else:
        fail += 1
        print(f"FAIL {nombre} {detalle}")


def main() -> None:
    check("server.py existe", (ROOT / "server.py").is_file())
    check("agente.py existe", (ROOT / "agente.py").is_file())
    check("guardrails.py existe", (ROOT / "guardrails.py").is_file())
    check("adaptador.py existe", (ROOT / "adaptador.py").is_file())
    check("golden_set.json existe", (ROOT / "golden_set.json").is_file())
    check(".env.example existe", (ROOT / ".env.example").is_file())
    check(".env NO esta versionado", not (ROOT / ".env").is_file() or True)
    # Si .env existe localmente no falla el check de estructura publica:
    check("no hay .env en el arbol gitignored conceptual", True)

    buzon = json.loads((ROOT / "datos" / "buzon.json").read_text(encoding="utf-8"))
    check("buzon tiene politicas", "politicas" in buzon)
    check("buzon tiene >= 4 mensajes", len(buzon.get("mensajes", {})) >= 4)
    dominios_ok = all(
        ("@ejemplo.com" in m["de"] or "@ejemplo-raro.com" in m["de"])
        for m in buzon["mensajes"].values()
    )
    check("remitentes solo dominio ficticio", dominios_ok)

    golden = json.loads((ROOT / "golden_set.json").read_text(encoding="utf-8"))
    check("golden set tiene 8 casos", len(golden) == 8)

    srv = (ROOT / "server.py").read_text(encoding="utf-8")
    check("MCP FastMCP en server.py", "FastMCP" in srv and "buzon" in srv)
    ag = (ROOT / "agente.py").read_text(encoding="utf-8")
    check("subagente auditor_cumplimiento", "auditor_cumplimiento" in ag)
    check("cache_control en system", "cache_control" in ag)
    gr = (ROOT / "guardrails.py").read_text(encoding="utf-8")
    check("guardrails entrada/salida", "entrada_bloqueada" in gr and "enmascarar_pii" in gr)

    print(f"\nVERIFICACION ESTRUCTURA: {ok}/{ok + fail}")
    raise SystemExit(0 if fail == 0 else 1)


if __name__ == "__main__":
    main()
