"""
ProFit Coach - Aplicación Principal Mejorada
Versión 2.0 con manejo robusto de errores y UX mejorado
"""

import streamlit as st
import streamlit.components.v1 as components
import logging
import time
import pandas as pd
import io
import re

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
from modules.chat_interface import handle_user_message, get_chat_history, detect_email_command, get_welcome_message
from modules.routine_export import generate_routine_excel_from_chat, create_download_button
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
        color: #0d47a1;        text-align: center;
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
        padding: 10px 14px;
        border-radius: 18px 18px 4px 18px;
        margin: 6px 0;
        max-width: 75%;
        float: right;
        clear: both;
        line-height: 1.4;
        word-wrap: break-word;
        font-size: 0.9rem;
        font-weight: 400;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .chat-ai {
        background: #F8FAFC;
        color: #334155;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 6px 0;
        max-width: 80%;
        float: left;
        clear: both;
        line-height: 1.5;
        word-wrap: break-word;
        font-size: 0.9rem;
        font-weight: 400;
        border: 1px solid #E2E8F0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .chat-ai strong {
        font-weight: 600;
        color: #1E293B;
        font-size: 0.85rem;
    }
    .chat-ai h1, .chat-ai h2, .chat-ai h3 {
        font-weight: 600;
        margin: 8px 0 4px 0;
        color: #1E293B;
    }
    .chat-ai code {
        background: #F1F5F9;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8rem;
        color: #475569;
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
    """Inicializa la aplicación con manejo de errores - OPTIMIZADO"""
    # 🚀 OPTIMIZACIÓN: Solo inicializar una vez por sesión
    if st.session_state.get("app_initialized", False):
        return  # Ya inicializado, salir inmediatamente
    
    try:
        # Configurar logging (solo si no está configurado)
        if not logging.getLogger().handlers:
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.StreamHandler(),
                    logging.FileHandler('profit_coach.log')
                ]
            )
        
        # Verificar conexión a BD (rápido)
        if not test_db_connection():
            st.error("❌ Error de conexión a la base de datos. Verifica la configuración.")
            st.stop()
        
        # Inicializar pool de conexiones (solo una vez)
        if not st.session_state.get("db_pool_initialized", False):
            initialize_connection_pool()
            st.session_state["db_pool_initialized"] = True
        
        # Crear tablas (solo una vez)
        if not st.session_state.get("tables_created", False):
            create_users_table()
            create_athletes_table()
            create_chat_tables()
            create_thread_table()
            st.session_state["tables_created"] = True
        
        # Gestionar estado de navegación
        navigation_state_manager()
        
        # Marcar como inicializado
        st.session_state["app_initialized"] = True
        logging.info("✅ Aplicación inicializada correctamente (optimizada)")
        
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
                ) or ""
                password = st.text_input(
                    "🔒 Contraseña", 
                    type="password",
                    placeholder="••••••••",
                    help="Ingresa tu contraseña"
                ) or ""
                
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
                ) or ""
                password = st.text_input(
                    "🔒 Contraseña",
                    type="password",
                    help="Mínimo 6 caracteres, debe incluir letras y números"
                ) or ""
                confirm_password = st.text_input(
                    "🔒 Confirmar contraseña",
                    type="password"
                ) or ""
                
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
                
                username = st.text_input("👤 Nombre de usuario") or ""
                new_password = st.text_input(
                    "🔒 Nueva contraseña", 
                    type="password",
                    help="Mínimo 6 caracteres, debe incluir letras y números"
                ) or ""
                confirm_password = st.text_input("🔒 Confirmar nueva contraseña", type="password") or ""
                
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
    
    # Templates rápidos si están activos
    show_quick_templates_section(athletes)

def process_uploaded_file(file):
    """Procesa un archivo adjunto y extrae su contenido"""
    try:
        # Verificar que el archivo es válido
        if not file or not hasattr(file, 'getvalue'):
            return "❌ Archivo inválido o corrupto"
            
        file_size = len(file.getvalue()) / 1024  # KB
        
        # Verificar tamaño máximo (10MB)
        if file_size > 10240:  # 10MB en KB
            return f"❌ **{file.name}** - Archivo demasiado grande ({file_size:.1f} KB). Máximo permitido: 10MB"
        
        file_type = file.type if file.type else "application/octet-stream"
        
        # Resetear el puntero del archivo
        file.seek(0)
        
        if file_type.startswith('text/') or file.name.endswith('.txt'):
            # Archivos de texto
            try:
                content = file.getvalue().decode('utf-8')
                return f"📄 **{file.name}** ({file_size:.1f} KB) - Archivo de texto:\n```\n{content[:2000]}{'...' if len(content) > 2000 else ''}\n```"
            except UnicodeDecodeError:
                return f"📄 **{file.name}** ({file_size:.1f} KB) - Archivo de texto (error de codificación - usar UTF-8)"
        
        elif file_type in ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel'] or file.name.endswith(('.xlsx', '.xls')):
            # Archivos Excel
            try:
                df = pd.read_excel(file, nrows=50)  # Limitar a 50 filas
                content = df.to_string(max_rows=20, max_cols=10)
                return f"📊 **{file.name}** ({file_size:.1f} KB) - Contenido Excel:\n```\n{content}\n```"
            except Exception as e:
                return f"📊 **{file.name}** ({file_size:.1f} KB) - Archivo Excel (error al leer: {str(e)})"
        
        elif file_type.startswith('image/'):
            # Imágenes
            return f"🖼️ **{file.name}** ({file_size:.1f} KB) - Imagen adjunta para análisis de ejercicios/técnica"
        
        elif file_type == 'application/pdf':
            # PDFs
            return f"📄 **{file.name}** ({file_size:.1f} KB) - Documento PDF adjunto"
        
        elif file_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' or file.name.endswith('.docx'):
            # Word
            return f"📝 **{file.name}** ({file_size:.1f} KB) - Documento Word adjunto"
        
        else:
            # Otros archivos
            return f"📎 **{file.name}** ({file_size:.1f} KB) - Archivo adjunto (tipo: {file_type})"
            
    except Exception as e:
        logging.error(f"Error procesando archivo {getattr(file, 'name', 'unknown')}: {e}")
        return f"❌ **{getattr(file, 'name', 'archivo')}** - Error al procesar archivo: {str(e)}"

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
                    
                    if st.button(
                        f"⚡ Rutinas Rápidas", 
                        key=f"quick_templates_{athlete[0]}", 
                        use_container_width=True,
                        type="secondary"
                    ):
                        st.session_state["show_quick_templates"] = athlete[0]
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
    
    # 🔽 GESTIÓN DE ATLETAS con expander pero título grande
    with st.expander("## ⚙️ Gestión de Atletas", expanded=False):
        # 🔄 REORDENADO: Primero "Agregar Nuevo", después "Editar"
        tab1, tab2 = st.tabs(["➕ Agregar Nuevo", "✏️ Editar Atleta"])
        
        # 🆕 TAB 1: AGREGAR NUEVO (AHORA PRIMERA)
        with tab1:
            with st.form("add_athlete_form"):
                st.markdown("### 🆕 Nuevo Atleta")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("👤 Nombre completo*") or ""
                    sport = st.text_input("🏃‍♂️ Deporte*") or ""
                with col2:
                    level = st.selectbox(
                        "📊 Nivel*", 
                        ["Principiante", "Intermedio", "Avanzado", "Semi Profesional", "Élite"]
                    ) or "Intermedio"
                    email = st.text_input("📧 Email") or ""
                
                goals = st.text_area("🎯 Objetivos", height=100) or ""
                
                if st.form_submit_button("✅ Crear Atleta", use_container_width=True, type="primary"):
                    if name and sport and level:
                        result = safe_execute(
                            lambda: add_athlete(user_id, name, sport, level, goals or "Sin objetivos específicos", email),
                            "Error al agregar atleta"
                        )
                        if result:
                            st.success(f"✅ Atleta {name} agregado correctamente")
                            time.sleep(1)
                            st.rerun()
                    else:
                        st.error("❌ Por favor completa todos los campos obligatorios (*)")
        
        # ✏️ TAB 2: EDITAR ATLETA (AHORA SEGUNDA)
        with tab2:
            if athletes:
                selected_name = st.selectbox(
                    "👤 Seleccionar atleta", 
                    [a[1] for a in athletes],
                    help="Elige el atleta que deseas editar"
                ) or (athletes[0][1] if athletes else "")
            
                athlete_data = next(a for a in athletes if a[1] == selected_name)
            
            with st.form("edit_athlete_form"):
                st.markdown("### 📝 Información del atleta")
                
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("👤 Nombre completo", value=athlete_data[1]) or ""
                    sport = st.text_input("🏃‍♂️ Deporte", value=athlete_data[2]) or ""
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
                    ) or "Intermedio"
                    email = st.text_input("📧 Email", value=athlete_data[5] or "") or ""
                
                goals = st.text_area("🎯 Objetivos", value=athlete_data[4] or "", height=100) or ""
                
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
                st.info("ℹ️ No tienes atletas registrados para editar")

def show_quick_templates_section(athletes):
    """Sección de templates rápidos"""
    athlete_id = st.session_state.get("show_quick_templates")
    
    if athlete_id:
        athlete_name = None
        for a in athletes:
            if a[0] == athlete_id:
                athlete_name = a[1]
                break
        
        if not athlete_name:
            st.error("❌ Atleta no encontrado")
            st.session_state["show_quick_templates"] = None
            st.rerun()
            return
        
        st.markdown("---")
        
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"## ⚡ Rutinas Rápidas para {athlete_name}")
            st.markdown("*Elige un template y se generará automáticamente en el chat*")
        with col2:
            if st.button("⬅️ Volver", use_container_width=True):
                st.session_state["show_quick_templates"] = None
                st.rerun()
        
        # Importar la función aquí para evitar errores de importación
        try:
            import sys
            import os
            # Asegurar que el path esté configurado correctamente
            if '/workspaces/ProFit Coach' not in sys.path:
                sys.path.insert(0, '/workspaces/ProFit Coach')
            
            from modules.quick_templates import show_quick_templates_interface
            show_quick_templates_interface(athlete_id, athlete_name)
        except ImportError as e:
            st.error(f"❌ Error importando módulo de templates: {e}")
            st.info("💡 Asegúrate de que el archivo modules/quick_templates.py existe")
        except Exception as e:
            st.error(f"❌ Error ejecutando templates: {e}")

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
        
        # 🎯 AUTO-SCROLL MEJORADO: Scroll automático al último mensaje
        if f"auto_scroll_{athlete_id}" not in st.session_state:
            st.session_state[f"auto_scroll_{athlete_id}"] = True
            # ⚡ USAR components.html para mejor control del scroll
            components.html("""
                <script>
                function scrollToBottom() {
                    // Scroll del contenedor principal
                    window.scrollTo({
                        top: document.body.scrollHeight,
                        behavior: 'smooth'
                    });
                    
                    // Scroll del contenedor del chat específicamente
                    const chatContainer = document.querySelector('[data-testid="column"] div[style*="height: 500px"]');
                    if (chatContainer) {
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }
                }
                
                // Ejecutar después de que se cargue el DOM
                setTimeout(scrollToBottom, 500);
                // Backup - ejecutar de nuevo por si acaso
                setTimeout(scrollToBottom, 1000);
                </script>
            """, height=0)
        
        # Contenedor del chat
        chat_container = st.container(height=500, border=True)
        
        with chat_container:
            chat_history = safe_execute(
                lambda: get_chat_history(athlete_id),
                "Error al cargar historial",
                []
            )
            
            if not chat_history:
                # Mostrar mensaje de bienvenida personalizado
                welcome_msg = get_welcome_message(athlete_id)
                st.markdown(f"""
                <div style='text-align:center; padding:40px; color:#1F2937; background:#f8fafc; border-radius:12px;'>
                    {welcome_msg.replace(chr(10), '<br>')}
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
                        ai_content_clean = ai_content.replace("[INICIO_NUEVA_RUTINA]", "").strip()
                        
                        # � FORMATO MEJORADO Y CONSISTENTE DE RUTINAS
                        lines = ai_content_clean.split('\n')
                        formatted_content = []
                        in_table = False
                        
                        for line in lines:
                            line = line.strip()
                            if not line:
                                if not in_table:  # Solo agregar espacios fuera de tablas
                                    formatted_content.append("<br>")
                                continue
                            
                            # 🏆 TÍTULOS PRINCIPALES (RUTINA, ENTRENAMIENTO)
                            if any(keyword in line.upper() for keyword in ['**📝 RUTINA:', '📋 RUTINA:', 'RUTINA:']):
                                title = line.replace('**', '').replace('📝', '').replace('📋', '').strip()
                                formatted_content.append(f"""
                                <div style='background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); 
                                     color: white; padding: 12px 20px; border-radius: 12px; margin: 10px 0;
                                     text-align: center; font-size: 1.2em; font-weight: bold; box-shadow: 0 4px 15px rgba(79, 70, 229, 0.3);'>
                                    🏆 {title}
                                </div>""")
                                continue
                            
                            # ⏱️ INFORMACIÓN CLAVE (Duración, Objetivo, Nivel)
                            if any(keyword in line for keyword in ['⏱️ Duración Total:', '🎯 Objetivo:', '📊 Nivel:']):
                                formatted_content.append(f"""
                                <div style='background: #F0F9FF; border-left: 4px solid #0EA5E9; 
                                     padding: 8px 15px; margin: 5px 0; border-radius: 0 8px 8px 0;'>
                                    <strong style='color: #0369A1;'>{line}</strong>
                                </div>""")
                                continue
                            
                            # 🔥 BLOQUES DE ENTRENAMIENTO (BLOQUE 1, 2, etc.)
                            if any(keyword in line.upper() for keyword in ['### **BLOQUE', 'BLOQUE 1', 'BLOQUE 2', 'BLOQUE 3', 'BLOQUE 4', 'BLOQUE 5']) and ('min)' in line or 'MIN)' in line):
                                block_name = line.replace('###', '').replace('**', '').strip()
                                formatted_content.append(f"""
                                <div style='background: linear-gradient(135deg, #059669 0%, #0D9488 100%); 
                                     color: white; padding: 10px 16px; border-radius: 8px; margin: 15px 0 5px 0;
                                     font-weight: bold; box-shadow: 0 2px 10px rgba(5, 150, 105, 0.2);'>
                                    🔸 {block_name}
                                </div>""")
                                continue
                            
                            # 📋 TABLA DE EJERCICIOS
                            if line.startswith('|------'):
                                in_table = True
                                continue  # Skip separator lines
                            elif line.startswith('|') and '|' in line[1:]:
                                if not in_table:
                                    # Header de tabla
                                    headers = [h.strip() for h in line.split('|')[1:-1]]
                                    if len(headers) >= 3:  # Verificar que sea una tabla de ejercicios
                                        formatted_content.append("""
                                        <div style='background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; margin: 10px 0; overflow: hidden;'>
                                        <table style='width: 100%; border-collapse: collapse;'>""")
                                        
                                        header_html = "<tr style='background: #64748B; color: white; font-weight: bold;'>"
                                        for header in headers:
                                            header_html += f"<td style='padding: 10px 12px; border: none; font-size: 0.85em;'>{header}</td>"
                                        header_html += "</tr>"
                                        formatted_content.append(header_html)
                                        in_table = True
                                        continue
                                else:
                                    # Row de datos
                                    cells = [c.strip() for c in line.split('|')[1:-1]]
                                    if len(cells) >= 3:
                                        row_html = "<tr style='border-bottom: 1px solid #E2E8F0;'>"
                                        for i, cell in enumerate(cells):
                                            if i == 0:  # Nombre del ejercicio
                                                row_html += f"<td style='padding: 10px 12px; font-weight: 600; color: #1E293B;'>{cell}</td>"
                                            elif 'x' in cell or 'rep' in cell.lower():  # Series/Reps
                                                highlighted_cell = re.sub(r'(\d+)\s*x\s*(\d+)', r'<span style="background:#DBEAFE; padding:2px 6px; border-radius:4px; font-weight:bold;">\1×\2</span>', cell)
                                                row_html += f"<td style='padding: 10px 12px; text-align: center;'>{highlighted_cell}</td>"
                                            elif any(time_word in cell.lower() for time_word in ['min', 'seg', 'segundo']):  # Tiempo
                                                highlighted_cell = re.sub(r'(\d+)\s*(min|seg)', r'<span style="background:#FEF3C7; padding:2px 6px; border-radius:4px; font-weight:bold;">\1\2</span>', cell)
                                                row_html += f"<td style='padding: 10px 12px; text-align: center;'>{highlighted_cell}</td>"
                                            else:
                                                row_html += f"<td style='padding: 10px 12px; color: #64748B;'>{cell}</td>"
                                        row_html += "</tr>"
                                        formatted_content.append(row_html)
                                        continue
                            else:
                                if in_table:
                                    formatted_content.append("</table></div>")
                                    in_table = False
                            
                            # 📋 NOTAS TÉCNICAS
                            if line.startswith('**📋 NOTAS TÉCNICAS'):
                                formatted_content.append(f"""
                                <div style='background: #FEF7CD; border: 1px solid #F59E0B; border-radius: 8px; 
                                     padding: 12px 16px; margin: 15px 0;'>
                                    <strong style='color: #92400E; font-size: 1.05em;'>📋 NOTAS TÉCNICAS IMPORTANTES</strong>
                                </div>""")
                                continue
                            
                            # 💡 NOTAS ESPECÍFICAS (Respiración, Técnica, etc.)
                            if line.startswith('- **') and any(keyword in line for keyword in ['Respiración:', 'Técnica:', 'Progresión:', 'Adaptaciones:']):
                                note_content = line.replace('- **', '').replace('**', '')
                                parts = note_content.split(':', 1)
                                if len(parts) == 2:
                                    note_title, note_desc = parts
                                    formatted_content.append(f"""
                                    <div style='margin: 8px 0 8px 15px; padding: 8px 12px; background: #F0FDF4; 
                                         border-left: 3px solid #22C55E; border-radius: 0 6px 6px 0;'>
                                        <strong style='color: #15803D;'>💡 {note_title.strip()}:</strong> 
                                        <span style='color: #374151;'>{note_desc.strip()}</span>
                                    </div>""")
                                    continue
                            
                            # ⏱️ TIEMPO ESTIMADO TOTAL
                            if '⏱️ Tiempo estimado total:' in line:
                                time_info = line.replace('⏱️ Tiempo estimado total:', '').strip()
                                formatted_content.append(f"""
                                <div style='background: #EDE9FE; border: 1px solid #8B5CF6; border-radius: 8px; 
                                     padding: 10px 15px; margin: 15px 0; text-align: center;'>
                                    <strong style='color: #6D28D9; font-size: 1.1em;'>⏱️ Tiempo Total: {time_info}</strong>
                                </div>""")
                                continue
                            
                            # 🎯 LÍNEAS NORMALES CON FORMATO MEJORADO
                            if line.startswith('**') and line.endswith('**'):
                                clean_line = line.replace('**', '')
                                formatted_content.append(f"<strong style='color: #1F2937; font-size: 1.05em;'>{clean_line}</strong>")
                            elif line.startswith('- '):
                                formatted_content.append(f"<div style='margin: 4px 0 4px 15px; color: #4B5563;'>• {line[2:]}</div>")
                            else:
                                formatted_content.append(f"<div style='color: #374151; line-height: 1.5;'>{line}</div>")
                        
                        # Cerrar tabla si quedó abierta
                        if in_table:
                            formatted_content.append("</table></div>")
                        
                        formatted_html = ''.join(formatted_content)
                        
                        st.markdown(f"""
                        <div style='display:flex; justify-content:flex-start; margin-bottom:16px;'>
                            <div class='chat-ai' style='max-width: 95%; background: white; border: 1px solid #E5E7EB; border-radius: 12px; box-shadow: 0 4px 25px rgba(0,0,0,0.1);'>
                                <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 12px 20px; border-radius: 12px 12px 0 0; font-weight: bold; text-align: center;'>
                                    🤖 ProFit Coach AI - ✨ Nueva Rutina Generada ✨
                                </div>
                                <div style='padding: 20px; line-height: 1.6; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;'>
                                    {formatted_html}
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Generar botón de descarga para rutina
                        excel_data, athlete_name = generate_routine_excel_from_chat(athlete_id, msg)
                        if excel_data:
                            col1, col2, col3 = st.columns([1, 2, 1])
                            with col2:
                                create_download_button(excel_data, athlete_name, "Rutina_Entrenamiento", unique_id=message_id)
                                st.markdown("""
                                <div style='text-align:center; margin:10px 0; padding:10px; background:#e8f5e8; border-radius:8px; color:#2d5a2d; font-size:0.9em;'>
                                    ✅ <strong>Rutina lista para descargar</strong><br>
                                    📁 Incluye: Días de entrenamiento y ejercicios detallados en Excel
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
                        
                        # 🎯 DETECCIÓN INTELIGENTE: Solo mostrar botones si es realmente una rutina completa
                        is_complete_routine = (
                            # Debe contener múltiples días Y ejercicios específicos
                            (ai_content.lower().count('día') >= 2 or ai_content.lower().count('sesión') >= 2) and
                            # Debe contener patrones de ejercicios
                            any(pattern in ai_content.lower() for pattern in [
                                'x', 'rep', 'series', 'ejercicio', 'bloque', 'calentamiento'
                            ]) and
                            # Debe ser suficientemente largo (rutina completa)
                            len(ai_content) > 500 and
                            # No debe ser solo una pregunta o respuesta corta
                            not any(question in ai_content.lower() for question in [
                                '¿qué te parece?', '¿alguna pregunta?', '¿necesitas algo más?', 
                                'cuéntame más', 'explícame', '¿cómo te sientes?'
                            ])
                        )
                        
                        if is_complete_routine:
                            excel_data, athlete_name = generate_routine_excel_from_chat(athlete_id, msg)
                            if excel_data:
                                col1, col2, col3 = st.columns([1, 2, 1])
                                with col2:
                                    st.markdown("---")
                                    st.markdown("**💡 ¿Quieres descargar esta rutina en Excel?**")
                                    # 🔄 SOLO mostrar botón de descarga (SIN email)
                                    create_download_button(excel_data, athlete_name, "Rutina_Entrenamiento", unique_id=f"{message_id}_alt")
        
        # Input del chat con adjuntar archivos integrado estilo ChatGPT
        
        # File uploader fuera del form para evitar conflictos
        attach_key = f"show_attach_{athlete_id}"
        uploaded_files = None
        
        # Mostrar file uploader si se activó
        if st.session_state.get(attach_key, False):
            st.markdown("**📎 Selecciona archivos para adjuntar**")
            uploaded_files = st.file_uploader(
                "Archivos",
                type=['pdf', 'jpg', 'jpeg', 'png', 'gif', 'xlsx', 'xls', 'docx', 'txt'],
                accept_multiple_files=True,
                key=f"file_uploader_{athlete_id}",
                label_visibility="collapsed"
            )
            
            # Mostrar preview de archivos seleccionados
            if uploaded_files:
                st.markdown("**📋 Archivos adjuntos:**")
                cols = st.columns(min(len(uploaded_files), 4))
                for idx, file in enumerate(uploaded_files):
                    with cols[idx % 4]:
                        file_size = len(file.getvalue()) / 1024  # KB
                        if file.type and file.type.startswith('image/'):
                            st.image(file, width=80)
                        st.caption(f"{file.name} ({file_size:.1f} KB)")
        
        # Formulario del chat
        with st.form("chat_input_form", clear_on_submit=True, border=False):
            # 3 columnas: input, enviar, adjuntar (REORDENADO)
            col_input, col_send, col_attach = st.columns([4.5, 1, 0.5])
            
            with col_input:
                # Placeholder dinámico según si hay archivos
                placeholder_text = "Escribe tu mensaje sobre los archivos adjuntos..." if uploaded_files else "Pregunta algo sobre entrenamiento"
                user_message = st.text_input(
                    "💬 Escribe tu mensaje...",
                    placeholder=placeholder_text,
                    label_visibility="collapsed",
                    key=f"chat_input_{athlete_id}"
                )
            
            with col_send:
                send_clicked = st.form_submit_button(
                    "🚀",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_attach:
                attach_clicked = st.form_submit_button(
                    "📎",
                    help="Adjuntar archivos",
                    type="secondary"
                )
            
            # Manejar clic en adjuntar archivos
            if attach_clicked:
                st.session_state[attach_key] = not st.session_state.get(attach_key, False)
                st.rerun()
            
            # Procesar el mensaje cuando se envía
            if send_clicked and (user_message.strip() or uploaded_files):
                # Preparar el mensaje con archivos adjuntos
                final_message = user_message.strip()
                
                # 🔧 ALMACENAR archivos en session_state para OpenAI
                if uploaded_files:
                    # Resetear los punteros de todos los archivos
                    for file in uploaded_files:
                        file.seek(0)
                    
                    # Guardar archivos en session_state para el chat_interface
                    st.session_state[f"uploaded_files_{athlete_id}"] = uploaded_files
                
                # Si hay archivos adjuntos, procesar su contenido para mostrar al usuario
                if uploaded_files:
                    file_contents = []
                    
                    for file in uploaded_files:
                        # Procesar cada archivo usando la función especializada
                        processed_content = process_uploaded_file(file)
                        file_contents.append(processed_content)
                    
                    # Agregar contenido de archivos al mensaje
                    if file_contents:
                        if final_message:
                            final_message = f"{final_message}\n\n[ARCHIVOS ADJUNTOS]\n" + "\n\n".join(file_contents)
                        else:
                            final_message = f"[ARCHIVOS ADJUNTOS]\n" + "\n\n".join(file_contents) + "\n\nAnaliza estos archivos y ayúdame con el entrenamiento."
                    
                    # Limpiar archivos adjuntos de la UI después del envío
                    st.session_state[attach_key] = False
                
                # Asegurar que el mensaje tenga contenido válido
                if not final_message.strip():
                    st.error("❌ Por favor escribe un mensaje o adjunta archivos")
                    return
                
                with st.spinner("🤖 Procesando mensaje..."):
                    response = handle_user_message(athlete_id, final_message)
                    if response:
                        # Limpiar archivos de session_state después del procesamiento
                        if f"uploaded_files_{athlete_id}" in st.session_state:
                            del st.session_state[f"uploaded_files_{athlete_id}"]
                        
                        # Mostrar confirmación especial si se envió email
                        if "✅" in response and "enviada exitosamente" in response:
                            st.success("📧 ¡Rutina enviada por email!")
                            st.balloons()
                        st.rerun()
                    else:
                        st.error("❌ Error al procesar el mensaje")
        
        # Información sobre el sistema de descarga y email automático
        with st.expander("📧 Sistema de Descarga y Email Automático", expanded=False):
            st.markdown("""
            **� Descarga de Rutinas:**
            - 📊 **Descarga Excel:** Botón automático en todas las rutinas generadas
            - 📋 **Formato Profesional:** Hojas separadas por bloque + seguimiento
            - 💾 **Archivo Completo:** Información del atleta y rutina detallada
            
            **📧 Envío Automático por Email (Solo mediante Chat):**
            - 🎯 Detecta automáticamente cuando solicitas envío por email en el chat
            - 📧 Envía la rutina al email configurado del atleta
            - 🔄 Si no hay email, te pide que lo proporciones
            - 💾 Guarda el email automáticamente para futuros envíos
            
            **📝 Ejemplos de Comandos para Email:**
            - "*Rutina de fútbol y envíala por email*"
            - "*Hazme un entrenamiento completo por mail*"
            - "*Mi email es juan@ejemplo.com, mándame una rutina*"
            - "*Circuito de fuerza por email*"
            
            **⚡ Proceso Simplificado:**
            1. 🗣 Solicitas rutina (aparece botón de descarga automáticamente)
            2. � **Opción 1:** Descargas Excel manualmente con el botón
            3. 📧 **Opción 2:** Solicitas envío por email mediante comando en chat
            4. ✅ Sistema procesa automáticamente según tu preferencia
            
            **🎯 Ventajas del Sistema:**
            - ✅ Interfaz más limpia (solo descarga visible)
            - ✅ Email automático mediante comandos naturales
            - ✅ Sin botones adicionales que compliquen la UI
            - ✅ Flexibilidad total según tus necesidades
            """)

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
            - 🎯 Posibilidad de elegir estructura tradicional o circuito integral
            
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
    # Debug temporal para Streamlit Cloud
    if st.sidebar.button("🔍 Debug Config"):
        st.sidebar.write("**Streamlit Environment:**")
        st.sidebar.write(f"- Has secrets: {hasattr(st, 'secrets')}")
        if hasattr(st, 'secrets'):
            st.sidebar.write(f"- Secrets keys: {list(st.secrets.keys())}")
            if 'openai' in st.secrets:
                api_key = st.secrets['openai'].get('api_key', '')
                st.sidebar.write(f"- API key length: {len(api_key)}")
                st.sidebar.write(f"- API key valid format: {'✅' if api_key and api_key.startswith('sk-') else '❌'}")
        
        st.sidebar.write("**Config Values:**")
        st.sidebar.write(f"- config.OPENAI_API_KEY: {'✅ SET' if config.OPENAI_API_KEY else '❌ NOT SET'}")
        st.sidebar.write(f"- config.OPENAI_ASSISTANT_ID: {'✅ SET' if config.OPENAI_ASSISTANT_ID else '❌ NOT SET'}")
    
    main()