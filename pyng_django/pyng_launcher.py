#!/usr/bin/env python
"""
Script simple para iniciar PYNG con servidor web y monitoreo
"""
import os
import sys
import subprocess
import time
import signal
import threading
from pathlib import Path

# Setup Django path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')

class PyNGLauncher:
    def __init__(self):
        self.web_process = None
        self.monitoring_process = None
        self.running = True
        
    def signal_handler(self, signum, frame):
        print(f'\nDeteniendo servicios...')
        self.running = False
        self.stop_all()
        sys.exit(0)
        
    def start_web_server(self):
        print("Iniciando servidor web...")
        try:
            self.web_process = subprocess.Popen([
                sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
            ])
            time.sleep(2)  # Dar tiempo para que inicie
            
            if self.web_process.poll() is None:
                print("Servidor web iniciado: http://localhost:8000")
                return True
            else:
                print("Error: No se pudo iniciar el servidor web")
                return False
        except Exception as e:
            print(f"Error iniciando servidor web: {e}")
            return False
    
    def start_monitoring(self):
        print("Iniciando monitoreo...")
        try:
            self.monitoring_process = subprocess.Popen([
                sys.executable, 'manage.py', 'start_monitoring'
            ])
            time.sleep(2)  # Dar tiempo para que inicie
            
            if self.monitoring_process.poll() is None:
                print("Monitoreo iniciado")
                return True
            else:
                print("Error: No se pudo iniciar el monitoreo")
                return False
        except Exception as e:
            print(f"Error iniciando monitoreo: {e}")
            return False
    
    def stop_all(self):
        print("Deteniendo servicios...")
        
        if self.web_process:
            try:
                self.web_process.terminate()
                self.web_process.wait(timeout=5)
                print("Servidor web detenido")
            except:
                self.web_process.kill()
                print("Servidor web forzado a terminar")
        
        if self.monitoring_process:
            try:
                self.monitoring_process.terminate()
                self.monitoring_process.wait(timeout=5)
                print("Monitoreo detenido")
            except:
                self.monitoring_process.kill()
                print("Monitoreo forzado a terminar")
    
    def run(self):
        # Configurar manejador de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        print("PYNG - Sistema de Monitoreo de Red")
        print("=" * 40)
        
        # Iniciar servicios
        web_ok = self.start_web_server()
        monitor_ok = self.start_monitoring()
        
        if not web_ok or not monitor_ok:
            print("Error: No se pudieron iniciar todos los servicios")
            self.stop_all()
            return False
        
        print("\nPYNG iniciado correctamente!")
        print("Servidor web: http://localhost:8000")
        print("Monitoreo: Activo")
        print("Presiona Ctrl+C para detener")
        print("=" * 40)
        
        # Mantener el proceso activo
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop_all()
            print("PYNG detenido")
        
        return True

def main():
    launcher = PyNGLauncher()
    launcher.run()

if __name__ == '__main__':
    main()
