#!/usr/bin/env python3
"""
Script para probar la adición de hosts con IP:Puerto
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

# Importar los modelos
from monitor.models import Hosts
from monitor.utils import validate_ip_port

# Probar agregar un host con IP:Puerto
test_ip = "127.0.0.1:8080"

try:
    # Validar el formato
    ip_only, port = validate_ip_port(test_ip)
    print(f"✅ Validación exitosa: IP={ip_only}, Puerto={port}")
    
    # Verificar si ya existe
    if Hosts.objects.filter(ip_address=test_ip).exists():
        print(f"⚠️  El host {test_ip} ya existe en la base de datos")
        # Eliminar para probar de nuevo
        Hosts.objects.filter(ip_address=test_ip).delete()
        print(f"🗑️  Host eliminado para prueba")
    
    # Crear el host
    host = Hosts.objects.create(
        ip_address=test_ip,
        hostname=f"test-host-{port}",
        status="🟢 Up 🟢",
        last_poll="2025-07-05 00:05:00"
    )
    
    print(f"✅ Host creado exitosamente:")
    print(f"   - IP completa: {host.ip_address}")
    print(f"   - IP solo: {host.get_ip_only()}")
    print(f"   - Puerto: {host.get_port()}")
    print(f"   - Hostname: {host.hostname}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
