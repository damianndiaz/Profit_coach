import bcrypt
import sqlite3
import logging
import re
from auth.database import get_db_connection, execute_query

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

def create_users_table():
    """Crea la tabla de usuarios si no existe"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            conn.commit()
            logging.info("✅ Tabla de usuarios creada/verificada correctamente")
    except Exception as e:
        logging.error(f"❌ Error al crear tabla de usuarios: {e}")
        raise

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
        
        # Hash de la contraseña
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        password_hash_str = password_hash.decode('utf-8')
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash_str)
            )
            conn.commit()
            logging.info(f"✅ Usuario '{username}' registrado exitosamente")
            return True, "Usuario creado exitosamente"
            
    except sqlite3.IntegrityError:
        logging.warning(f"⚠️ Intento de registro con usuario existente: {username}")
        return False, "El nombre de usuario ya existe"
    except Exception as e:
        logging.error(f"❌ Error al registrar usuario: {e}")
        return False, "Error interno del servidor"

def verify_user(username, password):
    """Verifica las credenciales del usuario"""
    try:
        username = username.strip() if username else ""
        
        if not username or not password:
            return False, "Usuario y contraseña son requeridos"
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT password_hash FROM users WHERE username = ? AND is_active = TRUE",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                stored_hash = result[0]
                # Verificar contraseña
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    # Actualizar último login
                    cursor.execute(
                        "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE username = ?",
                        (username,)
                    )
                    conn.commit()
                    logging.info(f"✅ Login exitoso para usuario: {username}")
                    return True, "Login exitoso"
                else:
                    logging.warning(f"⚠️ Contraseña incorrecta para usuario: {username}")
                    return False, "Contraseña incorrecta"
            else:
                logging.warning(f"⚠️ Usuario no encontrado: {username}")
                return False, "Usuario no encontrado"
                
    except Exception as e:
        logging.error(f"❌ Error al verificar usuario: {e}")
        return False, "Error interno del servidor"

def get_user_id(username):
    """Obtiene el ID del usuario por su nombre"""
    try:
        username = username.strip() if username else ""
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND is_active = TRUE",
                (username,)
            )
            result = cursor.fetchone()
            
            if result:
                return result[0]
            else:
                logging.warning(f"⚠️ ID no encontrado para usuario: {username}")
                return None
                
    except Exception as e:
        logging.error(f"❌ Error al obtener ID de usuario: {e}")
        return None

def update_user_password(username, new_password):
    """Actualiza la contraseña de un usuario"""
    try:
        username = username.strip() if username else ""
        
        # Validar usuario y contraseña
        if not username:
            return False, "Usuario requerido"
        
        valid_pass, pass_msg = validate_password(new_password)
        if not valid_pass:
            return False, pass_msg
        
        # Verificar que el usuario existe
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM users WHERE username = ? AND is_active = TRUE",
                (username,)
            )
            result = cursor.fetchone()
            
            if not result:
                return False, "Usuario no encontrado"
            
            # Hash de la nueva contraseña
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            password_hash_str = password_hash.decode('utf-8')
            
            # Actualizar contraseña
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (password_hash_str, username)
            )
            conn.commit()
            
            logging.info(f"✅ Contraseña actualizada para usuario: {username}")
            return True, "Contraseña actualizada exitosamente"
            
    except Exception as e:
        logging.error(f"❌ Error al actualizar contraseña: {e}")
        return False, "Error interno del servidor"
