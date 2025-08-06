"""
Sistema de Cache Inteligente para OpenAI
Reduce rate limits y mejora velocidad de respuesta
"""

import hashlib
import json
import time
import logging
from typing import Optional, Dict, Any
import sqlite3
import os
from datetime import datetime, timedelta

class AICacheManager:
    """Gestor de cache para respuestas de IA"""
    
    def __init__(self, cache_db_path="/workspaces/ProFit Coach/ai_cache.db"):
        self.cache_db_path = cache_db_path
        self._init_cache_db()
        
        # Configuración de cache
        self.CACHE_DURATION_HOURS = 24  # Cache válido por 24 horas
        self.MAX_CACHE_SIZE = 1000  # Máximo 1000 entradas
        
    def _init_cache_db(self):
        """Inicializar base de datos de cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS ai_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT UNIQUE,
                    athlete_context TEXT,
                    query TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    use_count INTEGER DEFAULT 1
                )
            ''')
            
            # Índices para optimizar búsquedas
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON ai_cache(query_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_created_at ON ai_cache(created_at)')
            
            conn.commit()
            conn.close()
            logging.info("✅ Cache database initialized")
            
        except Exception as e:
            logging.error(f"❌ Error initializing cache DB: {e}")
    
    def _generate_cache_key(self, athlete_data: dict, query: str) -> str:
        """Genera clave única para el cache basada en contexto del atleta y consulta"""
        # Crear contexto relevante del atleta (sin datos sensibles)
        athlete_context = {
            'sport': athlete_data.get('sport', ''),
            'level': athlete_data.get('level', ''),
            'age_range': self._get_age_range(athlete_data.get('age', 0)),  # Agrupar por rangos
            'goals': athlete_data.get('goals', ''),
            'availability': athlete_data.get('availability', '')
        }
        
        # Normalizar consulta (quitar variaciones menores)
        normalized_query = self._normalize_query(query)
        
        # Crear hash único
        cache_input = json.dumps({
            'athlete_context': athlete_context,
            'query': normalized_query
        }, sort_keys=True)
        
        return hashlib.md5(cache_input.encode()).hexdigest()
    
    def _get_age_range(self, age: int) -> str:
        """Agrupa edades en rangos para mejor cache hit"""
        if age < 18:
            return "junior"
        elif age < 25:
            return "young_adult"
        elif age < 35:
            return "adult"
        elif age < 45:
            return "mature"
        else:
            return "senior"
    
    def _normalize_query(self, query: str) -> str:
        """Normaliza consultas para mejorar cache hits"""
        # Convertir a minúsculas
        normalized = query.lower().strip()
        
        # Remover variaciones comunes que no afectan la respuesta
        replacements = {
            r'\bpor favor\b': '',
            r'\bgracias\b': '',
            r'\bhola\b': '',
            r'\bbuenos? días?\b': '',
            r'\bbuenas? tardes?\b': '',
            r'\bbuenas? noches?\b': '',
            r'\s+': ' ',  # Múltiples espacios -> uno solo
        }
        
        import re
        for pattern, replacement in replacements.items():
            normalized = re.sub(pattern, replacement, normalized)
        
        return normalized.strip()
    
    def get_cached_response(self, athlete_data: dict, query: str) -> Optional[str]:
        """Busca respuesta en cache"""
        try:
            cache_key = self._generate_cache_key(athlete_data, query)
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Buscar entrada válida
            cutoff_time = datetime.now() - timedelta(hours=self.CACHE_DURATION_HOURS)
            
            cursor.execute('''
                SELECT response, use_count 
                FROM ai_cache 
                WHERE query_hash = ? AND created_at > ?
            ''', (cache_key, cutoff_time.isoformat()))
            
            result = cursor.fetchone()
            
            if result:
                response, use_count = result
                
                # Actualizar estadísticas de uso
                cursor.execute('''
                    UPDATE ai_cache 
                    SET last_used = CURRENT_TIMESTAMP, use_count = ? 
                    WHERE query_hash = ?
                ''', (use_count + 1, cache_key))
                
                conn.commit()
                conn.close()
                
                logging.info(f"🎯 Cache hit for query (used {use_count + 1} times)")
                return response
            
            conn.close()
            return None
            
        except Exception as e:
            logging.error(f"❌ Error getting cached response: {e}")
            return None
    
    def cache_response(self, athlete_data: dict, query: str, response: str):
        """Guarda respuesta en cache"""
        try:
            cache_key = self._generate_cache_key(athlete_data, query)
            
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Insertar o actualizar
            athlete_context_str = json.dumps({
                'sport': athlete_data.get('sport', ''),
                'level': athlete_data.get('level', ''),
                'age_range': self._get_age_range(athlete_data.get('age', 0))
            })
            
            cursor.execute('''
                INSERT OR REPLACE INTO ai_cache 
                (query_hash, athlete_context, query, response, created_at, last_used, use_count)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, 1)
            ''', (cache_key, athlete_context_str, query, response))
            
            conn.commit()
            
            # Limpiar cache si excede el tamaño máximo
            self._cleanup_cache(cursor)
            
            conn.close()
            logging.info("💾 Response cached successfully")
            
        except Exception as e:
            logging.error(f"❌ Error caching response: {e}")
    
    def _cleanup_cache(self, cursor):
        """Limpia cache antiguo cuando excede el tamaño máximo"""
        try:
            # Contar entradas
            cursor.execute('SELECT COUNT(*) FROM ai_cache')
            count = cursor.fetchone()[0]
            
            if count > self.MAX_CACHE_SIZE:
                # Eliminar las entradas más antiguas y menos usadas
                entries_to_remove = count - int(self.MAX_CACHE_SIZE * 0.8)  # Dejar 80% del máximo
                
                cursor.execute('''
                    DELETE FROM ai_cache 
                    WHERE id IN (
                        SELECT id FROM ai_cache 
                        ORDER BY use_count ASC, last_used ASC 
                        LIMIT ?
                    )
                ''', (entries_to_remove,))
                
                logging.info(f"🧹 Cleaned {entries_to_remove} old cache entries")
                
        except Exception as e:
            logging.error(f"❌ Error cleaning cache: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del cache"""
        try:
            conn = sqlite3.connect(self.cache_db_path)
            cursor = conn.cursor()
            
            # Estadísticas generales
            cursor.execute('SELECT COUNT(*), AVG(use_count), MAX(use_count) FROM ai_cache')
            total, avg_uses, max_uses = cursor.fetchone()
            
            # Cache hits recientes (última hora)
            recent_cutoff = datetime.now() - timedelta(hours=1)
            cursor.execute('SELECT COUNT(*) FROM ai_cache WHERE last_used > ?', (recent_cutoff.isoformat(),))
            recent_hits = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_entries': total or 0,
                'average_uses': round(avg_uses or 0, 2),
                'max_uses': max_uses or 0,
                'recent_hits': recent_hits or 0,
                'cache_hit_rate': f"{(recent_hits / max(total, 1)) * 100:.1f}%" if total else "0%"
            }
            
        except Exception as e:
            logging.error(f"❌ Error getting cache stats: {e}")
            return {}

# Instancia global del cache manager
cache_manager = AICacheManager()
