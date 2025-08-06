"""
Sistema de Limpieza y Formateo de Respuestas de IA
Elimina texto extraño y mejora la presentación
"""

import re
import logging
from typing import Dict, Any, Optional

class ResponseCleaner:
    """Limpia y formatea respuestas de IA para mejor presentación"""
    
    def __init__(self):
        # Patrones de texto no deseado
        self.unwanted_patterns = [
            # Anotaciones técnicas
            r'【\d+:\d+†source】',
            r'\【.*?†.*?\】',
            r'【.*?】',
            
            # Marcadores de sistema
            r'\[ASSISTANT\]',
            r'\[USER\]',
            r'\[SYSTEM\]',
            r'<\|.*?\|>',
            
            # Códigos HTML residuales
            r'<div[^>]*>',
            r'</div>',
            r'<span[^>]*>',
            r'</span>',
            r'<br\s*/?>',
            r'&nbsp;',
            r'&amp;',
            r'&lt;',
            r'&gt;',
            
            # Marcadores de metadata
            r'\[metadata:.*?\]',
            r'\[timestamp:.*?\]',
            r'\[id:.*?\]',
            
            # Caracteres extraños Unicode
            r'[\ufeff\u200b\u200c\u200d\u2060]',  # Zero-width characters
            r'[^\x00-\x7F\u00C0-\u017F\u0100-\u024F\u1E00-\u1EFF\u00A0-\u00FF]',  # Non-Latin extended
        ]
        
        # Patrones de texto de inicio no deseado
        self.unwanted_starting_patterns = [
            r'^.*?(?=¡Hola)',
            r'^.*?(?=Hola)',
            r'^.*?(?=Bienvenido)',
            r'^.*?(?=¡Perfecto)',
            r'^.*?(?=Perfecto)',
            r'^.*?(?=Excelente)',
            r'^.*?(?=¡Excelente)',
            r'^.*?(?=Como)',
            r'^.*?(?=Para)',
            r'^.*?(?=Voy)',
        ]
        
        # Reemplazos de mejora
        self.improvements = {
            # Emojis consistentes
            r'🎯\s*🎯': '🎯',
            r'💪\s*💪': '💪',
            r'⚡\s*⚡': '⚡',
            
            # Espaciado consistente
            r'\n{3,}': '\n\n',
            r'\s{3,}': ' ',
            
            # Puntuación mejorada
            r'\.{2,}': '.',
            r'\?{2,}': '?',
            r'!{2,}': '!',
        }
    
    def clean_response(self, response: str) -> str:
        """Limpia una respuesta de IA de elementos no deseados"""
        if not response or not isinstance(response, str):
            return ""
        
        cleaned = response.strip()
        
        # 1. Eliminar patrones no deseados
        for pattern in self.unwanted_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
        
        # 2. Limpiar inicio de respuesta
        for pattern in self.unwanted_starting_patterns:
            match = re.search(pattern, cleaned, flags=re.IGNORECASE | re.DOTALL)
            if match:
                cleaned = cleaned[match.end():]
                break
        
        # 3. Aplicar mejoras
        for pattern, replacement in self.improvements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
        
        # 4. Limpiar espaciado final
        cleaned = cleaned.strip()
        
        # 5. Validar que no esté vacío
        if not cleaned or len(cleaned) < 10:
            return "🤔 Respuesta procesada pero no clara. Por favor, reformula tu pregunta."
        
        return cleaned
    
    def format_routine_response(self, response: str) -> str:
        """Formatea específicamente respuestas de rutinas"""
        cleaned = self.clean_response(response)
        
        # Mejorar formato de rutinas
        routine_improvements = {
            # Asegurar saltos de línea antes de bloques
            r'(\d+\.\s*[🍑⚡💪🔥🚀].*?)(?=\d+\.|\Z)': r'\1\n',
            
            # Mejorar formato de ejercicios
            r'([•\-\*])\s*([A-ZÁÉÍÓÚ].*?)(?=\n|$)': r'\1 \2',
            
            # Espaciado consistente en parámetros
            r'(\d+)\s*x\s*(\d+)': r'\1 x \2',
            r'(\d+)\s*seg': r'\1 seg',
            r'(\d+)\s*min': r'\1 min',
        }
        
        for pattern, replacement in routine_improvements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.MULTILINE)
        
        return cleaned
    
    def create_welcome_message(self, athlete_name: str, sport: str) -> str:
        """Crea un mensaje de bienvenida limpio y personalizado"""
        welcome_templates = {
            "default": f"¡Hola {athlete_name}! 👋\n\nSoy tu ProFit Coach AI especializado en **{sport}**. Estoy aquí para crear rutinas personalizadas usando nuestra metodología de 5 bloques.\n\n🎯 **¿En qué puedo ayudarte hoy?**\n• Rutina específica para entrenar\n• Plan de múltiples días\n• Adaptación de ejercicios\n• Consejos de entrenamiento\n\n¡Cuéntame qué necesitas! 💪",
            
            "futbol": f"¡Hola {athlete_name}! ⚽\n\nSoy tu ProFit Coach AI especializado en **fútbol**. Te ayudo a crear entrenamientos que combinen técnica, físico y prevención de lesiones.\n\n🎯 **¿Qué entrenamiento necesitas?**\n• Preparación física específica\n• Trabajo de velocidad y agilidad\n• Fortalecimiento preventivo\n• Rutinas de recuperación\n\n¡Vamos a potenciar tu rendimiento! 🚀",
            
            "running": f"¡Hola {athlete_name}! 🏃‍♂️\n\nSoy tu ProFit Coach AI especializado en **running**. Te ayudo con entrenamientos que mejoren tu resistencia, velocidad y eficiencia.\n\n🎯 **¿Qué tipo de entrenamiento buscas?**\n• Fuerza específica para corredores\n• Prevención de lesiones\n• Trabajo de potencia\n• Rutinas de cross-training\n\n¡Vamos a mejorar tu running! ⚡",
            
            "basquet": f"¡Hola {athlete_name}! 🏀\n\nSoy tu ProFit Coach AI especializado en **básquet**. Te ayudo con entrenamientos que potencien tu salto, agilidad y resistencia específica.\n\n🎯 **¿Qué necesitas trabajar?**\n• Potencia de salto\n• Agilidad y cambios de dirección\n• Fuerza funcional\n• Prevención de lesiones\n\n¡Vamos a elevar tu juego! 🚀"
        }
        
        # Seleccionar template apropiado
        sport_key = sport.lower()
        if sport_key in welcome_templates:
            return welcome_templates[sport_key]
        else:
            return welcome_templates["default"]
    
    def detect_and_clean_error_response(self, response: str) -> Optional[str]:
        """Detecta respuestas de error y las mejora"""
        error_indicators = [
            "i don't have access",
            "i cannot",
            "i'm unable",
            "i can't",
            "sorry, i",
            "error",
            "problem",
            "issue",
        ]
        
        response_lower = response.lower()
        
        # Si contiene indicadores de error en inglés, generar respuesta en español
        if any(indicator in response_lower for indicator in error_indicators):
            return "🤔 Parece que hubo un problema procesando tu consulta. Por favor:\n\n• Reformula tu pregunta de manera más específica\n• Menciona qué tipo de entrenamiento necesitas\n• Indica tu deporte y nivel\n\n¡Estoy aquí para ayudarte! 💪"
        
        return None
    
    def enhance_response_formatting(self, response: str) -> str:
        """Mejora el formato general de cualquier respuesta"""
        enhanced = self.clean_response(response)
        
        # Verificar si es una respuesta de error
        error_response = self.detect_and_clean_error_response(enhanced)
        if error_response:
            return error_response
        
        # Mejorar estructura general
        formatting_improvements = {
            # Asegurar espaciado después de emojis
            r'([🎯💪⚡🔥🚀🍑])([A-ZÁÉÍÓÚ])': r'\1 \2',
            
            # Mejorar listas
            r'^([•\-\*])\s*': r'\1 ',
            
            # Asegurar mayúsculas después de puntos
            r'(\.\s+)([a-záéíóú])': lambda m: m.group(1) + m.group(2).upper(),
            
            # Mejorar formato de números
            r'(\d+)\s*\.\s*([A-ZÁÉÍÓÚ])': r'\1. \2',
        }
        
        for pattern, replacement in formatting_improvements.items():
            if callable(replacement):
                enhanced = re.sub(pattern, replacement, enhanced, flags=re.MULTILINE)
            else:
                enhanced = re.sub(pattern, replacement, enhanced, flags=re.MULTILINE)
        
        return enhanced.strip()
    
    def get_cleaning_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de limpieza (para monitoreo)"""
        return {
            "unwanted_patterns": len(self.unwanted_patterns),
            "starting_patterns": len(self.unwanted_starting_patterns),
            "improvements": len(self.improvements),
            "status": "operational"
        }

# Instancia global del limpiador
response_cleaner = ResponseCleaner()
