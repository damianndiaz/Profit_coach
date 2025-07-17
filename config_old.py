"""
Configuración de ProFit Coach
"""
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Detectar si estamos en Streamlit Cloud
try:
    import streamlit as st
    IS_STREAMLIT_CLOUD = hasattr(st, 'secrets') and len(st.secrets) > 0
    logging.info(f"Streamlit Cloud detectado: {IS_STREAMLIT_CLOUD}")
    if IS_STREAMLIT_CLOUD:
        logging.info(f"Secrets disponibles: {list(st.secrets.keys())}")
except Exception as e:
    IS_STREAMLIT_CLOUD = False
    logging.warning(f"Error detectando Streamlit Cloud: {e}")

def get_secret(key, default="", section=None):
    """Obtiene secretos de Streamlit Cloud o variables de entorno"""
    if IS_STREAMLIT_CLOUD:
        try:
            if section:
                value = st.secrets[section].get(key, default)
                logging.info(f"Secret obtenido [{section}][{key}]: {'***' if 'password' in key.lower() or 'key' in key.lower() else value}")
                return value
            else:
                value = st.secrets.get(key, default)
                logging.info(f"Secret obtenido [{key}]: {'***' if 'password' in key.lower() or 'key' in key.lower() else value}")
                return value
        except (KeyError, AttributeError) as e:
            logging.warning(f"Error obteniendo secret {section}.{key}: {e}")
            return default
    else:
        value = os.getenv(key, default)
        logging.info(f"Env var obtenida [{key}]: {'***' if 'password' in key.lower() or 'key' in key.lower() else value}")
        return value

class Config:
    """Configuración principal de la aplicación"""
    
    # Base de datos - Soporte para Supabase y PostgreSQL local
    DB_HOST = get_secret("DB_HOST", "localhost", "database")
    DB_PORT = get_secret("DB_PORT", "5432", "database")
    DB_NAME = get_secret("DB_NAME", "profit_coach", "database")
    DB_USER = get_secret("DB_USER", "postgres", "database")
    DB_PASSWORD = get_secret("DB_PASSWORD", "", "database")
    
    # URL de conexión directa (para Supabase)
    DATABASE_URL = get_secret("DATABASE_URL", "", "database")
    
    # SSL para conexiones en la nube (Supabase requiere SSL)
    DB_SSL_MODE = get_secret("DB_SSL_MODE", "prefer", "database")
    
    # OpenAI
    OPENAI_API_KEY = get_secret("OPENAI_API_KEY", "", "openai")
    OPENAI_ASSISTANT_ID = get_secret("OPENAI_ASSISTANT_ID", "", "openai")
    
    # Email Configuration
    EMAIL_HOST = get_secret("EMAIL_HOST", "smtp.gmail.com", "email")
    EMAIL_PORT = int(get_secret("EMAIL_PORT", "587", "email"))
    EMAIL_USE_TLS = str(get_secret("EMAIL_USE_TLS", "True", "email")).lower() == "true"
    EMAIL_USERNAME = get_secret("EMAIL_USERNAME", "", "email")
    EMAIL_PASSWORD = get_secret("EMAIL_PASSWORD", "", "email")
    EMAIL_FROM_NAME = get_secret("EMAIL_FROM_NAME", "ProFit Coach", "email")
    EMAIL_FROM_EMAIL = get_secret("EMAIL_FROM_EMAIL", "", "email")
    
    # Configuración de la aplicación
    MAX_ATHLETES_PER_USER = int(get_secret("MAX_ATHLETES_PER_USER", "50", "app"))
    MAX_MESSAGE_LENGTH = int(get_secret("MAX_MESSAGE_LENGTH", "2000", "app"))
    CHAT_HISTORY_LIMIT = int(get_secret("CHAT_HISTORY_LIMIT", "50", "app"))
    SESSION_TIMEOUT_DAYS = int(get_secret("SESSION_TIMEOUT_DAYS", "30", "app"))
    
    # Configuración de logging
    LOG_LEVEL = get_secret("LOG_LEVEL", "INFO", "app")
    LOG_FILE = get_secret("LOG_FILE", "profit_coach.log", "app")
    
    # Configuración de conexiones
    DB_POOL_MIN_CONN = int(get_secret("DB_POOL_MIN_CONN", "1", "app"))
    DB_POOL_MAX_CONN = int(get_secret("DB_POOL_MAX_CONN", "20", "app"))
    
    # Timeouts
    OPENAI_TIMEOUT = int(get_secret("OPENAI_TIMEOUT", "30", "app"))
    DB_TIMEOUT = int(get_secret("DB_TIMEOUT", "10", "app"))
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración requerida"""
        required_vars = [
            ("DB_HOST", cls.DB_HOST),
            ("DB_NAME", cls.DB_NAME),
            ("DB_USER", cls.DB_USER),
            ("DB_PASSWORD", cls.DB_PASSWORD)
        ]
        
        missing_vars = []
        for var_name, var_value in required_vars:
            if not var_value:
                missing_vars.append(var_name)
        
        if missing_vars:
            raise ValueError(f"Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}")
        
        # Validaciones opcionales pero recomendadas
        warnings = []
        if not cls.OPENAI_API_KEY:
            warnings.append("OPENAI_API_KEY no configurada - funcionalidad de chat limitada")
        if not cls.OPENAI_ASSISTANT_ID:
            warnings.append("OPENAI_ASSISTANT_ID no configurada - funcionalidad de chat limitada")
        
        return warnings

class DevelopmentConfig(Config):
    """Configuración para desarrollo"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Configuración para producción"""
    DEBUG = False
    LOG_LEVEL = "WARNING"
    
    # Configuraciones más estrictas para producción
    MAX_ATHLETES_PER_USER = 30
    CHAT_HISTORY_LIMIT = 30
    SESSION_TIMEOUT_DAYS = 7

def get_config():
    """Obtiene la configuración según el entorno"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# Instancia global de configuración
config = get_config()
