#!/usr/bin/env python
"""
Comando de administración para PYNG con PostgreSQL
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')

def check_status():
    """Verificar estado de la aplicación"""
    print("=== Estado de PYNG ===\n")
    
    try:
        django.setup()
        from django.db import connection
        from django.contrib.auth.models import User
        from monitor.models import Hosts, WebThemes, Polling
        
        # Verificar conexión DB
        cursor = connection.cursor()
        cursor.execute("SELECT version()")
        db_version = cursor.fetchone()[0]
        print(f"✅ Base de datos: {db_version}")
        
        # Estadísticas
        print(f"👥 Usuarios: {User.objects.count()}")
        print(f"🖥️  Hosts: {Hosts.objects.count()}")
        print(f"🎨 Temas: {WebThemes.objects.count()}")
        
        # Configuración
        polling = Polling.objects.first()
        if polling:
            print(f"⏱️  Intervalo de monitoreo: {polling.poll_interval}s")
        
        # Tema activo
        active_theme = WebThemes.objects.filter(active=True).first()
        if active_theme:
            print(f"🎨 Tema activo: {active_theme.theme_name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def reset_database():
    """Resetear base de datos"""
    print("⚠️  ¿Estás seguro de que quieres resetear la base de datos?")
    confirm = input("Escribe 'SI' para confirmar: ")
    
    if confirm == 'SI':
        try:
            django.setup()
            from django.core.management import call_command
            
            print("Reseteando migraciones...")
            call_command('migrate', 'monitor', 'zero', '--fake')
            
            print("Aplicando migraciones...")
            call_command('migrate')
            
            print("✅ Base de datos reseteada")
            
            # Crear superusuario
            create_user = input("¿Crear superusuario? (s/n): ")
            if create_user.lower() == 's':
                call_command('createsuperuser')
                
        except Exception as e:
            print(f"❌ Error: {e}")

def create_backup():
    """Crear backup de la base de datos"""
    try:
        from decouple import config
        import subprocess
        from datetime import datetime
        
        db_name = config('DB_NAME', default='pyng_db')
        db_user = config('DB_USER', default='postgres')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"backup_pyng_{timestamp}.sql"
        
        print(f"Creando backup: {backup_file}")
        
        # Comando pg_dump
        cmd = [
            'pg_dump',
            '-h', db_host,
            '-p', db_port,
            '-U', db_user,
            '-f', backup_file,
            db_name
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Backup creado: {backup_file}")
        else:
            print(f"❌ Error creando backup: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def show_help():
    """Mostrar ayuda"""
    print("""
=== Comandos disponibles ===

python admin.py status       - Mostrar estado de la aplicación
python admin.py test         - Probar conexión a PostgreSQL

Gestión de usuarios:
python admin.py createadmin  - Crear usuario administrador
python admin.py createuser   - Crear usuario regular
python admin.py listusers    - Listar todos los usuarios
python admin.py deleteuser   - Eliminar un usuario

Base de datos:
python admin.py reset        - Resetear base de datos (¡CUIDADO!)
python admin.py backup       - Crear backup de la base de datos
python admin.py help         - Mostrar esta ayuda

=== Comandos Django útiles ===

python manage.py shell              - Abrir shell de Django
python manage.py createsuperuser    - Crear superusuario
python manage.py runserver          - Ejecutar servidor de desarrollo
python manage.py makemigrations     - Crear migraciones
python manage.py migrate            - Aplicar migraciones
python manage.py collectstatic      - Recopilar archivos estáticos
""")

def test_connection():
    """Probar conexión a la base de datos PostgreSQL"""
    print("=== Prueba de conexión PostgreSQL ===\n")
    
    try:
        from decouple import config
        
        # Mostrar configuración (sin password)
        db_name = config('DB_NAME', default='pyng_db')
        db_user = config('DB_USER', default='postgres')
        db_host = config('DB_HOST', default='localhost')
        db_port = config('DB_PORT', default='5432')
        
        print(f"Configuración:")
        print(f"  Host: {db_host}")
        print(f"  Puerto: {db_port}")
        print(f"  Base de datos: {db_name}")
        print(f"  Usuario: {db_user}")
        print()
        
        # Probar conexión directa con psycopg2
        print("Probando conexión directa con psycopg2...")
        import psycopg2
        
        db_password = config('DB_PASSWORD', default='Koke1988*')
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Conexión exitosa!")
        print(f"Versión PostgreSQL: {version}")
        
        cursor.close()
        conn.close()
        
        # Probar con Django
        print("\nProbando con Django...")
        django.setup()
        from django.db import connection
        
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Conexión Django exitosa!")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        print("Instala psycopg2-binary: pip install psycopg2-binary")
        return False
    except psycopg2.OperationalError as e:
        print(f"❌ Error de conexión PostgreSQL: {e}")
        print("\nPosibles soluciones:")
        print("1. Verificar que PostgreSQL esté ejecutándose")
        print("2. Verificar credenciales en .env")
        print("3. Verificar que la base de datos existe")
        print("4. Verificar permisos del usuario")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def create_admin_user():
    """Crear usuario administrador"""
    try:
        django.setup()
        from django.contrib.auth.models import User
        from monitor.models import Profile, Polling, SmtpServer, WebThemes
        
        print("=== Crear Usuario Administrador ===\n")
        
        # Verificar si ya existe un usuario
        if User.objects.exists():
            print("⚠️  Ya existen usuarios en la base de datos.")
            overwrite = input("¿Crear usuario adicional? (s/n): ")
            if overwrite.lower() != 's':
                return
        
        # Solicitar datos del usuario
        username = input("Nombre de usuario: ")
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario '{username}' ya existe.")
            return
            
        email = input("Email: ")
        password = input("Contraseña: ")
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            is_staff=True,
            is_superuser=True
        )
        
        # Crear perfil
        Profile.objects.get_or_create(user=user, defaults={'alerts_enabled': True})
        
        # Crear configuración por defecto si no existe
        if not Polling.objects.exists():
            Polling.objects.create(poll_interval=60, history_truncate_days=10)
            print("✅ Configuración de monitoreo creada")
        
        # Crear servidor SMTP por defecto si no existe
        if not SmtpServer.objects.exists():
            SmtpServer.objects.create(
                smtp_server='localhost',
                smtp_port=25,
                smtp_sender=email
            )
            print("✅ Configuración SMTP por defecto creada")
        
        # Crear temas por defecto si no existen
        if not WebThemes.objects.exists():
            WebThemes.objects.create(
                theme_name='Flatly (Claro)',
                theme_path='css/flatly.min.css',
                active=True
            )
            WebThemes.objects.create(
                theme_name='Darkly (Oscuro)',
                theme_path='css/darkly.min.css',
                active=False
            )
            print("✅ Temas por defecto creados")
        
        print(f"✅ Usuario administrador '{username}' creado exitosamente!")
        print("Ahora puedes iniciar sesión en la aplicación.")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_user():
    """Crear usuario regular (no administrador)"""
    try:
        django.setup()
        from django.contrib.auth.models import User
        from monitor.models import Profile
        
        print("=== Crear Usuario Regular ===\n")
        
        # Solicitar datos del usuario
        username = input("Nombre de usuario: ")
        if User.objects.filter(username=username).exists():
            print(f"❌ El usuario '{username}' ya existe.")
            return
            
        email = input("Email (opcional): ")
        password = input("Contraseña: ")
        
        # Preguntar sobre permisos
        print("\nPermisos del usuario:")
        print("1. Usuario regular (solo visualización)")
        print("2. Usuario con permisos de staff (puede acceder al admin)")
        
        perm_choice = input("Selecciona una opción (1-2): ")
        
        is_staff = False
        is_superuser = False
        
        if perm_choice == "2":
            is_staff = True
            make_super = input("¿Hacer superusuario? (s/n): ")
            if make_super.lower() == 's':
                is_superuser = True
        
        # Preguntar sobre alertas
        enable_alerts = input("¿Habilitar alertas para este usuario? (s/n): ")
        alerts_enabled = enable_alerts.lower() == 's'
        
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email if email else '',
            password=password,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        
        # Crear perfil
        Profile.objects.get_or_create(
            user=user, 
            defaults={'alerts_enabled': alerts_enabled}
        )
        
        print(f"✅ Usuario '{username}' creado exitosamente!")
        print(f"   - Tipo: {'Superusuario' if is_superuser else 'Staff' if is_staff else 'Regular'}")
        print(f"   - Email: {email if email else 'No especificado'}")
        print(f"   - Alertas: {'Habilitadas' if alerts_enabled else 'Deshabilitadas'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def list_users():
    """Listar todos los usuarios"""
    try:
        django.setup()
        from django.contrib.auth.models import User
        from monitor.models import Profile
        
        print("=== Lista de Usuarios ===\n")
        
        users = User.objects.all().order_by('username')
        
        if not users.exists():
            print("No hay usuarios en la base de datos.")
            return
        
        print(f"{'Usuario':<20} {'Email':<30} {'Tipo':<15} {'Alertas':<10} {'Último login'}")
        print("-" * 90)
        
        for user in users:
            # Obtener perfil
            try:
                profile = Profile.objects.get(user=user)
                alerts = "Sí" if profile.alerts_enabled else "No"
            except Profile.DoesNotExist:
                alerts = "N/A"
            
            # Determinar tipo de usuario
            if user.is_superuser:
                user_type = "Superusuario"
            elif user.is_staff:
                user_type = "Staff"
            else:
                user_type = "Regular"
            
            # Formatear último login
            last_login = user.last_login.strftime("%Y-%m-%d %H:%M") if user.last_login else "Nunca"
            
            print(f"{user.username:<20} {user.email:<30} {user_type:<15} {alerts:<10} {last_login}")
        
        print(f"\nTotal de usuarios: {users.count()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def delete_user():
    """Eliminar un usuario"""
    try:
        django.setup()
        from django.contrib.auth.models import User
        
        print("=== Eliminar Usuario ===\n")
        
        # Listar usuarios disponibles
        users = User.objects.all().order_by('username')
        
        if not users.exists():
            print("No hay usuarios en la base de datos.")
            return
        
        print("Usuarios disponibles:")
        for i, user in enumerate(users, 1):
            user_type = "Superusuario" if user.is_superuser else "Staff" if user.is_staff else "Regular"
            print(f"{i}. {user.username} ({user_type})")
        
        print("0. Cancelar")
        
        try:
            choice = int(input("\nSelecciona un usuario para eliminar: "))
            
            if choice == 0:
                print("Operación cancelada.")
                return
            
            if choice < 1 or choice > users.count():
                print("❌ Selección inválida.")
                return
            
            user_to_delete = users[choice - 1]
            
            # Confirmación
            print(f"\n⚠️  ¿Estás seguro de que quieres eliminar el usuario '{user_to_delete.username}'?")
            confirm = input("Escribe 'SI' para confirmar: ")
            
            if confirm == 'SI':
                username = user_to_delete.username
                user_to_delete.delete()
                print(f"✅ Usuario '{username}' eliminado exitosamente.")
            else:
                print("Operación cancelada.")
                
        except ValueError:
            print("❌ Por favor ingresa un número válido.")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == 'status':
        check_status()
    elif command == 'reset':
        reset_database()
    elif command == 'backup':
        create_backup()
    elif command == 'help':
        show_help()
    elif command == 'testconnection':
        test_connection()
    elif command == 'createadmin':
        create_admin_user()
    elif command == 'createuser':
        create_user()
    elif command == 'listusers':
        list_users()
    elif command == 'deleteuser':
        delete_user()
    else:
        print(f"Comando desconocido: {command}")
        show_help()

if __name__ == '__main__':
    main()
