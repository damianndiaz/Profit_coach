"""
Sistema de Base de Datos SQLite para ProFit Coach
Versión optimizada y más rápida para desarrollo local
"""

import sqlite3
import os
import logging
from contextlib import contextmanager

# Ruta de la base de datos SQLite
DB_PATH = "/workspaces/ProFit Coach/profit_coach.db"

def initialize_connection_pool():
    """Inicializar SQLite - no necesita pool de conexiones"""
    logging.info("✅ SQLite inicializado correctamente")
    return True

@contextmanager
def get_db_connection():
    """Context manager para conexiones SQLite"""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row  # Para acceder por nombre de columna
        conn.execute("PRAGMA foreign_keys = ON")  # Habilitar foreign keys
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"❌ Error en conexión SQLite: {e}")
        raise
    finally:
        if conn:
            conn.close()

def test_db_connection():
    """Prueba la conexión a la base de datos SQLite"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                logging.info("✅ Conexión SQLite exitosa")
                return True
            else:
                logging.error("❌ Conexión SQLite falló - no hay resultado")
                return False
    except Exception as e:
        logging.error(f"❌ Error conectando a SQLite: {e}")
        return False

def execute_query(query, params=None, fetch=False):
    """Ejecuta una consulta en SQLite"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                if fetch == 'one':
                    result = cursor.fetchone()
                    return dict(result) if result else None
                elif fetch == 'all':
                    results = cursor.fetchall()
                    return [dict(row) for row in results]
            else:
                conn.commit()
                return cursor.lastrowid
                
    except Exception as e:
        logging.error(f"❌ Error ejecutando query: {e}")
        logging.error(f"Query: {query}")
        logging.error(f"Params: {params}")
        raise

def create_tables_if_not_exist():
    """Crea todas las tablas necesarias si no existen"""
    
    # Tabla de usuarios
    users_table = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE
    )
    """
    
    # Tabla de atletas
    athletes_table = """
    CREATE TABLE IF NOT EXISTS athletes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        sport TEXT NOT NULL,
        level TEXT NOT NULL,
        goals TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_active BOOLEAN DEFAULT TRUE,
        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
    )
    """
    
    # Tabla de conversaciones
    conversations_table = """
    CREATE TABLE IF NOT EXISTS conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        thread_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    )
    """
    
    # Tabla de mensajes
    messages_table = """
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        conversation_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_user BOOLEAN NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (conversation_id) REFERENCES conversations (id) ON DELETE CASCADE
    )
    """
    
    # Tabla de threads
    threads_table = """
    CREATE TABLE IF NOT EXISTS threads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        athlete_id INTEGER NOT NULL,
        thread_id TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (athlete_id) REFERENCES athletes (id) ON DELETE CASCADE
    )
    """
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Crear todas las tablas
            cursor.execute(users_table)
            cursor.execute(athletes_table)
            cursor.execute(conversations_table)
            cursor.execute(messages_table)
            cursor.execute(threads_table)
            
            conn.commit()
            logging.info("✅ Todas las tablas SQLite creadas correctamente")
            
    except Exception as e:
        logging.error(f"❌ Error creando tablas SQLite: {e}")
        raise

def create_users_table():
    """Wrapper para compatibilidad"""
    create_tables_if_not_exist()

def create_athletes_table():
    """Wrapper para compatibilidad"""
    pass

def create_chat_tables():
    """Wrapper para compatibilidad"""
    pass

def create_thread_table():
    """Wrapper para compatibilidad"""
    pass
