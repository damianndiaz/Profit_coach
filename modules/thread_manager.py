"""
Sistema Inteligente de Gestión de Threads para OpenAI
Resuelve problemas de tokens, memoria y contexto
"""

import logging
import time
import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from modules.chat_manager import get_or_create_thread_id
from auth.database import get_db_cursor
import os

class ThreadManager:
    """Gestor inteligente de threads con rotación automática"""
    
    def __init__(self, db_path="/workspaces/ProFit Coach/performance_monitor.db"):
        self.db_path = db_path
        self._init_thread_monitoring()
        
        # Configuración de límites
        self.MAX_THREAD_TOKENS = 25000  # Límite por thread (conservador)
        self.MAX_THREAD_MESSAGES = 30   # Máximo mensajes por thread
        self.THREAD_LIFETIME_HOURS = 12 # Rotar threads cada 12 horas
        self.TOKEN_SAFETY_MARGIN = 5000 # Margen de seguridad
        
    def _init_thread_monitoring(self):
        """Inicializar tabla de monitoreo de threads con manejo robusto de errores"""
        try:
            # 🔒 SEGURIDAD: Verificar si el directorio existe y tiene permisos
            db_dir = os.path.dirname(self.db_path)
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            # 🔒 OPTIMIZACIÓN: Conexión con timeout para evitar locks
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            conn.execute("PRAGMA journal_mode=WAL")  # Write-Ahead Logging para mejor concurrencia
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS thread_monitoring (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    athlete_id INTEGER NOT NULL,
                    thread_id TEXT NOT NULL,
                    estimated_tokens INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    rotation_reason TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("✅ Thread monitoring database initialized")
            
        except Exception as e:
            logging.error(f"❌ Error inicializando thread monitoring: {e}")
            # 🔧 FALLBACK: Si SQLite falla, usar solo PostgreSQL
            self.db_path = None
            logging.warning("⚠️ Thread monitoring deshabilitado - funcionando sin cache local")
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_thread_athlete 
                ON thread_monitoring(athlete_id, is_active)
            ''')
            
            conn.commit()
            conn.close()
            logging.info("✅ Thread monitoring table initialized")
            
        except Exception as e:
            logging.error(f"❌ Error initializing thread monitoring: {e}")
    
    def estimate_message_tokens(self, message: str) -> int:
        """Estima tokens de un mensaje (aproximación conservadora)"""
        # Aproximación: 1 token ≈ 4 caracteres en español
        base_tokens = len(message) // 3  # Más conservador
        
        # Penalización por contexto de metodología 5 bloques
        if any(keyword in message.lower() for keyword in ['rutina', 'entrenamiento', 'ejercicio', '5 bloques']):
            base_tokens *= 1.3  # 30% más tokens por contexto deportivo
            
        return int(base_tokens)
    
    def should_rotate_thread(self, athlete_id: int) -> Tuple[bool, str]:
        """Determina si el thread necesita rotación"""
        conn = None
        try:
            # 🔧 PROTECCIÓN: Verificar si SQLite está disponible
            if not self.db_path:
                return False, "SQLite no disponible - usando solo PostgreSQL"
                
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT estimated_tokens, message_count, created_at, last_used 
                FROM thread_monitoring 
                WHERE athlete_id = ? AND is_active = TRUE
                ORDER BY last_used DESC LIMIT 1
            ''', (athlete_id,))
            
            result = cursor.fetchone()
            conn.close()
            conn = None  # Marcar como cerrada
            
            if not result:
                return False, "No hay thread activo"
            
            tokens, messages, created_str, last_used_str = result
            
            # Verificar límite de tokens
            if tokens > self.MAX_THREAD_TOKENS:
                return True, f"Tokens excedidos: {tokens}/{self.MAX_THREAD_TOKENS}"
            
            # Verificar límite de mensajes
            if messages > self.MAX_THREAD_MESSAGES:
                return True, f"Mensajes excedidos: {messages}/{self.MAX_THREAD_MESSAGES}"
            
            # Verificar tiempo de vida
            created_at = datetime.fromisoformat(created_str)
            if datetime.now() - created_at > timedelta(hours=self.THREAD_LIFETIME_HOURS):
                return True, f"Thread expirado: {self.THREAD_LIFETIME_HOURS}h límite"
            
            # Verificar proximidad al límite (prevención)
            if tokens > (self.MAX_THREAD_TOKENS - self.TOKEN_SAFETY_MARGIN):
                return True, f"Cerca del límite de tokens: {tokens}"
            
            return False, "Thread saludable"
            
        except Exception as e:
            logging.error(f"❌ Error checking thread rotation: {e}")
            # Cerrar conexión de forma segura en caso de error
            if conn:
                try:
                    conn.close()
                except Exception as close_error:
                    logging.warning(f"⚠️ Error cerrando conexión en should_rotate_thread: {close_error}")
            # Retornar False para no bloquear el sistema cuando SQLite falla
            return False, f"Error SQLite, usando thread existente: {e}"
    
    def rotate_thread(self, athlete_id: int, reason: str, openai_create_thread_func) -> str:
        """Rota el thread de un atleta creando uno nuevo"""
        conn = None
        try:
            # 🔧 PROTECCIÓN: Solo usar SQLite si está disponible
            if self.db_path:
                # 1. Marcar thread actual como inactivo en SQLite (monitoreo local)
                conn = sqlite3.connect(self.db_path, timeout=10.0)
                conn.execute("PRAGMA journal_mode=WAL")
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE thread_monitoring 
                    SET is_active = FALSE, rotation_reason = ?
                    WHERE athlete_id = ? AND is_active = TRUE
                ''', (reason, athlete_id))
                
                conn.commit()
            
            # 2. Crear nuevo thread usando OpenAI
            new_thread = openai_create_thread_func()
            new_thread_id = new_thread.id
            
            # 3. Registrar nuevo thread en ambas bases de datos
            if self.db_path and conn:
                cursor.execute('''
                    INSERT INTO thread_monitoring 
                    (athlete_id, thread_id, estimated_tokens, message_count, created_at, last_used, is_active)
                    VALUES (?, ?, 0, 0, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, TRUE)
                ''', (athlete_id, new_thread_id))
                
                conn.commit()
            
            # 4. Actualizar en PostgreSQL (sistema principal)
            try:
                with get_db_cursor() as cursor:
                    cursor.execute(
                        "UPDATE athletes SET thread_id = %s WHERE id = %s",
                        (new_thread_id, athlete_id)
                    )
                    logging.info(f"🔄 Thread actualizado en PostgreSQL para atleta {athlete_id}")
            except Exception as pg_error:
                logging.warning(f"⚠️ Error actualizando PostgreSQL: {pg_error}")
                # Continuar aunque PostgreSQL falle
            
            # 5. Cerrar conexión SQLite de forma segura
            if conn:
                conn.close()
            
            logging.info(f"🔄 Thread rotado para atleta {athlete_id}: {reason}")
            logging.info(f"🆕 Nuevo thread: {new_thread_id}")
            
            return new_thread_id
            
        except Exception as e:
            logging.error(f"❌ Error rotating thread: {e}")
            # Cerrar conexión en caso de error de forma segura
            if conn:
                try:
                    conn.close()
                except Exception as close_error:
                    logging.warning(f"⚠️ Error cerrando conexión SQLite: {close_error}")
            # No hacer raise para no bloquear el flujo principal
            # En su lugar, intentar obtener thread existente
            try:
                existing_thread_id = get_or_create_thread_id(athlete_id, openai_create_thread_func)
                logging.info(f"🔄 Usando thread existente como fallback: {existing_thread_id}")
                return existing_thread_id
            except Exception as fallback_error:
                logging.error(f"❌ Fallback también falló: {fallback_error}")
                raise
    
    def get_or_create_smart_thread(self, athlete_id: int, openai_create_thread_func) -> str:
        """Obtiene thread existente o crea uno nuevo con lógica inteligente"""
        try:
            # Verificar si necesita rotación
            should_rotate, reason = self.should_rotate_thread(athlete_id)
            
            if should_rotate:
                logging.info(f"🔄 Rotando thread para atleta {athlete_id}: {reason}")
                return self.rotate_thread(athlete_id, reason, openai_create_thread_func)
            
            # Usar thread existente
            thread_id = get_or_create_thread_id(athlete_id, openai_create_thread_func)
            
            # Asegurar que está en monitoreo
            self._ensure_thread_monitoring(athlete_id, thread_id)
            
            return thread_id
            
        except Exception as e:
            logging.error(f"❌ Error en get_or_create_smart_thread: {e}")
            # Fallback al método original
            return get_or_create_thread_id(athlete_id, openai_create_thread_func)
    
    def log_message_tokens(self, athlete_id: int, message: str, response: str = ""):
        """Registra tokens usados en un mensaje"""
        conn = None
        try:
            # 🔧 PROTECCIÓN: Solo usar SQLite si está disponible
            if not self.db_path:
                logging.debug("⚠️ SQLite no disponible - skipping token logging")
                return
                
            message_tokens = self.estimate_message_tokens(message)
            response_tokens = self.estimate_message_tokens(response) if response else 0
            total_tokens = message_tokens + response_tokens
            
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE thread_monitoring 
                SET estimated_tokens = estimated_tokens + ?,
                    message_count = message_count + 1,
                    last_used = CURRENT_TIMESTAMP
                WHERE athlete_id = ? AND is_active = TRUE
            ''', (total_tokens, athlete_id))
            
            conn.commit()
            conn.close()
            conn = None  # Marcar como cerrada
            
            logging.info(f"📊 Tokens registrados para atleta {athlete_id}: +{total_tokens}")
            
        except Exception as e:
            logging.error(f"❌ Error logging message tokens: {e}")
            # Cerrar conexión de forma segura
            if conn:
                try:
                    conn.close()
                except Exception as close_error:
                    logging.warning(f"⚠️ Error cerrando conexión en log_message_tokens: {close_error}")
            # No fallar la operación principal por esto
    
    def _ensure_thread_monitoring(self, athlete_id: int, thread_id: str):
        """Asegura que el thread esté en la tabla de monitoreo"""
        conn = None
        try:
            # 🔧 PROTECCIÓN: Solo usar SQLite si está disponible
            if not self.db_path:
                return
                
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR IGNORE INTO thread_monitoring 
                (athlete_id, thread_id, estimated_tokens, message_count)
                VALUES (?, ?, 0, 0)
            ''', (athlete_id, thread_id))
            
            conn.commit()
            conn.close()
            conn = None  # Marcar como cerrada
            
        except Exception as e:
            logging.error(f"❌ Error ensuring thread monitoring: {e}")
            # Cerrar conexión de forma segura
            if conn:
                try:
                    conn.close()
                except Exception as close_error:
                    logging.warning(f"⚠️ Error cerrando conexión en _ensure_thread_monitoring: {close_error}")
    
    def get_thread_stats(self, athlete_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas del thread actual"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, timeout=10.0)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT thread_id, estimated_tokens, message_count, created_at, last_used
                FROM thread_monitoring 
                WHERE athlete_id = ? AND is_active = TRUE
                ORDER BY last_used DESC LIMIT 1
            ''', (athlete_id,))
            
            result = cursor.fetchone()
            conn.close()
            conn = None  # Marcar como cerrada
            
            if not result:
                return {'status': 'No thread activo'}
            
            thread_id, tokens, messages, created, last_used = result
            
            # Calcular porcentajes
            token_usage = (tokens / self.MAX_THREAD_TOKENS) * 100
            message_usage = (messages / self.MAX_THREAD_MESSAGES) * 100
            
            # Tiempo desde creación
            created_dt = datetime.fromisoformat(created)
            age_hours = (datetime.now() - created_dt).total_seconds() / 3600
            
            return {
                'thread_id': thread_id,
                'tokens_used': tokens,
                'tokens_limit': self.MAX_THREAD_TOKENS,
                'token_usage_percent': round(token_usage, 1),
                'messages_count': messages,
                'messages_limit': self.MAX_THREAD_MESSAGES,
                'message_usage_percent': round(message_usage, 1),
                'age_hours': round(age_hours, 1),
                'lifetime_limit_hours': self.THREAD_LIFETIME_HOURS,
                'status': 'healthy' if token_usage < 80 and message_usage < 80 else 'warning',
                'next_rotation': 'soon' if token_usage > 80 or message_usage > 80 or age_hours > (self.THREAD_LIFETIME_HOURS - 2) else 'not_needed'
            }
            
        except Exception as e:
            logging.error(f"❌ Error getting thread stats: {e}")
            # Cerrar conexión de forma segura
            if conn:
                try:
                    conn.close()
                except Exception as close_error:
                    logging.warning(f"⚠️ Error cerrando conexión en get_thread_stats: {close_error}")
            return {'status': 'error', 'error': str(e)}
    
    def get_all_threads_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de todos los threads"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Threads activos
            cursor.execute('''
                SELECT COUNT(*), AVG(estimated_tokens), AVG(message_count), 
                       SUM(CASE WHEN estimated_tokens > ? THEN 1 ELSE 0 END)
                FROM thread_monitoring 
                WHERE is_active = TRUE
            ''', (self.MAX_THREAD_TOKENS * 0.8,))
            
            active_result = cursor.fetchone()
            
            # Threads rotados en últimas 24h
            yesterday = datetime.now() - timedelta(hours=24)
            cursor.execute('''
                SELECT COUNT(*), rotation_reason
                FROM thread_monitoring 
                WHERE is_active = FALSE AND last_used > ?
                GROUP BY rotation_reason
            ''', (yesterday.isoformat(),))
            
            rotation_stats = cursor.fetchall()
            
            conn.close()
            
            active_count, avg_tokens, avg_messages, high_usage_count = active_result or (0, 0, 0, 0)
            
            return {
                'active_threads': active_count or 0,
                'average_tokens': round(avg_tokens or 0),
                'average_messages': round(avg_messages or 0),
                'high_usage_threads': high_usage_count or 0,
                'rotations_24h': sum(count for count, _ in rotation_stats),
                'rotation_reasons': dict(rotation_stats),
                'system_health': 'good' if (high_usage_count or 0) < (active_count or 0) * 0.3 else 'attention_needed'
            }
            
        except Exception as e:
            logging.error(f"❌ Error getting threads summary: {e}")
            return {'status': 'error', 'error': str(e)}

# Instancia global del thread manager
thread_manager = ThreadManager()
