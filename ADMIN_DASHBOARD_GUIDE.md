"""
Cómo usar el Admin Dashboard - ProFit Coach
Guía completa para acceder y usar el panel de administración
"""

# 🛠️ ADMIN DASHBOARD - GUÍA DE USO

## ¿Qué es el Admin Dashboard?

El Admin Dashboard es un **panel de control completo** que te permite monitorear y gestionar todos los aspectos técnicos de ProFit Coach:

### 📊 Performance Monitor
- **Requests 24h**: Cuántas consultas se han hecho a OpenAI en las últimas 24 horas
- **Cache Hit Rate**: Porcentaje de respuestas que vienen del cache (mayor = mejor)
- **Tiempo de Respuesta**: Promedio de tiempo que tarda en responder la IA
- **Costo Estimado**: Cuánto dinero estás gastando en tokens de OpenAI

### 💾 Sistema de Cache
- **Total Entradas**: Cuántas respuestas están guardadas en cache
- **Hit Rate**: Qué tan efectivo es el cache
- **Uso Promedio**: Cuántas veces se reutiliza cada respuesta
- **Configuración**: Puedes ajustar duración y tamaño del cache

### 🚦 Rate Limits de OpenAI
- **Requests/Min**: Uso actual vs límite por minuto
- **Tokens/Min**: Tokens consumidos vs límite por minuto  
- **Requests/Día**: Uso diario vs límite diario
- **Recomendaciones**: Tips para optimizar costos

### 📧 Sistema de Email
- **Estado de Configuración**: Si está bien configurado el SMTP
- **Test de Conexión**: Prueba si puede conectarse al servidor de email
- **Email de Prueba**: Envía un email real para probar

### ⚙️ Configuración General
- **Estado de OpenAI**: Si las API keys están configuradas
- **Estado de BD**: Si la base de datos está conectada
- **Variables de Entorno**: Valores actuales de configuración

## 🚀 Cómo Acceder al Admin Dashboard

### Paso 1: Iniciar la aplicación
```bash
cd "/workspaces/ProFit Coach"
streamlit run main.py
```

### Paso 2: Hacer login
- Usa tu usuario y contraseña normales
- Una vez dentro de la aplicación principal

### Paso 3: Abrir el Admin Dashboard
- En el **sidebar izquierdo** verás un botón **"🛠️ Admin Dashboard"**
- Haz clic en ese botón
- Se abrirá el panel de administración completo

### Paso 4: Navegar por las pestañas
- **📊 Performance**: Para ver métricas en tiempo real
- **💾 Cache**: Para gestionar el sistema de cache
- **🚦 Rate Limits**: Para monitorear límites de OpenAI
- **📧 Email System**: Para configurar y probar emails
- **⚙️ Configuración**: Para revisar toda la configuración

### Paso 5: Cerrar el dashboard
- Haz clic en **"❌ Cerrar"** en la esquina superior derecha
- Regresarás a la aplicación principal

## 🔧 Funcionalidades Principales

### Monitoreo en Tiempo Real
- Ve cuántas requests se están haciendo
- Monitorea el rendimiento del cache
- Detecta problemas antes de que afecten a los usuarios

### Gestión del Cache
- **Limpiar Cache**: Elimina todas las respuestas guardadas
- **Optimizar Cache**: Elimina solo las respuestas poco usadas
- **Configurar Duración**: Cambia cuánto tiempo se guardan las respuestas

### Control de Costos
- Ve cuánto dinero estás gastando en OpenAI
- Recibe alertas cuando te acerques a los límites
- Obtén recomendaciones para optimizar costos

### Test de Email
- Prueba la conexión SMTP sin salir de la app
- Envía emails de prueba para verificar que funciona
- Ve el estado de configuración en tiempo real

## 🚨 Alertas y Monitoreo

El dashboard te avisará automáticamente cuando:
- El tiempo de respuesta sea muy lento (>10 segundos)
- Te acerques a los límites de OpenAI (>80% de uso)
- El cache tenga muy pocos hits (<30%)
- Haya errores en las requests

## 💡 Tips para Optimizar

### Mejorar Cache Hit Rate
- Si está bajo (<50%), considera:
  - Aumentar la duración del cache
  - Hacer preguntas más similares
  - Usar respuestas predeterminadas

### Reducir Costos de OpenAI
- Usa el cache más agresivamente
- Reduce la longitud de los prompts
- Programa requests para horas de menor uso
- Monitorea el uso diario

### Optimizar Performance
- Si el tiempo de respuesta es lento:
  - Verifica la conexión a internet
  - Reduce la complejidad de las consultas
  - Usa respuestas cached cuando sea posible

## 🔐 Seguridad

- Solo usuarios autenticados pueden acceder al dashboard
- No se muestran credenciales sensibles (passwords, API keys)
- Todas las acciones quedan registradas en logs

## 🆘 Solución de Problemas

### Si no ves el botón "🛠️ Admin Dashboard"
1. Asegúrate de estar logueado
2. Verifica que el módulo admin_dashboard.py esté en la carpeta modules/
3. Reinicia la aplicación

### Si el dashboard muestra errores
1. Verifica que todas las dependencias estén instaladas
2. Revisa los logs en la consola
3. Asegúrate de que las bases de datos estén creadas

### Si las métricas no aparecen
1. Haz algunas consultas normales a la IA primero
2. Espera unos minutos para que se generen datos
3. Verifica que las bases de datos de monitoreo estén funcionando

¡El Admin Dashboard te dará control total sobre el rendimiento y configuración de ProFit Coach! 🚀
