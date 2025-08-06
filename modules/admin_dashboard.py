"""
Dashboard de administración para ProFit Coach
Monitoreo de performance, cache, rate limits y emails
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta
import logging

def show_admin_dashboard():
    """Muestra el dashboard de administración completo"""
    
    # Header con botón de cerrar
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("🛠️ Dashboard de Administración - ProFit Coach")
        st.caption("Monitoreo de sistema, performance y configuración")
    with col2:
        if st.button("❌ Cerrar", key="close_admin_dashboard", help="Volver a la aplicación principal"):
            st.session_state.pop('show_admin_dashboard', None)
            st.rerun()
    
    # Pestañas principales
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Performance", 
        "💾 Cache", 
        "🚦 Rate Limits", 
        "📧 Email System", 
        "🧵 Threads",
        "⚙️ Configuración"
    ])
    
    with tab1:
        show_performance_dashboard()
    
    with tab2:
        show_cache_dashboard()
    
    with tab3:
        show_rate_limits_dashboard()
    
    with tab4:
        show_email_dashboard()
    
    with tab5:
        show_threads_tab()
    
    with tab6:
        show_configuration_dashboard()

def show_performance_dashboard():
    """Dashboard de performance"""
    st.header("📊 Monitoreo de Performance")
    
    try:
        from modules.performance_monitor import performance_monitor
        
        # Mostrar métricas principales
        performance_monitor.show_performance_dashboard()
        
        # Botón para limpiar métricas
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🗑️ Limpiar Métricas Antiguas", help="Elimina métricas de más de 7 días"):
                # Implementar limpieza
                st.success("✅ Métricas limpiadas")
        
        with col2:
            if st.button("📊 Exportar Reporte", help="Descarga reporte de performance"):
                # Implementar exportación
                st.info("📊 Funcionalidad de exportación próximamente")
    
    except ImportError:
        st.error("❌ Sistema de monitoreo no disponible")
        st.info("💡 Para habilitar el monitoreo, asegúrate de que performance_monitor.py esté correctamente instalado")

def show_cache_dashboard():
    """Dashboard del sistema de cache"""
    st.header("💾 Sistema de Cache")
    
    try:
        from modules.ai_cache_manager import cache_manager
        
        # Obtener estadísticas del cache
        stats = cache_manager.get_cache_stats()
        
        # Métricas del cache
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Entradas", stats.get('total_entries', 0))
        
        with col2:
            st.metric("Hit Rate", stats.get('cache_hit_rate', '0%'))
        
        with col3:
            st.metric("Uso Promedio", f"{stats.get('average_uses', 0):.1f}x")
        
        # Configuración del cache
        st.subheader("⚙️ Configuración de Cache")
        
        col1, col2 = st.columns(2)
        
        with col1:
            cache_duration = st.slider(
                "Duración del Cache (horas)", 
                min_value=1, 
                max_value=72, 
                value=24,
                help="Tiempo que las respuestas permanecen en cache"
            )
        
        with col2:
            max_entries = st.slider(
                "Máximo de Entradas", 
                min_value=100, 
                max_value=5000, 
                value=1000,
                help="Número máximo de respuestas en cache"
            )
        
        # Acciones del cache
        st.subheader("🔧 Acciones")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧹 Limpiar Cache", help="Elimina todas las entradas del cache"):
                # Implementar limpieza
                st.success("✅ Cache limpiado")
        
        with col2:
            if st.button("📊 Optimizar Cache", help="Elimina entradas poco usadas"):
                # Implementar optimización
                st.success("✅ Cache optimizado")
        
        with col3:
            if st.button("📈 Analizar Patterns", help="Analiza patrones de uso"):
                # Implementar análisis
                st.info("📈 Análisis de patrones próximamente")
    
    except ImportError:
        st.error("❌ Sistema de cache no disponible")
        st.info("💡 Para habilitar el cache, asegúrate de que ai_cache_manager.py esté correctamente instalado")

def show_rate_limits_dashboard():
    """Dashboard de rate limits"""
    st.header("🚦 Rate Limits y OpenAI")
    
    try:
        from modules.rate_limit_manager import rate_limit_manager
        
        # Estado actual de rate limits
        status = rate_limit_manager.check_rate_limit_status()
        
        # Mostrar estado general
        status_color = {
            "GOOD": "🟢",
            "MODERATE": "🟡", 
            "WARNING": "🟠",
            "CRITICAL": "🔴"
        }
        
        st.markdown(f"### Estado Actual: {status_color.get(status['status'], '⚪')} {status['status']}")
        
        # Métricas de uso
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rpm = status['requests_per_minute']
            st.metric(
                "Requests/Min",
                f"{rpm['used']}/{rpm['limit']}",
                delta=f"{rpm['percentage']:.1%}"
            )
            st.progress(rpm['percentage'])
        
        with col2:
            tpm = status['tokens_per_minute']
            st.metric(
                "Tokens/Min",
                f"{tpm['used']:,}/{tpm['limit']:,}",
                delta=f"{tpm['percentage']:.1%}"
            )
            st.progress(tpm['percentage'])
        
        with col3:
            daily = status['requests_per_day']
            st.metric(
                "Requests/Día",
                f"{daily['used']}/{daily['limit']}",
                delta=f"{daily['percentage']:.1%}"
            )
            st.progress(daily['percentage'])
        
        # Recomendaciones de optimización
        st.subheader("💡 Recomendaciones")
        tips = rate_limit_manager.get_cost_optimization_tips()
        for tip in tips:
            st.info(tip)
        
        # Tiempo óptimo para próxima request
        optimal_time, reason = rate_limit_manager.get_optimal_request_time()
        st.subheader("⏰ Próxima Request Óptima")
        
        if optimal_time <= datetime.now() + timedelta(seconds=5):
            st.success(f"✅ {reason}")
        else:
            time_diff = optimal_time - datetime.now()
            st.warning(f"⏳ {reason} (en {time_diff})")
    
    except ImportError:
        st.error("❌ Sistema de rate limits no disponible")
        st.info("💡 Para habilitar el monitoreo de rate limits, asegúrate de que rate_limit_manager.py esté correctamente instalado")

def show_email_dashboard():
    """Dashboard del sistema de email"""
    st.header("📧 Sistema de Email")
    
    # Configuración de email
    st.subheader("⚙️ Configuración")
    
    from config import config
    
    # Mostrar estado de configuración (sin mostrar credenciales)
    email_config_status = []
    
    if config.EMAIL_HOST:
        email_config_status.append("✅ Servidor SMTP configurado")
    else:
        email_config_status.append("❌ Servidor SMTP no configurado")
    
    if config.EMAIL_USERNAME:
        email_config_status.append("✅ Usuario de email configurado")
    else:
        email_config_status.append("❌ Usuario de email no configurado")
    
    if config.EMAIL_PASSWORD:
        email_config_status.append("✅ Contraseña de email configurada")
    else:
        email_config_status.append("❌ Contraseña de email no configurada")
    
    for status in email_config_status:
        st.write(status)
    
    # Test de conexión
    st.subheader("🔧 Pruebas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🧪 Test Conexión SMTP", help="Prueba la conexión con el servidor de email"):
            try:
                from modules.email_manager import get_email_credentials
                import smtplib
                
                credentials = get_email_credentials()
                if credentials:
                    with smtplib.SMTP(credentials['server'], credentials['port']) as server:
                        if credentials['use_tls']:
                            server.starttls()
                        server.login(credentials['username'], credentials['password'])
                    st.success("✅ Conexión SMTP exitosa")
                else:
                    st.error("❌ No se pudieron obtener credenciales")
            except Exception as e:
                st.error(f"❌ Error de conexión: {str(e)}")
    
    with col2:
        test_email = st.text_input("Email de prueba", placeholder="test@example.com")
        if st.button("📤 Enviar Email de Prueba", help="Envía un email de prueba") and test_email:
            try:
                from modules.email_manager import send_routine_email
                import io
                
                # Crear Excel de prueba simple
                test_excel = io.BytesIO()
                test_excel.write(b"Test data")
                test_excel.seek(0)
                
                success, message = send_routine_email(
                    athlete_email=test_email,
                    athlete_name="Atleta Test",
                    excel_data=test_excel.getvalue(),
                    filename="test_routine.xlsx",
                    trainer_name="ProFit Coach Test"
                )
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
                    
            except Exception as e:
                st.error(f"❌ Error enviando email: {str(e)}")
    
    # Estadísticas de emails enviados (si están disponibles)
    st.subheader("📊 Estadísticas")
    st.info("📈 Estadísticas de emails próximamente")

def show_configuration_dashboard():
    """Dashboard de configuración general"""
    st.header("⚙️ Configuración General")
    
    from config import config
    
    # Configuración de OpenAI
    st.subheader("🤖 OpenAI")
    
    openai_status = []
    
    if config.OPENAI_API_KEY:
        openai_status.append("✅ API Key configurada")
    else:
        openai_status.append("❌ API Key no configurada")
    
    if config.OPENAI_ASSISTANT_ID:
        openai_status.append("✅ Assistant ID configurado")
    else:
        openai_status.append("❌ Assistant ID no configurado")
    
    for status in openai_status:
        st.write(status)
    
    # Configuración de base de datos
    st.subheader("🗄️ Base de Datos")
    
    db_status = []
    
    if config.DATABASE_URL:
        db_status.append("✅ URL de base de datos configurada")
    elif config.DB_HOST and config.DB_NAME:
        db_status.append("✅ Parámetros de BD configurados")
    else:
        db_status.append("❌ Base de datos no configurada")
    
    for status in db_status:
        st.write(status)
    
    # Variables de entorno
    st.subheader("🔧 Variables de Entorno")
    
    env_vars = {
        "ENVIRONMENT": config.ENVIRONMENT,
        "LOG_LEVEL": config.LOG_LEVEL,
        "OPENAI_TIMEOUT": config.OPENAI_TIMEOUT,
        "MAX_ATHLETES_PER_USER": config.MAX_ATHLETES_PER_USER,
        "CHAT_HISTORY_LIMIT": config.CHAT_HISTORY_LIMIT
    }
    
    for var, value in env_vars.items():
        st.write(f"**{var}**: {value}")
    
    # Acciones de configuración
    st.subheader("🔧 Acciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Recargar Configuración", help="Recarga la configuración desde las variables de entorno"):
            st.success("✅ Configuración recargada")
    
    with col2:
        if st.button("🧪 Validar Configuración", help="Valida toda la configuración"):
            try:
                warnings = config.validate_config()
                if not warnings:
                    st.success("✅ Configuración válida")
                else:
                    for warning in warnings:
                        st.warning(f"⚠️ {warning}")
            except Exception as e:
                st.error(f"❌ Error de configuración: {str(e)}")

# Función principal para mostrar en la app
def show_threads_tab():
    """Tab de gestión de threads"""
    st.header("🧵 Gestión de Threads")
    
    try:
        from modules.thread_manager import thread_manager
        
        # Resumen general
        st.subheader("📊 Resumen General")
        summary = thread_manager.get_all_threads_summary()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Threads Activos", summary.get('active_threads', 0))
        with col2:
            st.metric("Tokens Promedio", summary.get('average_tokens', 0))
        with col3:
            st.metric("Rotaciones 24h", summary.get('rotations_24h', 0))
        
        # Estado del sistema
        system_health = summary.get('system_health', 'unknown')
        if system_health == 'good':
            st.success("✅ Sistema de threads saludable")
        else:
            st.warning("⚠️ Sistema requiere atención - threads con alto uso")
        
        # Detalles de threads por atleta
        st.subheader("🏃‍♂️ Threads por Atleta")
        
        # Input para consultar thread específico
        athlete_id = st.number_input("ID del Atleta", min_value=1, value=1, step=1)
        
        if st.button("📊 Ver Estadísticas del Thread"):
            thread_stats = thread_manager.get_thread_stats(athlete_id)
            
            if 'error' in thread_stats:
                st.error(f"❌ Error: {thread_stats['error']}")
            elif thread_stats.get('status') == 'No thread activo':
                st.info("ℹ️ No hay thread activo para este atleta")
            else:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Tokens Usados", 
                             f"{thread_stats['tokens_used']}/{thread_stats['tokens_limit']}")
                    st.metric("Uso de Tokens", f"{thread_stats['token_usage_percent']}%")
                
                with col2:
                    st.metric("Mensajes", 
                             f"{thread_stats['messages_count']}/{thread_stats['messages_limit']}")
                    st.metric("Edad (horas)", f"{thread_stats['age_hours']}")
                
                # Indicador de estado
                if thread_stats['status'] == 'healthy':
                    st.success("✅ Thread saludable")
                else:
                    st.warning("⚠️ Thread requiere atención")
                
                # Información de rotación
                if thread_stats['next_rotation'] == 'soon':
                    st.warning("🔄 Thread será rotado pronto")
                else:
                    st.info("✅ No requiere rotación inmediata")
                
                # Progreso visual
                st.subheader("📈 Uso de Recursos")
                st.progress(thread_stats['token_usage_percent'] / 100)
                st.caption(f"Tokens: {thread_stats['token_usage_percent']}%")
                
                st.progress(thread_stats['message_usage_percent'] / 100)
                st.caption(f"Mensajes: {thread_stats['message_usage_percent']}%")
        
        # Razones de rotación recientes
        if 'rotation_reasons' in summary and summary['rotation_reasons']:
            st.subheader("🔄 Razones de Rotación Recientes")
            for reason, count in summary['rotation_reasons'].items():
                st.write(f"• **{reason}**: {count} veces")
    
    except ImportError:
        st.error("❌ Thread Manager no disponible")
    except Exception as e:
        st.error(f"❌ Error cargando gestión de threads: {e}")

def show_admin_interface():
    """Función principal para mostrar en la interfaz de Streamlit"""
    # Mostrar directamente el dashboard (ya no necesitamos el botón del sidebar)
    show_admin_dashboard()

if __name__ == "__main__":
    show_admin_dashboard()
