"""
Interfaz de Chat con SQLite - Versión Simplificada
"""

import logging
from modules.chat_manager import get_chat_history as get_chat_history_db, save_message, get_welcome_message as get_welcome_db

def get_chat_history(athlete_id):
    """Obtiene el historial de chat"""
    return get_chat_history_db(athlete_id)

def get_welcome_message(athlete_id):
    """Obtiene mensaje de bienvenida"""
    return get_welcome_db(athlete_id)

def detect_email_command(message):
    """Detecta si el mensaje solicita envío por email"""
    email_keywords = [
        'email', 'mail', 'correo', 'enviar', 'mandar', 
        'por email', 'por mail', 'por correo'
    ]
    
    message_lower = message.lower()
    for keyword in email_keywords:
        if keyword in message_lower:
            return True
    return False

def handle_user_message(athlete_id, user_message, uploaded_files=None):
    """Maneja un mensaje del usuario"""
    try:
        # Guardar mensaje del usuario
        save_message(athlete_id, user_message, is_user=True)
        
        # Respuesta básica del AI (simplificada por ahora)
        ai_response = """
🤖 **ProFit Coach AI:**

¡Mensaje recibido! Por el momento estoy en modo de prueba con SQLite.

**Tu mensaje fue:** "{}"

**Próximamente podrás:**
• 💪 Generar rutinas personalizadas
• 📊 Recibir planes de entrenamiento
• ⚡ Usar templates rápidos
• 📧 Envío automático por email

**¡La funcionalidad completa estará disponible pronto!**
        """.format(user_message[:100] + "..." if len(user_message) > 100 else user_message)
        
        # Guardar respuesta del AI
        save_message(athlete_id, ai_response, is_user=False)
        
        logging.info(f"✅ Mensaje procesado para atleta {athlete_id}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Error procesando mensaje: {e}")
        return False
