"""
Utilidades para manejo de errores y UX mejorado en ProFit Coach
"""
import streamlit as st
import logging
import functools
import time
from typing import Callable, Any, Optional

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('profit_coach.log'),
        logging.StreamHandler()
    ]
)

def safe_execute(func: Callable, error_message: str = "Ha ocurrido un error", 
                default_return: Any = None, show_error: bool = True) -> Any:
    """
    Ejecuta una función de manera segura con manejo de errores
    """
    try:
        return func()
    except Exception as e:
        logging.error(f"Error en {func.__name__}: {str(e)}")
        if show_error:
            st.error(f"{error_message}. Por favor, inténtalo de nuevo.")
        return default_return

def with_loading(message: str = "Procesando..."):
    """
    Decorador para mostrar spinner durante operaciones largas
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with st.spinner(message):
                return func(*args, **kwargs)
        return wrapper
    return decorator

def validate_input(value: str, field_name: str, min_length: int = 1, 
                  max_length: int = 100, required: bool = True) -> bool:
    """
    Valida input del usuario con feedback inmediato
    """
    if required and not value.strip():
        st.error(f"El campo {field_name} es obligatorio")
        return False
    
    if value and len(value) < min_length:
        st.error(f"{field_name} debe tener al menos {min_length} caracteres")
        return False
        
    if value and len(value) > max_length:
        st.error(f"{field_name} no puede exceder {max_length} caracteres")
        return False
        
    return True

def validate_email(email: str) -> bool:
    """
    Valida formato de email
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if email and not re.match(pattern, email):
        st.error("Por favor, ingresa un email válido")
        return False
    return True

def show_success_message(message: str, duration: int = 3):
    """
    Muestra mensaje de éxito que se auto-oculta
    """
    success_placeholder = st.empty()
    success_placeholder.success(message)
    time.sleep(duration)
    success_placeholder.empty()

def confirm_action(message: str, key: str) -> bool:
    """
    Modal de confirmación para acciones críticas
    """
    if st.session_state.get(f"confirm_{key}"):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Confirmar", key=f"confirm_yes_{key}", type="primary"):
                st.session_state[f"confirm_{key}"] = False
                return True
        with col2:
            if st.button("✗ Cancelar", key=f"confirm_no_{key}"):
                st.session_state[f"confirm_{key}"] = False
                return False
        return False
    return False

def navigation_state_manager():
    """
    Maneja el estado de navegación de manera robusta
    """
    # Inicializar estados si no existen
    default_states = {
        "username": None,
        "show_register": False,
        "show_password_reset": False,
        "active_athlete_chat": None,
        "current_page": "login"
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def clear_form_states():
    """
    Limpia estados de formularios para evitar conflictos
    """
    form_keys = [k for k in st.session_state.keys() if k.startswith(('form_', 'temp_'))]
    for key in form_keys:
        del st.session_state[key]

def create_styled_button(text: str, key: str, button_type: str = "primary", 
                        onclick_action: Optional[Callable] = None) -> bool:
    """
    Crea botones con estilo consistente y acciones opcionales
    """
    clicked = st.button(text, key=key, type=button_type, use_container_width=True)
    if clicked and onclick_action:
        onclick_action()
    return clicked

def format_error_for_user(error: Exception) -> str:
    """
    Convierte errores técnicos en mensajes amigables para el usuario
    """
    error_messages = {
        "psycopg2.OperationalError": "Error de conexión con la base de datos. Verifica tu conexión.",
        "openai.OpenAIError": "Error de comunicación con el servicio de IA. Inténtalo más tarde.",
        "ConnectionError": "Error de conexión. Verifica tu conexión a internet.",
        "TimeoutError": "La operación tardó demasiado. Inténtalo de nuevo.",
        "ValueError": "Datos inválidos. Verifica la información ingresada.",
        "KeyError": "Falta información requerida. Completa todos los campos."
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, "Ha ocurrido un error inesperado. Inténtalo de nuevo.")

class DatabaseContextManager:
    """
    Context manager para manejo seguro de conexiones a BD
    """
    def __init__(self, get_connection_func):
        self.get_connection = get_connection_func
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        try:
            self.conn = self.get_connection()
            self.cursor = self.conn.cursor()
            return self.cursor
        except Exception as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            st.error("Error de conexión a la base de datos")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            if self.conn:
                self.conn.rollback()
            logging.error(f"Error en operación de BD: {exc_val}")
        else:
            if self.conn:
                self.conn.commit()
        
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

def retry_operation(max_retries: int = 3, delay: float = 1.0):
    """
    Decorador para reintentar operaciones fallidas
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logging.warning(f"Intento {attempt + 1} falló para {func.__name__}: {e}")
                        time.sleep(delay)
                    else:
                        logging.error(f"Todos los intentos fallaron para {func.__name__}: {e}")
            
            raise last_exception
        return wrapper
    return decorator

def performance_monitor(func):
    """
    Decorador para monitorear rendimiento de funciones críticas
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            if execution_time > 2.0:  # Log si toma más de 2 segundos
                logging.warning(f"{func.__name__} tardó {execution_time:.2f}s en ejecutarse")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logging.error(f"{func.__name__} falló después de {execution_time:.2f}s: {e}")
            raise
    return wrapper
