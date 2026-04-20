# agent/tools.py — Herramientas del agente
# Generado por AgentKit

"""
Herramientas específicas de OpositorPro.
Estas funciones extienden las capacidades del agente más allá de responder texto.
"""

import os
import yaml
import logging
from datetime import datetime

logger = logging.getLogger("agentkit")


def cargar_info_negocio() -> dict:
    """Carga la información del negocio desde business.yaml."""
    try:
        with open("config/business.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logger.error("config/business.yaml no encontrado")
        return {}


def obtener_horario() -> dict:
    """Retorna el horario de atención del negocio."""
    info = cargar_info_negocio()
    return {
        "horario": info.get("negocio", {}).get("horario", "No disponible"),
        "esta_abierto": True,  # 24/7 — siempre abierto
    }


def buscar_en_knowledge(consulta: str) -> str:
    """
    Busca información relevante en los archivos de /knowledge.
    Retorna el contenido más relevante encontrado.
    """
    resultados = []
    knowledge_dir = "knowledge"

    if not os.path.exists(knowledge_dir):
        return "No hay archivos de conocimiento disponibles."

    for archivo in os.listdir(knowledge_dir):
        ruta = os.path.join(knowledge_dir, archivo)
        if archivo.startswith(".") or not os.path.isfile(ruta):
            continue
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                if consulta.lower() in contenido.lower():
                    resultados.append(f"[{archivo}]: {contenido[:500]}")
        except (UnicodeDecodeError, IOError):
            continue

    if resultados:
        return "\n---\n".join(resultados)
    return "No encontré información específica sobre eso en mis archivos."


def registrar_lead(telefono: str, nombre: str, oposicion: str, interes: str) -> dict:
    """
    Registra un nuevo lead interesado en los servicios de OpositorPro.

    Args:
        telefono: Número de WhatsApp del interesado
        nombre: Nombre del interesado
        oposicion: Qué oposición está preparando
        interes: En qué servicio está interesado (app, asesoría, presencial)

    Returns:
        Diccionario con la confirmación del registro
    """
    logger.info(f"Nuevo lead: {nombre} — {oposicion} — interesado en: {interes}")
    return {
        "registrado": True,
        "nombre": nombre,
        "oposicion": oposicion,
        "interes": interes,
        "telefono": telefono,
        "fecha": datetime.now().isoformat(),
    }


def solicitar_asesoria(telefono: str, nombre: str, oposicion: str, disponibilidad: str) -> dict:
    """
    Registra una solicitud de asesoría online o sesión presencial.

    Args:
        telefono: Número de WhatsApp
        nombre: Nombre del opositor
        oposicion: Qué oposición prepara
        disponibilidad: Horarios en los que puede atender la asesoría

    Returns:
        Diccionario con la confirmación de la solicitud
    """
    logger.info(f"Solicitud de asesoría: {nombre} — {oposicion} — disponibilidad: {disponibilidad}")
    return {
        "solicitado": True,
        "nombre": nombre,
        "oposicion": oposicion,
        "disponibilidad": disponibilidad,
        "telefono": telefono,
        "fecha": datetime.now().isoformat(),
        "mensaje": f"Hemos registrado tu solicitud de asesoría, {nombre}. El equipo de OpositorPro te contactará pronto para confirmar el horario.",
    }
