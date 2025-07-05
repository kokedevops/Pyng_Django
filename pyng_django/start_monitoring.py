#!/usr/bin/env python
"""
Script para ejecutar el monitoreo de hosts automáticamente en segundo plano
"""
import os
import sys
import time
import django
import signal
import threading
from pathlib import Path
from datetime import datetime

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import Polling
from django.core.management import call_command

# Variable global para controlar el monitoreo
monitoring_active = True

def signal_handler(signum, frame):
    """Manejar señales para parada limpia"""
    global monitoring_active
    print(f"\n🛑 Recibida señal {signum}. Deteniendo monitoreo...")
    monitoring_active = False

def get_polling_interval():
    """Obtener el intervalo de monitoreo de la base de datos"""
    try:
        polling_config = Polling.objects.first()
        return polling_config.poll_interval if polling_config else 60
    except Exception:
        return 60

def run_monitoring():
    """Ejecutar monitoreo continuo"""
    global monitoring_active
    
    print("🔄 Iniciando servicio de monitoreo automático...")
    print("📋 Presiona Ctrl+C para detener")
    
    while monitoring_active:
        try:
            # Obtener intervalo actual de la base de datos
            interval = get_polling_interval()
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"⏰ [{timestamp}] Ejecutando monitoreo... (Intervalo: {interval}s)")
            
            # Ejecutar el comando de monitoreo
            call_command('poll_hosts', verbosity=0)
            print(f"✅ [{timestamp}] Monitoreo completado")
            
            # Esperar el intervalo configurado
            for i in range(interval):
                if not monitoring_active:
                    break
                time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n⛔ Monitoreo detenido por el usuario.")
            monitoring_active = False
            break
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"❌ [{timestamp}] Error en monitoreo: {e}")
            # Esperar 30 segundos antes de reintentar en caso de error
            time.sleep(30)
    
    print("🔚 Servicio de monitoreo detenido.")

def start_monitoring_service():
    """Iniciar el servicio de monitoreo"""
    # Configurar manejadores de señales
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Crear un hilo para el monitoreo
    monitoring_thread = threading.Thread(target=run_monitoring, daemon=True)
    monitoring_thread.start()
    
    try:
        # Mantener el proceso principal vivo
        while monitoring_active and monitoring_thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)
    
    # Esperar a que termine el hilo de monitoreo
    monitoring_thread.join(timeout=5)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'start':
            start_monitoring_service()
        elif command == 'test':
            # Ejecutar una sola vez para probar
            print("🧪 Ejecutando monitoreo de prueba...")
            call_command('poll_hosts')
            print("✅ Prueba completada")
        elif command == 'status':
            # Mostrar configuración actual
            interval = get_polling_interval()
            print(f"⚙️  Intervalo configurado: {interval} segundos")
        else:
            print("Uso: python start_monitoring.py [start|test|status]")
            print("  start  - Iniciar monitoreo automático")
            print("  test   - Ejecutar una sola vez")
            print("  status - Mostrar configuración actual")
    else:
        start_monitoring_service()
