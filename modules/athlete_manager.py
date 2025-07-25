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
            # Crear tabla básica con todas las columnas necesarias
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS athletes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    name TEXT NOT NULL,
                    sport TEXT NOT NULL DEFAULT 'Fútbol',
                    level TEXT NOT NULL DEFAULT 'Intermedio',
                    goals TEXT,
                    email TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                )
            """)
            
            # Verificar y agregar columnas faltantes una por una
            required_columns = {
                'sport': 'TEXT NOT NULL DEFAULT \'Fútbol\'',
                'level': 'TEXT NOT NULL DEFAULT \'Intermedio\'',
                'is_active': 'BOOLEAN DEFAULT TRUE',
                'goals': 'TEXT',
                'email': 'TEXT'
            }
            
            # Obtener columnas existentes
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'athletes'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Agregar columnas faltantes
            for col_name, col_def in required_columns.items():
                if col_name not in existing_columns:
                    logging.info(f"Agregando columna faltante: {col_name}")
                    cursor.execute(f"ALTER TABLE athletes ADD COLUMN {col_name} {col_def}")
                    
                    # Actualizar registros existentes si es necesario
                    if col_name == 'sport':
                        cursor.execute("UPDATE athletes SET sport = 'Fútbol' WHERE sport IS NULL")
                    elif col_name == 'level':
                        cursor.execute("UPDATE athletes SET level = 'Intermedio' WHERE level IS NULL")
                    elif col_name == 'is_active':
                        cursor.execute("UPDATE athletes SET is_active = TRUE WHERE is_active IS NULL")
            
            # Crear índices básicos (sin filtros problemáticos)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_user_id 
                ON athletes(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_sport 
                ON athletes(sport)
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
            # Primero verificar qué columnas existen
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'athletes'
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Construir query dinámicamente basado en columnas disponibles
            base_columns = ['id', 'name']
            optional_columns = ['sport', 'level', 'goals', 'email', 'created_at', 'updated_at']
            
            select_columns = base_columns[:]
            for col in optional_columns:
                if col in existing_columns:
                    select_columns.append(col)
                else:
                    # Agregar valor por defecto para columnas faltantes
                    if col == 'sport':
                        select_columns.append("'Fútbol' as sport")
                    elif col == 'level':
                        select_columns.append("'Intermedio' as level")
                    elif col in ['goals', 'email']:
                        select_columns.append(f"NULL as {col}")
                    elif col in ['created_at', 'updated_at']:
                        select_columns.append(f"CURRENT_TIMESTAMP as {col}")
            
            query = f"""
                SELECT {', '.join(select_columns)}
                FROM athletes 
                WHERE user_id = %s 
                {' AND is_active = TRUE' if 'is_active' in existing_columns else ''}
                ORDER BY name ASC
            """
            
            cursor.execute(query, (user_id,))
            athletes = cursor.fetchall()
            logging.info(f"Obtenidos {len(athletes)} atletas para usuario {user_id}")
            return athletes
            
    except Exception as e:
        logging.error(f"Error al obtener atletas para usuario {user_id}: {e}")
        # En caso de error, intentar query básica
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT id, name FROM athletes WHERE user_id = %s ORDER BY name ASC",
                    (user_id,)
                )
                return cursor.fetchall()
        except:
            return []

# Alias para compatibilidad con código existente
def get_user_athletes(user_id):
    """Alias de get_athletes_by_user para compatibilidad"""
    return get_athletes_by_user(user_id)

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