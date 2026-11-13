# Agente de triage y borradores de correo

Capstone **AI Engineer con Claude (AIENG01)**.

Agente que clasifica correos de un **buzon 100% simulado** (JSON), propone borradores y valida cumplimiento con un **subagente**, guardrails y costo medido. **No conecta a Outlook ni a buzones reales.**

## Quien lo usa / que resuelve

- **Quien:** analista de soporte (demo).
- **Que pide:** "Triagia el mensaje MSG-101 y guarda un borrador."
- **Como se sabe que funciono:** el JSON del buzon queda en `TRIAGEADO` / `SPAM` con categoria y borrador; el auditor responde CUMPLE o VIOLA_POLITICA; los casos adversarios se bloquean.

## Seguridad (repo publico)

Este repositorio es **publico**. Por diseno:

- Solo datos ficticios (`@ejemplo.com`).
- No hay API keys: usa `.env` local (gitignored) o el Cloud Workspace del bootcamp.
- No copies correos reales, NITs, clientes ni adjuntos de produccion.
- Revoca cualquier token que hayas pegado en un chat.

## Requisitos del curso cubiertos

| Requisito | Donde |
|---|---|
| Servidor MCP propio | `server.py` (FastMCP `buzon`) |
| Subagente con alcance restringido | `auditor_cumplimiento` en `agente.py` |
| Golden set + evals | `golden_set.json`, `evals.py` |
| Guardrails | `guardrails.py` |
| Costo + caching | `costing.py` + `cache_control` en system |

## Arranque rapido

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/Mac / Cloud Workspace:
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # solo local; no subir
```

Chequeo sin llamar al modelo:

```bash
python verificar.py
```

Demo (necesita `ANTHROPIC_API_KEY` en `.env` o Bedrock del workspace):

```bash
python adaptador.py "Triagia el mensaje MSG-101"
python evals.py --solo-guardrails --etiqueta smoke
```

En el Cloud Workspace del bootcamp, conecta este repo y usa el SDK/MCP del lab-09 (`entregar.sh` del curso si aplica).

## Mapa de archivos

| Archivo | Rol |
|---|---|
| `datos/buzon.json` | Buzon y politicas simuladas |
| `datos/manual_atencion.md` | Prefijo estable (cacheable) |
| `server.py` | MCP: listar, obtener, politicas, guardar |
| `agente.py` | Orquestador + subagente |
| `adaptador.py` | CLI + guardrails + costo |
| `guardrails.py` | Entrada/salida |
| `golden_set.json` | 8 casos (6 funcionales + 2 adversariales) |
| `costing.py` | Log JSONL de usage |
| `verificar.py` | Autochequeo de estructura |

## Guion corto de defensa (5 min)

1. Problema: triage manual de bandeja, riesgo de phishing y borradores inventados.
2. Demo: `python adaptador.py "Triagia MSG-104"` (spam) y `MSG-101` (accion).
3. Arquitectura: MCP + subagente auditor + guardrails + cache/costo.
4. Evals: abrir `golden_set.json` y un resultado en `resultados/`.
5. Limites: datos simulados; humano decide si envia el correo.

## Licencia

Material educativo del bootcamp. Sin garantia.
