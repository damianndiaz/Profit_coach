import psycopg2
import os
import logging
import time
from dotenv import load_dotenv
from psycopg2 import pool
from contextlib import contextmanager
from urllib.parse import urlparse

load_dotenv()

# Pool de conexiones para mejor rendimiento
connection_pool = None

def get_db_params():
    """Obtiene parámetros de conexión desde URL o variables individuales"""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Usar URL de conexión (Supabase)
        parsed = urlparse(database_url)
        return {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'dbname': parsed.path[1:],  # Remove leading '/'
            'user': parsed.username,
            'password': parsed.password,
            'sslmode': os.getenv("DB_SSL_MODE", "require")
        }
    else:
        # Usar variables individuales (local)
        return {
            'host': os.getenv("DB_HOST"),
            'port': os.getenv("DB_PORT"),
            'dbname': os.getenv("DB_NAME"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'sslmode': os.getenv("DB_SSL_MODE", "prefer")
        }

def initialize_connection_pool():
    """Inicializa el pool de conexiones"""
    global connection_pool
    try:
        db_params = get_db_params()
        connection_pool = psycopg2.pool.ThreadedConnectionPool(
            1, 20,  # min y max conexiones
            **db_params
        )
        logging.info("Pool de conexiones inicializado correctamente")
    except Exception as e:
        logging.error(f"Error al inicializar pool de conexiones: {e}")
        raise

def get_db_connection(max_retries=3, retry_delay=1.0):
    """
    Obtiene una conexión de la base de datos con reintentos automáticos
    """
    global connection_pool
    
    if connection_pool is None:
        initialize_connection_pool()
    
    last_exception = None
    for attempt in range(max_retries):
        try:
            if connection_pool:
                conn = connection_pool.getconn()
                if conn:
                    return conn
            
            # Fallback: conexión directa
            db_params = get_db_params()
            return psycopg2.connect(**db_params)
            
        except Exception as e:
            last_exception = e
            if attempt < max_retries - 1:
                logging.warning(f"Intento {attempt + 1} de conexión falló: {e}")
                time.sleep(retry_delay)
            else:
                logging.error(f"Todos los intentos de conexión fallaron: {e}")
    
    raise last_exception

def release_db_connection(conn):
    """Libera una conexión al pool"""
    global connection_pool
    try:
        if connection_pool and conn:
            connection_pool.putconn(conn)
        else:
            if conn:
                conn.close()
    except Exception as e:
        logging.error(f"Error al liberar conexión: {e}")

@contextmanager
def get_db_cursor():
    """
    Context manager para manejo seguro de conexiones y cursores
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logging.error(f"Error en operación de base de datos: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if conn:
            release_db_connection(conn)

def test_db_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result[0] == 1
    except Exception as e:
        logging.error(f"Prueba de conexión falló: {e}")
        return False