# agent/brain.py — Cerebro del agente: conexión con Claude API
"""
Lógica de IA del agente. Lee el system prompt de prompts.yaml
y la base de conocimiento de knowledge/, y genera respuestas usando Claude.
"""

import os
import glob
import yaml
import logging
from anthropic import AsyncAnthropic
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("agentkit")

client = AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def cargar_config_prompts() -> dict:
    try:
        with open("config/prompts.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        logger.error("config/prompts.yaml no encontrado")
        return {}


def cargar_knowledge_base() -> str:
    """Carga todos los archivos .md de la carpeta knowledge/ como contexto."""
    archivos = glob.glob("knowledge/*.md")
    if not archivos:
        logger.warning("No se encontraron archivos en knowledge/")
        return ""

    contenido = []
    for archivo in archivos:
        try:
            with open(archivo, "r", encoding="utf-8") as f:
                contenido.append(f.read())
            logger.info(f"Knowledge cargado: {archivo}")
        except Exception as e:
            logger.error(f"Error leyendo {archivo}: {e}")

    return "\n\n---\n\n".join(contenido)


def cargar_system_prompt() -> str:
    """Lee el system prompt de prompts.yaml y le añade la base de conocimiento."""
    config = cargar_config_prompts()
    base_prompt = config.get("system_prompt", "Eres un asistente útil. Responde en español.")

    knowledge = cargar_knowledge_base()
    if knowledge:
        return f"{base_prompt}\n\n## BASE DE CONOCIMIENTO\n\nUsa esta información para responder con precisión. NO inventes datos que no estén aquí:\n\n{knowledge}"
    return base_prompt


def obtener_mensaje_error() -> str:
    config = cargar_config_prompts()
    return config.get("error_message", "Lo siento, estoy teniendo problemas técnicos. Por favor intenta de nuevo en unos minutos.")


def obtener_mensaje_fallback() -> str:
    config = cargar_config_prompts()
    return config.get("fallback_message", "Disculpa, no entendí tu mensaje. ¿Podrías reformularlo?")


async def generar_respuesta(mensaje: str, historial: list[dict]) -> str:
    if not mensaje or len(mensaje.strip()) < 2:
        return obtener_mensaje_fallback()

    system_prompt = cargar_system_prompt()

    mensajes = []
    for msg in historial:
        mensajes.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    mensajes.append({
        "role": "user",
        "content": mensaje
    })

    try:
        response = await client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            messages=mensajes
        )

        respuesta = response.content[0].text
        logger.info(f"Respuesta generada ({response.usage.input_tokens} in / {response.usage.output_tokens} out)")
        return respuesta

    except Exception as e:
        logger.error(f"Error Claude API: {e}")
        return obtener_mensaje_error()
