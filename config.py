"""
Configuración de ProFit Coach
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración principal de la aplicación"""
    
    # Base de datos
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "profit_coach")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    
    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_ASSISTANT_ID = os.getenv("OPENAI_ASSISTANT_ID", "")
    
    # Email Configuration
    EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
    EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
    EMAIL_USERNAME = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
    EMAIL_FROM_NAME = os.getenv("EMAIL_FROM_NAME", "ProFit Coach")
    EMAIL_FROM_EMAIL = os.getenv("EMAIL_FROM_EMAIL", "")
    
    # Configuración de la aplicación
    MAX_ATHLETES_PER_USER = int(os.getenv("MAX_ATHLETES_PER_USER", "50"))
    MAX_MESSAGE_LENGTH = int(os.getenv("MAX_MESSAGE_LENGTH", "2000"))
    CHAT_HISTORY_LIMIT = int(os.getenv("CHAT_HISTORY_LIMIT", "50"))
    SESSION_TIMEOUT_DAYS = int(os.getenv("SESSION_TIMEOUT_DAYS", "30"))
    
    # Configuración de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "profit_coach.log")
    
    # Configuración de conexiones
    DB_POOL_MIN_CONN = int(os.getenv("DB_POOL_MIN_CONN", "1"))
    DB_POOL_MAX_CONN = int(os.getenv("DB_POOL_MAX_CONN", "20"))
    
    # Timeouts
    OPENAI_TIMEOUT = int(os.getenv("OPENAI_TIMEOUT", "30"))
    DB_TIMEOUT = int(os.getenv("DB_TIMEOUT", "10"))
    
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
