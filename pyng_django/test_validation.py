#!/usr/bin/env python3
"""
Script para probar la función validate_ip_port
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

# Importar la función
from monitor.utils import validate_ip_port

# Casos de prueba
test_cases = [
    "192.168.1.1",
    "127.0.0.1:8080",
    "10.0.0.1:80",
    "192.168.1.1:65535",
    "invalid_ip",
    "192.168.1.1:99999",
    "192.168.1.1:80:extra",
    "192.168.1.1:abc",
    "::1",  # IPv6
    "::1:8080",  # IPv6 con puerto
]

print("Probando función validate_ip_port:\n")

for test_case in test_cases:
    try:
        ip_only, port = validate_ip_port(test_case)
        print(f"✅ '{test_case}' -> IP: {ip_only}, Puerto: {port}")
    except ValueError as e:
        print(f"❌ '{test_case}' -> Error: {e}")

print("\n¡Prueba completada!")
