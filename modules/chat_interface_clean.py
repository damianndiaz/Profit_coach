"""
ProFit Coach - Chat Interface SQLite
Interfaz de chat simplificada para SQLite
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

# Importar configuración
from config import config

# OpenAI
from openai import OpenAI

# Módulos locales SQLite
from modules.athlete_manager import get_athlete_data
from modules.chat_manager import save_message, get_chat_history, get_welcome_message

# Configuración
OPENAI_TIMEOUT = 90
MAX_RESPONSE_LENGTH = 40000

def initialize_openai_client():
    """Inicializa el cliente de OpenAI"""
    try:
        if not config.OPENAI_API_KEY:
            raise ValueError("❌ No se encontró la API key de OpenAI")
        
        client = OpenAI(api_key=config.OPENAI_API_KEY)
        logging.info("✅ Cliente OpenAI inicializado correctamente")
        return client
    except Exception as e:
        logging.error(f"❌ Error inicializando OpenAI: {e}")
        return None

def detect_email_command(message):
    """Detecta si el mensaje contiene un comando de email"""
    email_patterns = [
        r'\b(enviar|mandar|email|correo|mail)\b.*\b(email|correo|mail)\b',
        r'\b(email|correo|mail)\b.*\b(enviar|mandar)\b',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    ]
    
    for pattern in email_patterns:
        if re.search(pattern, message.lower()):
            return True
    return False

def process_chat_message(athlete_id, user_message, openai_client):
    """Procesa un mensaje de chat y genera respuesta"""
    try:
        # Guardar mensaje del usuario
        save_message(athlete_id, user_message, is_user=True)
        
        # Obtener datos del atleta
        athlete_data = get_athlete_data(athlete_id)
        if not athlete_data:
            return "❌ Error: No se pudieron obtener los datos del atleta"
        
        # Obtener historial de chat
        chat_history = get_chat_history(athlete_id, limit=10)
        
        # Crear contexto para OpenAI
        system_message = f"""
Eres ProFit Coach AI, un entrenador personal especializado.

DATOS DEL ATLETA:
- Nombre: {athlete_data.get('name', 'N/A')}
- Deporte: {athlete_data.get('sport', 'N/A')}
- Nivel: {athlete_data.get('level', 'N/A')}
- Objetivos: {athlete_data.get('objectives', 'N/A')}

INSTRUCCIONES:
- Sé profesional pero amigable
- Personaliza las respuestas según el perfil del atleta
- Proporciona consejos específicos para su deporte y nivel
- Si necesitas más información, pregunta de manera específica
"""

        # Preparar mensajes para OpenAI
        messages = [{"role": "system", "content": system_message}]
        
        # Agregar historial de chat (últimos mensajes)
        for msg_content, is_user, _ in chat_history[-5:]:  # Últimos 5 mensajes
            role = "user" if is_user else "assistant"
            messages.append({"role": role, "content": msg_content})
        
        # Agregar mensaje actual
        messages.append({"role": "user", "content": user_message})
        
        # Llamada a OpenAI
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=3000,
            temperature=0.7,
            timeout=OPENAI_TIMEOUT
        )
        
        ai_response = response.choices[0].message.content
        
        # Truncar respuesta si es muy larga
        if len(ai_response) > MAX_RESPONSE_LENGTH:
            ai_response = ai_response[:MAX_RESPONSE_LENGTH] + "\n\n... [Respuesta truncada]"
        
        # Guardar respuesta de AI
        save_message(athlete_id, ai_response, is_user=False)
        
        return ai_response
        
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")
        error_msg = f"❌ Error procesando tu mensaje: {str(e)}"
        save_message(athlete_id, error_msg, is_user=False)
        return error_msg

def handle_user_message(athlete_id, user_message, openai_client=None):
    """Maneja un mensaje del usuario"""
    try:
        if not openai_client:
            openai_client = initialize_openai_client()
            if not openai_client:
                return "❌ Error: No se pudo conectar con el servicio de AI"
        
        # Detectar comandos especiales
        if detect_email_command(user_message):
            return "📧 Funcionalidad de email no disponible en esta versión SQLite"
        
        # Procesar mensaje normal
        return process_chat_message(athlete_id, user_message, openai_client)
        
    except Exception as e:
        logging.error(f"❌ Error en handle_user_message: {e}")
        return f"❌ Error procesando tu mensaje: {str(e)}"

def display_chat_interface(athlete_id):
    """Muestra la interfaz de chat en Streamlit"""
    try:
        st.subheader("💬 Chat con ProFit Coach AI")
        
        # Mostrar mensaje de bienvenida si no hay historial
        chat_history = get_chat_history(athlete_id)
        
        if not chat_history:
            welcome_msg = get_welcome_message(athlete_id)
            st.info(welcome_msg)
            save_message(athlete_id, welcome_msg, is_user=False)
        
        # Mostrar historial de chat
        for msg_content, is_user, created_at in chat_history:
            if is_user:
                st.chat_message("user").write(msg_content)
            else:
                st.chat_message("assistant").write(msg_content)
        
        # Input para nuevo mensaje
        if prompt := st.chat_input("Escribe tu mensaje..."):
            # Mostrar mensaje del usuario inmediatamente
            st.chat_message("user").write(prompt)
            
            # Procesar respuesta
            with st.chat_message("assistant"):
                with st.spinner("Pensando..."):
                    response = handle_user_message(athlete_id, prompt)
                    st.write(response)
            
            # Rerun para actualizar la interfaz
            st.rerun()
            
    except Exception as e:
        logging.error(f"❌ Error en display_chat_interface: {e}")
        st.error(f"❌ Error mostrando chat: {str(e)}")
