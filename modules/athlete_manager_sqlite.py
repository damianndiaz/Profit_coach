"""
Gestión de Atletas con SQLite - Versión Simplificada
"""

import logging
from auth.database import get_db_connection

def create_athletes_table():
    """Ya se crea en database.py"""
    pass

def get_athletes_by_user(user_id):
    """Obtiene todos los atletas de un usuario"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, sport, level, goals, email, created_at 
                FROM athletes 
                WHERE user_id = ? AND (is_active IS NULL OR is_active = 1)
                ORDER BY created_at DESC
            """, (user_id,))
            
            results = cursor.fetchall()
            # Convertir a lista de tuplas para compatibilidad
            athletes = []
            for row in results:
                athletes.append((
                    row[0],  # id
                    row[1],  # name
                    row[2],  # sport
                    row[3],  # level
                    row[4] or "",  # goals
                    row[5] or "",  # email
                    row[6]   # created_at
                ))
            
            logging.info(f"✅ {len(athletes)} atletas encontrados para usuario {user_id}")
            return athletes
            
    except Exception as e:
        logging.error(f"❌ Error obteniendo atletas: {e}")
        return []

def add_athlete(user_id, name, sport, level, goals="", email=""):
    """Agrega un nuevo atleta"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO athletes (user_id, name, sport, level, goals, email)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, name.strip(), sport.strip(), level, goals.strip(), email.strip()))
            
            athlete_id = cursor.lastrowid
            conn.commit()
            
            logging.info(f"✅ Atleta '{name}' agregado con ID {athlete_id}")
            return athlete_id
            
    except Exception as e:
        logging.error(f"❌ Error agregando atleta: {e}")
        return None

def update_athlete(athlete_id, name, sport, level, goals="", email=""):
    """Actualiza un atleta existente"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE athletes 
                SET name = ?, sport = ?, level = ?, goals = ?, email = ?, 
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name.strip(), sport.strip(), level, goals.strip(), email.strip(), athlete_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"✅ Atleta {athlete_id} actualizado correctamente")
                return True, "Atleta actualizado correctamente"
            else:
                logging.warning(f"⚠️ No se encontró atleta con ID {athlete_id}")
                return False, "Atleta no encontrado"
                
    except Exception as e:
        logging.error(f"❌ Error actualizando atleta: {e}")
        return False, "Error interno del servidor"

def delete_athlete(athlete_id):
    """Elimina un atleta (soft delete)"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE athletes 
                SET is_active = 0, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (athlete_id,))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"✅ Atleta {athlete_id} eliminado correctamente")
                return True, "Atleta eliminado correctamente"
            else:
                logging.warning(f"⚠️ No se encontró atleta con ID {athlete_id}")
                return False, "Atleta no encontrado"
                
    except Exception as e:
        logging.error(f"❌ Error eliminando atleta: {e}")
        return False, "Error interno del servidor"

def get_athlete_data(athlete_id):
    """Obtiene los datos de un atleta específico"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, sport, level, goals, email, created_at 
                FROM athletes 
                WHERE id = ? AND (is_active IS NULL OR is_active = 1)
            """, (athlete_id,))
            
            result = cursor.fetchone()
            if result:
                return {
                    'id': result[0],
                    'name': result[1],
                    'sport': result[2],
                    'level': result[3],
                    'goals': result[4] or '',
                    'email': result[5] or '',
                    'created_at': result[6]
                }
            else:
                logging.warning(f"⚠️ Atleta {athlete_id} no encontrado")
                return None
                
    except Exception as e:
        logging.error(f"❌ Error obteniendo datos del atleta: {e}")
        return None
