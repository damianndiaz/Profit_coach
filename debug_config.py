#!/usr/bin/env python3
"""
Diagnóstico completo de configuración para Streamlit Cloud
"""
import streamlit as st
import os
import sys
import logging

# Configurar logging para debug
logging.basicConfig(level=logging.INFO)

def test_streamlit_environment():
    """Testa el entorno de Streamlit y secrets"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DE CONFIGURACIÓN")
    print("=" * 50)
    
    # 1. Verificar entorno
    print(f"📍 Plataforma: {sys.platform}")
    print(f"📍 Python: {sys.version}")
    
    # 2. Verificar Streamlit
    try:
        print(f"📍 Streamlit: {st.__version__}")
        print(f"📍 Has secrets: {hasattr(st, 'secrets')}")
        
        if hasattr(st, 'secrets'):
            print(f"📍 Secrets length: {len(st.secrets)}")
            print(f"📍 Secrets keys: {list(st.secrets.keys())}")
            
            # 3. Verificar cada sección
            sections = ['database', 'openai', 'email']
            for section in sections:
                if section in st.secrets:
                    keys = list(st.secrets[section].keys())
                    print(f"✅ [{section}] keys: {keys}")
                    
                    # Verificar OpenAI específicamente
                    if section == 'openai':
                        api_key = st.secrets[section].get('api_key', '')
                        assistant_id = st.secrets[section].get('assistant_id', '')
                        print(f"🔑 api_key length: {len(api_key) if api_key else 0}")
                        print(f"🔑 api_key starts with: {'sk-' if api_key and api_key.startswith('sk-') else 'NO'}")
                        print(f"🔑 assistant_id length: {len(assistant_id) if assistant_id else 0}")
                        print(f"🔑 assistant_id starts with: {'asst_' if assistant_id and assistant_id.startswith('asst_') else 'NO'}")
                else:
                    print(f"❌ [{section}] section missing")
        else:
            print("❌ No secrets available")
            
    except Exception as e:
        print(f"❌ Error checking Streamlit: {e}")
    
    # 4. Verificar variables de entorno como fallback
    print("\n🌍 VARIABLES DE ENTORNO:")
    env_vars = ['OPENAI_API_KEY', 'OPENAI_ASSISTANT_ID', 'DATABASE_URL']
    for var in env_vars:
        value = os.getenv(var, '')
        print(f"   {var}: {'SET' if value else 'NOT SET'}")
    
    # 5. Test de config.py
    print("\n🔧 TEST DE CONFIG.PY:")
    try:
        sys.path.append('/mount/src/profit_coach')  # Ruta típica de Streamlit Cloud
        from config import config
        print(f"✅ Config importado correctamente")
        print(f"🔑 OPENAI_API_KEY: {'SET' if config.OPENAI_API_KEY else 'NOT SET'}")
        print(f"🔑 OPENAI_ASSISTANT_ID: {'SET' if config.OPENAI_ASSISTANT_ID else 'NOT SET'}")
        print(f"🗃️ DATABASE_URL: {'SET' if config.DATABASE_URL else 'NOT SET'}")
    except Exception as e:
        print(f"❌ Error importing config: {e}")

if __name__ == "__main__":
    test_streamlit_environment()
