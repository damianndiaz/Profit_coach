
#!/usr/bin/env python3
"""
ProFit Coach - Chat Interface con OpenAI v1.0+ compatibility
Versión optimizada para mejor rendimiento y cache inteligente
"""

import os
import sys
import logging
import time
import streamlit as st
import re
from typing import Optional

# Agregar el directorio raíz al path de Python
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# IMPORTANTE: Importar config ANTES de openai para configurar la API key
from config import config

# OpenAI v1.0+ - Usar cliente en lugar de módulo global
from openai import OpenAI, APITimeoutError, RateLimitError, APIConnectionError
from modules.athlete_manager import get_athlete_data
from modules.chat_manager import get_or_create_chat_session, save_message, load_chat_history, get_or_create_thread_id, get_previous_routines, save_routine_summary
from modules.training_variations import get_sport_adaptation_principles, get_progression_guidelines
from utils.app_utils import retry_operation, performance_monitor, with_loading

# Imports condicionales para evitar errores de dependencias
try:
    from modules.ai_cache_manager import cache_manager
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False
    cache_manager = None
    logging.warning("⚠️ AI Cache Manager no disponible")

try:
    from modules.auto_email_handler import auto_email_handler
    AUTO_EMAIL_AVAILABLE = True
except ImportError:
    AUTO_EMAIL_AVAILABLE = False
    auto_email_handler = None
    logging.warning("⚠️ Auto Email Handler no disponible")

try:
    from modules.rate_limit_manager import rate_limit_manager
    from modules.performance_monitor import performance_monitor
    MONITORING_AVAILABLE = True
except ImportError:
    MONITORING_AVAILABLE = False
    rate_limit_manager = None
    performance_monitor = None
    logging.warning("⚠️ Rate Limit Manager y Performance Monitor no disponibles")

try:
    from modules.thread_manager import thread_manager
    THREAD_MANAGER_AVAILABLE = True
except ImportError:
    THREAD_MANAGER_AVAILABLE = False
    thread_manager = None
    logging.warning("⚠️ Thread Manager no disponible")

try:
    from modules.response_cleaner import response_cleaner
    RESPONSE_CLEANER_AVAILABLE = True
except ImportError:
    RESPONSE_CLEANER_AVAILABLE = False
    response_cleaner = None
    logging.warning("⚠️ Response Cleaner no disponible")

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
MAX_RESPONSE_LENGTH = 15000  # 🔄 AUMENTADO: Permite rutinas completas sin cortes

# Crear decorador simple si performance_monitor no está disponible
def simple_performance_monitor(func):
    """Decorador simple para medir performance"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            logging.info(f"⏱️ {func.__name__} took {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logging.error(f"❌ {func.__name__} failed after {elapsed:.2f}s: {e}")
            raise
    return wrapper

# Usar el monitor de performance si está disponible, sino el simple
if MONITORING_AVAILABLE and performance_monitor and hasattr(performance_monitor, '__call__'):
    perf_monitor = performance_monitor
else:
    perf_monitor = simple_performance_monitor

# Validar configuración
if not openai_client:
    logging.error("❌ OPENAI_API_KEY no configurada - revisar secrets de Streamlit")
if not OPENAI_ASSISTANT_ID:
    logging.error("❌ OPENAI_ASSISTANT_ID no configurada - revisar secrets de Streamlit")

def get_welcome_message(athlete_id):
    """Genera mensaje de bienvenida personalizado y limpio"""
    try:
        if not RESPONSE_CLEANER_AVAILABLE or not response_cleaner:
            return "¡Hola! Soy tu ProFit Coach AI. ¿En qué puedo ayudarte hoy? 💪"
        
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "¡Hola! Soy tu ProFit Coach AI. ¿En qué puedo ayudarte hoy? 💪"
        
        return response_cleaner.create_welcome_message(
            athlete_data.get('name', 'Atleta'),
            athlete_data.get('sport', 'deportivo')
        )
        
    except Exception as e:
        logging.error(f"Error generando mensaje de bienvenida: {e}")
        return "¡Hola! Soy tu ProFit Coach AI. ¿En qué puedo ayudarte hoy? 💪"

def validate_message(message):
    """Valida el mensaje del usuario - versión optimizada"""
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío"
    
    if len(message) > 3000:  # Reducido para mejor rendimiento
        return False, "El mensaje no puede exceder 3000 caracteres"
    
    return True, ""

def detect_email_command(message):
    """Detecta comandos de email - versión mejorada usando auto_email_handler"""
    if AUTO_EMAIL_AVAILABLE and auto_email_handler:
        detected = auto_email_handler.detect_email_command(message)
        if detected:
            logging.info(f"📧 Email command detected: '{message}'")
        return detected
    else:
        # Fallback al método original si hay problemas de importación
        email_patterns = [
            r'\b(envía|manda|envíalo|envía|enviame|mandame|mandalo|mandaselo|envíaselo)\s*(por)?\s*(email|mail|correo)\b',
            r'\b(email|mail|correo)\s*(me|lo|la|esto|eso|la rutina|el plan)\b',
            r'\b(quiero|necesito|puedes|podrías)\s*(enviarlo|mandarlo|que lo envíes|que me lo mandes)\s*(por)?\s*(email|mail|correo)\b',
            r'\b(por favor|please)\s*(envía|manda|send)\s*(por)?\s*(email|mail|correo)\b',
            r'\b(send|enviar)\s*(by|por)?\s*(email|mail)\b',
            r'\b(via|por)\s*(email|mail|correo)\b',
            # NUEVOS patrones específicos
            r'\b(me\s*la\s*podes\s*mandar|me\s*la\s*puedes\s*mandar|me\s*lo\s*podes\s*mandar|me\s*lo\s*puedes\s*mandar)\s*(por)?\s*(email|mail|correo)?\b',
            r'\b(mándamela|mandamela|envíamela|enviamela)\s*(por)?\s*(email|mail|correo)?\b',
            r'\bmail\b(?!\s*(de|from|@))',  # Detectar "mail" solo
        ]
        
        message_lower = message.lower()
        for pattern in email_patterns:
            if re.search(pattern, message_lower):
                logging.info(f"📧 Email command detected (fallback): '{message}'")
                return True
        return False

@retry_operation(max_retries=2)  # Reducido reintentos
def generate_ai_response_with_assistant(athlete_id, user_message):
    """Versión optimizada de generación de respuestas AI con cache y rate limit management"""
    start_time = time.time()
    
    # Validaciones tempranas
    if not openai_client:
        return "❌ Cliente OpenAI no configurado. Verifica las credenciales."
    
    if not OPENAI_ASSISTANT_ID:
        return "❌ Assistant ID no configurado. Verifica la configuración."
    
    try:
        # Obtener datos del atleta
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "❌ No se encontraron datos del atleta"
        
        # 🎯 NUEVO: Verificar cache primero
        if CACHE_AVAILABLE and cache_manager:
            cached_response = cache_manager.get_cached_response(athlete_data, user_message)
            if cached_response:
                # Log cache hit
                if MONITORING_AVAILABLE and performance_monitor:
                    performance_monitor.log_request(
                        athlete_id=athlete_id,
                        request_type='cache_hit',
                        response_time=time.time() - start_time,
                        success=True
                    )
                logging.info(f"🚀 Cache hit - respuesta inmediata para atleta {athlete_id}")
                return cached_response
        
        # 🚦 NUEVO: Verificar rate limits antes de consultar OpenAI
        if MONITORING_AVAILABLE and rate_limit_manager:
            estimated_tokens = rate_limit_manager.estimate_tokens(user_message)
            should_throttle, reason, delay = rate_limit_manager.should_throttle_request(estimated_tokens)
            
            if should_throttle:
                logging.warning(f"🚦 Throttling request: {reason} (delay: {delay}s)")
                if delay > 30:  # Si el delay es muy largo, sugerir usar cache o esperar
                    return f"🚦 Sistema temporalmente ocupado. {reason}. Intenta en unos minutos o reformula tu pregunta para usar respuestas existentes."
                else:
                    time.sleep(delay)  # Delay corto
        
        # Si no hay cache, proceder con OpenAI
        logging.info(f"🔄 Cache miss - consultando OpenAI para atleta {athlete_id}")
        
        # Obtener principios deportivos
        sport_principles = get_sport_adaptation_principles(athlete_data['sport'])
        level_guidelines = get_progression_guidelines(athlete_data['level'])
        
        # Contexto de rutinas previas (simplificado)
        previous_routines = get_previous_routines(athlete_id, limit=2)  # Solo 2 últimas
        routine_context = ""
        if previous_routines:
            routine_context = f"\\nRutinas recientes: Evita repetir ejercicios de las últimas {len(previous_routines)} rutinas."
        
        # Detectar si es una solicitud de email para modificar contexto
        is_email_request = st.session_state.get(f'email_request_{athlete_id}', False)
        
        # Contexto adicional para emails
        email_context = ""
        if is_email_request:
            # Verificar si hay Excel disponible
            has_existing_excel = get_last_excel_from_session(athlete_id) is not None
            
            if has_existing_excel:
                email_context = "\n\nNOTA: El usuario solicita envío por email. Hay una rutina reciente disponible que se enviará automáticamente. Responde de forma natural confirmando el envío."
            else:
                email_context = "\n\nIMPORTANTE: El usuario solicita que la rutina se envíe por email. Genera una rutina completa y detallada con [INICIO_NUEVA_RUTINA] al inicio."
            
            # Limpiar el flag
            st.session_state.pop(f'email_request_{athlete_id}', None)
        
        # Prompt ULTRA COMPACTO para mejor rendimiento y menor uso de tokens
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
        PLANIFICACIONES: Si piden múltiples días (ej: 5 días), asegúrate de incluir TODOS los días solicitados.
        EMAIL: Si el usuario solicita envío por email, SIEMPRE genera rutina completa con [INICIO_NUEVA_RUTINA] - el sistema enviará automáticamente. IMPORTANTE: Cuando detectes solicitud de email, proporciona una rutina COMPLETA y DETALLADA sin limitaciones de longitud.{routine_context}{email_context}
        """
        
        # Prompt final optimizado para tokens
        prompt = f"{context}\\n\\nConsulta: {user_message}"
        
        # Obtener o crear thread para el atleta - NUEVA GESTIÓN INTELIGENTE
        def create_thread():
            if not openai_client or not hasattr(openai_client, 'beta'):
                raise ValueError("OpenAI client no configurado correctamente")
            return openai_client.beta.threads.create()
        
        # Usar thread manager inteligente si está disponible
        if THREAD_MANAGER_AVAILABLE and thread_manager:
            thread_id = thread_manager.get_or_create_smart_thread(athlete_id, create_thread)
            # Registrar estimación de tokens del mensaje
            thread_manager.log_message_tokens(athlete_id, user_message)
        else:
            # Fallback al método original
            thread_id = get_or_create_thread_id(athlete_id, create_thread)
        
        # Añadir mensaje del usuario
        if not openai_client or not hasattr(openai_client, 'beta'):
            return "❌ OpenAI client no configurado correctamente"
            
        openai_client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt
        )
        
        # Ejecutar assistant con timeout optimizado
        run = openai_client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID
        )
        
        # Esperar respuesta con timeout más corto
        start_openai = time.time()
        
        while True:
            elapsed_time = time.time() - start_openai
            if elapsed_time > OPENAI_TIMEOUT:
                logging.error(f"Timeout ({OPENAI_TIMEOUT}s) - atleta {athlete_id}")
                # Log timeout
                if MONITORING_AVAILABLE and performance_monitor:
                    performance_monitor.log_request(
                        athlete_id=athlete_id,
                        request_type='openai',
                        response_time=time.time() - start_time,
                        success=False,
                        error_message="Timeout"
                    )
                return "⏱️ Timeout. Intenta con una pregunta más corta o específica."
            
            try:
                run_status = openai_client.beta.threads.runs.retrieve(
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
                # Log failure
                if MONITORING_AVAILABLE and performance_monitor:
                    performance_monitor.log_request(
                        athlete_id=athlete_id,
                        request_type='openai',
                        response_time=time.time() - start_time,
                        success=False,
                        error_message="OpenAI run failed"
                    )
                return "❌ Error procesando consulta. Intenta reformularla."
            elif run_status.status in ["cancelled", "expired"]:
                return "⚠️ Consulta interrumpida. Inténtalo de nuevo."
            
            time.sleep(POLL_INTERVAL)
        
        # Recuperar respuesta con optimización
        try:
            messages = openai_client.beta.threads.messages.list(thread_id=thread_id)
            
            # Buscar respuesta más reciente
            for msg in messages.data:
                if msg.role == "assistant" and msg.run_id == run.id and msg.content:
                    # Manejar diferentes tipos de contenido de manera segura
                    response = ""
                    for content_block in msg.content:
                        try:
                            # Solo intentar acceder a text si el tipo lo soporta
                            if hasattr(content_block, 'text'):
                                text_obj = getattr(content_block, 'text', None)
                                if text_obj and hasattr(text_obj, 'value'):
                                    response = text_obj.value
                                    break
                        except (AttributeError, TypeError):
                            continue
                    
                    if not response:
                        continue
                    
                    # 🧹 NUEVO: Limpiar respuesta usando response_cleaner
                    if RESPONSE_CLEANER_AVAILABLE and response_cleaner:
                        if "[INICIO_NUEVA_RUTINA]" in response:
                            response = response_cleaner.format_routine_response(response)
                        else:
                            response = response_cleaner.enhance_response_formatting(response)
                    
                    # 🎯 OPTIMIZACIÓN INTELIGENTE: Solo cortar si NO es rutina completa
                    # Verificar si era una solicitud de email (usando el contexto modificado)
                    is_email_request = "El usuario solicita que la rutina se envíe por email" in prompt
                    is_routine_response = any(keyword in response.lower() for keyword in [
                        'día 1', 'día 2', 'sesión 1', 'sesión 2', 'bloque', 'calentamiento', 
                        'entrenamiento', 'ejercicio', 'series', 'repeticiones'
                    ])
                    
                    # Solo aplicar límite si NO es una rutina y NO es email
                    if not is_routine_response and not is_email_request:
                        max_length = MAX_RESPONSE_LENGTH // 2  # Límite más estricto para respuestas generales
                        if len(response) > max_length:
                            response = response[:max_length-50] + "\\n\\n⚡ *Respuesta resumida. Pregunta por detalles específicos.*"
                    elif len(response) > MAX_RESPONSE_LENGTH * 3:  # Solo cortar rutinas EXTREMADAMENTE largas
                        response = response[:MAX_RESPONSE_LENGTH * 3-100] + "\\n\\n📋 *Rutina optimizada. Solicita detalles adicionales si los necesitas.*"
                    
                    # Estimar tokens usados
                    estimated_tokens_used = (len(prompt) + len(response)) // 4  # Aproximación
                    
                    # 📊 NUEVO: Registrar tokens de respuesta en thread manager
                    if THREAD_MANAGER_AVAILABLE and thread_manager:
                        thread_manager.log_message_tokens(athlete_id, "", response)
                    
                    # 📊 Log successful request
                    if MONITORING_AVAILABLE:
                        if performance_monitor:
                            performance_monitor.log_request(
                                athlete_id=athlete_id,
                                request_type='openai',
                                response_time=time.time() - start_time,
                                tokens_used=estimated_tokens_used,
                                success=True
                            )
                        if rate_limit_manager:
                            rate_limit_manager.log_request(estimated_tokens_used)
                    
                    # �💾 NUEVO: Guardar en cache
                    if CACHE_AVAILABLE and cache_manager:
                        cache_manager.cache_response(athlete_data, user_message, response)
                    
                    logging.info(f"Respuesta exitosa - atleta {athlete_id} ({len(response)} chars, ~{estimated_tokens_used} tokens)")
                    return response
            
            # Fallback simplificado
            return "🤔 Consulta procesada pero sin respuesta clara. Reformula tu pregunta."
                
        except Exception as e:
            logging.error(f"Error recuperando respuesta: {e}")
            # Log error
            if MONITORING_AVAILABLE and performance_monitor:
                performance_monitor.log_request(
                    athlete_id=athlete_id,
                    request_type='openai',
                    response_time=time.time() - start_time,
                    success=False,
                    error_message=str(e)
                )
            return "❌ Error recuperando respuesta. Inténtalo de nuevo."
        
    except APITimeoutError:
        return "⏱️ Timeout de API. Inténtalo de nuevo."
    except RateLimitError:
        return "🚦 Servicio ocupado. Espera un momento e inténtalo de nuevo."
    except APIConnectionError:
        return "🌐 Error de conexión. Verifica tu internet."
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        # Log unexpected error
        if MONITORING_AVAILABLE and performance_monitor:
            performance_monitor.log_request(
                athlete_id=athlete_id,
                request_type='openai',
                response_time=time.time() - start_time,
                success=False,
                error_message=str(e)
            )
        return "❌ Error inesperado. Inténtalo más tarde."

@with_loading("Procesando mensaje...")
def handle_user_message(athlete_id, user_message):
    """Maneja mensajes del usuario - versión optimizada"""
    try:
        # Validar mensaje
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            return error_msg
        
        # Detectar comando de email y preparar contexto
        wants_email = detect_email_command(user_message)
        logging.info(f"🔍 Email detection for '{user_message}': {wants_email}")
        
        if wants_email:
            # NO modificar el mensaje del usuario visible
            # En su lugar, usar flag para modificar el contexto del sistema
            logging.info(f"📧 Email command detected, will modify system context")
            st.session_state[f'email_request_{athlete_id}'] = True
        
        # Generar respuesta
        ai_response = generate_ai_response_with_assistant(athlete_id, user_message)
        
        # 🔍 DEBUGGING: Log longitud de respuesta
        logging.info(f"📝 Response length: {len(ai_response)} chars. First 100 chars: {ai_response[:100]}...")
        
        # Guardar en base de datos
        session_id = get_or_create_chat_session(athlete_id)
        save_message(session_id, user_message, True)
        save_message(session_id, ai_response, False)
        
        # Guardar resumen si es rutina
        if "[INICIO_NUEVA_RUTINA]" in ai_response:
            save_routine_summary(session_id, ai_response)
        
        # 📧 NUEVO: Sistema inteligente de email que usa Excel existente
        if wants_email:
            email_sent = False
            
            # 🎯 ESTRATEGIA 1: Buscar último Excel generado en la sesión
            last_excel_data = get_last_excel_from_session(athlete_id)
            
            if last_excel_data and AUTO_EMAIL_AVAILABLE and auto_email_handler:
                logging.info(f"📧 Usando Excel existente para envío automático - Atleta {athlete_id}")
                
                # Usar Excel ya generado
                success, email_message = auto_email_handler.send_existing_excel(
                    athlete_id=athlete_id,
                    excel_data=last_excel_data['excel_data'],
                    filename=last_excel_data['filename'],
                    user_message=user_message
                )
                
                if success:
                    ai_response += f"\n\n✅ {email_message} (usando rutina ya generada)"
                    email_sent = True
                else:
                    logging.warning(f"⚠️ Falló envío de Excel existente: {email_message}")
            
            # 🎯 ESTRATEGIA 2: Si no hay Excel, generar rutina nueva (solo si no se envió ya)
            if not email_sent:
                if "[INICIO_NUEVA_RUTINA]" in ai_response:
                    # Ya hay rutina nueva, usar el sistema original
                    if AUTO_EMAIL_AVAILABLE and auto_email_handler:
                        success, email_message = auto_email_handler.process_email_request(
                            athlete_id=athlete_id,
                            routine_text=ai_response,
                            user_message=user_message
                        )
                        
                        if success:
                            ai_response += f"\n\n✅ {email_message}"
                        else:
                            ai_response += f"\n\n❌ {email_message}"
                
                # 🎯 ESTRATEGIA 3: Detectar rutinas sin marcador específico
                elif any(keyword in ai_response.lower() for keyword in ['rutina', 'entrenamiento', 'ejercicio', 'día 1', 'bloque']):
                    if AUTO_EMAIL_AVAILABLE and auto_email_handler:
                        success, email_message = auto_email_handler.process_email_request(
                            athlete_id=athlete_id,
                            routine_text=ai_response,
                            user_message=user_message
                        )
                        
                        if success:
                            ai_response += f"\n\n✅ {email_message}"
                        else:
                            ai_response += f"\n\n⚠️ {email_message}"
                
                # 🎯 ESTRATEGIA 4: Si no hay rutina, informar que no hay contenido
                else:
                    ai_response += "\n\n📋 No hay rutina disponible para enviar. Solicita una rutina primero y luego pide el envío por email."
        
        return ai_response
        
    except Exception as e:
        logging.error(f"Error en handle_user_message: {e}")
        return "❌ Error procesando mensaje. Inténtalo de nuevo."

def get_last_excel_from_session(athlete_id: int) -> Optional[dict]:
    """
    Obtiene los datos del último Excel generado para un atleta
    Busca en session_state por archivos Excel recientes
    """
    try:
        import streamlit as st
        
        # Buscar keys que contengan datos de Excel para este atleta
        excel_keys = [key for key in st.session_state.keys() 
                     if key.startswith(f'excel_data_{athlete_id}_') or 
                        key.startswith(f'routine_excel_{athlete_id}_')]
        
        if not excel_keys:
            logging.info(f"📊 No se encontró Excel previo para atleta {athlete_id}")
            return None
        
        # Obtener el más reciente (por timestamp en el key)
        latest_key = max(excel_keys, key=lambda k: st.session_state.get(f"{k}_timestamp", 0))
        excel_data = st.session_state.get(latest_key)
        
        if excel_data:
            # Buscar también el filename asociado
            filename_key = f"{latest_key}_filename"
            filename = st.session_state.get(filename_key, f"Rutina_Atleta_{athlete_id}.xlsx")
            
            logging.info(f"✅ Excel encontrado para atleta {athlete_id}: {filename}")
            return {
                'excel_data': excel_data,
                'filename': filename,
                'key': latest_key
            }
        
        return None
        
    except Exception as e:
        logging.error(f"❌ Error obteniendo último Excel: {e}")
        return None


# Función para obtener historial (simplificada)
def get_chat_history(athlete_id):
    """Obtiene historial de chat optimizado"""
    try:
        return load_chat_history(athlete_id, limit=15)  # Límite reducido
    except Exception as e:
        logging.error(f"Error cargando historial: {e}")
        return []
