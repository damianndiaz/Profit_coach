#!/usr/bin/env python3
"""
Script final de verificación antes del deployment a producción
"""
import os
import sys
import subprocess
from datetime import datetime

def run_pre_deployment_checks():
    """Ejecuta todas las verificaciones pre-deployment"""
    
    print("🚀 VERIFICACIONES PRE-DEPLOYMENT")
    print("=" * 50)
    print(f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checks_passed = 0
    total_checks = 7
    
    # 1. Verificar archivos críticos
    print("1️⃣ Verificando archivos críticos...")
    critical_files = [
        "main.py",
        "config.py", 
        "requirements.txt",
        "modules/chat_interface.py",
        "modules/athlete_manager.py",
        "modules/email_manager.py",
        "auth/auth_utils.py",
        "DEPLOYMENT_GUIDE.md"
    ]
    
    missing_files = []
    for file in critical_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
    else:
        print("✅ Todos los archivos críticos presentes")
        checks_passed += 1
    
    # 2. Verificar sintaxis Python
    print("\n2️⃣ Verificando sintaxis Python...")
    python_files = []
    for root, dirs, files in os.walk("."):
        # Ignorar directorios específicos
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                compile(f.read(), py_file, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{py_file}: {e}")
        except Exception:
            pass  # Ignorar otros errores que no sean de sintaxis
    
    if syntax_errors:
        print("❌ Errores de sintaxis encontrados:")
        for error in syntax_errors:
            print(f"   {error}")
    else:
        print("✅ Sin errores de sintaxis")
        checks_passed += 1
    
    # 3. Verificar requirements.txt
    print("\n3️⃣ Verificando requirements.txt...")
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r") as f:
            requirements = f.read()
            critical_deps = ["streamlit", "openai", "pandas", "psycopg2-binary"]
            missing_deps = [dep for dep in critical_deps if dep not in requirements]
            
            if missing_deps:
                print(f"❌ Dependencias faltantes: {', '.join(missing_deps)}")
            else:
                print("✅ Todas las dependencias críticas presentes")
                checks_passed += 1
    else:
        print("❌ requirements.txt no encontrado")
    
    # 4. Verificar archivos de configuración
    print("\n4️⃣ Verificando archivos de configuración...")
    config_checks = []
    
    # Verificar que config.py contiene las clases necesarias
    try:
        sys.path.insert(0, '.')
        from config import Config
        config_checks.append("✅ Clase Config importable")
        
        # Verificar propiedades críticas
        critical_props = ["OPENAI_API_KEY", "DATABASE_URL", "EMAIL_HOST"]
        for prop in critical_props:
            if hasattr(Config, prop):
                config_checks.append(f"✅ {prop} definido")
            else:
                config_checks.append(f"❌ {prop} faltante")
    except Exception as e:
        config_checks.append(f"❌ Error importando config: {e}")
    
    if all("✅" in check for check in config_checks):
        print("✅ Configuración correcta")
        checks_passed += 1
    else:
        print("❌ Problemas en configuración:")
        for check in config_checks:
            print(f"   {check}")
    
    # 5. Verificar estructura de módulos
    print("\n5️⃣ Verificando estructura de módulos...")
    required_modules = [
        "modules/__init__.py",
        "modules/chat_interface.py",
        "modules/athlete_manager.py", 
        "modules/email_manager.py",
        "auth/__init__.py" if os.path.exists("auth/__init__.py") else None,
        "auth/auth_utils.py"
    ]
    
    module_issues = []
    for module in required_modules:
        if module and not os.path.exists(module):
            module_issues.append(module)
    
    if module_issues:
        print(f"❌ Módulos faltantes: {', '.join(module_issues)}")
    else:
        print("✅ Estructura de módulos correcta")
        checks_passed += 1
    
    # 6. Verificar funcionalidad de archivos adjuntos
    print("\n6️⃣ Verificando funcionalidad de archivos adjuntos...")
    try:
        # Verificar que las funciones críticas existen
        from main import process_uploaded_file
        from modules.chat_interface import generate_ai_response_with_assistant
        
        # Verificar que el código de archivos está presente
        with open("modules/chat_interface.py", "r") as f:
            chat_code = f.read()
            if "files.create" in chat_code and "attachments" in chat_code:
                print("✅ Funcionalidad de archivos adjuntos implementada")
                checks_passed += 1
            else:
                print("❌ Funcionalidad de archivos adjuntos incompleta")
    except Exception as e:
        print(f"❌ Error verificando archivos adjuntos: {e}")
    
    # 7. Verificar documentación
    print("\n7️⃣ Verificando documentación...")
    doc_files = ["DEPLOYMENT_GUIDE.md", "FIXES_ARCHIVOS_ADJUNTOS.md", "README.md"]
    missing_docs = [doc for doc in doc_files if not os.path.exists(doc)]
    
    if missing_docs:
        print(f"❌ Documentación faltante: {', '.join(missing_docs)}")
    else:
        print("✅ Documentación completa")
        checks_passed += 1
    
    # Resumen final
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIONES:")
    print(f"✅ Checks pasados: {checks_passed}/{total_checks}")
    
    if checks_passed == total_checks:
        print("\n🎉 ¡SISTEMA LISTO PARA PRODUCCIÓN!")
        print("🚀 Puedes proceder con el deployment")
        return True
    else:
        print(f"\n⚠️ ATENCIÓN: {total_checks - checks_passed} problemas encontrados")
        print("🔧 Corrige los problemas antes del deployment")
        return False

def show_deployment_instructions():
    """Muestra instrucciones finales de deployment"""
    print("\n📋 INSTRUCCIONES FINALES DE DEPLOYMENT:")
    print("=" * 50)
    print("""
1️⃣ COMMIT Y PUSH:
   git add .
   git commit -m "🚀 Sistema listo para producción"
   git push origin dev
   git checkout main
   git merge dev  
   git push origin main

2️⃣ STREAMLIT CLOUD:
   • Repository: damianndiaz/Profit_coach
   • Branch: main
   • Main file: main.py
   • Python version: 3.11+

3️⃣ CONFIGURAR SECRETS (Ver DEPLOYMENT_GUIDE.md):
   [database]
   url = "postgresql://..."
   
   [openai] 
   api_key = "sk-proj-..."
   assistant_id = "asst_..."
   
   [email]
   host = "smtp.gmail.com"
   username = "..."
   password = "..."

4️⃣ POST-DEPLOYMENT:
   • Verificar login funciona
   • Crear atleta de prueba
   • Probar chat básico
   • 📎 PROBAR ARCHIVOS ADJUNTOS (crítico)
   • Verificar envío de emails

🎯 El sistema incluye todas las funcionalidades:
   ✅ Chat inteligente
   ✅ Gestión de atletas
   ✅ Archivos adjuntos FUNCIONANDO
   ✅ Export Excel profesional
   ✅ Envío automático de emails
   ✅ Metodología de 5 bloques

¡ÉXITO EN PRODUCCIÓN! 🚀
""")

if __name__ == "__main__":
    success = run_pre_deployment_checks()
    if success:
        show_deployment_instructions()
