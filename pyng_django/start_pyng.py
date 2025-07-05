#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comando para iniciar tanto el servidor web como el servicio de monitoreo
"""
import os
import sys
import django
import subprocess
import threading
import time
import signal
from pathlib import Path

# Configurar codificación para Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

# Setup Django
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')

class PyNGService:
    def __init__(self):
        self.web_process = None
        self.monitoring_process = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        """Manejar señales para parada limpia"""
        print(f'\n[STOP] Recibida señal {signum}. Deteniendo servicios...')
        self.running = False
        self.stop_services()
        
    def start_web_server(self):
        """Iniciar servidor web Django"""
        try:
            print("[WEB] Iniciando servidor web Django...")
            self.web_process = subprocess.Popen([
                sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Dar tiempo para que el servidor se inicie
            time.sleep(3)
            
            if self.web_process.poll() is None:
                print("[OK] Servidor web iniciado en http://0.0.0.0:8000")
                return True
            else:
                stdout, stderr = self.web_process.communicate()
                print(f"[ERROR] Error iniciando servidor web:")
                if stderr:
                    print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error al iniciar servidor web: {e}")
            return False
    
    def start_monitoring_service(self):
        """Iniciar servicio de monitoreo"""
        try:
            print("[MON] Iniciando servicio de monitoreo...")
            self.monitoring_process = subprocess.Popen([
                sys.executable, 'manage.py', 'start_monitoring'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Dar tiempo para que el monitoreo se inicie
            time.sleep(2)
            
            if self.monitoring_process.poll() is None:
                print("[OK] Servicio de monitoreo iniciado")
                return True
            else:
                stdout, stderr = self.monitoring_process.communicate()
                print(f"[ERROR] Error iniciando monitoreo:")
                if stderr:
                    print(f"STDERR: {stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error al iniciar monitoreo: {e}")
            return False
    
    def stop_services(self):
        """Detener todos los servicios"""
        print("\n[STOP] Deteniendo servicios...")
        
        # Detener monitoreo
        if self.monitoring_process and self.monitoring_process.poll() is None:
            try:
                self.monitoring_process.terminate()
                self.monitoring_process.wait(timeout=5)
                print("[OK] Servicio de monitoreo detenido")
            except subprocess.TimeoutExpired:
                self.monitoring_process.kill()
                print("[FORCE] Servicio de monitoreo forzado a terminar")
        
        # Detener servidor web
        if self.web_process and self.web_process.poll() is None:
            try:
                self.web_process.terminate()
                self.web_process.wait(timeout=5)
                print("[OK] Servidor web detenido")
            except subprocess.TimeoutExpired:
                self.web_process.kill()
                print("[FORCE] Servidor web forzado a terminar")
        
        # Limpiar archivos PID
        if os.path.exists('.monitoring_pid'):
            os.remove('.monitoring_pid')
        if os.path.exists('.web_pid'):
            os.remove('.web_pid')
    
    def monitor_processes(self):
        """Monitorear los procesos y reiniciarlos si es necesario"""
        while self.running:
            try:
                # Verificar servidor web
                if self.web_process and self.web_process.poll() is not None:
                    print("[WARN] Servidor web se detuvo. Reiniciando...")
                    self.start_web_server()
                
                # Verificar monitoreo
                if self.monitoring_process and self.monitoring_process.poll() is not None:
                    print("[WARN] Servicio de monitoreo se detuvo. Reiniciando...")
                    self.start_monitoring_service()
                
                time.sleep(10)  # Verificar cada 10 segundos
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"[ERROR] Error en monitoreo de procesos: {e}")
                time.sleep(10)
    
    def start_all_services(self):
        """Iniciar todos los servicios"""
        print("[START] Iniciando PYNG - Sistema de Monitoreo de Red")
        print("=" * 50)
        
        # Configurar manejadores de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Verificar base de datos
        try:
            django.setup()
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            print("[OK] Conexión a base de datos verificada")
        except Exception as e:
            print(f"[ERROR] Error de base de datos: {e}")
            return False
        
        # Iniciar servicios
        web_started = self.start_web_server()
        monitoring_started = self.start_monitoring_service()
        
        if not web_started or not monitoring_started:
            print("[ERROR] No se pudieron iniciar todos los servicios")
            self.stop_services()
            return False
        
        # Guardar PIDs
        if self.web_process:
            with open('.web_pid', 'w') as f:
                f.write(str(self.web_process.pid))
        
        if self.monitoring_process:
            with open('.monitoring_pid', 'w') as f:
                f.write(str(self.monitoring_process.pid))
        
        print("\n[SUCCESS] PYNG iniciado correctamente!")
        print("=" * 50)
        print("[WEB] Servidor web: http://localhost:8000")
        print("[MON] Monitoreo: Activo")
        print("[INFO] Presiona Ctrl+C para detener todos los servicios")
        print("=" * 50)
        
        # Iniciar monitoreo de procesos
        try:
            self.monitor_processes()
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_services()
            print("\n[END] PYNG detenido. Hasta la proxima!")
        
        return True

def main():
    """Función principal"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("""
PYNG - Sistema de Monitoreo de Red
==================================

Uso: python start_pyng.py [opciones]

Opciones:
  --help    Mostrar esta ayuda

Este comando inicia tanto el servidor web como el servicio de monitoreo
automático de hosts. Ambos servicios se ejecutan simultáneamente.

Para detener todos los servicios, presiona Ctrl+C.
        """)
        return
    
    service = PyNGService()
    try:
        service.start_all_services()
    except KeyboardInterrupt:
        print("\n[STOP] Deteniendo servicios...")
        service.stop_services()
    except Exception as e:
        print(f"[ERROR] Error fatal: {e}")
        service.stop_services()

if __name__ == '__main__':
    main()
