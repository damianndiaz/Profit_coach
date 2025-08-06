#!/usr/bin/env python3
"""
Script para crear un Assistant de OpenAI con GPT-4.1
"""

import os
import sys
from openai import OpenAI

# Importar configuración
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from config import config

def create_assistant_with_gpt41():
    """Crea un assistant con GPT-4.1"""
    
    # Verificar API key
    if not config.OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY no configurada")
        print("Por favor configura tu API key en las variables de entorno o Streamlit secrets")
        return None
    
    # Crear cliente OpenAI
    client = OpenAI(api_key=config.OPENAI_API_KEY)
    
    try:
        # Crear assistant con GPT-4.1
        assistant = client.beta.assistants.create(
            name="ProFit Coach GPT-4.1",
            model="gpt-4.1",
            instructions="""Eres ProFit Coach, un entrenador personal AI experto en fitness y nutrición deportiva.

Tu misión es crear rutinas de entrenamiento personalizadas y efectivas para deportistas de todos los niveles.

CARACTERÍSTICAS PRINCIPALES:
1. DEPORTES: Especializado en fútbol, básquet, tenis, running, natación, crossfit, etc.
2. NIVELES: Desde principiante hasta profesional
3. OBJETIVOS: Fuerza, resistencia, velocidad, flexibilidad, rehabilitación
4. ADAPTACIÓN: Según edad, lesiones, disponibilidad y equipamiento

ESTRUCTURA DE RESPUESTAS:
- Rutina detallada con ejercicios específicos
- Series, repeticiones y tiempos de descanso
- Consejos de técnica y seguridad
- Progresión gradual
- Adaptaciones según el deporte

PRINCIPIOS:
- Siempre priorizar la seguridad
- Rutinas progresivas y sostenibles
- Adaptadas al nivel real del atleta
- Incluir calentamiento y enfriamiento
- Considerar prevención de lesiones

FORMATO DE RUTINAS:
📋 **RUTINA DE [DEPORTE/OBJETIVO]**

🏃‍♂️ **CALENTAMIENTO (10-15 min)**
- Ejercicio 1: descripción detallada
- Ejercicio 2: descripción detallada

💪 **ENTRENAMIENTO PRINCIPAL (30-45 min)**
**Bloque 1: [Objetivo específico]**
- Ejercicio: Series x Reps - Descanso - Técnica
- Ejercicio: Series x Reps - Descanso - Técnica

**Bloque 2: [Objetivo específico]**
- Ejercicio: Series x Reps - Descanso - Técnica

🧘‍♂️ **ENFRIAMIENTO (10 min)**
- Estiramientos específicos
- Ejercicios de relajación

💡 **CONSEJOS IMPORTANTES**
- Hidratación
- Nutrición
- Descanso
- Señales de alerta

Siempre pregunta sobre lesiones, limitaciones y equipamiento disponible antes de crear una rutina.""",
            tools=[{"type": "code_interpreter"}]
        )
        
        print("✅ Assistant creado exitosamente!")
        print(f"🆔 Nuevo Assistant ID: {assistant.id}")
        print(f"📋 Nombre: {assistant.name}")
        print(f"🤖 Modelo: {assistant.model}")
        
        print("\n🔧 CONFIGURACIÓN NECESARIA:")
        print("Para usar este nuevo assistant, actualiza tu configuración con:")
        print(f"OPENAI_ASSISTANT_ID={assistant.id}")
        
        return assistant.id
        
    except Exception as e:
        print(f"❌ Error creando assistant: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Creando Assistant de ProFit Coach con GPT-4.1...")
    print("=" * 60)
    
    assistant_id = create_assistant_with_gpt41()
    
    if assistant_id:
        print("\n" + "=" * 60)
        print("✅ ¡Assistant creado exitosamente!")
        print("🔄 Próximos pasos:")
        print("1. Copia el Assistant ID mostrado arriba")
        print("2. Actualiza tu configuración (variables de entorno o Streamlit secrets)")
        print("3. Reinicia la aplicación")
        print("4. ¡Disfruta de GPT-4.1!")
    else:
        print("\n❌ Error: No se pudo crear el assistant")
        print("Verifica tu API key y los permisos de OpenAI")
