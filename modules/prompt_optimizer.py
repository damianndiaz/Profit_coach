"""
Optimizador inteligente de prompts para gestionar tokens sin perder calidad
"""

def optimize_prompt_for_tokens(base_prompt, max_tokens=4000):
    """
    Optimiza dinámicamente el prompt para mantenerse bajo el límite de tokens
    Mantiene la calidad pero reduce contenido innecesario
    """
    if len(base_prompt) <= max_tokens:
        return base_prompt
    
    # Estrategias de optimización progresiva que mantienen funcionalidad
    optimizations = [
        # 1. Quitar emojis decorativos pero mantener estructura
        lambda p: p.replace('🍑', '').replace('⚡', '').replace('💪', '').replace('🔥', '').replace('🚀', ''),
        # 2. Simplificar descripciones largas pero mantener instrucciones clave
        lambda p: p.replace(' - 5 bloques: Activación→Dinámico→Fuerza1→Fuerza2→Contraste', ''),
        # 3. Compactar formato pero mantener funcionalidad EMAIL crítica
        lambda p: p.replace('Si pides enviar rutina por mail→GENERAR', 'Si solicitas email→GENERAR'),
        # 4. Reducir texto explicativo redundante
        lambda p: p.replace('...rutina...[FIN_RUTINA] + confirmar envío', 'rutina[FIN_RUTINA]+envío'),
        # 5. Simplificar formato manteniendo estructura
        lambda p: p.replace('FORMATO: [INICIO_NUEVA_RUTINA] para rutinas completas.', ''),
        # 6. Compactar información del atleta
        lambda p: p.replace('ATLETA: ', '').replace(' | ', ', ')
    ]
    
    optimized = base_prompt
    for optimization in optimizations:
        optimized = optimization(optimized)
        if len(optimized) <= max_tokens:
            break
    
    # Si aún es muy largo, aplicar optimización más agresiva manteniendo lo esencial
    if len(optimized) > max_tokens:
        # Extraer solo las partes esenciales
        lines = optimized.split('\n')
        essential_lines = []
        for line in lines:
            if any(keyword in line for keyword in ['EMAIL:', '[INICIO_NUEVA_RUTINA]', 'ProFit Coach']):
                essential_lines.append(line)
        optimized = '\n'.join(essential_lines)
    
    return optimized

def create_smart_routine_context(previous_routines, max_chars=50):
    """
    Crea un contexto inteligente de rutinas anteriores ultra-compacto
    """
    if not previous_routines:
        return ""
    
    # Extraer palabras clave de la rutina anterior
    last_routine = previous_routines[0][0].lower()
    keywords = []
    
    # Detectar grupos musculares
    muscle_groups = {
        'piernas': ['piernas', 'cuádriceps', 'glúteos', 'femoral'],
        'pecho': ['pecho', 'pectorales'],
        'espalda': ['espalda', 'dorsales', 'trapecio'],
        'brazos': ['bíceps', 'tríceps', 'brazos'],
        'cardio': ['cardio', 'correr', 'bici', 'elíptica'],
        'core': ['core', 'abdomen', 'abdominal']
    }
    
    for group, terms in muscle_groups.items():
        if any(term in last_routine for term in terms):
            keywords.append(group)
    
    # Detectar tipo de entrenamiento
    if 'fuerza' in last_routine:
        keywords.append('fuerza')
    if 'resistencia' in last_routine:
        keywords.append('resistencia')
    
    if keywords:
        context = f"\\nAnterior: {', '.join(keywords[:3])}"  # Max 3 palabras clave
        return context if len(context) <= max_chars else f"\\nAnterior: {keywords[0]}"
    
    return ""
