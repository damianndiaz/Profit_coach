# 🏃‍♂️ ProFit Coach

## Aplicación de Entrenamiento Inteligente para Atletas

ProFit Coach es una aplicación web desarrollada en Streamlit que permite a entrenadores gestionar atletas y proporcionar asesoramiento personalizado mediante IA.

## 🚀 Características Principales

- **Gestión de Atletas**: Agregar, editar y eliminar atletas
- **Chat Inteligente**: Conversaciones personalizadas con IA especializada en entrenamiento
- **Interfaz Moderna**: UI/UX optimizada y responsive
- **Manejo Robusto de Errores**: Sistema de logging y recuperación de errores
- **Base de Datos Segura**: Pool de conexiones y transacciones seguras
- **Validaciones Completas**: Validación de datos en tiempo real

## 🛠️ Tecnologías Utilizadas

- **Frontend**: Streamlit
- **Backend**: Python
- **Base de Datos**: PostgreSQL
- **IA**: OpenAI GPT (Assistant API)
- **Autenticación**: bcrypt
- **Email**: yagmail

## 📋 Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Cuenta de OpenAI con API Key
- Cuenta de email para notificaciones (opcional)

## 🔧 Instalación

### 1. Clonar y Configurar

```bash
# Clonar el repositorio (o descargar los archivos)
cd "ProFit Coach"

# Instalar dependencias
pip install -r requirements_fixed.txt
```

### 2. Configurar Variables de Entorno

Crear un archivo `.env` con:

```env
# Base de datos
DB_HOST=localhost
DB_PORT=5432
DB_NAME=profit_coach
DB_USER=postgres
DB_PASSWORD=tu_password

# OpenAI
OPENAI_API_KEY=tu_openai_api_key
OPENAI_ASSISTANT_ID=tu_assistant_id

# Email (opcional)
EMAIL_USER=tu_email@gmail.com
EMAIL_PASS=tu_app_password

# Configuración opcional
MAX_ATHLETES_PER_USER=50
CHAT_HISTORY_LIMIT=50
ENVIRONMENT=development
```

### 3. Configurar Base de Datos

```sql
-- Crear base de datos
CREATE DATABASE profit_coach;

-- El script creará las tablas automáticamente
```

### 4. Verificar Instalación

```bash
# Ejecutar verificador de configuración
python setup_checker.py
```

## 🚀 Uso

### Iniciar la Aplicación

```bash
# Versión mejorada (recomendada)
streamlit run main_improved.py

# Versión original (con mejoras básicas)
streamlit run main.py
```

### Primer Uso

1. **Ejecutar verificador**: `python setup_checker.py`
2. **Crear datos de ejemplo** cuando se solicite
3. **Abrir navegador** en `http://localhost:8501`
4. **Iniciar sesión** con `admin` / `admin123` (si se crearon datos de ejemplo)

## 📊 Estructura del Proyecto

```
ProFit Coach/
├── main.py                    # Aplicación principal (versión mejorada)
├── main_improved.py           # Aplicación principal (versión completa)
├── setup_checker.py           # Verificador de configuración
├── config.py                  # Configuraciones
├── requirements_fixed.txt     # Dependencias corregidas
├── .env                      # Variables de entorno
├── auth/
│   ├── auth_utils.py         # Utilidades de autenticación
│   └── database.py           # Conexión a base de datos
├── modules/
│   ├── athlete_manager.py    # Gestión de atletas
│   ├── chat_interface.py     # Interfaz de chat
│   ├── chat_manager.py       # Gestión de sesiones de chat
│   └── export_utils.py       # Utilidades de exportación
└── utils/
    └── app_utils.py          # Utilidades generales
```

## 🔧 Configuración Avanzada

### OpenAI Assistant

1. Crear un Assistant en [OpenAI Platform](https://platform.openai.com/assistants)
2. Configurar el prompt del Assistant:

```
Eres ProFit Coach AI, un entrenador deportivo especializado.

INSTRUCCIONES:
- Proporciona consejos específicos y personalizados
- Mantén un tono profesional pero amigable
- Si generas rutinas, márcalas con [INICIO_NUEVA_RUTINA] al inicio
- Incluye aspectos de seguridad cuando sea relevante
- Responde en español
- Limita respuestas a 500 palabras máximo

ESPECIALIDADES:
- Planes de entrenamiento personalizados
- Nutrición deportiva
- Técnicas de recuperación
- Prevención de lesiones
- Motivación y psicología deportiva
```

3. Copiar el Assistant ID al archivo `.env`

### Configuración de Producción

```env
ENVIRONMENT=production
LOG_LEVEL=WARNING
MAX_ATHLETES_PER_USER=30
CHAT_HISTORY_LIMIT=30
SESSION_TIMEOUT_DAYS=7
```

## 🐛 Solución de Problemas

### Error de Conexión a Base de Datos

```bash
# Verificar que PostgreSQL esté corriendo
sudo service postgresql status

# Verificar conexión
python setup_checker.py
```

### Error de OpenAI API

```bash
# Verificar API Key
echo $OPENAI_API_KEY

# Verificar límites de uso en OpenAI Platform
```

### Problemas de Dependencias

```bash
# Reinstalar dependencias
pip install -r requirements_fixed.txt --force-reinstall

# Verificar versiones
pip list | grep -E "(streamlit|psycopg2|openai)"
```

## 📝 Logs y Debugging

- **Logs de aplicación**: `profit_coach.log`
- **Logs de setup**: `setup.log`
- **Nivel de log**: Configurable via `LOG_LEVEL` en `.env`

```bash
# Ver logs en tiempo real
tail -f profit_coach.log
```

## 🔒 Seguridad

- **Contraseñas hasheadas** con bcrypt
- **Validación de entrada** en todos los formularios
- **Pool de conexiones** para prevenir ataques de conexión
- **Sanitización de datos** antes de guardar en BD
- **Timeouts configurables** para prevenir bloqueos

## 🚀 Mejoras Implementadas

### Versión Original vs Mejorada

| Característica | Original | Mejorada |
|---|---|---|
| Manejo de errores | ❌ Básico | ✅ Robusto |
| Validación de datos | ❌ Mínima | ✅ Completa |
| Pool de conexiones | ❌ No | ✅ Sí |
| Logging | ❌ No | ✅ Completo |
| UX/UI | ⚠️ Básica | ✅ Moderna |
| Reintentos automáticos | ❌ No | ✅ Sí |
| Configuración centralizada | ❌ No | ✅ Sí |
| Verificador de setup | ❌ No | ✅ Sí |

### Funcionalidades Agregadas

- **Sistema de reintentos** para operaciones fallidas
- **Validación en tiempo real** de formularios
- **Mensajes de error específicos** y amigables
- **Indicadores de estado** visual
- **Timeouts configurables** para OpenAI
- **Limpieza automática** de sesiones antiguas
- **Exportación de chat** a texto
- **Estadísticas de uso** por atleta

## 📞 Soporte

Para reportar problemas o solicitar funcionalidades:

1. **Verificar logs**: Revisar `profit_coach.log` para errores
2. **Ejecutar verificador**: `python setup_checker.py`
3. **Documentar el problema**: Incluir logs y pasos para reproducir
4. **Contactar al administrador**: Con detalles del entorno

## 📄 Licencia

Este proyecto es privado y confidencial. Todos los derechos reservados.

---

**Desarrollado con ❤️ para mejorar el entrenamiento deportivo**
