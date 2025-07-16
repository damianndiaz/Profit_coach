# 📧 Configuración de Email - ProFit Coach

## 🎯 Funcionalidad
La aplicación ahora puede enviar automáticamente las rutinas de entrenamiento por email a los atletas con:
- ✅ **Diseño HTML profesional** con colores corporativos
- ✅ **Mensaje personalizado** para cada atleta
- ✅ **Archivo Excel adjunto** con la rutina completa
- ✅ **Verificación automática** del email del atleta
- ✅ **Solicitud de email** si no está registrado

## ⚙️ Configuración Rápida

### 1. Configurar Gmail (Recomendado)

1. **Activa la verificación en 2 pasos** en tu cuenta de Gmail
2. Ve a https://myaccount.google.com/apppasswords
3. **Genera una contraseña de aplicación** específica
4. Copia el archivo `.env.example` como `.env`
5. **Completa las variables**:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=tu_email@gmail.com
EMAIL_PASSWORD=tu_contraseña_de_aplicacion_de_16_caracteres
EMAIL_FROM_NAME=ProFit Coach
EMAIL_FROM_EMAIL=tu_email@gmail.com
```

### 2. Configurar Outlook/Hotmail

```env
EMAIL_HOST=smtp.live.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=tu_email@outlook.com
EMAIL_PASSWORD=tu_contraseña
EMAIL_FROM_NAME=ProFit Coach
EMAIL_FROM_EMAIL=tu_email@outlook.com
```

### 3. Alternativa con Streamlit Secrets

Crea un archivo `.streamlit/secrets.toml`:

```toml
[email]
host = "smtp.gmail.com"
port = 587
use_tls = true
username = "tu_email@gmail.com"
password = "tu_contraseña_de_aplicacion"
from_name = "ProFit Coach"
from_email = "tu_email@gmail.com"
```

## 🚀 Cómo Usar

### Para el Entrenador:
1. **Genera una rutina** con el AI Assistant
2. **Haz clic en "📧 Enviar por Email"**
3. **Verifica/ingresa el email** del atleta
4. **Envía** con un clic

### Para el Atleta:
- **Recibe email profesional** con:
  - Saludo personalizado
  - Instrucciones detalladas
  - Rutina en Excel adjunta
  - Consejos de entrenamiento

## 📋 Plantilla de Email

El email incluye:
- **Encabezado** con branding de ProFit Coach
- **Saludo personalizado** con el nombre del atleta
- **Instrucciones importantes** de entrenamiento
- **Motivación** y consejos profesionales
- **Archivo Excel** con la rutina completa

## 🔧 Solución de Problemas

### Error: "Autenticación fallida"
- ✅ Verifica que usas **contraseña de aplicación** (no la contraseña normal)
- ✅ Verifica que la **verificación en 2 pasos** está activada

### Error: "Email inválido"
- ✅ Verifica el formato del email del atleta
- ✅ Verifica tu configuración de email

### Error: "No se pueden obtener credenciales"
- ✅ Verifica que el archivo `.env` existe
- ✅ Verifica que las variables están bien escritas

## 🔐 Seguridad

- ✅ **Nunca compartas** tu contraseña de aplicación
- ✅ **Usa variables de entorno** para credenciales
- ✅ **No subas el archivo .env** a repositorios públicos
- ✅ **Rota las contraseñas** periódicamente

## 📱 Características Adicionales

- **Auto-actualización** del email en el perfil del atleta
- **Validación** de formato de email
- **Preview** del mensaje antes de enviar
- **Logs** detallados para troubleshooting
- **Interfaz intuitiva** en Streamlit
