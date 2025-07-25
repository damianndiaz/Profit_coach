#!/usr/bin/env python3
"""
Versión optimizada de chat_interface.py con OpenAI v1.0+ compatibility
"""

import os
import logging
import time
import streamlit as st
import re

# IMPORTANTE: Importar config ANTES de openai para configurar la API key
from config import config

# OpenAI v1.0+ - Usar cliente en lugar de módulo global
from openai import OpenAI
from modules.athlete_manager import get_athlete_data
from modules.chat_manager import get_or_create_chat_session, save_message, load_chat_history, get_or_create_thread_id, get_previous_routines, save_routine_summary
from modules.training_variations import get_sport_adaptation_principles, get_progression_guidelines
from utils.app_utils import retry_operation, performance_monitor, with_loading

# Configuración OpenAI v1.0+ - NUEVA SINTAXIS
OPENAI_API_KEY = config.OPENAI_API_KEY
OPENAI_ASSISTANT_ID = config.OPENAI_ASSISTANT_ID

# Crear cliente OpenAI (v1.0+ requiere cliente instanciado)
if OPENAI_API_KEY:
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    logging.info("✅ OpenAI client v1.0+ configurado correctamente")
else:
    openai_client = None
    logging.error("❌ OPENAI_API_KEY no configurada - revisar secrets de Streamlit")

# Log para debug
logging.info(f"🔑 OpenAI API Key configured: {'YES' if OPENAI_API_KEY else 'NO'}")
logging.info(f"🤖 Assistant ID configured: {'YES' if OPENAI_ASSISTANT_ID else 'NO'}")
logging.info(f"🔧 OpenAI Client: {'READY' if openai_client else 'NOT READY'}")

# Configuración de rendimiento optimizada
OPENAI_TIMEOUT = 35  # Reducido para mejor experiencia
POLL_INTERVAL = 1    # Polling más frecuente
MAX_RESPONSE_LENGTH = 4500  # Respuestas más cortas y rápidas

# Validar configuración
if not OPENAI_API_KEY:
    logging.error("❌ OPENAI_API_KEY no configurada - revisar secrets de Streamlit")
if not OPENAI_ASSISTANT_ID:
    logging.error("❌ OPENAI_ASSISTANT_ID no configurada - revisar secrets de Streamlit")

def validate_message(message):
    """Valida el mensaje del usuario - versión optimizada"""
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío"
    
    if len(message) > 2000:  # Reducido para mejor rendimiento
        return False, "El mensaje es demasiado largo (máximo 2000 caracteres)"
    
    return True, ""

def detect_email_command(message):
    """Detecta si el usuario quiere enviar por email - versión mejorada"""
    email_patterns = [
        r'env[ií]a.*por.*email',
        r'mand[aá].*por.*correo',
        r'email.*me.*la.*rutina',
        r'correo.*electr[óo]nico',
        r'env[ií]a.*rutina.*email',
        r'mand[aá].*rutina.*correo',
        r'por.*email.*por.*favor',
        r'env[ií]a.*por.*mail',
        r'mand[aá].*por.*mail'
    ]
    
    message_lower = message.lower()
    for pattern in email_patterns:
        if re.search(pattern, message_lower):
            return True
    
    return False

@performance_monitor
def handle_user_message(user_message, athlete_id, email=None):
    """
    Maneja mensajes del usuario con IA - Versión optimizada y compacta
    """
    if not openai_client:
        return "❌ Error: Cliente OpenAI no configurado. Revisar secrets de Streamlit.", False, False
    
    if not OPENAI_ASSISTANT_ID:
        return "❌ Error: Assistant ID no configurado. Revisar secrets de Streamlit.", False, False
    
    try:
        # Validación rápida
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            return f"❌ {error_msg}", False, False
        
        # Detectar comando de email automáticamente
        should_email = detect_email_command(user_message)
        
        # Obtener datos del atleta de forma optimizada
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "❌ Error: No se encontraron datos del atleta", False, False
        
        # Preparar contexto súper compacto (80% reducción)
        level_guidelines = get_progression_guidelines(athlete_data['level'])
        sport_principles = get_sport_adaptation_principles(athlete_data['sport'])
        
        # Historial de rutinas para evitar repetición (limitado)
        previous_routines = get_previous_routines(athlete_id, limit=3)
        routine_context = ""
        if previous_routines:
            routine_context = f"\\n\\nRUTINAS PREVIAS (evitar repetir): {', '.join([r['summary'][:50] for r in previous_routines])}"
        
        # Contexto ultra-compacto para mejor rendimiento
        context = f"""METODOLOGÍA 5 BLOQUES - {athlete_data['name']} ({athlete_data['sport']}, {athlete_data['level']})
        
        1. 🍑 ACTIVACIÓN GLÚTEA (5-10min): Activación neuromuscular
        2. ⚡ DINÁMICO/POTENCIA (10-15min): Movimientos explosivos + zona media  
        3. 💪 FUERZA 1 (15-20min): Patrones fundamentales + unilateral
        4. 🔥 FUERZA 2 (15-20min): Movimientos complejos + rotacionales
        5. 🚀 CONTRASTE/PREVENTIVOS (10-15min): Velocidad + prevención
        
        NIVEL {athlete_data['level']}: {level_guidelines['filosofia'][:80]}...
        DEPORTE {athlete_data['sport']}: {sport_principles['enfoque'][0][:80]}...
        
        FORMATO: Usa [INICIO_NUEVA_RUTINA] para rutinas completas.
        ESTILO: Conciso, profesional, con parámetros específicos.
        VARIACIÓN: Nunca repitas rutinas idénticas.
        PLANIFICACIONES: Si piden múltiples días (ej: 5 días), asegúrate de incluir TODOS los días solicitados.{routine_context}
        """
        
        # Prompt final mucho más corto
        prompt = f"{context}\\n\\nConsulta: {user_message}"
        
        # Obtener o crear thread para el atleta
        def create_thread():
            return openai_client.beta.threads.create()
        
        thread_id = get_or_create_thread_id(athlete_id, create_thread)
        
        # Añadir mensaje del usuario
        openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Crear y ejecutar run
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID,
            timeout=OPENAI_TIMEOUT
        )
        
        # Polling optimizado con timeout reducido
        start_time = time.time()
        while time.time() - start_time < OPENAI_TIMEOUT:
            time.sleep(POLL_INTERVAL)
            
            try:
                run_status = openai_client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )
                
                if run_status.status == 'completed':
                    break
                elif run_status.status in ['failed', 'expired', 'cancelled']:
                    return f"❌ Error en procesamiento: {run_status.status}", False, False
                    
            except Exception as e:
                logging.error(f"Error checking run status: {e}")
                continue
        else:
            return "⏰ Timeout: El agente tardó demasiado en responder. Intenta de nuevo.", False, False
        
        # Obtener respuesta
        try:
            messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
            if messages.data:
                assistant_message = messages.data[0].content[0].text.value
                
                # Truncar respuesta si es muy larga
                if len(assistant_message) > MAX_RESPONSE_LENGTH:
                    assistant_message = assistant_message[:MAX_RESPONSE_LENGTH] + "\\n\\n✂️ *Respuesta truncada para mejor rendimiento*"
                
                # Guardar en historial
                save_message(athlete_id, user_message, assistant_message)
                
                # Extraer y guardar resumen de rutina si aplica
                if "[INICIO_NUEVA_RUTINA]" in assistant_message:
                    routine_summary = assistant_message.split("[INICIO_NUEVA_RUTINA]")[1][:200]
                    save_routine_summary(athlete_id, routine_summary)
                
                return assistant_message, True, should_email
            else:
                return "❌ No se recibió respuesta del asistente", False, False
                
        except Exception as e:
            logging.error(f"Error getting messages: {e}")
            return "❌ Error al obtener la respuesta", False, False
    
    except Exception as e:
        # Manejo específico de errores de OpenAI v1.0+
        error_message = str(e)
        
        if "api_key" in error_message.lower():
            logging.error(f"❌ OpenAI API Key Error: {error_message}")
            return "❌ Error de configuración: API Key no válida. Contacta al administrador.", False, False
        
        logging.error(f"Error inesperado: {e}")
        return f"❌ Error inesperado: {error_message}", False, False

# Función de compatibilidad para testing
def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    if not openai_client:
        return False, "Cliente OpenAI no configurado"
    
    try:
        # Test simple: crear un thread
        thread = openai_client.beta.threads.create()
        return True, f"Conexión exitosa. Thread ID: {thread.id}"
    except Exception as e:
        return False, f"Error de conexión: {e}"
