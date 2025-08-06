# ProFit Coach - Sistema de Entrenamiento Personalizado

Una aplicación de coaching deportivo con IA que utiliza la metodología de 5 bloques para crear rutinas de entrenamiento personalizadas.

## 🚀 Funcionalidades

- **Sistema de Usuarios**: Autenticación segura con bcrypt
- **Gestión de Atletas**: Crear y administrar atletas con información deportiva
- **IA Personalizada**: Generación de rutinas usando OpenAI GPT con metodología especializada
- **Exportación Excel**: Descarga automática de rutinas en formato profesional
- **Envío por Email**: Sistema automatizado de envío de rutinas por correo
- **Chat Inteligente**: Interfaz conversacional para interacción natural

## 🏗️ Arquitectura

- **Frontend**: Streamlit
- **Backend**: Python con PostgreSQL (Supabase)
- **IA**: OpenAI GPT Assistant con prompts especializados
- **Base de Datos**: PostgreSQL con autenticación bcrypt

## 🔧 Deployment en Streamlit Cloud

### Secrets Requeridos

Configura los siguientes secrets en Streamlit Cloud:

```toml
[database]
url = "postgresql://user:password@host:port/database"

[openai]
api_key = "tu-openai-api-key"
assistant_id = "tu-assistant-id"

[email]
host = "smtp.gmail.com"
port = 587
use_tls = true
username = "tu-email@gmail.com"
password = "tu-app-password"
from_name = "ProFit Coach"
from_email = "tu-email@gmail.com"
```

### Variables de Entorno (Desarrollo Local)

Para desarrollo local, crea un archivo `.env`:

```env
# Database
DATABASE_URL=postgresql://user:password@host:port/database

# OpenAI
OPENAI_API_KEY=tu-openai-api-key
OPENAI_ASSISTANT_ID=tu-assistant-id

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=tu-email@gmail.com
EMAIL_PASSWORD=tu-app-password
EMAIL_FROM_NAME=ProFit Coach
EMAIL_FROM_EMAIL=tu-email@gmail.com
```

## 📦 Dependencias

Ver `requirements.txt` para la lista completa de dependencias.

## 🏃‍♂️ Cómo usar

1. **Registro/Login**: Crea una cuenta o inicia sesión
2. **Crear Atleta**: Añade información del atleta (nombre, deporte, nivel)
3. **Chat con IA**: Pide rutinas específicas usando lenguaje natural
4. **Exportar**: Descarga rutinas en Excel o envía por email

## 🎯 Metodología de 5 Bloques

1. **🍑 Activación Glútea**: Preparación neuromuscular
2. **⚡ Dinámico/Potencia**: Movimientos explosivos + zona media
3. **💪 Fuerza 1**: Patrones fundamentales + unilateral
4. **🔥 Fuerza 2**: Movimientos complejos + rotacionales
5. **🚀 Contraste/Preventivos**: Velocidad + prevención

## 📧 Comandos de Email

La IA detecta automáticamente comandos como:
- "envía por email"
- "manda por correo"
- "email me la rutina"

## 🔒 Seguridad

- Autenticación con bcrypt
- SSL para conexiones de base de datos
- Secrets management para credenciales
- Validación de entrada de usuarios

## 🌟 Características Avanzadas

- **Detección automática de comandos**
- **Generación de rutinas no repetitivas**
- **Adaptación por deporte y nivel**
- **Interfaz responsive**
- **Manejo robusto de errores**

---

Desarrollado con ❤️ para entrenadores y atletas
