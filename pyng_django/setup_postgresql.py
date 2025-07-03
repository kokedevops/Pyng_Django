#!/usr/bin/env python
"""
Script para configurar PostgreSQL para PYNG
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')

def create_env_file():
    """Crear archivo .env si no existe"""
    env_file = project_root / '.env'
    if not env_file.exists():
        print("Creando archivo .env...")
        db_name = input("Nombre de la base de datos [pyng_db]: ") or "pyng_db"
        db_user = input("Usuario de PostgreSQL [postgres]: ") or "postgres"
        db_password = input("Contraseña de PostgreSQL: ")
        db_host = input("Host de PostgreSQL [localhost]: ") or "localhost"
        db_port = input("Puerto de PostgreSQL [5432]: ") or "5432"
        
        env_content = f"""# Configuración de la base de datos PostgreSQL
DB_NAME={db_name}
DB_USER={db_user}
DB_PASSWORD={db_password}
DB_HOST={db_host}
DB_PORT={db_port}

# Configuración de desarrollo
DEBUG=True
"""
        env_file.write_text(env_content)
        print(f"Archivo .env creado en: {env_file}")
    else:
        print("El archivo .env ya existe.")

def check_database_connection():
    """Verificar conexión a la base de datos"""
    try:
        django.setup()
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexión a PostgreSQL exitosa!")
        return True
    except Exception as e:
        print(f"❌ Error conectando a PostgreSQL: {e}")
        return False

def run_migrations():
    """Ejecutar migraciones"""
    try:
        from django.core.management import execute_from_command_line
        print("Ejecutando migraciones...")
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones completadas!")
        return True
    except Exception as e:
        print(f"❌ Error en migraciones: {e}")
        return False

def main():
    print("=== Configuración de PostgreSQL para PYNG ===\n")
    
    # Paso 1: Crear archivo .env
    create_env_file()
    
    # Paso 2: Verificar conexión
    if not check_database_connection():
        print("\n❌ No se puede conectar a PostgreSQL.")
        print("Asegúrate de que:")
        print("1. PostgreSQL esté instalado y ejecutándose")
        print("2. La base de datos existe")
        print("3. Las credenciales en .env sean correctas")
        return
    
    # Paso 3: Ejecutar migraciones
    if run_migrations():
        print("\n✅ ¡Configuración completada!")
        print("Ahora puedes ejecutar: python manage.py runserver")
    
if __name__ == '__main__':
    main()
