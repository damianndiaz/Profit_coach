"""
ProFit Coach - Aplicación Principal Mejorada
Versión 2.0 con manejo robusto de errores y UX mejorado
"""

import streamlit as st
import logging
import time

# Configurar logging al inicio
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Para mostrar en consola/logs de Streamlit
    ]
)

# Importar config después de configurar logging
from config import config

logging.info("🚀 Iniciando ProFit Coach...")
# Ocultar información sensible en logs
masked_host = config.DB_HOST[:10] + "***" if config.DB_HOST and len(config.DB_HOST) > 10 else "***"
logging.info(f"🔧 Configuración cargada: DB_HOST={masked_host}")

from utils.app_utils import (
    safe_execute, navigation_state_manager, validate_input, validate_email,
    create_styled_button, confirm_action, with_loading, clear_form_states
)
from auth.auth_utils import (
    create_users_table, register_user, verify_user, get_user_id, update_user_password
)
from modules.athlete_manager import (
    create_athletes_table, get_athletes_by_user, add_athlete, update_athlete, delete_athlete, get_athlete_data
)
from modules.chat_manager import create_chat_tables, create_thread_table
from modules.chat_interface import handle_user_message, get_chat_history, detect_email_command
from modules.routine_export import generate_routine_excel_from_chat, create_download_and_email_interface
from auth.database import test_db_connection, initialize_connection_pool

# Configuración de página
st.set_page_config(
    page_title="ProFit Coach",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS personalizado para mejor UX
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #0d47a1;
        text-align: center;
        margin-bottom: 2rem;
        letter-spacing: 1px;
    }
    .athlete-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        background: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
    }
    .athlete-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 0.75rem;
        border-radius: 0.375rem;
        margin: 1rem 0;
    }
    .chat-user {
        background: #2563EB;
        color: white;
        padding: 12px 16px;
        border-radius: 12px 12px 0 12px;
        margin: 8px 0;
        max-width: 85%;
        float: right;
        clear: both;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .chat-ai {
        background: #F3F4F6;
        color: #1F2937;
        padding: 12px 16px;
        border-radius: 12px 12px 12px 0;
        margin: 8px 0;
        max-width: 85%;
        float: left;
        clear: both;
        line-height: 1.5;
        word-wrap: break-word;
    }
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    .status-online { background-color: #10b981; }
    .status-offline { background-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

def preserve_session_state():
    """Preserva el estado de la sesión durante recargas"""
    if "session_preserved" not in st.session_state:
        st.session_state["session_preserved"] = True
    
    # Mantener variables críticas durante recargas
    critical_keys = [
        "username", 
        "current_page", 
        "active_athlete_chat",
        "show_register",
        "show_password_reset"
    ]
    
    for key in critical_keys:
        if key in st.session_state:
            # Re-asegurar que la variable existe
            temp_value = st.session_state[key]
            st.session_state[key] = temp_value

def initialize_app():
    """Inicializa la aplicación con manejo de errores"""
    try:
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('profit_coach.log')
            ]
        )
        
        # Verificar conexión a BD
        if not test_db_connection():
            st.error("❌ Error de conexión a la base de datos. Verifica la configuración.")
            st.stop()
        
        # Inicializar pool de conexiones
        initialize_connection_pool()
        
        # Crear tablas
        create_users_table()
        create_athletes_table()
        create_chat_tables()
        create_thread_table()
        
        # Gestionar estado de navegación
        navigation_state_manager()
        
        logging.info("Aplicación inicializada correctamente")
        
    except Exception as e:
        logging.error(f"Error al inicializar aplicación: {e}")
        st.error("❌ Error al inicializar la aplicación. Contacta al administrador.")
        st.stop()

def show_app_status():
    """Muestra el estado de la aplicación en la barra lateral"""
    with st.sidebar:
        st.markdown("### 🏃‍♂️ ProFit Coach")
        st.markdown("---")
        
        # Estado de conexión
        db_status = test_db_connection()
        status_color = "status-online" if db_status else "status-offline"
        status_text = "Conectado" if db_status else "Sin conexión"
        
        st.markdown(f"""
        <div style='margin: 10px 0;'>
            <span class='status-indicator {status_color}'></span>
            Base de datos: {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("username"):
            st.markdown(f"**Usuario:** {st.session_state['username']}")
            
            # Botón de logout mejorado
            if st.button("🚪 Cerrar Sesión", key="sidebar_logout", use_container_width=True):
                st.session_state.clear()
                navigation_state_manager()
                st.rerun()

def login_screen():
    """Pantalla de login mejorada"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-header">🏃‍♂️ ProFit Coach</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#6B7280; font-size:1.1rem; margin-bottom:2rem;'>Entrenamiento inteligente para atletas</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            st.markdown("### 🔐 Iniciar Sesión")
            
            with st.form("login_form", clear_on_submit=False):
                username = st.text_input(
                    "👤 Usuario", 
                    placeholder="Tu nombre de usuario",
                    help="Ingresa tu nombre de usuario"
                )
                password = st.text_input(
                    "🔒 Contraseña", 
                    type="password",
                    placeholder="••••••••",
                    help="Ingresa tu contraseña"
                )
                
                col_login, col_register = st.columns(2)
                
                with col_login:
                    login_clicked = st.form_submit_button(
                        "🚀 Ingresar", 
                        use_container_width=True, 
                        type="primary"
                    )
                
                with col_register:
                    register_clicked = st.form_submit_button(
                        "📝 Registro",
                        use_container_width=True
                    )
                
                if login_clicked:
                    if not username.strip() or not password:
                        st.error("Por favor, completa todos los campos")
                    else:
                        with st.spinner("Verificando credenciales..."):
                            success, message = safe_execute(
                                lambda: verify_user(username, password),
                                "Error de autenticación",
                                (False, "Error de conexión")
                            )
                            
                            if success:
                                st.session_state["username"] = username.strip()
                                st.session_state["current_page"] = "main"
                                st.success("✅ ¡Bienvenido!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("❌ Credenciales incorrectas")
                
                if register_clicked:
                    st.session_state["show_register"] = True
                    st.session_state["current_page"] = "register"
                    st.rerun()
            
            # Enlaces adicionales
            col_forgot, col_help = st.columns(2)
            with col_forgot:
                if st.button("🔄 ¿Olvidaste tu contraseña?", use_container_width=True):
                    st.session_state["show_password_reset"] = True
                    st.session_state["current_page"] = "password_reset"
                    st.rerun()
            
            with col_help:
                if st.button("❓ Ayuda", use_container_width=True):
                    st.info("📧 Contacta al administrador para obtener ayuda")

def register_screen():
    """Pantalla de registro mejorada"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-header">📝 Crear Cuenta</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("register_form", clear_on_submit=True):
                st.markdown("### Información de la cuenta")
                
                username = st.text_input(
                    "👤 Nombre de usuario",
                    help="Mínimo 3 caracteres, solo letras, números y guiones bajos"
                )
                password = st.text_input(
                    "🔒 Contraseña",
                    type="password",
                    help="Mínimo 6 caracteres, debe incluir letras y números"
                )
                confirm_password = st.text_input(
                    "🔒 Confirmar contraseña",
                    type="password"
                )
                
                col_back, col_register = st.columns(2)
                
                with col_back:
                    if st.form_submit_button("⬅️ Volver", use_container_width=True):
                        st.session_state["show_register"] = False
                        st.session_state["current_page"] = "login"
                        st.rerun()
                
                with col_register:
                    register_clicked = st.form_submit_button(
                        "✅ Crear Cuenta", 
                        use_container_width=True, 
                        type="primary"
                    )
                
                if register_clicked:
                    # Validaciones
                    if not all([username.strip(), password, confirm_password]):
                        st.error("❌ Por favor, completa todos los campos")
                    elif password != confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                    else:
                        with st.spinner("Creando cuenta..."):
                            success, message = safe_execute(
                                lambda: register_user(username, password),
                                "Error al crear cuenta",
                                (False, "Error de conexión")
                            )
                            
                            if success:
                                st.success("✅ ¡Cuenta creada exitosamente!")
                                st.balloons()
                                time.sleep(2)
                                st.session_state["show_register"] = False
                                st.session_state["current_page"] = "login"
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

def password_reset_screen():
    """Pantalla de recuperación de contraseña mejorada"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="main-header">🔄 Recuperar Contraseña</div>', unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("password_reset_form", clear_on_submit=True):
                st.markdown("### Actualizar contraseña")
                
                username = st.text_input("👤 Nombre de usuario")
                new_password = st.text_input(
                    "🔒 Nueva contraseña", 
                    type="password",
                    help="Mínimo 6 caracteres, debe incluir letras y números"
                )
                confirm_password = st.text_input("🔒 Confirmar nueva contraseña", type="password")
                
                col_back, col_reset = st.columns(2)
                
                with col_back:
                    if st.form_submit_button("⬅️ Volver", use_container_width=True):
                        st.session_state["show_password_reset"] = False
                        st.session_state["current_page"] = "login"
                        st.rerun()
                
                with col_reset:
                    reset_clicked = st.form_submit_button(
                        "🔄 Actualizar", 
                        use_container_width=True, 
                        type="primary"
                    )
                
                if reset_clicked:
                    if not all([username.strip(), new_password, confirm_password]):
                        st.error("❌ Por favor, completa todos los campos")
                    elif new_password != confirm_password:
                        st.error("❌ Las contraseñas no coinciden")
                    else:
                        with st.spinner("Actualizando contraseña..."):
                            success, message = safe_execute(
                                lambda: update_user_password(username, new_password),
                                "Error al actualizar contraseña",
                                (False, "Error de conexión")
                            )
                            
                            if success:
                                st.success("✅ ¡Contraseña actualizada correctamente!")
                                time.sleep(2)
                                st.session_state["show_password_reset"] = False
                                st.session_state["current_page"] = "login"
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

def main_app(username):
    """Aplicación principal mejorada"""
    # Header
    col1, col2, col3 = st.columns([2, 3, 1])
    with col1:
        st.markdown('<div class="main-header">🏃‍♂️ ProFit Coach</div>', unsafe_allow_html=True)
    with col3:
        if st.button("🚪 Cerrar Sesión", type="secondary"):
            st.session_state.clear()
            navigation_state_manager()
            st.rerun()
    
    # Obtener user_id de manera segura
    user_id = safe_execute(
        lambda: get_user_id(username),
        "Error al obtener información del usuario"
    )
    
    if not user_id:
        st.error("❌ Error al cargar información del usuario")
        return
    
    # Obtener atletas
    athletes = safe_execute(
        lambda: get_athletes_by_user(user_id),
        "Error al cargar atletas",
        []
    )
    
    # Mostrar atletas
    show_athletes_section(athletes, user_id)
    
    # Panel de gestión
    show_athlete_management(athletes, user_id)
    
    # Chat si hay atleta activo
    show_chat_section(athletes)

def show_athletes_section(athletes, user_id):
    """Muestra la sección de atletas con tarjetas mejoradas"""
    st.markdown("---")
    st.markdown("## 🏃‍♂️ Tus Atletas")
    
    if athletes:
        # Mostrar en grid
        cols = st.columns(3)
        for idx, athlete in enumerate(athletes):
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"""
                    <div style='text-align:center; padding:16px;'>
                        <div style='width:64px; height:64px; background:linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                    border-radius:50%; margin:0 auto 16px; display:flex; align-items:center; justify-content:center;'>
                            <span style='font-size:1.5rem; color:white;'>🏃‍♂️</span>
                        </div>
                        <h3 style='margin-bottom:8px; color:#2563EB;'>{athlete[1]}</h3>
                        <p style='color:#6B7280; margin-bottom:4px;'><strong>{athlete[2]}</strong></p>
                        <p style='color:#6B7280; margin-bottom:16px; font-size:0.9rem;'>{athlete[3]}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(
                        f"💬 Chat con {athlete[1]}", 
                        key=f"start_chat_{athlete[0]}", 
                        use_container_width=True,
                        type="primary"
                    ):
                        st.session_state["active_athlete_chat"] = athlete[0]
                        st.rerun()
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; background:#F8FAFC; border-radius:12px; border:2px dashed #E2E8F0;'>
            <h3 style='color:#64748B; margin-bottom:16px;'>🏃‍♂️ No tienes atletas registrados</h3>
            <p style='color:#94A3B8; margin-bottom:24px;'>Comienza agregando tu primer atleta para empezar a entrenar</p>
        </div>
        """, unsafe_allow_html=True)

def show_athlete_management(athletes, user_id):
    """Panel de gestión de atletas mejorado"""
    st.markdown("---")
    st.markdown("## ⚙️ Gestión de Atletas")
    
    tab1, tab2 = st.tabs(["✏️ Editar Atleta", "➕ Agregar Nuevo"])
    
    with tab1:
        if athletes:
            selected_name = st.selectbox(
                "👤 Seleccionar atleta", 
                [a[1] for a in athletes],
                help="Elige el atleta que deseas editar"
            )
            
            athlete_data = next(a for a in athletes if a[1] == selected_name)
            
            with st.form("edit_athlete_form"):
                st.markdown("### 📝 Información del atleta")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("👤 Nombre completo", value=athlete_data[1])
                    sport = st.text_input("🏃‍♂️ Deporte", value=athlete_data[2])
                with col2:
                    # Lista de niveles disponibles
                    available_levels = ["Principiante", "Intermedio", "Avanzado", "Semi Profesional", "Élite"]
                    # Obtener el nivel actual o usar un valor por defecto
                    current_level = athlete_data[3]
                    try:
                        level_index = available_levels.index(current_level)
                    except ValueError:
                        # Si el nivel no existe en la lista, usar "Intermedio" como valor por defecto
                        level_index = 1  # Intermedio
                        st.warning(f"⚠️ Nivel '{current_level}' actualizado a 'Intermedio'. Por favor, selecciona el nivel correcto.")
                    
                    level = st.selectbox(
                        "📊 Nivel", 
                        available_levels,
                        index=level_index
                    )
                    email = st.text_input("📧 Email", value=athlete_data[5] or "")
                
                goals = st.text_area("🎯 Objetivos", value=athlete_data[4] or "", height=100)
                
                col_save, col_delete = st.columns(2)
                
                with col_save:
                    if st.form_submit_button("💾 Guardar Cambios", type="primary", use_container_width=True):
                        if validate_input(name, "Nombre", min_length=2) and validate_input(sport, "Deporte", min_length=2):
                            if not email or validate_email(email):
                                with st.spinner("Guardando cambios..."):
                                    success, message = safe_execute(
                                        lambda: update_athlete(athlete_data[0], name, sport, level, goals, email),
                                        "Error al actualizar atleta",
                                        (False, "Error de conexión")
                                    )
                                    
                                    if success:
                                        st.success("✅ Atleta actualizado correctamente")
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                
                with col_delete:
                    if st.form_submit_button("🗑️ Eliminar", use_container_width=True):
                        st.session_state[f"confirm_delete_{athlete_data[0]}"] = True
            
            # Confirmación de eliminación
            if st.session_state.get(f"confirm_delete_{athlete_data[0]}"):
                st.warning(f"⚠️ ¿Estás seguro de que quieres eliminar a **{athlete_data[1]}**? Esta acción no se puede deshacer.")
                
                col_confirm, col_cancel = st.columns(2)
                with col_confirm:
                    if st.button("✅ Confirmar Eliminación", type="primary", use_container_width=True):
                        with st.spinner("Eliminando atleta..."):
                            success, message = safe_execute(
                                lambda: delete_athlete(athlete_data[0]),
                                "Error al eliminar atleta",
                                (False, "Error de conexión")
                            )
                            
                            if success:
                                st.success("✅ Atleta eliminado correctamente")
                                del st.session_state[f"confirm_delete_{athlete_data[0]}"]
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                
                with col_cancel:
                    if st.button("❌ Cancelar", use_container_width=True):
                        del st.session_state[f"confirm_delete_{athlete_data[0]}"]
                        st.rerun()
        else:
            st.info("📝 No tienes atletas registrados para editar")
    
    with tab2:
        with st.form("add_athlete_form"):
            st.markdown("### ➕ Nuevo Atleta")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("👤 Nombre completo", help="Nombre y apellido del atleta")
                sport = st.text_input("🏃‍♂️ Deporte principal", help="Ej: Fútbol, Tenis, Natación")
            with col2:
                level = st.selectbox("📊 Nivel", ["Principiante", "Intermedio", "Avanzado", "Semi Profesional", "Élite"])
                email = st.text_input("📧 Email (opcional)", help="Email para notificaciones")
            
            goals = st.text_area(
                "🎯 Objetivos", 
                help="Describe los objetivos específicos del atleta",
                height=100
            )
            
            if st.form_submit_button("➕ Agregar Atleta", type="primary", use_container_width=True):
                if validate_input(name, "Nombre", min_length=2) and validate_input(sport, "Deporte", min_length=2):
                    if not email or validate_email(email):
                        with st.spinner("Agregando atleta..."):
                            success, message = safe_execute(
                                lambda: add_athlete(user_id, name, sport, level, goals, email),
                                "Error al agregar atleta",
                                (False, "Error de conexión")
                            )
                            
                            if success:
                                st.success("✅ Atleta agregado exitosamente")
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")

def show_chat_section(athletes):
    """Sección de chat mejorada"""
    athlete_id = st.session_state.get("active_athlete_chat")
    
    if athlete_id:
        athlete_name = None
        for a in athletes:
            if a[0] == athlete_id:
                athlete_name = a[1]
                break
        
        if not athlete_name:
            st.error("❌ Atleta no encontrado")
            st.session_state["active_athlete_chat"] = None
            st.rerun()
            return
        
        st.markdown("---")
        
        # Header del chat
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## 💬 Chat con {athlete_name}")
        with col2:
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state["active_athlete_chat"] = None
                st.rerun()
        
        # Contenedor del chat
        chat_container = st.container(height=500, border=True)
        
        with chat_container:
            chat_history = safe_execute(
                lambda: get_chat_history(athlete_id),
                "Error al cargar historial",
                []
            )
            
            if not chat_history:
                st.markdown("""
                <div style='text-align:center; padding:40px; color:#6B7280;'>
                    🎯 <strong>¡Hola! Soy ProFit Coach AI</strong> 🤖<br><br>
                    
                    <div style='color:#1F2937; margin:20px 0; font-size:1.1em;'>
                        <strong>🚀 Especialista en Metodología de 5 Bloques</strong><br><br>
                        
                        <div style='background:#f0f9ff; padding:20px; border-radius:12px; margin:20px 0;'>
                            <strong>� ¿Qué puedo hacer por ti?</strong><br><br>
                            🏋️ <strong>Rutinas personalizadas</strong> con descarga automática en Excel<br>
                            🥗 <strong>Consejos de nutrición</strong> deportiva específica<br>
                            🛡️ <strong>Prevención de lesiones</strong> adaptada a tu deporte<br>
                            🎯 <strong>Entrenamientos específicos</strong> según tu nivel<br><br>
                        </div>
                        
                        <div style='background:#f0fdf4; padding:15px; border-radius:8px; margin:15px 0;'>
                            <strong>💡 Ejemplos rápidos:</strong><br>
                            🟢 "Rutina completa para fútbol"<br>
                            🟢 "Ejercicios para prevenir lesiones"<br>
                            🟢 "Circuito de fuerza y velocidad"<br>
                        </div>
                    </div>
                    
                    <p style='color:#9CA3AF; font-size:0.9em; margin-top:25px;'>
                        ⚡ Sin tiempos fijos - adaptación completa a tus necesidades ⚡
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            for idx, (msg, is_user, created_at) in enumerate(chat_history):
                if is_user:
                    st.markdown(f"""
                    <div style='display:flex; justify-content:flex-end; margin-bottom:16px;'>
                        <div class='chat-user'>
                            {msg}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Procesar respuestas especiales del AI
                    ai_content = msg.replace("🤖 ProFit Coach AI:", "").strip()
                    
                    # Generar ID único para este mensaje
                    message_id = f"{athlete_id}_{idx}_{created_at.strftime('%Y%m%d_%H%M%S') if created_at else 'no_date'}"
                    
                    # Detectar si es una rutina
                    if "[INICIO_NUEVA_RUTINA]" in ai_content:
                        ai_content_clean = ai_content.replace("[INICIO_NUEVA_RUTINA]", "")
                        st.markdown(f"""
                        <div style='display:flex; justify-content:flex-start; margin-bottom:16px;'>
                            <div class='chat-ai' style='max-width: 85%;'>
                                <strong>🤖 ProFit Coach AI - Nueva Rutina 💪:</strong><br>
                                <div style='white-space: pre-line; font-family: monospace; font-size: 0.9em; background: #f8f9fa; padding: 12px; border-radius: 8px; margin-top: 8px;'>
                                {ai_content_clean}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Generar botón de descarga para rutina
                        excel_data, athlete_name = generate_routine_excel_from_chat(athlete_id, msg)
                        if excel_data:
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                create_download_and_email_interface(athlete_id, excel_data, athlete_name, "Rutina_Entrenamiento", unique_id=message_id)
                                st.markdown("""
                                <div style='text-align:center; margin:10px 0; padding:10px; background:#e8f5e8; border-radius:8px; color:#2d5a2d; font-size:0.9em;'>
                                    ✅ <strong>Rutina lista para descargar y enviar</strong><br>
                                    📁 Incluye: Días de entrenamiento, ejercicios detallados y envío por email
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style='display:flex; justify-content:flex-start; margin-bottom:16px;'>
                            <div class='chat-ai' style='max-width: 85%;'>
                                <strong>🤖 ProFit Coach AI:</strong><br>
                                <div style='white-space: pre-line;'>{ai_content}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Detectar rutinas sin marcador específico
                        if any(keyword in ai_content.lower() for keyword in ['día 1', 'día 2', 'semana', 'rutina semanal', 'entrenamiento semanal']):
                            excel_data, athlete_name = generate_routine_excel_from_chat(athlete_id, msg)
                            if excel_data:
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    st.markdown("---")
                                    st.markdown("**💡 ¿Quieres descargar esta rutina en Excel?**")
                                    create_download_and_email_interface(athlete_id, excel_data, athlete_name, "Rutina_Entrenamiento", unique_id=f"{message_id}_alt")
        
        # Input del chat
        with st.form("chat_input_form", clear_on_submit=True, border=False):
            col_input, col_send = st.columns([5, 1])
            
            with col_input:
                user_message = st.text_input(
                    "💬 Escribe tu mensaje...",
                    placeholder="Pregunta algo sobre entrenamiento",
                    label_visibility="collapsed",
                    key=f"chat_input_{athlete_id}"
                )
            
            with col_send:
                send_clicked = st.form_submit_button(
                    "🚀",
                    use_container_width=True,
                    type="primary"
                )
            
            # Procesar el mensaje cuando se envía
            if send_clicked and user_message.strip():
                # Detectar si es un comando de email
                is_email_command = detect_email_command(user_message)
                
                if is_email_command:
                    st.info("📧 Detecté que quieres enviar algo por email. Procesando...")
                
                with st.spinner("🤖 Generando respuesta inteligente..."):
                    response = handle_user_message(athlete_id, user_message)
                    if response:
                        # Si es respuesta de email exitosa, mostrar confirmación especial
                        if "✅" in response and "enviado" in response.lower():
                            st.success("📧 ¡Email enviado exitosamente!")
                            st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error al procesar el mensaje")
        
        # Mostrar interfaz de email automático si se detectó una rutina nueva con solicitud de email
        if st.session_state.get(f'auto_email_routine_{athlete_id}'):
            auto_email_data = st.session_state[f'auto_email_routine_{athlete_id}']
            st.markdown("---")
            st.markdown("### 📧 Envío Automático por Email")
            st.info("🤖 Detecté que querías enviar la rutina por email. Aquí tienes las opciones:")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("📤 Sí, enviar ahora", key=f"auto_send_{athlete_id}", type="primary"):
                    from modules.routine_export import create_simple_routine_excel
                    from modules.email_manager import send_routine_email
                    from datetime import datetime
                    
                    athlete_data = get_athlete_data(athlete_id)
                    email_to_use = auto_email_data.get('email') or athlete_data.get('email', '').strip()
                    
                    if email_to_use:
                        excel_data = create_simple_routine_excel(athlete_id, auto_email_data['routine'])
                        if excel_data:
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            filename = f"Rutina_{athlete_data['name'].replace(' ', '_')}_{timestamp}.xlsx"
                            
                            success, message = send_routine_email(email_to_use, athlete_data['name'], excel_data, filename)
                            
                            if success:
                                st.success(f"✅ ¡Rutina enviada exitosamente a {email_to_use}!")
                                st.balloons()
                            else:
                                st.error(f"❌ Error al enviar: {message}")
                        else:
                            st.error("❌ Error al generar el Excel")
                    else:
                        st.error("❌ No se encontró email válido")
                    
                    # Limpiar estado
                    del st.session_state[f'auto_email_routine_{athlete_id}']
                    st.rerun()
            
            with col2:
                if st.button("❌ No por ahora", key=f"auto_cancel_{athlete_id}"):
                    del st.session_state[f'auto_email_routine_{athlete_id}']
                    st.rerun()
        
        # Información adicional sobre el chat
        with st.expander("ℹ️ Metodología de 5 Bloques Especializados", expanded=False):
            st.markdown("""
            **🚀 Nueva Metodología ProFit Coach - 5 Bloques Sin Tiempos Fijos:**
            
            **📋 Estructura de 5 Bloques:**
            - 🍑 **Bloque 1 - Activación Glútea:** Activación específica del complejo glúteo y estabilizadores
            - ⚡ **Bloque 2 - Dinámico/Potencia/Diagonales/Zona Media:** Adaptable según objetivo del deportista
            - � **Bloque 3 - Fuerza 1:** Patrones fundamentales - empuje, tracción, movimientos unilaterales
            - 🔥 **Bloque 4 - Fuerza 2:** Movimientos complejos, combinados y de alta transferencia
            - � **Bloque 5 - Contraste/Preventivos/RSA:** Contraste velocidad, prevención y acondicionamiento específico
            
            **� Alternativa Circuito Integral:**
            - **Formato:** 6 ejercicios x 5 series
            - **Reemplaza:** Bloque 3 y 4 (Fuerza 1 y 2)
            - **Integra:** Fuerza + Potencia + Velocidad + Zona Media en un solo circuito
            - **Ventaja:** Máxima eficiencia temporal con estímulo completo
            
            **� Características Clave:**
            - ❌ **SIN TIEMPOS FIJOS** - Adaptación completa a tus necesidades
            - ✅ Flexibilidad total en duración de cada bloque
            - 🎨 Variabilidad constante - nunca se repiten rutinas
            - � Personalización según deporte, nivel y objetivos
            - � Posibilidad de elegir estructura tradicional o circuito integral
            
            **📥 Funcionalidad Excel Automática:**
            - 📊 Generación automática cuando detecta rutinas
            - 📋 Hojas separadas por cada bloque de entrenamiento
            - 📝 Hoja de seguimiento y progresión
            - 📈 Información personalizada del atleta
            
            **💡 Ejemplos de Consultas Optimizadas:**
            - "*Rutina completa de 5 bloques para fútbol*"
            - "*Solo el bloque de activación glúteo para prevenir lesiones*"
            - "*Circuito integral de 6 ejercicios para rugby*"
            - "*Bloque 2 enfocado en potencia explosiva para tenis*"
            - "*Bloque 5 con RSA específico para natación*"
            
            **⚡ Sistema Inteligente:**
            - 🧠 Recuerda rutinas previas y evita repeticiones
            - 🎯 Adapta según equipamiento disponible
            - 📊 Progresiones automáticas según nivel
            - 🔄 Variaciones infinitas dentro de cada bloque
            """)
            
            # Mostrar estadísticas si hay historial
            if chat_history:
                routine_count = len([msg for msg, is_user, _ in chat_history if not is_user and any(keyword in msg.lower() for keyword in ['día 1', 'día 2', 'rutina'])])
                st.markdown(f"**Estadísticas:** {len(chat_history)} mensajes total | {routine_count} rutinas generadas")

# --- Punto de entrada principal ---
def main():
    """Función principal de la aplicación"""
    try:
        # Preservar estado de sesión
        preserve_session_state()
        
        # Inicializar aplicación
        initialize_app()
        
        # Mostrar estado en sidebar
        show_app_status()
        
        # Enrutamiento basado en estado
        if st.session_state.get("username"):
            main_app(st.session_state["username"])
        elif st.session_state.get("show_register"):
            register_screen()
        elif st.session_state.get("show_password_reset"):
            password_reset_screen()
        else:
            login_screen()
            
    except Exception as e:
        logging.error(f"Error crítico en aplicación: {e}")
        st.error("❌ Error crítico en la aplicación. Por favor, recarga la página.")
        
        if st.button("🔄 Recargar Aplicación"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
