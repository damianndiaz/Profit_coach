"""
Módulo para Templates de Rutinas Rápidas
Permite generar rutinas predefinidas con un solo clic
"""

import streamlit as st
import logging
import time
from datetime import datetime

# Templates predefinidos
QUICK_TEMPLATES = {
    # Templates por Duración
    "express_20": {
        "name": "⚡ Express 20min",
        "category": "duración",
        "description": "Rutina rápida para días ocupados",
        "icon": "⚡",
        "color": "#FF6B35",
        "prompt": """Crea una rutina EXPRESS de 20 minutos máximo con esta estructura:
        
🔥 BLOQUE 1 (5 min): Activación dinámica específica
💪 BLOQUE 2 (12 min): Circuito principal con 4-5 ejercicios
🧘 BLOQUE 3 (3 min): Vuelta a la calma y estiramientos

Que sea intensa pero eficiente. Ejercicios funcionales sin equipamiento complejo."""
    },
    
    "standard_45": {
        "name": "🏃‍♂️ Estándar 45min",
        "category": "duración", 
        "description": "Rutina completa balanceada",
        "icon": "🏃‍♂️",
        "color": "#4ECDC4",
        "prompt": """Crea una rutina ESTÁNDAR de 45 minutos con los 5 bloques de la metodología ProFit:

🍑 BLOQUE 1: Activación glútea y estabilizadores
⚡ BLOQUE 2: Dinámico/Potencia adaptado al deporte
💪 BLOQUE 3: Fuerza 1 - Patrones básicos
🔥 BLOQUE 4: Fuerza 2 - Movimientos complejos  
🏃‍♂️ BLOQUE 5: Contraste/Preventivos/RSA

Rutina completa y equilibrada."""
    },
    
    "intensive_60": {
        "name": "🔥 Intensiva 60min",
        "category": "duración",
        "description": "Sesión completa de alta intensidad",
        "icon": "🔥", 
        "color": "#E74C3C",
        "prompt": """Crea una rutina INTENSIVA de 60 minutos con máxima exigencia:

Los 5 bloques tradicionales PERO con mayor volumen e intensidad:
- Más series por ejercicio
- Cargas más altas
- Menor descanso entre ejercicios
- Ejercicios más complejos y demandantes

Diseñada para atletas avanzados en excelente condición."""
    },
    
    # Templates por Objetivo
    "strength": {
        "name": "💪 Solo Fuerza",
        "category": "objetivo",
        "description": "Enfoque exclusivo en fuerza máxima",
        "icon": "🏋️‍♂️",
        "color": "#8E44AD",
        "prompt": """Crea una rutina enfocada 100% en DESARROLLO DE FUERZA:

- Ejercicios básicos multiarticulares
- Trabajo con cargas altas (75-90% RM)
- Series de 3-6 repeticiones
- Descansos largos (2-4 minutos)
- Énfasis en técnica perfecta

Incluye: Sentadillas, Press, Dominadas, Peso muerto y variantes."""
    },
    
    "cardio_hiit": {
        "name": "❤️ Cardio HIIT",
        "category": "objetivo",
        "description": "Intervalos de alta intensidad",
        "icon": "💓",
        "color": "#E67E22",
        "prompt": """Crea una rutina de CARDIO HIIT puro:

- Intervalos de alta intensidad
- Trabajo/descanso 30"/15" o 45"/15"
- 4-6 ejercicios diferentes
- 3-4 rondas totales
- Sin equipamiento pesado
- Ejercicios explosivos y funcionales

Que sea agotador pero motivante."""
    },
    
    "mobility": {
        "name": "🤸‍♂️ Movilidad",
        "category": "objetivo", 
        "description": "Flexibilidad y trabajo correctivo",
        "icon": "🧘‍♂️",
        "color": "#2ECC71",
        "prompt": """Crea una rutina de MOVILIDAD Y FLEXIBILIDAD:

- Movilidad articular dinámica
- Estiramientos estáticos y dinámicos  
- Trabajo de fascias y liberación miofascial
- Ejercicios correctivos posturales
- Respiración y relajación
- Movimientos fluidos y controlados

Perfecta para días de recuperación activa."""
    },
    
    "recovery": {
        "name": "🛌 Recuperación",
        "category": "objetivo",
        "description": "Recuperación activa suave",
        "icon": "💆‍♂️", 
        "color": "#95A5A6",
        "prompt": """Crea una rutina de RECUPERACIÓN ACTIVA:

- Ejercicios de muy baja intensidad
- Movimientos suaves y fluidos
- Activación de sistemas parasimpáticos
- Estiramientos prolongados
- Trabajo de respiración
- Autorelajación y mindfulness

Diseñada para promover la regeneración."""
    },
    
    # Templates Específicos
    "warm_up": {
        "name": "🔥 Solo Calentamiento",
        "category": "específico",
        "description": "Calentamiento completo independiente", 
        "icon": "🌡️",
        "color": "#F39C12",
        "prompt": """Crea un CALENTAMIENTO COMPLETO de 15-20 minutos:

- Activación cardiovascular suave
- Movilidad articular específica
- Activación muscular progresiva
- Patrones de movimiento del deporte
- Preparación del sistema nervioso

Que prepare perfectamente para el entrenamiento principal."""
    },
    
    "core_abs": {
        "name": "🔲 Core Intenso", 
        "category": "específico",
        "description": "Trabajo específico de core y abdominales",
        "icon": "⭐",
        "color": "#9B59B6",
        "prompt": """Crea una rutina ESPECÍFICA DE CORE:

- Trabajo de zona media en todos los planos
- Estabilización y fuerza funcional
- Ejercicios isométricos y dinámicos
- Progresiones de dificultad
- Sin equipamiento complejo

15-25 minutos de trabajo intenso y efectivo."""
    }
}

def show_quick_templates_interface(athlete_id, athlete_name):
    """Muestra la interfaz de templates rápidos para un atleta"""
    
    st.markdown(f"### ⚡ Rutinas Rápidas para {athlete_name}")
    st.markdown("*Genera rutinas predefinidas con un solo clic*")
    
    # Organizar por categorías
    categories = {
        "duración": "⏱️ Por Duración",
        "objetivo": "🎯 Por Objetivo", 
        "específico": "🔍 Específicas"
    }
    
    for cat_key, cat_name in categories.items():
        with st.expander(cat_name, expanded=True):
            templates_in_category = [t for t in QUICK_TEMPLATES.values() if t["category"] == cat_key]
            
            # Mostrar en grid de 2 columnas
            cols = st.columns(2)
            for idx, template in enumerate(templates_in_category):
                with cols[idx % 2]:
                    # Crear contenedor visual sin botón duplicado
                    st.markdown(f"""
                    <div style='
                        background: {template["color"]};
                        padding: 15px;
                        border-radius: 10px;
                        margin: 5px 0;
                        text-align: center;
                        color: white;
                        font-weight: bold;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    '>
                        <div style='font-size: 1.5em;'>{template["icon"]}</div>
                        <div>{template["name"]}</div>
                        <div style='font-size: 0.8em; margin-top: 5px; opacity: 0.9;'>{template["description"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Botón funcional ÚNICO con key específico
                    template_key = f"gen_{athlete_id}_{template['name'].replace(' ', '_').replace('🤸‍♂️', 'mobility').replace('⚡', 'express').replace('🔥', 'intensive').replace('💪', 'strength').replace('❤️', 'cardio').replace('🌡️', 'warmup').replace('🔲', 'core')}_{idx}"
                    
                    if st.button(
                        f"🚀 Generar", 
                        key=template_key,
                        use_container_width=True,
                        type="primary"
                    ):
                        generate_quick_routine_and_redirect(athlete_id, template)
                        st.rerun()

def generate_quick_routine_and_redirect(athlete_id, template):
    """Genera una rutina usando un template y redirige automáticamente al chat"""
    try:
        # Importar funciones localmente para evitar errores circulares
        from modules import athlete_manager
        from modules import chat_interface
        
        # Obtener datos del atleta para personalización
        athlete_data = athlete_manager.get_athlete_data(athlete_id)
        
        if not athlete_data:
            st.error("❌ No se pudieron obtener los datos del atleta")
            return
        
        # Personalizar el prompt con datos del atleta - MEJORADO
        personalized_prompt = f"""[INICIO_NUEVA_RUTINA]

INFORMACIÓN DEL ATLETA:
- Nombre: {athlete_data['name']}
- Deporte: {athlete_data['sport']}
- Nivel: {athlete_data['level']}
- Objetivos: {athlete_data['goals']}

TEMPLATE SOLICITADO: {template['name']}

{template['prompt']}

FORMATO REQUERIDO:
- Incluye título claro: "RUTINA {template['name'].upper()} - {athlete_data['name'].upper()}"
- Estructura visual con emojis y separadores
- Cada ejercicio con: nombre, series, repeticiones, descanso
- Tiempo estimado total
- Notas técnicas importantes
- Que sea fácil de leer en chat y exportar a Excel

PERSONALIZACIÓN:
- Adapta TODOS los ejercicios al deporte {athlete_data['sport']}
- Considera el nivel {athlete_data['level']} para la intensidad
- Incluye progresiones según el nivel del atleta
"""
        
        # Mostrar indicador de generación
        with st.spinner(f"🤖 Generando {template['name']} personalizada..."):
            # Usar el sistema de chat existente para generar
            response = chat_interface.handle_user_message(athlete_id, personalized_prompt)
            
        if response:
            # 🎉 ÉXITO: Mostrar confirmación y redirigir
            st.success(f"✅ {template['name']} generada exitosamente!")
            st.balloons()
            
            # 🔄 REDIRECCIÓN AUTOMÁTICA AL CHAT
            st.session_state["show_quick_templates"] = None  # Salir de templates
            st.session_state["active_athlete_chat"] = athlete_id  # Ir al chat
            
            # Mensaje de confirmación temporal
            st.info(f"""
            🚀 **¡Rutina generada!** Redirigiendo al chat...
            
            📋 **{template['name']}** para **{athlete_data['name']}**
            🎯 Personalizada para **{athlete_data['sport']}** nivel **{athlete_data['level']}**
            """)
            
            # Forzar actualización para mostrar el chat
            time.sleep(1)  # Dar tiempo para que el usuario lea el mensaje
            
        else:
            st.error("❌ Error al generar la rutina. Inténtalo de nuevo.")
            
    except Exception as e:
        logging.error(f"Error generando rutina rápida: {e}")
        st.error("❌ Error al generar la rutina rápida")

def generate_quick_routine(athlete_id, template):
    """Genera una rutina usando un template específico"""
    try:
        # Importar funciones localmente para evitar errores circulares
        from modules import athlete_manager
        from modules import chat_interface
        
        # Obtener datos del atleta para personalización
        athlete_data = athlete_manager.get_athlete_data(athlete_id)
        
        if not athlete_data:
            st.error("❌ No se pudieron obtener los datos del atleta")
            return
        
        # Personalizar el prompt con datos del atleta
        personalized_prompt = f"""
        INFORMACIÓN DEL ATLETA:
        - Nombre: {athlete_data['name']}
        - Deporte: {athlete_data['sport']}
        - Nivel: {athlete_data['level']}
        - Objetivos: {athlete_data['goals']}
        
        TEMPLATE SOLICITADO: {template['name']}
        
        {template['prompt']}
        
        IMPORTANTE: 
        - Adapta TODOS los ejercicios al deporte {athlete_data['sport']}
        - Considera el nivel {athlete_data['level']} para la intensidad
        - Incluye el marcador [INICIO_NUEVA_RUTINA] al inicio
        - Formato claro y estructurado para Excel
        - Que sea una rutina completa y lista para usar
        """
        
        # Mostrar indicador de generación
        with st.spinner(f"🤖 Generando {template['name']} personalizada..."):
            # Usar el sistema de chat existente para generar
            response = chat_interface.handle_user_message(athlete_id, personalized_prompt)
            
        if response:
            st.success(f"✅ {template['name']} generada exitosamente!")
            st.balloons()
            
            # Mostrar mensaje de confirmación
            st.info(f"""
            🎉 **Rutina generada:** {template['name']}
            
            📋 **Qué incluye:**
            - {template['description']}
            - Personalizada para {athlete_data['sport']}
            - Adaptada al nivel {athlete_data['level']}
            
            💬 **Ver la rutina:** Ve al chat con el atleta para ver la rutina completa y descargarla.
            """)
            
        else:
            st.error("❌ Error al generar la rutina. Inténtalo de nuevo.")
            
    except Exception as e:
        logging.error(f"Error generando rutina rápida: {e}")
        st.error("❌ Error al generar la rutina rápida")

def create_custom_template_form():
    """Permite crear templates personalizados (funcionalidad avanzada)"""
    with st.expander("🛠️ Crear Template Personalizado", expanded=False):
        with st.form("custom_template_form"):
            name = st.text_input("🏷️ Nombre del template")
            description = st.text_area("📝 Descripción")
            icon = st.selectbox("🎨 Icono", ["⚡", "🔥", "💪", "🏃‍♂️", "🤸‍♂️", "🧘‍♂️"])
            duration = st.slider("⏱️ Duración (minutos)", 10, 90, 45)
            
            prompt = st.text_area(
                "🤖 Instrucciones para el AI",
                placeholder="Describe exactamente qué tipo de rutina quieres que genere...",
                height=100
            )
            
            if st.form_submit_button("💾 Guardar Template"):
                # Aquí se guardaría en la base de datos
                st.success("✅ Template personalizado guardado!")
                st.info("Esta funcionalidad se desarrollará en futuras versiones")
