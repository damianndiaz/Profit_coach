# 🏃‍♂️ ProFit Coach - AI-Powered Training Coach

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Descripción

**ProFit Coach** es una aplicación web inteligente de coaching deportivo que utiliza IA para generar rutinas de entrenamiento personalizadas. Implementa una metodología innovadora de **5 Bloques Especializados** adaptada a cada deporte, nivel y objetivos específicos del atleta.

## ✨ Características Principales

### 🤖 IA Especializada
- **OpenAI Assistant** entrenado específicamente en metodologías deportivas
- **Detección automática de comandos** (ej: "envíalo por email")
- **Generación de rutinas sin repetición** usando historial inteligente
- **Adaptación por deporte y nivel** (Principiante → Élite)

### 📊 Gestión Integral
- **Dashboard de atletas** con información completa
- **Chat inteligente** con historial persistente
- **Exportación automática a Excel** con formato profesional
- **Sistema de email** integrado para envío de rutinas

### 🏋️‍♂️ Metodología Única - 5 Bloques
1. **🍑 Activación Glútea:** Preparación específica del complejo glúteo
2. **⚡ Dinámico/Potencia:** Entrenamiento explosivo y zona media
3. **💪 Fuerza 1:** Patrones fundamentales (empuje, tracción, unilateral)
4. **🔥 Fuerza 2:** Movimientos complejos y alta transferencia
5. **🛡️ Contraste/Preventivos:** Velocidad, prevención y RSA

### 🔄 Flexibilidad Total
- **Sin tiempos fijos** - Adaptación completa a necesidades
- **Alternativa de Circuito Integral** (6 ejercicios x 5 series)
- **Variabilidad infinita** - nunca se repiten rutinas idénticas

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.9+
- PostgreSQL (local o en la nube)
- Cuenta de OpenAI con API Key
- Cuenta de Gmail para envío de emails (opcional)

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/profit-coach.git
cd profit-coach
```

### 2. Configurar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```env
# Base de Datos PostgreSQL
DATABASE_URL=postgresql://usuario:contraseña@host:puerto/database

# OpenAI Configuration
OPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
OPENAI_ASSISTANT_ID=asst_XXXXXXXXXXXXXXXXXXXXXXXX

# Email Configuration (Opcional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USERNAME=tu_email@gmail.com
EMAIL_PASSWORD=tu_app_password_de_16_caracteres
EMAIL_FROM_NAME=ProFit Coach
EMAIL_FROM_EMAIL=tu_email@gmail.com
```

### 5. Inicializar Base de Datos
```bash
python migrate_database.py
```

### 6. Ejecutar la Aplicación
```bash
streamlit run main.py
```

## 🌐 Despliegue en Streamlit Community Cloud

### Configuración de Secretos
En Streamlit Community Cloud, configura los siguientes secretos:

```toml
[database]
url = "postgresql://usuario:contraseña@host:puerto/database"

[openai]
api_key = "tu_api_key"
assistant_id = "tu_assistant_id"

[email]
host = "smtp.gmail.com"
port = 587
use_tls = true
username = "tu_email@gmail.com"
password = "tu_app_password"
from_name = "ProFit Coach"
from_email = "tu_email@gmail.com"
```

## 🎯 Guía de Uso

### 1. **Registro y Login**
- Crear cuenta nueva o iniciar sesión
- Sistema de autenticación seguro con hash de contraseñas

### 2. **Gestión de Atletas**
- ➕ **Agregar atletas** con información completa
- ✏️ **Editar perfiles** incluyendo email para notificaciones
- 🗑️ **Eliminar atletas** con confirmación de seguridad

### 3. **Chat Inteligente**
- 💬 **Conversación natural** con la IA especializada
- 🎯 **Solicitudes específicas** adaptadas a cada deporte
- 📧 **Comandos de email** automáticos ("envíalo por mail")

### 4. **Ejemplos de Consultas Optimizadas**
```
✅ "Rutina completa de 5 bloques para fútbol"
✅ "Solo activación glútea para prevenir lesiones"
✅ "Circuito integral de 6 ejercicios para rugby"
✅ "Bloque de potencia explosiva para tenis"
✅ "Envía la rutina por email a atleta@gmail.com"
```

## 🔧 Estructura del Proyecto

```
profit-coach/
├── 📁 auth/                    # Autenticación y base de datos
│   ├── auth_utils.py          # Utilidades de autenticación
│   └── database.py            # Conexión y gestión de BD
├── 📁 modules/                # Módulos principales
│   ├── athlete_manager.py     # Gestión de atletas
│   ├── chat_interface.py      # Interfaz de chat con IA
│   ├── chat_manager.py        # Gestión de sesiones de chat
│   ├── email_manager.py       # Sistema de envío de emails
│   ├── routine_export.py      # Exportación a Excel
│   └── training_variations.py # Metodologías de entrenamiento
├── 📁 utils/                  # Utilidades generales
│   └── app_utils.py          # Funciones auxiliares
├── 📄 main.py                 # Aplicación principal
├── 📄 config.py              # Configuración central
├── 📄 requirements.txt       # Dependencias Python
└── 📄 .env                   # Variables de entorno (no incluido)
```

## 🔒 Seguridad y Mejores Prácticas

### 🛡️ Autenticación
- **Hash seguro de contraseñas** usando bibliotecas estándar
- **Gestión de sesiones** con estado persistente
- **Validación de entrada** en todos los formularios

### 🗄️ Base de Datos
- **Pool de conexiones** para mejor rendimiento
- **Transacciones seguras** con manejo de errores
- **Validación SQL** para prevenir inyecciones

### 📧 Email
- **Configuración SMTP segura** con TLS
- **Validación de direcciones** de email
- **Plantillas HTML profesionales**

## 🌟 Ramas de Desarrollo

### `main` / `master`
- **Rama principal** para producción
- **Código estable** y probado
- **Despliegue automático** en Streamlit Cloud

### `development`
- **Rama de desarrollo** para nuevas características
- **Testing y experimentación**
- **Integración antes de producción**

### `feature/*`
- **Ramas específicas** para nuevas funcionalidades
- **Desarrollo aislado** de características individuales

## 📊 Tecnologías Utilizadas

- **🐍 Python 3.9+** - Lenguaje principal
- **🚀 Streamlit** - Framework web
- **🗄️ PostgreSQL** - Base de datos
- **🤖 OpenAI API** - Inteligencia artificial
- **📧 SMTP/Gmail** - Sistema de emails
- **📊 openpyxl** - Generación de Excel
- **🔐 hashlib** - Seguridad de contraseñas

## 🤝 Contribución

1. **Fork** el repositorio
2. Crear rama de feature (`git checkout -b feature/nueva-caracteristica`)
3. **Commit** cambios (`git commit -am 'Agregar nueva característica'`)
4. **Push** a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear **Pull Request**

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

- **📧 Email:** soporte@profitcoach.com
- **🐛 Issues:** [GitHub Issues](https://github.com/tu-usuario/profit-coach/issues)
- **📖 Documentación:** [Wiki del proyecto](https://github.com/tu-usuario/profit-coach/wiki)

---

**Desarrollado con ❤️ para revolucionar el entrenamiento deportivo con IA**
