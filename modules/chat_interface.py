#!/usr/bin/env python3
"""
Versión optimizada de chat_interface.py con prompts más cortos y mejor rendimiento
"""

import os
import logging
import time
import streamlit as st
import re

# IMPORTANTE: Importar config ANTES de openai para configurar la API key
from config import config

import openai
from modules.athlete_manager import get_athlete_data
from modules.chat_manager import get_or_create_chat_session, save_message, load_chat_history, get_or_create_thread_id, get_previous_routines, save_routine_summary
from modules.training_variations import get_sport_adaptation_principles, get_progression_guidelines
from utils.app_utils import retry_operation, performance_monitor, with_loading

# Configuración optimizada de OpenAI usando config centralizado
openai.api_key = config.OPENAI_API_KEY
OPENAI_ASSISTANT_ID = config.OPENAI_ASSISTANT_ID

# Log para debug
logging.info(f"🔑 OpenAI API Key configured: {'YES' if openai.api_key else 'NO'}")
logging.info(f"🤖 Assistant ID configured: {'YES' if OPENAI_ASSISTANT_ID else 'NO'}")

# Configuración de rendimiento optimizada
OPENAI_TIMEOUT = 35  # Reducido para mejor experiencia
POLL_INTERVAL = 1    # Polling más frecuente
MAX_RESPONSE_LENGTH = 4500  # Respuestas más cortas y rápidas

# Validar configuración
if not openai.api_key:
    logging.error("❌ OPENAI_API_KEY no configurada - revisar secrets de Streamlit")
if not OPENAI_ASSISTANT_ID:
    logging.error("❌ OPENAI_ASSISTANT_ID no configurada - revisar secrets de Streamlit")

def validate_message(message):
    """Valida el mensaje del usuario - versión optimizada"""
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío"
    
    if len(message) > 3000:  # Reducido para mejor rendimiento
        return False, "El mensaje no puede exceder 3000 caracteres"
    
    return True, ""

def detect_email_command(message):
    """Detecta comandos de email - versión mejorada"""
    email_patterns = [
        r'\b(envía|manda|envíalo|envía|enviame|mandame|mandalo|mandaselo|envíaselo)\s*(por)?\s*(email|mail|correo)\b',
        r'\b(email|mail|correo)\s*(me|lo|la|esto|eso|la rutina|el plan)\b',
        r'\b(quiero|necesito|puedes|podrías)\s*(enviarlo|mandarlo|que lo envíes|que me lo mandes)\s*(por)?\s*(email|mail|correo)\b',
        r'\b(por favor|please)\s*(envía|manda|send)\s*(por)?\s*(email|mail|correo)\b',
        r'\b(send|enviar)\s*(by|por)?\s*(email|mail)\b',
        r'\b(via|por)\s*(email|mail|correo)\b'
    ]
    
    message_lower = message.lower()
    for pattern in email_patterns:
        if re.search(pattern, message_lower):
            return True
    return False

@retry_operation(max_retries=2)  # Reducido reintentos
@performance_monitor
def generate_ai_response_with_assistant(athlete_id, user_message):
    """Versión optimizada de generación de respuestas AI"""
    try:
        # Obtener datos del atleta
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "❌ No se encontraron datos del atleta"
        
        # Obtener principios deportivos
        sport_principles = get_sport_adaptation_principles(athlete_data['sport'])
        level_guidelines = get_progression_guidelines(athlete_data['level'])
        
        # Contexto de rutinas previas (simplificado)
        previous_routines = get_previous_routines(athlete_id, limit=2)  # Solo 2 últimas
        routine_context = ""
        if previous_routines:
            routine_context = f"\\nRutinas recientes: Evita repetir ejercicios de las últimas {len(previous_routines)} rutinas."
        
        # Prompt ULTRA COMPACTO para mejor rendimiento
        context = f"""
        Eres ProFit Coach AI, especialista en metodología de 5 bloques.
        
        ATLETA: {athlete_data['name']} | {athlete_data['sport']} | {athlete_data['level']}
        
        METODOLOGÍA 5 BLOQUES:
        1. 🍑 ACTIVACIÓN GLÚTEA (8-12min): Preparación neuromuscular
        2. ⚡ DINÁMICO/POTENCIA (12-18min): Movimientos explosivos + zona media
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
            return openai.beta.threads.create()
        
        thread_id = get_or_create_thread_id(athlete_id, create_thread)
        
        # Añadir mensaje del usuario
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Ejecutar assistant con timeout optimizado
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID
        )
        
        # Esperar respuesta con timeout más corto
        start_time = time.time()
        
        while True:
            elapsed_time = time.time() - start_time
            if elapsed_time > OPENAI_TIMEOUT:
                logging.error(f"Timeout ({OPENAI_TIMEOUT}s) - atleta {athlete_id}")
                return "⏱️ Timeout. Intenta con una pregunta más corta o específica."
            
            try:
                run_status = openai.beta.threads.runs.retrieve(
                    thread_id=thread_id, 
                    run_id=run.id
                )
            except Exception as e:
                logging.error(f"Error verificando run: {e}")
                time.sleep(POLL_INTERVAL)
                continue
            
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                logging.error(f"OpenAI falló - atleta {athlete_id}")
                return "❌ Error procesando consulta. Intenta reformularla."
            elif run_status.status in ["cancelled", "expired"]:
                return "⚠️ Consulta interrumpida. Inténtalo de nuevo."
            
            time.sleep(POLL_INTERVAL)
        
        # Recuperar respuesta con optimización
        try:
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            
            # Buscar respuesta más reciente
            for msg in messages.data:
                if msg.role == "assistant" and msg.run_id == run.id and msg.content:
                    response = msg.content[0].text.value
                    
                    # Optimizar longitud de respuesta
                    if len(response) > MAX_RESPONSE_LENGTH:
                        response = response[:MAX_RESPONSE_LENGTH-50] + "\\n\\n⚡ *Optimizado para velocidad. Pregunta por detalles específicos.*"
                    
                    logging.info(f"Respuesta exitosa - atleta {athlete_id} ({len(response)} chars)")
                    return response
            
            # Fallback simplificado
            return "🤔 Consulta procesada pero sin respuesta clara. Reformula tu pregunta."
                
        except Exception as e:
            logging.error(f"Error recuperando respuesta: {e}")
            return "❌ Error recuperando respuesta. Inténtalo de nuevo."
        
    except openai.APITimeoutError:
        return "⏱️ Timeout de API. Inténtalo de nuevo."
    except openai.RateLimitError:
        return "🚦 Servicio ocupado. Espera un momento e inténtalo de nuevo."
    except openai.APIConnectionError:
        return "🌐 Error de conexión. Verifica tu internet."
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return "❌ Error inesperado. Inténtalo más tarde."

@with_loading("Procesando mensaje...")
def handle_user_message(athlete_id, user_message):
    """Maneja mensajes del usuario - versión optimizada"""
    try:
        # Validar mensaje
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            return error_msg
        
        # Detectar comando de email
        wants_email = detect_email_command(user_message)
        if wants_email:
            user_message += " [COMANDO_EMAIL_SOLICITADO]"
        
        # Generar respuesta
        ai_response = generate_ai_response_with_assistant(athlete_id, user_message)
        
        # Guardar en base de datos
        session_id = get_or_create_chat_session(athlete_id)
        save_message(session_id, user_message, True)
        save_message(session_id, ai_response, False)
        
        # Guardar resumen si es rutina
        if "[INICIO_NUEVA_RUTINA]" in ai_response:
            save_routine_summary(session_id, ai_response)
            
            # Si se solicitó email automático, configurar flag para mostrarlo
            if wants_email:
                import streamlit as st
                st.session_state[f'auto_email_routine_{athlete_id}'] = {
                    'routine_text': ai_response,
                    'routine': ai_response,  # Agregar ambas claves por compatibilidad
                    'timestamp': str(int(time.time()))
                }
        
        return ai_response
        
    except Exception as e:
        logging.error(f"Error en handle_user_message: {e}")
        return "❌ Error procesando mensaje. Inténtalo de nuevo."

# Función para obtener historial (simplificada)
def get_chat_history(athlete_id):
    """Obtiene historial de chat optimizado"""
    try:
        return load_chat_history(athlete_id, limit=15)  # Límite reducido
    except Exception as e:
        logging.error(f"Error cargando historial: {e}")
        return []
