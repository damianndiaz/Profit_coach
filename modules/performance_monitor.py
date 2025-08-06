"""
Monitor de rendimiento y rate limits para ProFit Coach
Incluye métricas de OpenAI, cache, y sistema de alertas
"""

import time
import logging
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import streamlit as st

class PerformanceMonitor:
    """Monitor integral de rendimiento de la aplicación"""
    
    def __init__(self, db_path="/workspaces/ProFit Coach/performance_monitor.db"):
        self.db_path = db_path
        self._init_monitor_db()
        
        # Límites de OpenAI (ajustar según tu plan)
        self.RATE_LIMITS = {
            'requests_per_minute': 3500,  # GPT-4 Turbo
            'tokens_per_minute': 150000,  # GPT-4 Turbo
            'requests_per_day': 5000,     # Límite conservador
        }
        
        # Alertas - 🎯 AJUSTADAS para ser más realistas
        self.ALERT_THRESHOLDS = {
            'response_time_slow': 25.0,      # 25 segundos (antes 10s)
            'response_time_critical': 45.0,  # 45 segundos (antes 20s)
            'rate_limit_warning': 0.8,       # 80% del límite
            'cache_hit_rate_low': 0.3        # 30% hit rate
        }
    
    def _init_monitor_db(self):
        """Inicializar base de datos de monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Tabla de métricas de requests
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS request_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    athlete_id INTEGER,
                    request_type TEXT,  -- 'openai', 'cache_hit', 'cache_miss'
                    response_time REAL,
                    tokens_used INTEGER DEFAULT 0,
                    success BOOLEAN,
                    error_message TEXT
                )
            ''')
            
            # Tabla de métricas diarias agregadas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT UNIQUE,
                    total_requests INTEGER,
                    openai_requests INTEGER,
                    cache_hits INTEGER,
                    cache_misses INTEGER,
                    total_tokens INTEGER,
                    avg_response_time REAL,
                    error_count INTEGER
                )
            ''')
            
            # Tabla de alertas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    alert_type TEXT,
                    severity TEXT,  -- 'info', 'warning', 'critical'
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Índices para optimizar consultas
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON request_metrics(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON daily_metrics(date)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_alert_timestamp ON alerts(timestamp)')
            
            conn.commit()
            conn.close()
            logging.info("✅ Performance monitor database initialized")
            
        except Exception as e:
            logging.error(f"❌ Error initializing monitor DB: {e}")
    
    def log_request(self, athlete_id: int, request_type: str, response_time: float, 
                   tokens_used: int = 0, success: bool = True, error_message: str = ""):
        """Registra una request en el sistema de monitoreo"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO request_metrics 
                (athlete_id, request_type, response_time, tokens_used, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (athlete_id, request_type, response_time, tokens_used, success, error_message))
            
            conn.commit()
            conn.close()
            
            # Verificar alertas en tiempo real
            self._check_realtime_alerts(request_type, response_time, tokens_used, success)
            
        except Exception as e:
            logging.error(f"Error logging request metrics: {e}")
    
    def _check_realtime_alerts(self, request_type: str, response_time: float, 
                              tokens_used: int, success: bool):
        """Verifica alertas en tiempo real"""
        try:
            # Alerta por tiempo de respuesta lento
            if response_time > self.ALERT_THRESHOLDS['response_time_critical']:
                self._create_alert(
                    'response_time', 'critical',
                    f"Tiempo de respuesta crítico: {response_time:.1f}s"
                )
            elif response_time > self.ALERT_THRESHOLDS['response_time_slow']:
                self._create_alert(
                    'response_time', 'warning',
                    f"Tiempo de respuesta lento: {response_time:.1f}s"
                )
            
            # Alerta por errores
            if not success:
                self._create_alert(
                    'request_error', 'warning',
                    f"Error en request de tipo: {request_type}"
                )
            
            # Verificar rate limits si es request de OpenAI
            if request_type == 'openai':
                self._check_rate_limits()
                
        except Exception as e:
            logging.error(f"Error checking real-time alerts: {e}")
    
    def _check_rate_limits(self):
        """Verifica si estamos cerca de los rate limits"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Requests en la última hora
            hour_ago = datetime.now() - timedelta(hours=1)
            cursor.execute('''
                SELECT COUNT(*), SUM(tokens_used) 
                FROM request_metrics 
                WHERE request_type = 'openai' AND timestamp > ?
            ''', (hour_ago.isoformat(),))
            
            hourly_requests, hourly_tokens = cursor.fetchone()
            hourly_requests = hourly_requests or 0
            hourly_tokens = hourly_tokens or 0
            
            # Extrapolar a requests por minuto
            requests_per_minute = hourly_requests
            tokens_per_minute = hourly_tokens
            
            # Verificar límites
            rpm_usage = requests_per_minute / self.RATE_LIMITS['requests_per_minute']
            tpm_usage = tokens_per_minute / self.RATE_LIMITS['tokens_per_minute']
            
            if rpm_usage > self.ALERT_THRESHOLDS['rate_limit_warning']:
                self._create_alert(
                    'rate_limit', 'warning',
                    f"Cerca del límite de requests/min: {rpm_usage:.1%}"
                )
            
            if tpm_usage > self.ALERT_THRESHOLDS['rate_limit_warning']:
                self._create_alert(
                    'rate_limit', 'warning',
                    f"Cerca del límite de tokens/min: {tpm_usage:.1%}"
                )
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error checking rate limits: {e}")
    
    def _create_alert(self, alert_type: str, severity: str, message: str):
        """Crea una nueva alerta"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Evitar duplicar alertas recientes
            recent_cutoff = datetime.now() - timedelta(minutes=10)
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE alert_type = ? AND message = ? AND timestamp > ?
            ''', (alert_type, message, recent_cutoff.isoformat()))
            
            if cursor.fetchone()[0] == 0:  # No hay alertas similares recientes
                cursor.execute('''
                    INSERT INTO alerts (alert_type, severity, message)
                    VALUES (?, ?, ?)
                ''', (alert_type, severity, message))
                
                conn.commit()
                logging.warning(f"🚨 ALERT [{severity.upper()}] {alert_type}: {message}")
            
            conn.close()
            
        except Exception as e:
            logging.error(f"Error creating alert: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de rendimiento"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Métricas de las últimas 24 horas
            day_ago = datetime.now() - timedelta(days=1)
            
            # Requests totales
            cursor.execute('''
                SELECT COUNT(*), AVG(response_time), 
                       SUM(CASE WHEN request_type = 'openai' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN request_type = 'cache_hit' THEN 1 ELSE 0 END),
                       SUM(CASE WHEN request_type = 'cache_miss' THEN 1 ELSE 0 END),
                       SUM(tokens_used),
                       SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END)
                FROM request_metrics 
                WHERE timestamp > ?
            ''', (day_ago.isoformat(),))
            
            result = cursor.fetchone()
            total_requests, avg_response_time, openai_requests, cache_hits, cache_misses, total_tokens, errors = result
            
            # Calcular métricas derivadas
            cache_hit_rate = cache_hits / max(cache_hits + cache_misses, 1) if cache_hits or cache_misses else 0
            error_rate = errors / max(total_requests, 1) if total_requests else 0
            
            # Alertas activas
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE resolved = FALSE')
            active_alerts = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_requests_24h': total_requests or 0,
                'openai_requests_24h': openai_requests or 0,
                'cache_hit_rate': cache_hit_rate,
                'avg_response_time': round(avg_response_time or 0, 2),
                'total_tokens_24h': total_tokens or 0,
                'error_rate': error_rate,
                'active_alerts': active_alerts,
                'estimated_cost_24h': self._estimate_cost(total_tokens or 0)
            }
            
        except Exception as e:
            logging.error(f"Error getting performance summary: {e}")
            return {}
    
    def _estimate_cost(self, tokens: int) -> float:
        """Estima costo en USD basado en tokens"""
        # Precios aproximados para GPT-4 Turbo (actualizar según pricing actual)
        input_cost_per_1k = 0.01   # USD por 1K tokens input
        output_cost_per_1k = 0.03  # USD por 1K tokens output
        
        # Asumir 50/50 input/output (ajustar según uso real)
        estimated_cost = (tokens / 1000) * ((input_cost_per_1k + output_cost_per_1k) / 2)
        return round(estimated_cost, 4)
    
    def get_recent_alerts(self, limit: int = 10) -> List[Dict]:
        """Obtiene alertas recientes"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, alert_type, severity, message, resolved
                FROM alerts 
                ORDER BY timestamp DESC 
                LIMIT ?
            ''', (limit,))
            
            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'timestamp': row[0],
                    'type': row[1],
                    'severity': row[2],
                    'message': row[3],
                    'resolved': bool(row[4])
                })
            
            conn.close()
            return alerts
            
        except Exception as e:
            logging.error(f"Error getting recent alerts: {e}")
            return []
    
    def show_performance_dashboard(self):
        """Muestra dashboard de rendimiento en Streamlit"""
        if not st:
            return
        
        st.subheader("📊 Monitor de Rendimiento")
        
        # Obtener métricas
        summary = self.get_performance_summary()
        alerts = self.get_recent_alerts(5)
        
        # Métricas principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Requests 24h", 
                summary.get('total_requests_24h', 0),
                delta=f"OpenAI: {summary.get('openai_requests_24h', 0)}"
            )
        
        with col2:
            st.metric(
                "Cache Hit Rate", 
                f"{summary.get('cache_hit_rate', 0):.1%}",
                delta="↑ Bueno" if summary.get('cache_hit_rate', 0) > 0.5 else "↓ Mejorar"
            )
        
        with col3:
            st.metric(
                "Tiempo Respuesta", 
                f"{summary.get('avg_response_time', 0):.1f}s",
                delta="↑ Lento" if summary.get('avg_response_time', 0) > 5 else "↓ Rápido"
            )
        
        with col4:
            st.metric(
                "Costo Estimado 24h", 
                f"${summary.get('estimated_cost_24h', 0):.4f}",
                delta=f"Tokens: {summary.get('total_tokens_24h', 0):,}"
            )
        
        # Alertas activas
        if summary.get('active_alerts', 0) > 0:
            st.warning(f"🚨 {summary['active_alerts']} alertas activas")
            
            with st.expander("Ver Alertas Recientes"):
                for alert in alerts:
                    severity_icon = {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(alert['severity'], "⚪")
                    status_icon = "✅" if alert['resolved'] else "❌"
                    st.write(f"{severity_icon} {status_icon} **{alert['type']}**: {alert['message']}")
                    st.caption(f"📅 {alert['timestamp']}")

# Instancia global del monitor
performance_monitor = PerformanceMonitor()
