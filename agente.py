# Orquestador + subagente auditor (Claude Agent SDK).
# El system se arma con el manual simulado y cache_control para medir ahorro (L8).

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANUAL = (ROOT / "datos" / "manual_atencion.md").read_text(encoding="utf-8")

SYSTEM_TEXT = (
    "Eres el agente de triage de un buzon de soporte SIMULADO.\n"
    "Usa las herramientas MCP del servidor 'buzon'. No inventes mensajes.\n"
    "Antes de llamar guardar_triage, invoca al subagente auditor_cumplimiento.\n"
    "Nunca envies el correo: solo clasificas y propones borrador.\n\n"
    + MANUAL
)


def construir_system() -> list[dict]:
    # Prompt caching: el manual es estable entre preguntas.
    return [{"type": "text", "text": SYSTEM_TEXT, "cache_control": {"type": "ephemeral"}}]


SERVIDORES = {"buzon": "python server.py"}

HERRAMIENTAS = [
    "mcp__buzon__listar_pendientes",
    "mcp__buzon__obtener_mensaje",
    "mcp__buzon__consultar_politicas",
    "mcp__buzon__guardar_triage",
]


def agentes():
    from claude_agent_sdk import AgentDefinition

    return {
        "auditor_cumplimiento": AgentDefinition(
            description="Auditor de cumplimiento. Valida categoria y borrador contra politicas.",
            prompt=(
                "Eres auditor estricto del buzon simulado. "
                "Consulta politicas con MCP. Responde solo: CUMPLE o VIOLA_POLITICA: <motivo>."
            ),
            tools=["mcp__buzon__consultar_politicas", "mcp__buzon__obtener_mensaje"],
            model="inherit",
        )
    }


def opciones():
    # Cableado tipico del bootcamp (L4/L6): tools Agent + MCP + subagentes.
    return {
        "system": construir_system(),
        "mcp_servers": SERVIDORES,
        "tools": ["Agent"],
        "allowed_tools": HERRAMIENTAS + ["Agent"],
        "agents": agentes(),
    }
