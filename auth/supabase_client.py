"""
Cliente de Supabase para ProFit Coach
"""
import logging
from supabase import create_client, Client
from config import config

# Cliente global de Supabase
supabase_client: Client = None

def get_supabase_client():
    """Obtiene o crea el cliente de Supabase"""
    global supabase_client
    
    if supabase_client is None:
        if not config.SUPABASE_URL or not config.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL y SUPABASE_KEY son requeridos")
        
        logging.info(f"🔗 Conectando a Supabase: {config.SUPABASE_URL}")
        supabase_client = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        logging.info("✅ Cliente Supabase inicializado correctamente")
    
    return supabase_client

def test_supabase_connection():
    """Prueba la conexión a Supabase"""
    try:
        client = get_supabase_client()
        # Hacer una consulta simple para probar la conexión
        response = client.table('users').select('count').limit(1).execute()
        logging.info("✅ Conexión a Supabase exitosa")
        return True
    except Exception as e:
        logging.error(f"❌ Error conectando a Supabase: {e}")
        return False

# Funciones helper para operaciones comunes
def execute_query(table_name, operation, **kwargs):
    """Ejecuta una operación en Supabase"""
    try:
        client = get_supabase_client()
        table = client.table(table_name)
        
        if operation == 'select':
            columns = kwargs.get('columns', '*')
            query = table.select(columns)
            
            # Aplicar filtros si existen
            if 'filters' in kwargs:
                for filter_dict in kwargs['filters']:
                    query = query.eq(filter_dict['column'], filter_dict['value'])
            
            # Aplicar límite si existe
            if 'limit' in kwargs:
                query = query.limit(kwargs['limit'])
            
            return query.execute()
            
        elif operation == 'insert':
            return table.insert(kwargs['data']).execute()
            
        elif operation == 'update':
            query = table.update(kwargs['data'])
            if 'filters' in kwargs:
                for filter_dict in kwargs['filters']:
                    query = query.eq(filter_dict['column'], filter_dict['value'])
            return query.execute()
            
        elif operation == 'delete':
            query = table.delete()
            if 'filters' in kwargs:
                for filter_dict in kwargs['filters']:
                    query = query.eq(filter_dict['column'], filter_dict['value'])
            return query.execute()
            
    except Exception as e:
        logging.error(f"❌ Error ejecutando operación {operation} en tabla {table_name}: {e}")
        raise

# Funciones específicas para las tablas de la aplicación
def create_user(username, email, password_hash):
    """Crea un nuevo usuario"""
    return execute_query(
        'users',
        'insert',
        data={'username': username, 'email': email, 'password_hash': password_hash}
    )

def get_user_by_username(username):
    """Obtiene un usuario por nombre de usuario"""
    response = execute_query(
        'users',
        'select',
        filters=[{'column': 'username', 'value': username}],
        limit=1
    )
    return response.data[0] if response.data else None

def get_user_by_email(email):
    """Obtiene un usuario por email"""
    response = execute_query(
        'users',
        'select',
        filters=[{'column': 'email', 'value': email}],
        limit=1
    )
    return response.data[0] if response.data else None

def get_athletes_by_user_id(user_id):
    """Obtiene todos los atletas de un usuario"""
    response = execute_query(
        'athletes',
        'select',
        filters=[{'column': 'user_id', 'value': user_id}]
    )
    return response.data

def create_athlete(user_id, name, age, sport, position, weight, height):
    """Crea un nuevo atleta"""
    return execute_query(
        'athletes',
        'insert',
        data={
            'user_id': user_id,
            'name': name,
            'age': age,
            'sport': sport,
            'position': position,
            'weight': weight,
            'height': height
        }
    )

def update_athlete(athlete_id, **updates):
    """Actualiza un atleta"""
    return execute_query(
        'athletes',
        'update',
        data=updates,
        filters=[{'column': 'id', 'value': athlete_id}]
    )

def delete_athlete(athlete_id):
    """Elimina un atleta"""
    return execute_query(
        'athletes',
        'delete',
        filters=[{'column': 'id', 'value': athlete_id}]
    )

def get_chat_history_by_thread(thread_id, limit=50):
    """Obtiene el historial de chat de un thread"""
    response = execute_query(
        'chat_messages',
        'select',
        filters=[{'column': 'thread_id', 'value': thread_id}],
        limit=limit
    )
    return response.data

def save_chat_message(thread_id, message, is_user=True):
    """Guarda un mensaje de chat"""
    return execute_query(
        'chat_messages',
        'insert',
        data={
            'thread_id': thread_id,
            'message': message,
            'is_user': is_user
        }
    )
