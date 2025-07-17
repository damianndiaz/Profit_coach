"""
Configuración de ProFit Coach
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Configurar logging si no está configurado
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

# Detectar si estamos en Streamlit Cloud
try:
    import streamlit as st
    IS_STREAMLIT_CLOUD = hasattr(st, 'secrets') and len(st.secrets) > 0
    logging.info(f"🔧 Entorno: {'Cloud' if IS_STREAMLIT_CLOUD else 'Local'}")
except Exception as e:
    IS_STREAMLIT_CLOUD = False
    logging.warning(f"⚠️ Error detectando entorno: entorno local")

def get_secret(key, default="", section=None):
    """Obtiene secretos de Streamlit Cloud o variables de entorno"""
    if IS_STREAMLIT_CLOUD:
        try:
            if section:
                value = st.secrets[section].get(key, default)
                # Solo logear en desarrollo, NUNCA en producción
                if not IS_STREAMLIT_CLOUD:
                    masked_value = '***' if any(word in key.lower() for word in ['password', 'key', 'secret', 'url', 'host', 'id']) else value
                    logging.debug(f"🔑 Secret [{section}][{key}]: {masked_value}")
                return value
            else:
                value = st.secrets.get(key, default)
                if not IS_STREAMLIT_CLOUD:
                    masked_value = '***' if any(word in key.lower() for word in ['password', 'key', 'secret', 'url', 'host', 'id']) else value
                    logging.debug(f"🔑 Secret [{key}]: {masked_value}")
                return value
        except (KeyError, AttributeError) as e:
            logging.warning(f"❌ Error obteniendo secret {section}.{key}")
            return default
    else:
        value = os.getenv(key, default)
        # Solo en desarrollo local
        masked_value = '***' if any(word in key.lower() for word in ['password', 'key', 'secret', 'url', 'host', 'id']) else value
        logging.debug(f"🌍 Env var [{key}]: {masked_value}")
        return value

class Config:
    """Configuración principal de la aplicación"""
    
    # Base de datos - Usar Neon PostgreSQL
    DB_HOST = get_secret("host", "ep-royal-unit-acq1k30a-pooler.sa-east-1.aws.neon.tech", "database")
    DB_PORT = get_secret("port", "5432", "database")
    DB_NAME = get_secret("name", "neondb", "database")
    DB_USER = get_secret("user", "neondb_owner", "database")
    DB_PASSWORD = get_secret("password", "npg_wML7Qj3eRSNA", "database")
    
    # URL de conexión directa para Neon PostgreSQL
    DATABASE_URL = get_secret("url", "postgresql://neondb_owner:npg_wML7Qj3eRSNA@ep-royal-unit-acq1k30a-pooler.sa-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require", "database")
    
    # SSL para conexiones en la nube (Neon requiere SSL)
    DB_SSL_MODE = get_secret("ssl_mode", "require", "database")
    
    # OpenAI
    OPENAI_API_KEY = get_secret("api_key", "", "openai")
    OPENAI_ASSISTANT_ID = get_secret("assistant_id", "", "openai")
    
    # Email Configuration
    EMAIL_HOST = get_secret("host", "smtp.gmail.com", "email")
    EMAIL_PORT = int(get_secret("port", "587", "email"))
    EMAIL_USE_TLS = str(get_secret("use_tls", "True", "email")).lower() == "true"
    EMAIL_USERNAME = get_secret("username", "", "email")
    EMAIL_PASSWORD = get_secret("password", "", "email")
    EMAIL_FROM_NAME = get_secret("from_name", "ProFit Coach", "email")
    EMAIL_FROM_EMAIL = get_secret("from_email", "", "email")
    
    # Configuración de la aplicación
    MAX_ATHLETES_PER_USER = int(get_secret("MAX_ATHLETES_PER_USER", "50", "app") or "50")
    MAX_MESSAGE_LENGTH = int(get_secret("MAX_MESSAGE_LENGTH", "2000", "app") or "2000")
    CHAT_HISTORY_LIMIT = int(get_secret("CHAT_HISTORY_LIMIT", "50", "app") or "50")
    SESSION_TIMEOUT_DAYS = int(get_secret("SESSION_TIMEOUT_DAYS", "30", "app") or "30")
    
    # Configuración de logging
    LOG_LEVEL = get_secret("LOG_LEVEL", "WARNING", "app") or "WARNING"  # Menos verbose en producción
    LOG_FILE = get_secret("LOG_FILE", "profit_coach.log", "app") or "profit_coach.log"
    
    # Configuración de conexiones
    DB_POOL_MIN_CONN = int(get_secret("DB_POOL_MIN_CONN", "1", "app") or "1")
    DB_POOL_MAX_CONN = int(get_secret("DB_POOL_MAX_CONN", "20", "app") or "20")
    
    # Timeouts
    OPENAI_TIMEOUT = int(get_secret("OPENAI_TIMEOUT", "30", "app") or "30")
    DB_TIMEOUT = int(get_secret("DB_TIMEOUT", "10", "app") or "10")
    
    @classmethod
    def validate_config(cls):
        """Valida la configuración requerida"""
        logging.info("🔍 Validando configuración...")
        
        # Verificar si tenemos URL de conexión o parámetros individuales
        if cls.DATABASE_URL:
            logging.info("✅ Usando DATABASE_URL para conexión")
            return []
        
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
            logging.error(f"❌ Variables requeridas no configuradas: {', '.join(missing_vars)}")
            raise ValueError(f"Variables de entorno requeridas no configuradas: {', '.join(missing_vars)}")
        
        # Validaciones opcionales pero recomendadas
        warnings = []
        if not cls.OPENAI_API_KEY:
            warnings.append("OPENAI_API_KEY no configurada - funcionalidad de chat limitada")
        if not cls.OPENAI_ASSISTANT_ID:
            warnings.append("OPENAI_ASSISTANT_ID no configurada - funcionalidad de chat limitada")
        
        for warning in warnings:
            logging.warning(f"⚠️ {warning}")
        
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
    env = get_secret("ENVIRONMENT", "production", "app") or "production"  # Default a producción para seguridad
    logging.info(f"🌍 Entorno detectado: {env}")
    
    if env == "development":
        return DevelopmentConfig()
    else:
        return ProductionConfig()

# Instancia global de configuración
config = get_config()

# Validar configuración al cargar
try:
    config.validate_config()
    logging.info("✅ Configuración validada correctamente")
except Exception as e:
    logging.error(f"❌ Error en configuración: {e}")
    raise
