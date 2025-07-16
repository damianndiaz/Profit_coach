import logging
import re
from auth.database import get_db_cursor
from utils.app_utils import retry_operation, performance_monitor

def validate_athlete_data(name, sport, level, email=None):
    """Valida datos del atleta"""
    errors = []
    
    if not name or len(name.strip()) < 2:
        errors.append("El nombre debe tener al menos 2 caracteres")
    elif len(name) > 100:
        errors.append("El nombre no puede exceder 100 caracteres")
    
    if not sport or len(sport.strip()) < 2:
        errors.append("El deporte debe tener al menos 2 caracteres")
    elif len(sport) > 50:
        errors.append("El deporte no puede exceder 50 caracteres")
    
    valid_levels = ["Principiante", "Intermedio", "Avanzado", "Élite"]
    if level not in valid_levels:
        errors.append(f"El nivel debe ser uno de: {', '.join(valid_levels)}")
    
    if email and email.strip():
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email.strip()):
            errors.append("El formato del email no es válido")
    
    return errors

@retry_operation(max_retries=3)
@performance_monitor
def create_athletes_table():
    """Crea la tabla de atletas si no existe"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS athletes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    sport TEXT NOT NULL,
                    level TEXT NOT NULL,
                    goals TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            # Crear índices para mejores consultas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_user_id 
                ON athletes(user_id) WHERE is_active = TRUE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_sport 
                ON athletes(sport) WHERE is_active = TRUE
            """)
            logging.info("Tabla de atletas creada/verificada correctamente")
    except Exception as e:
        logging.error(f"Error al crear tabla de atletas: {e}")
        raise

@retry_operation(max_retries=3)
def add_athlete(user_id, name, sport, level, goals, email):
    """Agrega un nuevo atleta con validaciones"""
    try:
        # Validar datos
        if not user_id:
            return False, "ID de usuario requerido"
        
        name = name.strip() if name else ""
        sport = sport.strip() if sport else ""
        email = email.strip() if email else None
        goals = goals.strip() if goals else ""
        
        errors = validate_athlete_data(name, sport, level, email)
        if errors:
            return False, "; ".join(errors)
        
        with get_db_cursor() as cursor:
            # Verificar límite de atletas por usuario (ej: máximo 50)
            cursor.execute(
                "SELECT COUNT(*) FROM athletes WHERE user_id = %s AND is_active = TRUE",
                (user_id,)
            )
            athlete_count = cursor.fetchone()[0]
            if athlete_count >= 50:
                return False, "Has alcanzado el límite máximo de 50 atletas"
            
            # Verificar que no existe otro atleta con el mismo nombre para este usuario
            cursor.execute(
                "SELECT id FROM athletes WHERE user_id = %s AND LOWER(name) = LOWER(%s) AND is_active = TRUE",
                (user_id, name)
            )
            if cursor.fetchone():
                return False, "Ya tienes un atleta con ese nombre"
            
            # Insertar atleta
            cursor.execute(
                """INSERT INTO athletes (user_id, name, sport, level, goals, email) 
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (user_id, name, sport, level, goals, email)
            )
            athlete_id = cursor.fetchone()[0]
            
            logging.info(f"Atleta '{name}' agregado exitosamente (ID: {athlete_id})")
            return True, "Atleta agregado exitosamente"
            
    except Exception as e:
        logging.error(f"Error al agregar atleta: {e}")
        return False, "Error al agregar atleta. Inténtalo de nuevo."

@retry_operation(max_retries=3)
@performance_monitor
def get_athletes_by_user(user_id):
    """Obtiene atletas por usuario con información ordenada"""
    try:
        if not user_id:
            return []
        
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT id, name, sport, level, goals, email, created_at, updated_at
                   FROM athletes 
                   WHERE user_id = %s AND is_active = TRUE 
                   ORDER BY name ASC""",
                (user_id,)
            )
            athletes = cursor.fetchall()
            logging.info(f"Obtenidos {len(athletes)} atletas para usuario {user_id}")
            return athletes
            
    except Exception as e:
        logging.error(f"Error al obtener atletas para usuario {user_id}: {e}")
        return []

@retry_operation(max_retries=3)
def get_athlete_data(athlete_id):
    """Obtiene datos completos de un atleta"""
    try:
        if not athlete_id:
            return None
        
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT id, user_id, name, sport, level, goals, email, created_at, updated_at
                   FROM athletes 
                   WHERE id = %s AND is_active = TRUE""",
                (athlete_id,)
            )
            athlete = cursor.fetchone()
            
            if athlete:
                return {
                    "id": athlete[0],
                    "user_id": athlete[1],
                    "name": athlete[2],
                    "sport": athlete[3],
                    "level": athlete[4],
                    "goals": athlete[5],
                    "email": athlete[6],
                    "created_at": athlete[7],
                    "updated_at": athlete[8]
                }
            return None
            
    except Exception as e:
        logging.error(f"Error al obtener datos del atleta {athlete_id}: {e}")
        return None

@retry_operation(max_retries=3)
def update_athlete(athlete_id, name, sport, level, goals, email):
    """Actualiza datos del atleta con validaciones"""
    try:
        if not athlete_id:
            return False, "ID de atleta requerido"
        
        name = name.strip() if name else ""
        sport = sport.strip() if sport else ""
        email = email.strip() if email else None
        goals = goals.strip() if goals else ""
        
        errors = validate_athlete_data(name, sport, level, email)
        if errors:
            return False, "; ".join(errors)
        
        with get_db_cursor() as cursor:
            # Verificar que el atleta existe
            cursor.execute(
                "SELECT user_id FROM athletes WHERE id = %s AND is_active = TRUE",
                (athlete_id,)
            )
            if not cursor.fetchone():
                return False, "Atleta no encontrado"
            
            cursor.execute(
                """UPDATE athletes 
                   SET name = %s, sport = %s, level = %s, goals = %s, email = %s, 
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = %s AND is_active = TRUE""",
                (name, sport, level, goals, email, athlete_id)
            )
            
            if cursor.rowcount == 0:
                return False, "No se pudo actualizar el atleta"
            
            logging.info(f"Atleta {athlete_id} actualizado exitosamente")
            return True, "Atleta actualizado exitosamente"
            
    except Exception as e:
        logging.error(f"Error al actualizar atleta {athlete_id}: {e}")
        return False, "Error al actualizar atleta. Inténtalo de nuevo."

@retry_operation(max_retries=3)
def delete_athlete(athlete_id):
    """Elimina (desactiva) un atleta y limpia datos relacionados"""
    try:
        if not athlete_id:
            return False, "ID de atleta requerido"
        
        with get_db_cursor() as cursor:
            # Verificar que el atleta existe
            cursor.execute(
                "SELECT name FROM athletes WHERE id = %s AND is_active = TRUE",
                (athlete_id,)
            )
            athlete = cursor.fetchone()
            if not athlete:
                return False, "Atleta no encontrado"
            
            athlete_name = athlete[0]
            
            # Marcar atleta como inactivo (soft delete)
            cursor.execute(
                "UPDATE athletes SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (athlete_id,)
            )
            
            # Limpiar sesiones de chat relacionadas (opcional)
            cursor.execute(
                "UPDATE chat_sessions SET is_active = FALSE WHERE athlete_id = %s",
                (athlete_id,)
            )
            
            logging.info(f"Atleta '{athlete_name}' (ID: {athlete_id}) eliminado exitosamente")
            return True, f"Atleta '{athlete_name}' eliminado exitosamente"
            
    except Exception as e:
        logging.error(f"Error al eliminar atleta {athlete_id}: {e}")
        return False, "Error al eliminar atleta. Inténtalo de nuevo."

def get_athlete_statistics(user_id):
    """Obtiene estadísticas de atletas por usuario"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT 
                   COUNT(*) as total_athletes,
                   COUNT(CASE WHEN level = 'Principiante' THEN 1 END) as beginners,
                   COUNT(CASE WHEN level = 'Intermedio' THEN 1 END) as intermediate,
                   COUNT(CASE WHEN level = 'Avanzado' THEN 1 END) as advanced,
                   COUNT(CASE WHEN level = 'Élite' THEN 1 END) as elite,
                   sport, COUNT(*) as count
                   FROM athletes 
                   WHERE user_id = %s AND is_active = TRUE
                   GROUP BY sport
                   ORDER BY count DESC""",
                (user_id,)
            )
            return cursor.fetchall()
    except Exception as e:
        logging.error(f"Error al obtener estadísticas de atletas: {e}")
        return []