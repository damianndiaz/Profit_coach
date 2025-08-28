"""
Gestión de Chat con SQLite - Versión Simplificada
"""

import logging
from auth.database import get_db_connection

def create_chat_tables():
    """Ya se crean en database.py"""
    pass

def create_thread_table():
    """Ya se crea en database.py"""
    pass

def get_chat_history(athlete_id, limit=50):
    """Obtiene el historial de chat de un atleta"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Primero buscar si existe una conversación para este atleta
            cursor.execute("""
                SELECT id FROM conversations 
                WHERE athlete_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (athlete_id,))
            
            conversation = cursor.fetchone()
            
            if not conversation:
                logging.info(f"ℹ️ No hay conversación para atleta {athlete_id}")
                return []
            
            conversation_id = conversation[0]
            
            # Obtener mensajes de la conversación
            cursor.execute("""
                SELECT content, is_user, created_at 
                FROM messages 
                WHERE conversation_id = ? 
                ORDER BY created_at ASC 
                LIMIT ?
            """, (conversation_id, limit))
            
            messages = cursor.fetchall()
            
            # Convertir a formato esperado (mensaje, es_usuario, fecha)
            chat_history = []
            for msg in messages:
                chat_history.append((
                    msg[0],  # content
                    bool(msg[1]),  # is_user
                    msg[2]   # created_at
                ))
            
            logging.info(f"✅ {len(chat_history)} mensajes cargados para atleta {athlete_id}")
            return chat_history
            
    except Exception as e:
        logging.error(f"❌ Error obteniendo historial de chat: {e}")
        return []

def save_message(athlete_id, message, is_user=True):
    """Guarda un mensaje en el chat"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Buscar o crear conversación
            cursor.execute("""
                SELECT id FROM conversations 
                WHERE athlete_id = ? 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (athlete_id,))
            
            conversation = cursor.fetchone()
            
            if not conversation:
                # Crear nueva conversación
                cursor.execute("""
                    INSERT INTO conversations (athlete_id) 
                    VALUES (?)
                """, (athlete_id,))
                conversation_id = cursor.lastrowid
                logging.info(f"✅ Nueva conversación creada para atleta {athlete_id}")
            else:
                conversation_id = conversation[0]
            
            # Guardar mensaje
            cursor.execute("""
                INSERT INTO messages (conversation_id, content, is_user) 
                VALUES (?, ?, ?)
            """, (conversation_id, message, is_user))
            
            conn.commit()
            
            logging.info(f"✅ Mensaje guardado en conversación {conversation_id}")
            return True
            
    except Exception as e:
        logging.error(f"❌ Error guardando mensaje: {e}")
        return False

def get_welcome_message(athlete_id):
    """Genera mensaje de bienvenida personalizado"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name, sport, level 
                FROM athletes 
                WHERE id = ?
            """, (athlete_id,))
            
            athlete = cursor.fetchone()
            
            if athlete:
                name = athlete[0]
                sport = athlete[1]
                level = athlete[2]
                
                return f"""
🏃‍♂️ ¡Hola {name}! Soy tu ProFit Coach AI.

🎯 **Tu Perfil:**
• **Deporte:** {sport}
• **Nivel:** {level}

💪 **¿Cómo puedo ayudarte hoy?**
• Crear rutinas personalizadas
• Planificar entrenamientos
• Asesorar sobre técnica
• Ajustar cargas de trabajo
• Prevención de lesiones

**Escribe tu consulta y comencemos a entrenar! 🚀**
                """.strip()
            else:
                return """
🏃‍♂️ ¡Bienvenido a ProFit Coach AI!

💪 Estoy aquí para ayudarte con:
• Rutinas personalizadas
• Planificación de entrenamientos  
• Consejos de técnica
• Prevención de lesiones

**¡Cuéntame qué necesitas para empezar!**
                """.strip()
                
    except Exception as e:
        logging.error(f"❌ Error generando mensaje de bienvenida: {e}")
        return "¡Hola! Soy tu ProFit Coach AI. ¿En qué puedo ayudarte hoy?"
