# Servidor MCP propio: buzon de correos SIMULADO (JSON). Sin Outlook ni datos reales.

from __future__ import annotations

import json
import os

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("buzon")
RUTA_DATOS = os.path.join(os.path.dirname(__file__), "datos", "buzon.json")


def _cargar() -> dict:
    with open(RUTA_DATOS, "r", encoding="utf-8") as f:
        return json.load(f)


def _guardar(datos: dict) -> None:
    with open(RUTA_DATOS, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


@mcp.tool()
def listar_pendientes() -> str:
    """Lista mensajes en estado PENDIENTE (id, de, asunto)."""
    d = _cargar()
    filas = []
    for mid, m in d["mensajes"].items():
        if m.get("estado") == "PENDIENTE":
            filas.append({"id": mid, "de": m["de"], "asunto": m["asunto"]})
    return json.dumps(filas, ensure_ascii=False)


@mcp.tool()
def obtener_mensaje(id_mensaje: str) -> str:
    """Devuelve el mensaje simulado por ID (ej. MSG-101)."""
    d = _cargar()
    item = d["mensajes"].get(id_mensaje)
    if not item:
        return f"Error: {id_mensaje} no existe."
    return json.dumps({"id": id_mensaje, **item}, ensure_ascii=False)


@mcp.tool()
def consultar_politicas() -> str:
    """Retorna politicas de triage y redaccion del buzon simulado."""
    return json.dumps(_cargar()["politicas"], ensure_ascii=False)


@mcp.tool()
def guardar_triage(id_mensaje: str, categoria: str, borrador: str, estado: str) -> str:
    """Guarda categoria, borrador propuesto y estado (TRIAGEADO, SPAM, IGNORADO)."""
    d = _cargar()
    if id_mensaje not in d["mensajes"]:
        return f"Error: {id_mensaje} no existe."
    permitidos = {"TRIAGEADO", "SPAM", "IGNORADO", "PENDIENTE"}
    if estado not in permitidos:
        return f"Error: estado invalido. Use uno de {sorted(permitidos)}."
    cats = d["politicas"].get("categorias", [])
    if categoria not in cats:
        return f"Error: categoria invalida. Use una de {cats}."
    d["mensajes"][id_mensaje]["categoria"] = categoria
    d["mensajes"][id_mensaje]["borrador"] = borrador
    d["mensajes"][id_mensaje]["estado"] = estado
    _guardar(d)
    return f"Mensaje {id_mensaje} actualizado a '{estado}' ({categoria})."


if __name__ == "__main__":
    mcp.run()
