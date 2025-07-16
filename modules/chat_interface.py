import openai
import logging
import time
import streamlit as st
import re
from modules.athlete_manager import get_athlete_data
from modules.chat_manager import get_or_create_chat_session, save_message, load_chat_history, get_or_create_thread_id, get_previous_routines, save_routine_summary
from modules.training_variations import (
    get_sport_adaptation_principles, get_progression_guidelines, get_creativity_strategies,
    get_exercise_categories, CREATIVE_COMBINATIONS, ROUTINE_METHODOLOGY, 
    TRAINING_PRINCIPLES, CREATIVITY_PRINCIPLES, SPORT_ADAPTATION_PRINCIPLES
)
from utils.app_utils import retry_operation, performance_monitor, with_loading
import os

# Configurar OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")
OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID")

# Validar configuración
if not openai.api_key:
    logging.error("OPENAI_API_KEY no configurada")
if not OPENAI_ASSISTANT_ID:
    logging.error("OPENAI_ASSISTANT_ID no configurada")

def validate_message(message):
    """Valida el mensaje del usuario"""
    if not message or not message.strip():
        return False, "El mensaje no puede estar vacío"
    
    if len(message) > 5000:
        return False, "El mensaje no puede exceder 5000 caracteres"
    
    # Filtro básico de contenido inapropiado
    inappropriate_words = ["spam", "hack", "malware"]  # Expandir según necesidades
    message_lower = message.lower()
    if any(word in message_lower for word in inappropriate_words):
        return False, "El mensaje contiene contenido inapropiado"
    
    return True, ""

def detect_email_command(message):
    """Detecta si el mensaje contiene un comando para enviar por email"""
    email_patterns = [
        r'\b(envía|envía|envíalo|manda|mandalo|mandaselo|envíaselo)\s*(por)?\s*(email|mail|correo)\b',
        r'\b(email|mail|correo)\s*(me|lo|la|esto|eso)\b',
        r'\b(send|enviar)\s*(by|por)?\s*(email|mail)\b',
        r'\b(quiero|necesito|puedes)\s*(enviarlo|mandarlo)\s*(por)?\s*(email|mail|correo)\b',
        r'\b(por favor|please)\s*(envía|manda|send)\s*(por)?\s*(email|mail|correo)\b'
    ]
    
    message_lower = message.lower()
    for pattern in email_patterns:
        if re.search(pattern, message_lower, re.IGNORECASE):
            return True
    return False

def extract_email_from_message(message):
    """Extrae una dirección de email del mensaje si existe"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, message)
    return emails[0] if emails else None

@retry_operation(max_retries=2)
@performance_monitor
def generate_ai_response_with_assistant(athlete_id, user_message):
    """Genera respuesta de IA usando OpenAI Assistant con manejo robusto de errores"""
    try:
        # Validar configuración
        if not openai.api_key or not OPENAI_ASSISTANT_ID:
            return "Error de configuración del servicio de IA. Contacta al administrador."
        
        # Obtener datos del atleta
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "Error: No se encontró información del atleta."
        
        # Obtener rutinas previas para evitar repeticiones
        previous_routines = get_previous_routines(athlete_id, limit=3)
        routine_context = ""
        
        if previous_routines:
            routine_context = "\n\nRUTINAS PREVIAS GENERADAS (evita repetir):\n"
            for idx, (summary, date) in enumerate(previous_routines, 1):
                routine_context += f"Rutina {idx} ({date.strftime('%d/%m')}):\n{summary}\n\n"
            routine_context += "IMPORTANTE: Genera rutinas COMPLETAMENTE DIFERENTES a las anteriores.\n"
        
        # Obtener datos del deportista para metodología híbrida inteligente
        sport_principles = get_sport_adaptation_principles(athlete_data['sport'])
        level_guidelines = get_progression_guidelines(athlete_data['level'])
        
        hybrid_context = f"""
        
        METODOLOGÍA HÍBRIDA PROFIT COACH:
        
        🎯 FILOSOFÍA INTELIGENTE:
        - COMBINA ejercicios tradicionales con innovaciones funcionales
        - VARÍA sistemáticamente - nunca repite rutinas idénticas
        - ADAPTA según deporte, nivel y contexto específico
        - PERSONALIZA completamente cada propuesta
        
        📋 ESTRUCTURA METODOLÓGICA - 5 BLOQUES ESPECIALIZADOS:
        1. ACTIVACIÓN GLÚTEA: {ROUTINE_METHODOLOGY['bloque_1']['principios'][0]}
        2. DINÁMICO/POTENCIA/DIAGONALES/ZONA MEDIA: {ROUTINE_METHODOLOGY['bloque_2']['principios'][0]}
        3. FUERZA 1: {ROUTINE_METHODOLOGY['bloque_3']['principios'][0]}
        4. FUERZA 2: {ROUTINE_METHODOLOGY['bloque_4']['principios'][0]}
        5. CONTRASTE/PREVENTIVOS/RSA: {ROUTINE_METHODOLOGY['bloque_5']['principios'][0]}
        
        🔄 ALTERNATIVA CIRCUITO INTEGRAL:
        - Formato: {ROUTINE_METHODOLOGY['alternativa_circuito']['formato']}
        - Reemplaza: Bloque 3 y 4 (Fuerza 1 y 2) por un circuito que integra todas las capacidades
        - Enfoque: {ROUTINE_METHODOLOGY['alternativa_circuito']['principios'][0]}
        
        🏃‍♂️ ADAPTACIÓN ESPECÍFICA PARA {athlete_data['sport'].upper()}:
        - Enfoque: {sport_principles['enfoque'][0]}
        - Demandas: {sport_principles['enfoque'][1] if len(sport_principles['enfoque']) > 1 else 'Desarrollo integral'}
        - Categoría: Deporte específico adaptado
        
        📊 GUÍAS NIVEL {athlete_data['level'].upper()}:
        - Filosofía: {level_guidelines['filosofia']}
        - Métodos preferidos: {', '.join(level_guidelines['metodos_preferidos'])}
        - Parámetros: Volumen {level_guidelines['parametros']['volumen']}, Intensidad {level_guidelines['parametros']['intensidad']}
        
        🎨 PRINCIPIOS DE CREATIVIDAD:
        - Variación sistemática: {CREATIVITY_PRINCIPLES['variacion_sistematica']['estrategias'][0]}
        - Combinación inteligente: {CREATIVITY_PRINCIPLES['combinacion_inteligente']['criterios'][0]}
        - Individualización: {CREATIVITY_PRINCIPLES['individualizacion']['factores'][0]}
        """
        
        # Construir contexto metodológico híbrido
        context = f"""
        Eres ProFit Coach AI, especialista en metodología de entrenamiento híbrida e inteligente.
        
        ATLETA: {athlete_data['name']}
        - Deporte: {athlete_data['sport']}
        - Nivel: {athlete_data['level']}
        - Objetivos: {athlete_data.get('goals', 'No especificados')}
        
        🎯 METODOLOGÍA HÍBRIDA INTELIGENTE:
        - COMBINA ejercicios tradicionales sólidos con innovaciones funcionales
        - USA ejercicios tradicionales como BASE, no como limitación
        - INCORPORA elementos creativos para transferencia y motivación
        - VARÍA sistemáticamente manteniendo objetivos claros
        - NUNCA te limites a listas fijas - CREA según el contexto
        
        🧠 PRINCIPIOS DE VARIABILIDAD:
        - Cada rutina debe ser ÚNICA pero LÓGICA
        - Combina patrones fundamentales (sentadilla, empuje, tracción) con variaciones
        - Alterna entre métodos tradicionales e innovadores según el momento
        - Progresa de ejercicios conocidos a combinaciones creativas
        - Mantén coherencia con las demandas del deporte
        
        📋 ESTRUCTURA PROFESIONAL PARA RUTINAS:
        
        [INICIO_NUEVA_RUTINA]
        
        🍑 BLOQUE 1 - ACTIVACIÓN GLÚTEA
        Principio: {ROUTINE_METHODOLOGY['bloque_1']['principios'][0]}
        - [Activación glúteo medio/mayor]: [Progresión específica]
        - [Estabilización pélvica]: [Técnica detallada]
        - [Preparación para movimientos complejos]: [Metodología]
        
        ⚡ BLOQUE 2 - DINÁMICO/POTENCIA/DIAGONALES/ZONA MEDIA
        Principio: {ROUTINE_METHODOLOGY['bloque_2']['principios'][0]}
        - [Selección según objetivo]: [Potencia/Diagonales/Zona Media]
        - [Movimientos multiplanares]: [Progresión específica]
        - [Transferencia deportiva]: [Aplicación directa]
        
        💪 BLOQUE 3 - FUERZA 1
        Principio: {ROUTINE_METHODOLOGY['bloque_3']['principios'][0]}
        - [Patrón fundamental]: [Ejercicio tradicional + variación]
        - [Movimiento unilateral]: [Progresión específica]
        - [Base sólida]: [Metodología estructurada]
        
        🔥 BLOQUE 4 - FUERZA 2  
        Principio: {ROUTINE_METHODOLOGY['bloque_4']['principios'][0]}
        - [Movimiento combinado]: [Complejidad coordinativa]
        - [Patrón asimétrico/rotacional]: [Transferencia específica]
        - [Alta demanda técnica]: [Progresión avanzada]
        
        🚀 BLOQUE 5 - CONTRASTE/PREVENTIVOS/RSA
        Principio: {ROUTINE_METHODOLOGY['bloque_5']['principios'][0]}
        - [Contraste fuerza-velocidad]: [Metodología específica]
        - [Ejercicios preventivos]: [Enfoque personalizado]
        - [RSA específico del deporte]: [Aplicación contextual]
        
        � ALTERNATIVA - CIRCUITO INTEGRAL (6 ejercicios x 5 series)
        Reemplaza Fuerza 1 y 2: {ROUTINE_METHODOLOGY['alternativa_circuito']['principios'][0]}
        - [Ejercicio fuerza]: [Parámetros]
        - [Ejercicio potencia]: [Progresión]
        - [Ejercicio velocidad]: [Aplicación]
        - [Ejercicio zona media]: [Técnica]
        - [Ejercicio transferencia]: [Especificidad]
        - [Ejercicio funcional]: [Innovación]
        
        🎨 CREATIVIDAD INTELIGENTE:
        - PUEDES usar sentadilla, pero varíala (búlgara, frontal, unilateral, con salto)
        - PUEDES usar press, pero combínalo (con rotación, unilateral, en superficies inestables)
        - PUEDES usar ejercicios tradicionales, pero adáptales al deporte específico
        - CREA combinaciones lógicas (fuerza + potencia, técnico + físico)
        - INNOVA dentro de la lógica del entrenamiento
        
        ✅ ENFOQUE HÍBRIDO RECOMENDADO:
        - Base sólida con ejercicios tradicionales eficaces
        - Variaciones funcionales para transferencia
        - Elementos creativos para motivación
        - Progresiones específicas del deporte
        - Metodología adaptada al nivel
        
        🎯 PERSONALIZACIÓN NIVEL {athlete_data['level'].upper()}:
        - Filosofía: {level_guidelines['filosofia']}
        - Métodos: {', '.join(level_guidelines['metodos_preferidos'][:2])}
        - Innovación: {level_guidelines['innovacion']}
        
        🏃‍♂️ ESPECIFICIDAD {athlete_data['sport'].upper()}:
        - Enfoque principal: {sport_principles['enfoque'][0]}
        - Demanda secundaria: {sport_principles['enfoque'][1] if len(sport_principles['enfoque']) > 1 else 'Desarrollo integral'}
        
        INSTRUCCIONES FINALES:
        - Responde en español con terminología profesional
        - Combina inteligentemente tradicional + innovador
        - Sé específico con parámetros y progresiones
        - Marca rutinas completas con [INICIO_NUEVA_RUTINA]
        - NUNCA repitas rutinas idénticas - varía sistemáticamente
        - Explica la lógica detrás de cada elección
        - Mantén coherencia con objetivos específicos
        - Adapta complejidad al nivel del atleta
        {routine_context}
        {hybrid_context}
        """
        
        prompt = f"{context}\n\nConsulta del atleta: {user_message}"
        
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
        
        # Ejecutar assistant
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPENAI_ASSISTANT_ID
        )
        
        # Esperar respuesta con timeout extendido
        max_wait_time = 60  # Aumentado a 60 segundos
        start_time = time.time()
        
        while True:
            if time.time() - start_time > max_wait_time:
                logging.error(f"Timeout al esperar respuesta de OpenAI para atleta {athlete_id}")
                return "⏱️ La consulta está tardando más de lo esperado. Por favor, inténtalo de nuevo con una consulta más específica."
            
            try:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            except Exception as e:
                logging.error(f"Error al verificar estado del run: {e}")
                time.sleep(2)
                continue
            
            if run_status.status == "completed":
                break
            elif run_status.status == "failed":
                logging.error(f"OpenAI Assistant falló para atleta {athlete_id}: {run_status.last_error}")
                return "❌ No pude procesar tu consulta en este momento. Por favor, inténtalo de nuevo."
            elif run_status.status in ["cancelled", "expired"]:
                logging.error(f"OpenAI run {run_status.status} para atleta {athlete_id}")
                return "⚠️ La consulta fue interrumpida. Por favor, inténtalo de nuevo."
            elif run_status.status == "requires_action":
                logging.warning(f"OpenAI run requiere acción para atleta {athlete_id}")
                # Continuar esperando por si se resuelve automáticamente
            
            time.sleep(2)  # Aumentado el tiempo de espera entre verificaciones
        
        # Recuperar respuesta con manejo robusto
        try:
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            
            # Buscar la respuesta más reciente del assistant
            for msg in messages.data:
                if msg.role == "assistant" and msg.run_id == run.id and msg.content:
                    response = msg.content[0].text.value
                    
                    # Solo cortar si es extremadamente largo (más de 8000 caracteres)
                    if len(response) > 8000:
                        response = response[:7995] + "\n\n[Respuesta cortada por límite de longitud. Puedes preguntar por más detalles específicos.]"
                    
                    logging.info(f"Respuesta generada exitosamente para atleta {athlete_id}")
                    return response
            
            # Fallback: última respuesta del assistant
            for msg in messages.data:
                if msg.role == "assistant" and msg.content:
                    response = msg.content[0].text.value
                    # Solo cortar si es extremadamente largo
                    if len(response) > 8000:
                        response = response[:7995] + "\n\n[Respuesta cortada por límite de longitud. Puedes preguntar por más detalles específicos.]"
                    
                    logging.info(f"Respuesta fallback obtenida para atleta {athlete_id}")
                    return response
            
            # Si no se encuentra respuesta, verificar si hay algún mensaje en el thread
            if messages.data:
                logging.warning(f"Thread tiene mensajes pero ninguna respuesta válida para atleta {athlete_id}")
                return "🤔 Recibí tu consulta pero tuve problemas generando la respuesta. ¿Podrías intentar reformular tu pregunta?"
            else:
                logging.error(f"No se encontraron mensajes en el thread para atleta {athlete_id}")
                return "❌ No se pudo recuperar la respuesta. Por favor, inténtalo de nuevo."
                
        except Exception as e:
            logging.error(f"Error al recuperar mensajes del thread: {e}")
            return "❌ Error al recuperar la respuesta. Por favor, inténtalo de nuevo."
        
    except openai.APITimeoutError:
        logging.error(f"Timeout de OpenAI API para atleta {athlete_id}")
        return "La consulta está tardando más de lo esperado. Por favor, inténtalo de nuevo."
    
    except openai.RateLimitError:
        logging.error(f"Rate limit excedido para atleta {athlete_id}")
        return "Servicio temporalmente sobrecargado. Por favor, espera un momento e inténtalo de nuevo."
    
    except openai.APIConnectionError:
        logging.error(f"Error de conexión con OpenAI para atleta {athlete_id}")
        return "Error de conexión con el servicio de IA. Verifica tu conexión a internet."
    
    except openai.AuthenticationError:
        logging.error("Error de autenticación con OpenAI")
        return "Error de configuración del servicio. Contacta al administrador."
    
    except Exception as e:
        logging.error(f"Error inesperado en generate_ai_response_with_assistant: {e}")
        return "Ocurrió un error inesperado. Por favor, inténtalo de nuevo más tarde."

@with_loading("Procesando tu mensaje...")
def handle_user_message(athlete_id, user_message):
    """Maneja el mensaje del usuario con validaciones, detección de comandos de email y manejo de errores"""
    try:
        logging.info(f"Iniciando procesamiento de mensaje para atleta {athlete_id}")
        
        # Validar mensaje
        is_valid, error_msg = validate_message(user_message)
        if not is_valid:
            logging.warning(f"Mensaje inválido para atleta {athlete_id}: {error_msg}")
            st.error(error_msg)
            return None
        
        # Detectar comando de email
        email_requested = detect_email_command(user_message)
        extracted_email = extract_email_from_message(user_message) if email_requested else None
        
        # Obtener sesión de chat
        session_id = get_or_create_chat_session(athlete_id)
        if not session_id:
            logging.error(f"No se pudo crear sesión de chat para atleta {athlete_id}")
            st.error("Error al crear sesión de chat")
            return None
        
        logging.info(f"Sesión de chat obtenida: {session_id} para atleta {athlete_id}")
        
        # Guardar mensaje del usuario
        success = save_message(session_id, user_message.strip(), is_from_user=True)
        if not success:
            logging.error(f"Error al guardar mensaje del usuario para sesión {session_id}")
            st.error("Error al guardar tu mensaje")
            return None
        
        logging.info(f"Mensaje del usuario guardado exitosamente para sesión {session_id}")
        
        # Si se solicitó email y hay una rutina previa, intentar enviarla
        if email_requested:
            handled_email = handle_email_request(athlete_id, extracted_email, user_message)
            if handled_email:
                return handled_email
        
        # Generar respuesta de IA
        logging.info(f"Iniciando generación de respuesta IA para atleta {athlete_id}")
        ai_response = generate_ai_response_with_assistant(athlete_id, user_message)
        
        if not ai_response:
            logging.error(f"No se generó respuesta IA para atleta {athlete_id}")
            st.error("No se pudo generar una respuesta")
            return None
        
        logging.info(f"Respuesta IA generada exitosamente para atleta {athlete_id}, longitud: {len(ai_response)}")
        
        # Guardar respuesta de IA
        success = save_message(session_id, ai_response, is_from_user=False)
        if not success:
            logging.warning(f"Respuesta generada pero no se pudo guardar para sesión {session_id}")
            st.warning("Respuesta generada pero no se pudo guardar en el historial")
        else:
            logging.info(f"Respuesta IA guardada exitosamente para sesión {session_id}")
        
        # Si es una rutina, guardar resumen para evitar repeticiones
        if ("[INICIO_NUEVA_RUTINA]" in ai_response or 
            any(keyword in ai_response.lower() for keyword in ['día 1', 'día 2', 'rutina semanal', 'entrenamiento semanal'])):
            logging.info(f"Detectada rutina en respuesta para sesión {session_id}")
            save_routine_summary(session_id, ai_response)
            
            # Si se solicitó email y se generó una nueva rutina, mostrar opción automática
            if email_requested:
                st.session_state[f'auto_email_routine_{athlete_id}'] = {
                    'routine': ai_response,
                    'email': extracted_email
                }
        
        logging.info(f"Mensaje procesado exitosamente para atleta {athlete_id}")
        return ai_response
        
    except Exception as e:
        logging.error(f"Error en handle_user_message para atleta {athlete_id}: {e}", exc_info=True)
        st.error("Error al procesar tu mensaje. Por favor, inténtalo de nuevo.")
        return None

def handle_email_request(athlete_id, extracted_email, original_message):
    """Maneja solicitudes de envío por email"""
    try:
        from modules.routine_export import create_simple_routine_excel
        from modules.email_manager import send_routine_email
        
        # Obtener datos del atleta
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "❌ No se encontraron datos del atleta."
        
        # Obtener la última rutina generada
        previous_routines = get_previous_routines(athlete_id, limit=1)
        if not previous_routines:
            return "🤔 No encontré ninguna rutina previa para enviar. ¿Podrías pedirme que genere una rutina primero?"
        
        last_routine = previous_routines[0][0]  # Obtener el contenido de la rutina
        
        # Determinar email a usar
        email_to_use = extracted_email or athlete_data.get('email', '').strip()
        
        if not email_to_use:
            return "📧 Para enviarte la rutina por email, necesito que me proporciones una dirección de email. Puedes escribir algo como: 'Envíalo a mi.email@gmail.com'"
        
        # Generar Excel
        excel_data = create_simple_routine_excel(athlete_id, last_routine)
        if not excel_data:
            return "❌ Hubo un problema al generar el archivo Excel de la rutina."
        
        # Crear nombre de archivo
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Rutina_{athlete_data['name'].replace(' ', '_')}_{timestamp}.xlsx"
        
        # Enviar email
        success, message = send_routine_email(
            email_to_use,
            athlete_data['name'],
            excel_data,
            filename
        )
        
        if success:
            # Actualizar email del atleta si es diferente
            if extracted_email and extracted_email != athlete_data.get('email', ''):
                from modules.email_manager import update_athlete_email
                update_athlete_email(athlete_id, extracted_email)
            
            return f"✅ ¡Perfecto! He enviado tu rutina por email a: {email_to_use}\n\nRevisa tu bandeja de entrada (y también la carpeta de spam por si acaso). El email incluye:\n\n📋 Tu rutina completa en formato Excel\n📧 Instrucciones detalladas\n💪 Consejos importantes para el entrenamiento\n\n¡A entrenar se ha dicho! 🚀"
        else:
            return f"❌ Hubo un problema al enviar el email: {message}\n\nPor favor, verifica que la dirección {email_to_use} sea correcta e inténtalo de nuevo."
    
    except Exception as e:
        logging.error(f"Error en handle_email_request para atleta {athlete_id}: {e}")
        return "❌ Ocurrió un error al procesar tu solicitud de email. Por favor, inténtalo de nuevo."

@performance_monitor
def get_chat_history(athlete_id, limit=50):
    """Obtiene historial de chat con límite para mejor rendimiento"""
    try:
        session_id = get_or_create_chat_session(athlete_id)
        if not session_id:
            return []
        
        history = load_chat_history(session_id, limit=limit)
        logging.info(f"Historial obtenido para atleta {athlete_id}: {len(history)} mensajes")
        return history
        
    except Exception as e:
        logging.error(f"Error al obtener historial para atleta {athlete_id}: {e}")
        return []

def export_chat_to_text(athlete_id):
    """Exporta el chat a formato de texto"""
    try:
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return None
        
        history = get_chat_history(athlete_id)
        
        export_text = f"""
HISTORIAL DE CHAT - PROFIT COACH
===============================

Atleta: {athlete_data['name']}
Deporte: {athlete_data['sport']}
Nivel: {athlete_data['level']}
Fecha de exportación: {time.strftime('%Y-%m-%d %H:%M:%S')}

CONVERSACIÓN:
-------------

"""
        
        for msg, is_user, created_at in history:
            sender = "ATLETA" if is_user else "COACH AI"
            timestamp = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else "N/A"
            export_text += f"[{timestamp}] {sender}: {msg}\n\n"
        
        return export_text
        
    except Exception as e:
        logging.error(f"Error al exportar chat para atleta {athlete_id}: {e}")
        return None

def get_chat_statistics(athlete_id):
    """Obtiene estadísticas del chat"""
    try:
        history = get_chat_history(athlete_id)
        
        user_messages = sum(1 for _, is_user, _ in history if is_user)
        ai_messages = sum(1 for _, is_user, _ in history if not is_user)
        total_messages = len(history)
        
        if history:
            first_message = history[0][2] if history[0][2] else None
            last_message = history[-1][2] if history[-1][2] else None
        else:
            first_message = last_message = None
        
        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "first_message_date": first_message,
            "last_message_date": last_message
        }
        
    except Exception as e:
        logging.error(f"Error al obtener estadísticas de chat para atleta {athlete_id}: {e}")
        return {}