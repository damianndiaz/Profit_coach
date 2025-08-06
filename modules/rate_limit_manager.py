"""
Configuración y gestión de rate limits para OpenAI
Estrategias para optimizar uso y evitar límites
"""

import time
import logging
from typing import Dict, Tuple, List, Any
from datetime import datetime, timedelta

class RateLimitManager:
    """Gestiona los rate limits de OpenAI de forma inteligente"""
    
    def __init__(self):
        # Configuración de límites (ajustar según tu plan de OpenAI)
        self.limits = {
            # GPT-4 Turbo límites estándar (ajustar según tu tier)
            'gpt-4-turbo': {
                'requests_per_minute': 500,
                'tokens_per_minute': 30000,
                'requests_per_day': 10000
            },
            # GPT-4 límites (más restrictivos)
            'gpt-4': {
                'requests_per_minute': 200,
                'tokens_per_minute': 10000,
                'requests_per_day': 5000
            }
        }
        
        # Estrategias de optimización
        self.optimization_strategies = {
            'peak_hours': (9, 18),  # Horas pico UTC
            'retry_delay_base': 1.0,  # Delay base para reintentos
            'max_retries': 3,
            'request_spacing': 0.1,  # Espaciado mínimo entre requests
        }
        
        # Cache de rate limit state
        self.request_history = []
        self.last_request_time = 0
        
    def check_rate_limit_status(self, model: str = 'gpt-4-turbo') -> Dict[str, Any]:
        """Verifica el estado actual de los rate limits"""
        now = datetime.now()
        model_limits = self.limits.get(model, self.limits['gpt-4-turbo'])
        
        # Filtrar requests de la última hora
        hour_ago = now - timedelta(hours=1)
        recent_requests = [
            req for req in self.request_history 
            if req['timestamp'] > hour_ago
        ]
        
        # Calcular uso actual
        requests_last_minute = len([
            req for req in recent_requests 
            if req['timestamp'] > now - timedelta(minutes=1)
        ])
        
        tokens_last_minute = sum([
            req['tokens'] for req in recent_requests 
            if req['timestamp'] > now - timedelta(minutes=1)
        ])
        
        requests_today = len([
            req for req in recent_requests 
            if req['timestamp'].date() == now.date()
        ])
        
        # Calcular percentajes de uso
        rpm_usage = requests_last_minute / model_limits['requests_per_minute']
        tpm_usage = tokens_last_minute / model_limits['tokens_per_minute']
        daily_usage = requests_today / model_limits['requests_per_day']
        
        return {
            'model': model,
            'requests_per_minute': {
                'used': requests_last_minute,
                'limit': model_limits['requests_per_minute'],
                'percentage': rpm_usage,
                'available': model_limits['requests_per_minute'] - requests_last_minute
            },
            'tokens_per_minute': {
                'used': tokens_last_minute,
                'limit': model_limits['tokens_per_minute'], 
                'percentage': tpm_usage,
                'available': model_limits['tokens_per_minute'] - tokens_last_minute
            },
            'requests_per_day': {
                'used': requests_today,
                'limit': model_limits['requests_per_day'],
                'percentage': daily_usage,
                'available': model_limits['requests_per_day'] - requests_today
            },
            'status': self._determine_status(rpm_usage, tpm_usage, daily_usage)
        }
    
    def _determine_status(self, rpm_usage: float, tpm_usage: float, daily_usage: float) -> str:
        """Determina el estado general de los rate limits"""
        max_usage = max(rpm_usage, tpm_usage, daily_usage)
        
        if max_usage >= 0.95:
            return "CRITICAL"  # 95%+ usado
        elif max_usage >= 0.8:
            return "WARNING"   # 80%+ usado
        elif max_usage >= 0.6:
            return "MODERATE"  # 60%+ usado
        else:
            return "GOOD"      # < 60% usado
    
    def should_throttle_request(self, estimated_tokens: int = 1000, model: str = 'gpt-4-turbo') -> Tuple[bool, str, float]:
        """
        Determina si se debe throttlear una request
        Returns: (should_throttle, reason, suggested_delay)
        """
        status = self.check_rate_limit_status(model)
        now = datetime.now()
        
        # Verificar si hay suficiente espacio para la request
        rpm_status = status['requests_per_minute']
        tpm_status = status['tokens_per_minute']
        daily_status = status['requests_per_day']
        
        # Throttle si estamos cerca de límites críticos
        if rpm_status['available'] < 1:
            return True, "Requests per minute limit reached", 60.0
        
        if tpm_status['available'] < estimated_tokens:
            return True, f"Not enough token capacity ({tpm_status['available']} < {estimated_tokens})", 60.0
        
        if daily_status['available'] < 1:
            return True, "Daily request limit reached", 3600.0
        
        # Throttle inteligente basado en estado
        if status['status'] == "CRITICAL":
            return True, "Rate limits in critical state", 30.0
        elif status['status'] == "WARNING":
            # Throttle durante horas pico
            if self._is_peak_hour(now):
                return True, "Warning state during peak hours", 15.0
        
        # Verificar espaciado mínimo entre requests
        time_since_last = time.time() - self.last_request_time
        min_spacing = self.optimization_strategies['request_spacing']
        
        if time_since_last < min_spacing:
            return True, "Minimum request spacing not met", min_spacing - time_since_last
        
        return False, "OK", 0.0
    
    def _is_peak_hour(self, dt: datetime) -> bool:
        """Verifica si es hora pico"""
        peak_start, peak_end = self.optimization_strategies['peak_hours']
        return peak_start <= dt.hour < peak_end
    
    def log_request(self, tokens_used: int = 1000, model: str = 'gpt-4-turbo'):
        """Registra una request realizada"""
        self.request_history.append({
            'timestamp': datetime.now(),
            'tokens': tokens_used,
            'model': model
        })
        
        self.last_request_time = time.time()
        
        # Limpiar historial antiguo (mantener solo últimas 24 horas)
        cutoff = datetime.now() - timedelta(hours=24)
        self.request_history = [
            req for req in self.request_history 
            if req['timestamp'] > cutoff
        ]
    
    def get_optimal_request_time(self, model: str = 'gpt-4-turbo') -> Tuple[datetime, str]:
        """Sugiere el momento óptimo para hacer una request"""
        status = self.check_rate_limit_status(model)
        now = datetime.now()
        
        if status['status'] == "GOOD":
            return now, "Request can be made immediately"
        
        elif status['status'] == "MODERATE":
            if self._is_peak_hour(now):
                # Esperar hasta después de horas pico
                peak_end = now.replace(hour=self.optimization_strategies['peak_hours'][1], minute=0, second=0)
                if now.hour >= self.optimization_strategies['peak_hours'][1]:
                    peak_end += timedelta(days=1)
                return peak_end, "Wait until after peak hours"
            else:
                return now + timedelta(seconds=5), "Small delay recommended"
        
        elif status['status'] == "WARNING":
            # Esperar al próximo minuto
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            return next_minute, "Wait for rate limit reset"
        
        else:  # CRITICAL
            # Esperar significativamente más tiempo
            next_hour = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            return next_hour, "Rate limits critical - wait for hourly reset"
    
    def get_cache_strategy_recommendation(self) -> Dict[str, Any]:
        """Recomienda estrategia de cache basada en uso actual"""
        status = self.check_rate_limit_status()
        
        if status['status'] in ["WARNING", "CRITICAL"]:
            return {
                'cache_duration_hours': 48,  # Cache más agresivo
                'similarity_threshold': 0.7,  # Menos estricto en similaridad
                'prioritize_cache': True,
                'reason': f"Rate limits in {status['status']} state"
            }
        elif status['status'] == "MODERATE":
            return {
                'cache_duration_hours': 24,
                'similarity_threshold': 0.8,
                'prioritize_cache': True,
                'reason': "Moderate usage - balanced caching"
            }
        else:
            return {
                'cache_duration_hours': 12,
                'similarity_threshold': 0.9,  # Más estricto
                'prioritize_cache': False,
                'reason': "Low usage - normal caching"
            }
    
    def estimate_tokens(self, text: str) -> int:
        """Estima tokens de un texto (aproximación)"""
        # Aproximación: ~4 caracteres = 1 token en español
        # Esto es una estimación, para mayor precisión usar tiktoken
        return len(text) // 4
    
    def get_cost_optimization_tips(self) -> List[str]:
        """Proporciona tips para optimizar costos"""
        status = self.check_rate_limit_status()
        tips = []
        
        if status['status'] in ["WARNING", "CRITICAL"]:
            tips.extend([
                "🎯 Usa el sistema de cache más agresivamente",
                "✂️ Reduce la longitud de los prompts",
                "🔄 Implementa retry con exponential backoff",
                "⏰ Programa requests para horas de menor uso"
            ])
        
        tips.extend([
            "💾 Usa respuestas cached cuando sea posible",
            "📝 Optimiza prompts para ser más concisos",
            "🧠 Implementa respuestas predeterminadas para consultas comunes",
            "📊 Monitorea el uso diario para planificar mejor"
        ])
        
        return tips

# Instancia global del rate limit manager
rate_limit_manager = RateLimitManager()
