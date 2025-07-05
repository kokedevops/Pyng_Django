#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher simple para PYNG
"""
import os
import sys
import subprocess
import time
import signal

def start_services():
    """Iniciar servicios"""
    print("=== INICIANDO PYNG ===")
    
    # Iniciar servidor web
    print("Iniciando servidor web...")
    web_process = subprocess.Popen([
        sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'
    ])
    
    time.sleep(2)
    
    # Iniciar monitoreo
    print("Iniciando monitoreo...")
    monitor_process = subprocess.Popen([
        sys.executable, 'manage.py', 'start_monitoring'
    ])
    
    print("=== PYNG INICIADO ===")
    print("Servidor web: http://localhost:8000")
    print("Monitoreo: Activo")
    print("Presiona Ctrl+C para detener")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nDeteniendo servicios...")
        web_process.terminate()
        monitor_process.terminate()
        web_process.wait()
        monitor_process.wait()
        print("Servicios detenidos")

if __name__ == '__main__':
    start_services()
