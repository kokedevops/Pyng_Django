#!/usr/bin/env python
"""
Script para migrar datos de SQLite a PostgreSQL
"""
import os
import sys
import django
from pathlib import Path
import json

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')

def export_sqlite_data():
    """Exportar datos de SQLite a JSON"""
    print("Configurando para SQLite...")
    
    # Temporalmente cambiar a SQLite
    from django.conf import settings
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': project_root / 'pyng.sqlite',
    }
    
    django.setup()
    
    from django.core.management import call_command
    from django.db import connection
    
    # Verificar si existe la base de datos SQLite
    sqlite_file = project_root / 'pyng.sqlite'
    if not sqlite_file.exists():
        print(f"❌ No se encontró la base de datos SQLite en: {sqlite_file}")
        return False
    
    print("Exportando datos de SQLite...")
    try:
        # Exportar datos a JSON
        with open('data_backup.json', 'w', encoding='utf-8') as f:
            call_command('dumpdata', 
                        '--natural-foreign', 
                        '--natural-primary',
                        '--exclude=contenttypes',
                        '--exclude=auth.permission',
                        stdout=f)
        print("✅ Datos exportados a data_backup.json")
        return True
    except Exception as e:
        print(f"❌ Error exportando datos: {e}")
        return False

def import_postgresql_data():
    """Importar datos a PostgreSQL"""
    print("Configurando para PostgreSQL...")
    
    # Recargar configuración para PostgreSQL
    from django.conf import settings
    from decouple import config
    
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='pyng_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
    
    # Reconectar Django
    from django.db import connection
    connection.close()
    
    print("Importando datos a PostgreSQL...")
    try:
        from django.core.management import call_command
        
        # Verificar si existe el archivo de respaldo
        if not os.path.exists('data_backup.json'):
            print("❌ No se encontró data_backup.json")
            return False
        
        # Importar datos
        call_command('loaddata', 'data_backup.json')
        print("✅ Datos importados a PostgreSQL")
        return True
    except Exception as e:
        print(f"❌ Error importando datos: {e}")
        return False

def main():
    print("=== Migración de datos SQLite → PostgreSQL ===\n")
    
    # Verificar que existe el archivo .env
    env_file = project_root / '.env'
    if not env_file.exists():
        print("❌ No se encontró el archivo .env")
        print("Ejecuta primero: python setup_postgresql.py")
        return
    
    # Paso 1: Exportar datos de SQLite
    if export_sqlite_data():
        # Paso 2: Importar datos a PostgreSQL
        if import_postgresql_data():
            print("\n✅ ¡Migración completada!")
            print("Los datos se han migrado exitosamente de SQLite a PostgreSQL")
            
            # Limpiar archivo temporal
            if os.path.exists('data_backup.json'):
                os.remove('data_backup.json')
                print("Archivo temporal eliminado")
        else:
            print("\n❌ Error en la importación")
    else:
        print("\n❌ Error en la exportación")

if __name__ == '__main__':
    main()
