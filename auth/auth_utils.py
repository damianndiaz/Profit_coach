import bcrypt
import psycopg2
import logging
import re
from auth.database import get_db_cursor
from utils.app_utils import retry_operation, performance_monitor

def validate_username(username):
    """Valida formato del nombre de usuario"""
    if not username or len(username.strip()) < 3:
        return False, "El usuario debe tener al menos 3 caracteres"
    
    if len(username) > 50:
        return False, "El usuario no puede exceder 50 caracteres"
    
    # Permitir letras, números, espacios, guiones bajos y guiones
    if not re.match("^[a-zA-ZÀ-ÿ0-9 _-]+$", username.strip()):
        return False, "El usuario solo puede contener letras, números, espacios, guiones y guiones bajos"
    
    # Verificar que no tenga espacios múltiples consecutivos
    if "  " in username:
        return False, "No se permiten espacios múltiples consecutivos"
    
    # Verificar que no empiece o termine con espacio
    if username != username.strip():
        return False, "El usuario no puede empezar o terminar con espacios"
    
    return True, ""

def validate_password(password):
    """Valida fortaleza de la contraseña"""
    if not password or len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres"
    
    if len(password) > 100:
        return False, "La contraseña no puede exceder 100 caracteres"
    
    # Verificar que tenga al menos una letra y un número
    if not re.search(r"[a-zA-Z]", password) or not re.search(r"[0-9]", password):
        return False, "La contraseña debe contener al menos una letra y un número"
    
    return True, ""

@retry_operation(max_retries=3)
@performance_monitor
def create_users_table():
    """Crea la tabla de usuarios si no existe"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            # Crear índice para mejores consultas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username) WHERE is_active = TRUE
            """)
            logging.info("Tabla de usuarios creada/verificada correctamente")
    except Exception as e:
        logging.error(f"Error al crear tabla de usuarios: {e}")
        raise

@retry_operation(max_retries=3)
def register_user(username, password):
    """Registra un nuevo usuario con validaciones"""
    try:
        # Validar entrada
        username = username.strip() if username else ""
        
        valid_user, user_msg = validate_username(username)
        if not valid_user:
            return False, user_msg
        
        valid_pass, pass_msg = validate_password(password)
        if not valid_pass:
            return False, pass_msg
        
        # Hash de la contraseña como string (no bytes)
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        # Convertir a string para almacenar en TEXT column
        password_hash_str = password_hash.decode('utf-8')
        
        with get_db_cursor() as cursor:
            # Guardar username tal como lo escribió el usuario
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
                (username, password_hash_str)  # Guardar como string
            )
            logging.info(f"Usuario '{username}' registrado exitosamente")
            return True, "Usuario creado exitosamente"
            
    except psycopg2.IntegrityError:
        logging.warning(f"Intento de registro con usuario existente: {username}")
        return False, "El usuario ya existe"
    except Exception as e:
        logging.error(f"Error al registrar usuario '{username}': {e}")
        return False, "Error al crear el usuario. Inténtalo de nuevo."

@retry_operation(max_retries=3)
@performance_monitor
def verify_user(username, password):
    """Verifica credenciales del usuario"""
    try:
        if not username or not password:
            return False, "Usuario y contraseña son requeridos"
        
        username = username.strip()
        
        with get_db_cursor() as cursor:
            # Búsqueda case-insensitive usando LOWER()
            cursor.execute(
                """SELECT username, password_hash, is_active FROM users 
                   WHERE LOWER(username) = LOWER(%s)""",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user:
                logging.warning(f"Intento de login con usuario inexistente: {username}")
                return False, "Credenciales incorrectas"
            
            actual_username, password_hash, is_active = user
            
            if not is_active:
                logging.warning(f"Intento de login con usuario inactivo: {actual_username}")
                return False, "Cuenta desactivada"
            
            # Manejar password_hash como string
            try:
                # Si viene como string (lo esperado), convertir a bytes
                if isinstance(password_hash, str):
                    password_hash_bytes = password_hash.encode('utf-8')
                elif isinstance(password_hash, bytes):
                    password_hash_bytes = password_hash
                elif isinstance(password_hash, memoryview):
                    password_hash_bytes = password_hash.tobytes()
                else:
                    logging.error(f"Tipo de hash no soportado para usuario: {actual_username}")
                    return False, "Error en los datos del usuario"
                
                # Verificar que el hash tenga el formato correcto
                if not password_hash_bytes or len(password_hash_bytes) < 10:
                    logging.error(f"Hash de contraseña inválido para usuario: {actual_username}")
                    return False, "Error en los datos del usuario"
                
                # Verificar contraseña
                if bcrypt.checkpw(password.encode('utf-8'), password_hash_bytes):
                    # Actualizar último login usando el username exacto
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = %s",
                        (actual_username,)
                    )
                    logging.info(f"Login exitoso para usuario: {actual_username}")
                    return True, "Login exitoso"
                else:
                    logging.warning(f"Contraseña incorrecta para usuario: {actual_username}")
                    return False, "Credenciales incorrectas"
                    
            except ValueError as ve:
                logging.error(f"Error de formato en hash para usuario {actual_username}: {ve}")
                return False, "Error en el formato de datos. Contacta al administrador."
                
    except Exception as e:
        logging.error(f"Error al verificar usuario '{username}': {e}")
        return False, "Error de autenticación. Inténtalo de nuevo."

@retry_operation(max_retries=3)
def get_user_id(username):
    """Obtiene el ID del usuario por nombre de usuario"""
    try:
        if not username:
            return None
        
        username = username.strip()  # Solo limpiar espacios
        
        with get_db_cursor() as cursor:
            # Búsqueda case-insensitive
            cursor.execute(
                "SELECT id FROM users WHERE LOWER(username) = LOWER(%s) AND is_active = TRUE",
                (username,)
            )
            user = cursor.fetchone()
            return user[0] if user else None
            
    except Exception as e:
        logging.error(f"Error al obtener ID de usuario '{username}': {e}")
        return None

@retry_operation(max_retries=3)
def update_user_password(username, new_password):
    """Actualiza la contraseña del usuario"""
    try:
        if not username or not new_password:
            return False, "Usuario y contraseña son requeridos"
        
        username = username.strip().lower()
        
        # Validar nueva contraseña
        valid_pass, pass_msg = validate_password(new_password)
        if not valid_pass:
            return False, pass_msg
        
        # Verificar que el usuario existe
        if not get_user_id(username):
            return False, "Usuario no encontrado"
        
        password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password_hash = %s WHERE username = %s",
                (password_hash, username)
            )
            
            if cursor.rowcount == 0:
                return False, "No se pudo actualizar la contraseña"
            
            logging.info(f"Contraseña actualizada para usuario: {username}")
            return True, "Contraseña actualizada exitosamente"
            
    except Exception as e:
        logging.error(f"Error al actualizar contraseña para '{username}': {e}")
        return False, "Error al actualizar contraseña. Inténtalo de nuevo."

def get_user_stats(username):
    """Obtiene estadísticas del usuario"""
    try:
        username = username.strip().lower()
        
        with get_db_cursor() as cursor:
            cursor.execute(
                """SELECT created_at, last_login, 
                   (SELECT COUNT(*) FROM athletes WHERE user_id = users.id) as athlete_count
                   FROM users WHERE username = %s""",
                (username,)
            )
            return cursor.fetchone()
            
    except Exception as e:
        logging.error(f"Error al obtener estadísticas de '{username}': {e}")
        return None