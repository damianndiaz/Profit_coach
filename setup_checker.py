"""
Script de inicialización y verificación de ProFit Coach
Ejecuta este script para verificar que todo esté configurado correctamente
"""

import sys
import os
import logging
from datetime import datetime

# Agregar el directorio actual al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def setup_logging():
    """Configura el logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('setup.log')
        ]
    )

def check_environment():
    """Verifica las variables de entorno"""
    print("🔍 Verificando configuración del entorno...")
    
    try:
        from config import config
        warnings = config.validate_config()
        
        print("✅ Configuración básica válida")
        
        if warnings:
            print("\n⚠️  Advertencias de configuración:")
            for warning in warnings:
                print(f"   - {warning}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False

def check_dependencies():
    """Verifica las dependencias"""
    print("\n📦 Verificando dependencias...")
    
    required_packages = [
        'streamlit',
        'psycopg2',
        'bcrypt',
        'openai',
        'pandas',
        'python-dotenv',
        'yagmail'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - NO INSTALADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Faltan dependencias: {', '.join(missing_packages)}")
        print("   Ejecuta: pip install -r requirements_fixed.txt")
        return False
    
    return True

def check_database():
    """Verifica la conexión a la base de datos"""
    print("\n🗃️  Verificando conexión a base de datos...")
    
    try:
        from auth.database import test_db_connection, initialize_connection_pool
        
        if test_db_connection():
            print("   ✅ Conexión a base de datos exitosa")
            
            # Inicializar pool
            initialize_connection_pool()
            print("   ✅ Pool de conexiones inicializado")
            
            return True
        else:
            print("   ❌ No se pudo conectar a la base de datos")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar base de datos: {e}")
        return False

def check_openai():
    """Verifica la configuración de OpenAI"""
    print("\n🤖 Verificando configuración de OpenAI...")
    
    try:
        import openai
        from config import config
        
        if not config.OPENAI_API_KEY:
            print("   ⚠️  OPENAI_API_KEY no configurada")
            return False
        
        if not config.OPENAI_ASSISTANT_ID:
            print("   ⚠️  OPENAI_ASSISTANT_ID no configurada")
            return False
        
        # Configurar cliente
        openai.api_key = config.OPENAI_API_KEY
        
        # Test básico (solo verifica que la clave sea válida)
        try:
            # Intentar crear un thread de prueba
            thread = openai.beta.threads.create()
            if thread.id:
                print("   ✅ API Key de OpenAI válida")
                print("   ✅ Assistant ID configurado")
                return True
        except Exception as api_error:
            print(f"   ❌ Error con API de OpenAI: {api_error}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error al verificar OpenAI: {e}")
        return False

def initialize_database():
    """Inicializa las tablas de la base de datos"""
    print("\n🏗️  Inicializando tablas de base de datos...")
    
    try:
        from auth.auth_utils import create_users_table
        from modules.athlete_manager import create_athletes_table
        from modules.chat_manager import create_chat_tables, create_thread_table
        
        create_users_table()
        print("   ✅ Tabla de usuarios")
        
        create_athletes_table()
        print("   ✅ Tabla de atletas")
        
        create_chat_tables()
        print("   ✅ Tablas de chat")
        
        create_thread_table()
        print("   ✅ Tabla de threads")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error al inicializar tablas: {e}")
        return False

def create_sample_data():
    """Crea datos de ejemplo (opcional)"""
    print("\n📊 ¿Deseas crear datos de ejemplo? (s/n): ", end="")
    response = input().lower().strip()
    
    if response in ['s', 'si', 'y', 'yes']:
        try:
            from auth.auth_utils import register_user
            from modules.athlete_manager import add_athlete, get_athletes_by_user
            from auth.auth_utils import get_user_id
            
            # Crear usuario de ejemplo
            print("   📝 Creando usuario de ejemplo...")
            success, message = register_user("admin", "admin123")
            
            if success:
                print("   ✅ Usuario 'admin' creado (contraseña: admin123)")
                
                # Obtener ID del usuario
                user_id = get_user_id("admin")
                
                if user_id:
                    # Crear atleta de ejemplo
                    print("   🏃‍♂️ Creando atleta de ejemplo...")
                    success, message = add_athlete(
                        user_id,
                        "Juan Pérez",
                        "Fútbol",
                        "Intermedio",
                        "Mejorar resistencia y velocidad",
                        "juan.perez@email.com"
                    )
                    
                    if success:
                        print("   ✅ Atleta 'Juan Pérez' creado")
                    else:
                        print(f"   ⚠️  No se pudo crear atleta: {message}")
            else:
                print(f"   ⚠️  No se pudo crear usuario: {message}")
                
        except Exception as e:
            print(f"   ❌ Error al crear datos de ejemplo: {e}")

def show_startup_info():
    """Muestra información de inicio"""
    print("\n🚀 Información de inicio:")
    print("   - Para iniciar la aplicación: streamlit run main_improved.py")
    print("   - Para usar la versión original: streamlit run main.py")
    print("   - Archivos de log: profit_coach.log, setup.log")
    print("   - Usuario de ejemplo: admin / admin123 (si se creó)")
    print("\n📚 URLs útiles:")
    print("   - Aplicación local: http://localhost:8501")
    print("   - Streamlit docs: https://docs.streamlit.io")
    print("   - OpenAI docs: https://platform.openai.com/docs")

def main():
    """Función principal de verificación"""
    setup_logging()
    
    print("=" * 60)
    print("🏃‍♂️ PROFIT COACH - SCRIPT DE INICIALIZACIÓN")
    print("=" * 60)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Lista de verificaciones
    checks = [
        ("Entorno", check_environment),
        ("Dependencias", check_dependencies),
        ("Base de datos", check_database),
        ("OpenAI", check_openai),
        ("Inicialización BD", initialize_database)
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        try:
            results[check_name] = check_function()
        except Exception as e:
            print(f"❌ Error en verificación de {check_name}: {e}")
            results[check_name] = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("📋 RESUMEN DE VERIFICACIONES")
    print("=" * 60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASÓ" if passed else "❌ FALLÓ"
        print(f"   {check_name:<20} {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 ¡Todas las verificaciones pasaron!")
        create_sample_data()
        show_startup_info()
    else:
        print("\n⚠️  Algunas verificaciones fallaron. Revisa los errores arriba.")
        print("   Consulta la documentación o contacta al administrador.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
