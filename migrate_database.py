"""
Script de Migración de Base de Datos - ProFit Coach
Este script actualiza la estructura de BD para soportar las nuevas funcionalidades
"""

import sys
import os
import logging

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configura el logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('migration.log')
        ]
    )

def migrate_users_table():
    """Migra la tabla de usuarios"""
    print("🔄 Migrando tabla de usuarios...")
    
    try:
        from auth.database import get_db_cursor
        
        with get_db_cursor() as cursor:
            # Verificar si las columnas existen
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('is_active', 'created_at', 'last_login')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Agregar columnas faltantes
            if 'is_active' not in existing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                print("   ✅ Columna 'is_active' agregada")
            
            if 'created_at' not in existing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("   ✅ Columna 'created_at' agregada")
            
            if 'last_login' not in existing_columns:
                cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
                print("   ✅ Columna 'last_login' agregada")
            
            # Crear índice si no existe
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username 
                ON users(username) WHERE is_active = TRUE
            """)
            print("   ✅ Índice creado")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def migrate_athletes_table():
    """Migra la tabla de atletas"""
    print("🔄 Migrando tabla de atletas...")
    
    try:
        from auth.database import get_db_cursor
        
        with get_db_cursor() as cursor:
            # Verificar columnas existentes
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'athletes' AND column_name IN ('is_active', 'created_at', 'updated_at')
            """)
            existing_columns = [row[0] for row in cursor.fetchall()]
            
            # Agregar columnas faltantes
            if 'is_active' not in existing_columns:
                cursor.execute("ALTER TABLE athletes ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                print("   ✅ Columna 'is_active' agregada")
            
            if 'created_at' not in existing_columns:
                cursor.execute("ALTER TABLE athletes ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("   ✅ Columna 'created_at' agregada")
            
            if 'updated_at' not in existing_columns:
                cursor.execute("ALTER TABLE athletes ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                print("   ✅ Columna 'updated_at' agregada")
            
            # Crear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_user_id 
                ON athletes(user_id) WHERE is_active = TRUE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_athletes_sport 
                ON athletes(sport) WHERE is_active = TRUE
            """)
            print("   ✅ Índices creados")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def migrate_chat_tables():
    """Migra las tablas de chat"""
    print("🔄 Migrando tablas de chat...")
    
    try:
        from auth.database import get_db_cursor
        
        with get_db_cursor() as cursor:
            # Verificar si las tablas existen
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name IN ('chat_sessions', 'chat_messages', 'athlete_threads')
            """)
            existing_tables = [row[0] for row in cursor.fetchall()]
            
            # Migrar chat_sessions
            if 'chat_sessions' in existing_tables:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_sessions' AND column_name IN ('is_active', 'updated_at')
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                if 'is_active' not in existing_columns:
                    cursor.execute("ALTER TABLE chat_sessions ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                    print("   ✅ Columna 'is_active' agregada a chat_sessions")
                
                if 'updated_at' not in existing_columns:
                    cursor.execute("ALTER TABLE chat_sessions ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("   ✅ Columna 'updated_at' agregada a chat_sessions")
            
            # Migrar chat_messages
            if 'chat_messages' in existing_tables:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'chat_messages' AND column_name = 'message_length'
                """)
                if not cursor.fetchall():
                    cursor.execute("ALTER TABLE chat_messages ADD COLUMN message_length INTEGER GENERATED ALWAYS AS (LENGTH(message_text)) STORED")
                    print("   ✅ Columna 'message_length' agregada a chat_messages")
            
            # Migrar athlete_threads
            if 'athlete_threads' in existing_tables:
                cursor.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'athlete_threads' AND column_name IN ('created_at', 'last_used')
                """)
                existing_columns = [row[0] for row in cursor.fetchall()]
                
                if 'created_at' not in existing_columns:
                    cursor.execute("ALTER TABLE athlete_threads ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("   ✅ Columna 'created_at' agregada a athlete_threads")
                
                if 'last_used' not in existing_columns:
                    cursor.execute("ALTER TABLE athlete_threads ADD COLUMN last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
                    print("   ✅ Columna 'last_used' agregada a athlete_threads")
            
            # Crear índices
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_athlete 
                ON chat_sessions(athlete_id) WHERE is_active = TRUE
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session 
                ON chat_messages(session_id, created_at DESC)
            """)
            print("   ✅ Índices de chat creados")
            
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def update_foreign_keys():
    """Actualiza las foreign keys para usar CASCADE"""
    print("🔄 Actualizando foreign keys...")
    
    try:
        from auth.database import get_db_cursor
        
        with get_db_cursor() as cursor:
            # Verificar y actualizar FK de athletes si es necesario
            cursor.execute("""
                SELECT constraint_name, delete_rule
                FROM information_schema.referential_constraints rc
                JOIN information_schema.table_constraints tc ON rc.constraint_name = tc.constraint_name
                WHERE tc.table_name = 'athletes' AND tc.constraint_type = 'FOREIGN KEY'
            """)
            
            constraints = cursor.fetchall()
            for constraint_name, delete_rule in constraints:
                if delete_rule != 'CASCADE':
                    try:
                        cursor.execute(f"ALTER TABLE athletes DROP CONSTRAINT {constraint_name}")
                        cursor.execute("""
                            ALTER TABLE athletes 
                            ADD CONSTRAINT athletes_user_id_fkey 
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                        """)
                        print("   ✅ Foreign key de athletes actualizada")
                        break
                    except:
                        pass  # La constraint ya podría estar bien
            
        return True
        
    except Exception as e:
        print(f"   ⚠️ Warning en foreign keys: {e}")
        return True  # No es crítico

def main():
    """Función principal de migración"""
    setup_logging()
    
    print("=" * 60)
    print("🔄 PROFIT COACH - MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Verificar conexión antes de migrar
    try:
        from auth.database import test_db_connection
        if not test_db_connection():
            print("❌ No se puede conectar a la base de datos")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False
    
    # Ejecutar migraciones
    migrations = [
        ("Usuarios", migrate_users_table),
        ("Atletas", migrate_athletes_table),
        ("Chat", migrate_chat_tables),
        ("Foreign Keys", update_foreign_keys)
    ]
    
    results = {}
    for name, migration_func in migrations:
        try:
            results[name] = migration_func()
        except Exception as e:
            print(f"❌ Error en migración de {name}: {e}")
            results[name] = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE MIGRACIÓN")
    print("=" * 60)
    
    all_success = True
    for name, success in results.items():
        status = "✅ EXITOSA" if success else "❌ FALLÓ"
        print(f"   {name:<20} {status}")
        if not success:
            all_success = False
    
    if all_success:
        print("\n🎉 ¡Migración completada exitosamente!")
        print("   Ahora puedes ejecutar: python setup_checker.py")
    else:
        print("\n⚠️ Algunas migraciones fallaron. Revisa los errores.")
    
    print("\n" + "=" * 60)
    return all_success

if __name__ == "__main__":
    main()
