# Evaluacion ligera del golden set (estructura + guardrails).
# En el Cloud Workspace del curso puedes sustituir por el evals.py oficial del lab-09.

from __future__ import annotations

import argparse
import json
from pathlib import Path

import guardrails
from adaptador import correr

ROOT = Path(__file__).resolve().parent
GOLDEN = json.loads((ROOT / "golden_set.json").read_text(encoding="utf-8"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--etiqueta", default="corrida")
    ap.add_argument("--solo-guardrails", action="store_true")
    a = ap.parse_args()

    resultados = []
    for caso in GOLDEN:
        fila = {"id": caso["id"], "pregunta": caso["pregunta"]}
        if caso["id"].startswith("c7") or caso["id"].startswith("c8") or a.solo_guardrails:
            bloqueo = guardrails.entrada_bloqueada(caso["pregunta"])
            fila["ok"] = bloqueo is not None
            fila["detalle"] = bloqueo or "no bloqueo"
        else:
            # Llamada real (consume tokens). Comenta si solo quieres chequear estructura.
            out = correr(caso["pregunta"])
            fila["ok"] = bool(out.get("ok"))
            fila["detalle"] = (out.get("respuesta") or out.get("error") or "")[:240]
            fila["modo"] = out.get("modo")
        resultados.append(fila)
        marca = "OK" if fila["ok"] else "FAIL"
        print(f"[{marca}] {fila['id']}: {fila['detalle'][:120]}")

    out_dir = ROOT / "resultados"
    out_dir.mkdir(exist_ok=True)
    ruta = out_dir / f"evals_{a.etiqueta}.json"
    ruta.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Guardado {ruta}")


if __name__ == "__main__":
    main()
