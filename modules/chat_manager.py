import logging
import datetime
from auth.database import get_db_cursor
from utils.app_utils import retry_operation, performance_monitor

@retry_operation(max_retries=3)
@performance_monitor
def create_chat_tables():
    """Crea las tablas de chat si no existen"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    athlete_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (athlete_id) REFERENCES athletes(id) ON DELETE CASCADE
                )
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER NOT NULL,
                    message_text TEXT NOT NULL,
                    is_from_user BOOLEAN NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    message_length INTEGER GENERATED ALWAYS AS (LENGTH(message_text)) STORED,
                    is_routine BOOLEAN DEFAULT FALSE,
                    routine_summary TEXT,
                    FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
                )
            ''')
            
            # Crear índices para mejor rendimiento
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_athlete 
                ON chat_sessions(athlete_id) WHERE is_active = TRUE
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session 
                ON chat_messages(session_id, created_at DESC)
            ''')
            
            logging.info("Tablas de chat creadas/verificadas correctamente")
    except Exception as e:
        logging.error(f"Error al crear tablas de chat: {e}")
        raise

@retry_operation(max_retries=3)
def create_thread_table():
    """Crea tabla para threads de OpenAI"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS athlete_threads (
                    athlete_id INTEGER PRIMARY KEY,
                    thread_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (athlete_id) REFERENCES athletes(id) ON DELETE CASCADE
                )
            ''')
            logging.info("Tabla de threads creada/verificada correctamente")
    except Exception as e:
        logging.error(f"Error al crear tabla de threads: {e}")
        raise

@retry_operation(max_retries=3)
def create_chat_session(athlete_id):
    """Crea una nueva sesión de chat para un atleta"""
    try:
        if not athlete_id:
            raise ValueError("athlete_id es requerido")
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO chat_sessions (athlete_id) VALUES (%s) RETURNING id",
                (athlete_id,)
            )
            session_id = cursor.fetchone()[0]
            logging.info(f"Nueva sesión de chat creada: {session_id} para atleta {athlete_id}")
            return session_id
    except Exception as e:
        logging.error(f"Error al crear sesión de chat para atleta {athlete_id}: {e}")
        raise

@retry_operation(max_retries=3)
@performance_monitor
def get_or_create_chat_session(athlete_id):
    """Obtiene o crea una sesión de chat para un atleta"""
    try:
        if not athlete_id:
            logging.error("athlete_id no proporcionado")
            return None
        
        with get_db_cursor() as cursor:
            # Buscar sesión activa más reciente
            cursor.execute(
                """SELECT id FROM chat_sessions 
                   WHERE athlete_id = %s AND is_active = TRUE 
                   ORDER BY updated_at DESC LIMIT 1""",
                (athlete_id,)
            )
            session = cursor.fetchone()
            
            if session:
                session_id = session[0]
                # Actualizar timestamp de uso
                cursor.execute(
                    "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (session_id,)
                )
                return session_id
            else:
                # Crear nueva sesión
                return create_chat_session(athlete_id)
                
    except Exception as e:
        logging.error(f"Error al obtener/crear sesión para atleta {athlete_id}: {e}")
        return None

@retry_operation(max_retries=3)
def save_message(session_id, message, is_from_user):
    """Guarda un mensaje en la sesión de chat"""
    try:
        if not session_id or not message:
            logging.error("session_id y message son requeridos")
            return False
        
        # Validar longitud del mensaje
        if len(message) > 5000:  # Límite de seguridad
            message = message[:4997] + "..."
            logging.warning(f"Mensaje truncado por exceder límite de longitud")
        
        with get_db_cursor() as cursor:
            # Verificar que la sesión existe
            cursor.execute(
                "SELECT id FROM chat_sessions WHERE id = %s AND is_active = TRUE",
                (session_id,)
            )
            if not cursor.fetchone():
                logging.error(f"Sesión {session_id} no existe o está inactiva")
                return False
            
            cursor.execute(
                "INSERT INTO chat_messages (session_id, message_text, is_from_user) VALUES (%s, %s, %s)",
                (session_id, message.strip(), is_from_user)
            )
            
            # Actualizar timestamp de la sesión
            cursor.execute(
                "UPDATE chat_sessions SET updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (session_id,)
            )
            
            logging.info(f"Mensaje guardado en sesión {session_id}: {'Usuario' if is_from_user else 'AI'}")
            return True
            
    except Exception as e:
        logging.error(f"Error al guardar mensaje en sesión {session_id}: {e}")
        return False

@retry_operation(max_retries=3)
@performance_monitor
def load_chat_history(session_id, limit=50):
    """Carga el historial de chat de una sesión con límite"""
    try:
        if not session_id:
            return []
        
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT message_text, is_from_user, created_at 
                   FROM chat_messages 
                   WHERE session_id = %s 
                   ORDER BY created_at DESC 
                   LIMIT %s""",
                (session_id, limit)
            )
            messages = cursor.fetchall()
            
            # Retornar en orden cronológico (más antiguo primero)
            messages.reverse()
            
            logging.info(f"Historial cargado para sesión {session_id}: {len(messages)} mensajes")
            return messages
            
    except Exception as e:
        logging.error(f"Error al cargar historial de sesión {session_id}: {e}")
        return []

@retry_operation(max_retries=3)
def get_or_create_thread_id(athlete_id, openai_create_thread_func):
    """Obtiene o crea un thread_id de OpenAI para un atleta"""
    try:
        if not athlete_id:
            raise ValueError("athlete_id es requerido")
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT thread_id FROM athlete_threads WHERE athlete_id = %s",
                (athlete_id,)
            )
            row = cursor.fetchone()
            
            if row:
                thread_id = row[0]
                # Actualizar timestamp de último uso
                cursor.execute(
                    "UPDATE athlete_threads SET last_used = CURRENT_TIMESTAMP WHERE athlete_id = %s",
                    (athlete_id,)
                )
                logging.info(f"Thread existente reutilizado para atleta {athlete_id}: {thread_id}")
                return thread_id
            else:
                # Crear nuevo thread
                try:
                    thread = openai_create_thread_func()
                    thread_id = thread.id
                    
                    cursor.execute(
                        "INSERT INTO athlete_threads (athlete_id, thread_id) VALUES (%s, %s)",
                        (athlete_id, thread_id)
                    )
                    
                    logging.info(f"Nuevo thread creado para atleta {athlete_id}: {thread_id}")
                    return thread_id
                    
                except Exception as openai_error:
                    logging.error(f"Error al crear thread de OpenAI para atleta {athlete_id}: {openai_error}")
                    raise
                    
    except Exception as e:
        logging.error(f"Error al obtener/crear thread para atleta {athlete_id}: {e}")
        raise

def get_chat_session_stats(athlete_id):
    """Obtiene estadísticas de las sesiones de chat de un atleta"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT 
                   COUNT(DISTINCT cs.id) as total_sessions,
                   COUNT(cm.id) as total_messages,
                   COUNT(CASE WHEN cm.is_from_user THEN 1 END) as user_messages,
                   COUNT(CASE WHEN NOT cm.is_from_user THEN 1 END) as ai_messages,
                   MIN(cs.created_at) as first_session,
                   MAX(cs.updated_at) as last_activity
                   FROM chat_sessions cs
                   LEFT JOIN chat_messages cm ON cs.id = cm.session_id
                   WHERE cs.athlete_id = %s AND cs.is_active = TRUE""",
                (athlete_id,)
            )
            return cursor.fetchone()
    except Exception as e:
        logging.error(f"Error al obtener estadísticas de chat para atleta {athlete_id}: {e}")
        return None

def cleanup_old_sessions(days_old=30):
    """Limpia sesiones de chat antiguas (soft delete)"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """UPDATE chat_sessions 
                   SET is_active = FALSE 
                   WHERE updated_at < CURRENT_TIMESTAMP - INTERVAL '%s days'
                   AND is_active = TRUE""",
                (days_old,)
            )
            affected_rows = cursor.rowcount
            logging.info(f"Limpieza completada: {affected_rows} sesiones antiguas desactivadas")
            return affected_rows
    except Exception as e:
        logging.error(f"Error en limpieza de sesiones: {e}")
        return 0

def delete_chat_session(session_id):
    """Elimina una sesión de chat y todos sus mensajes"""
    try:
        with get_db_cursor() as cursor:
            # Verificar que la sesión existe
            cursor.execute(
                "SELECT athlete_id FROM chat_sessions WHERE id = %s",
                (session_id,)
            )
            if not cursor.fetchone():
                return False, "Sesión no encontrada"
            
            # Marcar como inactiva (soft delete)
            cursor.execute(
                "UPDATE chat_sessions SET is_active = FALSE WHERE id = %s",
                (session_id,)
            )
            
            logging.info(f"Sesión de chat {session_id} eliminada")
            return True, "Sesión eliminada exitosamente"
            
    except Exception as e:
        logging.error(f"Error al eliminar sesión {session_id}: {e}")
        return False, "Error al eliminar sesión"

@retry_operation(max_retries=3)
def get_previous_routines(athlete_id, limit=3):
    """Obtiene rutinas previas del atleta para evitar repeticiones"""
    try:
        session_id = get_or_create_chat_session(athlete_id)
        if not session_id:
            return []
        
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT routine_summary, created_at 
                FROM chat_messages 
                WHERE session_id = %s AND is_routine = TRUE AND routine_summary IS NOT NULL
                ORDER BY created_at DESC 
                LIMIT %s
            """, (session_id, limit))
            
            routines = cursor.fetchall()
            return routines if routines else []
            
    except Exception as e:
        logging.error(f"Error al obtener rutinas previas para atleta {athlete_id}: {e}")
        return []

@retry_operation(max_retries=3)
def save_routine_summary(session_id, message_text):
    """Guarda un resumen de la rutina para evitar repeticiones futuras"""
    try:
        # Extraer resumen básico de la rutina
        summary_parts = []
        
        # Buscar días y ejercicios principales
        lines = message_text.split('\n')
        current_day = ""
        
        for line in lines:
            line = line.strip()
            if 'día' in line.lower() and ('-' in line or ':' in line):
                current_day = line[:50]  # Primeros 50 caracteres
                summary_parts.append(current_day)
            elif any(keyword in line.lower() for keyword in ['sentadilla', 'press', 'sprint', 'salto', 'peso muerto']):
                if len(summary_parts) < 10:  # Limitar a 10 ejercicios clave
                    exercise = line[:30]  # Primeros 30 caracteres
                    summary_parts.append(f"  - {exercise}")
        
        routine_summary = '\n'.join(summary_parts[:15])  # Máximo 15 líneas
        
        # Actualizar el último mensaje que no es del usuario
        with get_db_cursor() as cursor:
            # Primero obtener el ID del último mensaje
            cursor.execute("""
                SELECT id FROM chat_messages 
                WHERE session_id = %s AND is_from_user = FALSE 
                ORDER BY created_at DESC 
                LIMIT 1
            """, (session_id,))
            
            result = cursor.fetchone()
            if result:
                message_id = result[0]
                # Ahora actualizar ese mensaje específico
                cursor.execute("""
                    UPDATE chat_messages 
                    SET is_routine = TRUE, routine_summary = %s
                    WHERE id = %s
                """, (routine_summary, message_id))
                
                logging.info(f"Resumen de rutina guardado para sesión {session_id}")
            else:
                logging.warning(f"No se encontró mensaje para actualizar en sesión {session_id}")
            
    except Exception as e:
        logging.error(f"Error al guardar resumen de rutina: {e}")
