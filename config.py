"""
Configuración de ProFit Coach
"""
import os
import logging
from dotenv import load_dotenv

load_dotenv()

# ⚡ OPTIMIZACIÓN: Configurar logging más eficiente
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.ERROR,  # Solo errores críticos para reducir ruido
        format='%(asctime)s - %(levelname)s - %(message)s'  # Formato con timestamp
    )

# Detectar si estamos en Streamlit Cloud
try:
    import streamlit as st
    IS_STREAMLIT_CLOUD = hasattr(st, 'secrets') and len(st.secrets) > 0
    if IS_STREAMLIT_CLOUD:
        logging.info(f"🔧 Entorno: Streamlit Cloud - {len(st.secrets)} secciones de secrets detectadas")
        # Log de secciones disponibles (sin valores sensibles)
        secret_sections = list(st.secrets.keys()) if hasattr(st.secrets, 'keys') else []
        logging.info(f"🔑 Secciones de secrets disponibles: {secret_sections}")
    else:
        logging.info("🔧 Entorno: Local")
except Exception as e:
    IS_STREAMLIT_CLOUD = False
    logging.warning(f"⚠️ Error detectando entorno: {e}")

def get_secret(key, default="", section=None, silent=False):
    """Obtiene secretos de Streamlit Cloud o variables de entorno
    PRIORIDAD: Streamlit Secrets -> Variables de entorno -> Default
    """
    # Intentar primero desde Streamlit secrets
    if IS_STREAMLIT_CLOUD:
        try:
            import streamlit as st
            if section:
                if section in st.secrets and key in st.secrets[section]:
                    value = st.secrets[section][key]
                    if not silent:
                        logging.info(f"✅ Found secret [{section}][{key}]")
                    return value
            else:
                if key in st.secrets:
                    value = st.secrets[key]
                    if not silent:
                        logging.info(f"✅ Found secret [{key}]")
                    return value
        except Exception as e:
            if not silent:
                logging.error(f"❌ Error accessing Streamlit secrets: {e}")
    
    # Si no está en secrets, usar variable de entorno
    value = os.getenv(key, default)
    if value != default:
        if not silent:
            logging.debug(f"🌍 Using environment variable [{key}]")
    else:
        if not silent:
            logging.debug(f"⚠️ Using default value for [{key}]")
    
    return value

class Config:
    """Configuración principal de la aplicación"""
    
    # Base de datos - Usar Supabase PostgreSQL
    DB_HOST = get_secret("DB_HOST", "")
    DB_PORT = get_secret("DB_PORT", "5432")
    DB_NAME = get_secret("DB_NAME", "postgres")
    DB_USER = get_secret("DB_USER", "")
    DB_PASSWORD = get_secret("DB_PASSWORD", "")
    
    # Database Configuration - Prioridad: Streamlit secrets -> ENV
    DATABASE_URL = get_secret("url", section="database") or get_secret("DATABASE_URL", "")
    
    # SSL para conexiones en la nube (Supabase requiere SSL)
    DB_SSL_MODE = get_secret("ssl_mode", "require", section="database") or get_secret("DB_SSL_MODE", "require")
    
    # OpenAI Configuration - Prioridad: Streamlit secrets -> ENV
    OPENAI_API_KEY = get_secret("api_key", section="openai") or get_secret("OPENAI_API_KEY") or None
    OPENAI_ASSISTANT_ID = get_secret("assistant_id", section="openai") or get_secret("OPENAI_ASSISTANT_ID") or None
    
    # Email Configuration - Prioridad: Streamlit secrets -> ENV
    EMAIL_HOST = get_secret("host", "smtp.gmail.com", section="email") or get_secret("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(get_secret("port", "587", section="email") or get_secret("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = str(get_secret("use_tls", "True", section="email") or get_secret("EMAIL_USE_TLS", "True")).lower() == "true"
    EMAIL_USERNAME = get_secret("username", section="email") or get_secret("EMAIL_USERNAME", "")
    EMAIL_PASSWORD = get_secret("password", section="email") or get_secret("EMAIL_PASSWORD", "")
    EMAIL_FROM_NAME = get_secret("from_name", "ProFit Coach", section="email") or get_secret("EMAIL_FROM_NAME", "ProFit Coach")
    EMAIL_FROM_EMAIL = get_secret("from_email", section="email") or get_secret("EMAIL_FROM_EMAIL", "")
    
    # Configuración de la aplicación (silenciosas para evitar warnings innecesarios)
    MAX_ATHLETES_PER_USER = int(get_secret("MAX_ATHLETES_PER_USER", "100", "app", silent=True) or "100")  # Aumentado para producción
    MAX_MESSAGE_LENGTH = int(get_secret("MAX_MESSAGE_LENGTH", "8000", "app", silent=True) or "8000")  # Aumentado para archivos
    CHAT_HISTORY_LIMIT = int(get_secret("CHAT_HISTORY_LIMIT", "100", "app", silent=True) or "100")  # Más historial
    SESSION_TIMEOUT_DAYS = int(get_secret("SESSION_TIMEOUT_DAYS", "30", "app", silent=True) or "30")
    
    # Configuración de logging
    LOG_LEVEL = get_secret("LOG_LEVEL", "INFO", "app", silent=True) or "INFO"  # Más detallado para producción inicial
    LOG_FILE = get_secret("LOG_FILE", "profit_coach.log", "app", silent=True) or "profit_coach.log"
    
    # Configuración de conexiones
    DB_POOL_MIN_CONN = int(get_secret("DB_POOL_MIN_CONN", "1", "app", silent=True) or "1")
    DB_POOL_MAX_CONN = int(get_secret("DB_POOL_MAX_CONN", "20", "app", silent=True) or "20")
    
    # Timeouts
    OPENAI_TIMEOUT = int(get_secret("OPENAI_TIMEOUT", "30", "app", silent=True) or "30")
    DB_TIMEOUT = int(get_secret("DB_TIMEOUT", "10", "app", silent=True) or "10")
    
    # Environment
    ENVIRONMENT = get_secret("ENVIRONMENT", "development", silent=True)
    
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
    env = get_secret("ENVIRONMENT", "development")  # Default a desarrollo para testing local
    logging.info(f"🌍 Entorno detectado: {env}")
    
    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()

# Instancia global de configuración
config = get_config()

# Validar configuración al cargar
try:
    config.validate_config()
    logging.info("✅ Configuración validada correctamente")
except Exception as e:
    logging.error(f"❌ Error en configuración: {e}")
    raise
