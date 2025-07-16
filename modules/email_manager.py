"""
Módulo para envío de emails con rutinas de entrenamiento
Incluye configuración SMTP y plantillas de mensajes
"""

import smtplib
import logging
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import io
from config import Config

def get_email_credentials():
    """Obtiene las credenciales de email desde configuración"""
    try:
        # Intentar obtener desde secrets de Streamlit primero
        if hasattr(st, 'secrets') and 'email' in st.secrets:
            return {
                'server': st.secrets.email.get('host', Config.EMAIL_HOST),
                'port': int(st.secrets.email.get('port', Config.EMAIL_PORT)),
                'use_tls': st.secrets.email.get('use_tls', Config.EMAIL_USE_TLS),
                'username': st.secrets.email.username,
                'password': st.secrets.email.password,
                'from_name': st.secrets.email.get('from_name', Config.EMAIL_FROM_NAME),
                'from_email': st.secrets.email.get('from_email', st.secrets.email.username)
            }
        else:
            # Usar configuración del archivo config.py
            return {
                'server': Config.EMAIL_HOST,
                'port': Config.EMAIL_PORT,
                'use_tls': Config.EMAIL_USE_TLS,
                'username': Config.EMAIL_USERNAME,
                'password': Config.EMAIL_PASSWORD,
                'from_name': Config.EMAIL_FROM_NAME,
                'from_email': Config.EMAIL_FROM_EMAIL or Config.EMAIL_USERNAME
            }
    except Exception as e:
        logging.error(f"Error al obtener credenciales de email: {e}")
        return None

def create_email_template(athlete_name, trainer_name="ProFit Coach"):
    """Crea el template HTML para el email"""
    template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                margin: 0;
                padding: 20px;
            }}
            .header {{
                background-color: #366092;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 8px 8px 0 0;
            }}
            .content {{
                background-color: #f9f9f9;
                padding: 30px;
                border-radius: 0 0 8px 8px;
                border: 1px solid #ddd;
            }}
            .footer {{
                margin-top: 20px;
                padding: 15px;
                background-color: #366092;
                color: white;
                text-align: center;
                border-radius: 5px;
                font-size: 14px;
            }}
            .highlight {{
                background-color: #5B9BD5;
                color: white;
                padding: 10px;
                border-radius: 5px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🏋️‍♂️ {trainer_name}</h1>
            <h2>Plan de Entrenamiento Personalizado</h2>
        </div>
        
        <div class="content">
            <h3>¡Hola {athlete_name}! 👋</h3>
            
            <p>Espero que te encuentres muy bien. Te envío tu <strong>plan de entrenamiento personalizado</strong> que hemos diseñado especialmente para ti.</p>
            
            <div class="highlight">
                <h4>📋 ¿Qué encontrarás en tu rutina?</h4>
                <ul>
                    <li>✅ Ejercicios específicos para tu nivel y deporte</li>
                    <li>✅ Series y repeticiones detalladas</li>
                    <li>✅ Espacio para anotar las cargas utilizadas</li>
                    <li>✅ Notas importantes para cada ejercicio</li>
                </ul>
            </div>
            
            <h4>📝 Instrucciones importantes:</h4>
            <ul>
                <li><strong>Calentamiento:</strong> Siempre realiza un calentamiento adecuado antes de comenzar</li>
                <li><strong>Técnica:</strong> Prioriza siempre la técnica correcta sobre la carga</li>
                <li><strong>Progresión:</strong> Aumenta las cargas gradualmente según te sientas cómodo/a</li>
                <li><strong>Descanso:</strong> Respeta los tiempos de descanso entre series</li>
                <li><strong>Comunicación:</strong> Cualquier duda o molestia, no dudes en consultarme</li>
            </ul>
            
            <p><strong>💪 Recuerda:</strong> La constancia y la paciencia son claves para alcanzar tus objetivos. ¡Confío en que vas a lograr resultados excelentes!</p>
            
            <p>Si tienes alguna pregunta sobre los ejercicios o necesitas modificar algo, por favor escríbeme.</p>
            
            <p>¡Que tengas excelentes entrenamientos! 🚀</p>
            
            <p>Saludos cordiales,<br>
            <strong>{trainer_name}</strong></p>
        </div>
        
        <div class="footer">
            <p>📧 Este email contiene tu plan de entrenamiento personalizado</p>
            <p>📅 Generado el {datetime.now().strftime("%d/%m/%Y a las %H:%M")}</p>
        </div>
    </body>
    </html>
    """
    return template

def send_routine_email(athlete_email, athlete_name, excel_data, filename, trainer_name="ProFit Coach"):
    """Envía el email con la rutina en Excel adjunta"""
    try:
        # Obtener credenciales
        credentials = get_email_credentials()
        if not credentials:
            return False, "No se pudieron obtener las credenciales de email"
        
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['From'] = f"{credentials['from_name']} <{credentials['from_email']}>"
        msg['To'] = athlete_email
        msg['Subject'] = f"🏋️‍♂️ Tu Plan de Entrenamiento Personalizado - {athlete_name}"
        
        # Crear contenido HTML
        html_content = create_email_template(athlete_name, trainer_name)
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Adjuntar Excel
        if excel_data:
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(excel_data)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )
            msg.attach(attachment)
        
        # Enviar email
        with smtplib.SMTP(credentials['server'], credentials['port']) as server:
            if credentials['use_tls']:
                server.starttls()
            server.login(credentials['username'], credentials['password'])
            server.send_message(msg)
            
        logging.info(f"Email enviado exitosamente a {athlete_email}")
        return True, "Email enviado exitosamente"
        
    except smtplib.SMTPAuthenticationError:
        error_msg = "Error de autenticación: verifica las credenciales de email"
        logging.error(error_msg)
        return False, error_msg
    except smtplib.SMTPRecipientsRefused:
        error_msg = f"Email del destinatario inválido: {athlete_email}"
        logging.error(error_msg)
        return False, error_msg
    except smtplib.SMTPException as e:
        error_msg = f"Error SMTP: {str(e)}"
        logging.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Error inesperado al enviar email: {str(e)}"
        logging.error(error_msg)
        return False, error_msg

def validate_email_address(email):
    """Valida formato de email"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def show_email_sending_interface(athlete_data, excel_data, filename):
    """Muestra la interfaz para enviar email en Streamlit"""
    try:
        athlete_email = athlete_data.get('email', '').strip()
        athlete_name = athlete_data.get('name', '')
        
        st.subheader("📧 Enviar Rutina por Email")
        
        # Si no hay email, solicitar uno
        if not athlete_email:
            st.warning("⚠️ No se encontró email registrado para este atleta")
            athlete_email = st.text_input(
                "📧 Ingresa el email del atleta:",
                placeholder="atleta@email.com",
                key="email_input"
            )
        else:
            st.success(f"✅ Email registrado: {athlete_email}")
            # Opción para cambiar email
            if st.checkbox("📝 Usar un email diferente"):
                athlete_email = st.text_input(
                    "📧 Nuevo email:",
                    value=athlete_email,
                    key="email_change"
                )
        
        # Mostrar preview del mensaje
        if st.checkbox("👀 Ver preview del mensaje"):
            st.markdown("### 📋 Vista previa del email:")
            preview_html = create_email_template(athlete_name)
            st.components.v1.html(preview_html, height=600, scrolling=True)
        
        # Botón para enviar
        if athlete_email and validate_email_address(athlete_email):
            if st.button("📤 Enviar Rutina por Email", type="primary", use_container_width=True):
                with st.spinner("Enviando email..."):
                    success, message = send_routine_email(
                        athlete_email, 
                        athlete_name, 
                        excel_data, 
                        filename
                    )
                    
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        
                        # Actualizar email en la base de datos si es diferente
                        if athlete_email != athlete_data.get('email', ''):
                            update_athlete_email(athlete_data['id'], athlete_email)
                            st.info("📝 Email actualizado en el perfil del atleta")
                    else:
                        st.error(f"❌ {message}")
        elif athlete_email:
            st.error("❌ El formato del email no es válido")
        
    except Exception as e:
        st.error(f"Error en la interfaz de email: {e}")
        logging.error(f"Error en show_email_sending_interface: {e}")

def update_athlete_email(athlete_id, new_email):
    """Actualiza el email del atleta en la base de datos"""
    try:
        from auth.database import get_db_cursor
        
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE athletes SET email = %s, updated_at = CURRENT_TIMESTAMP WHERE id = %s",
                (new_email, athlete_id)
            )
        
        logging.info(f"Email actualizado para atleta {athlete_id}: {new_email}")
        return True
        
    except Exception as e:
        logging.error(f"Error al actualizar email del atleta: {e}")
        return False
