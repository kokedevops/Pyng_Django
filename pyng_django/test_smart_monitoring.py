#!/usr/bin/env python3
"""
Script para probar el monitoreo inteligente de IP e IP:Puerto
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.utils import poll_host_smart, poll_host_ip, poll_host_port

# Casos de prueba
test_cases = [
    ("8.8.8.8", "Solo IP - DNS Google (debería estar UP)"),
    ("192.168.1.1", "Solo IP - Gateway local (puede estar UP o DOWN)"),
    ("127.0.0.1:80", "IP:Puerto - HTTP local (probablemente DOWN)"),
    ("8.8.8.8:53", "IP:Puerto - DNS Google puerto 53 (debería estar UP)"),
    ("127.0.0.1:8080", "IP:Puerto - Puerto local 8080 (probablemente DOWN)"),
    ("google.com:443", "IP:Puerto - HTTPS Google (debería estar UP)"),
    ("192.168.1.8", "IP inexistente (debería estar DOWN)"),
    ("127.0.0.1:9999", "IP:Puerto inexistente (debería estar DOWN)"),
]

print("=== PRUEBA DE MONITOREO INTELIGENTE ===\n")

for test_ip, description in test_cases:
    print(f"Probando: {test_ip}")
    print(f"Descripción: {description}")
    
    try:
        if ':' in test_ip and not '::' in test_ip:
            # Es IP:Puerto
            ip_part, port_part = test_ip.split(':')
            print(f"  → Tipo: IP:Puerto")
            print(f"  → IP: {ip_part}, Puerto: {port_part}")
            
            # Probar función de puerto específico
            port_result = poll_host_port(ip_part, int(port_part))
            print(f"  → Resultado puerto TCP: {port_result}")
        else:
            # Es solo IP
            print(f"  → Tipo: Solo IP")
            
            # Probar función de ping
            ping_result = poll_host_ip(test_ip)
            print(f"  → Resultado ping ICMP: {ping_result}")
        
        # Probar función inteligente
        smart_result = poll_host_smart(test_ip)
        print(f"  → Resultado inteligente: {smart_result}")
        
    except Exception as e:
        print(f"  → Error: {e}")
    
    print()

print("=== PRUEBA COMPLETADA ===")
print("Nota: Los resultados pueden variar según la red y los servicios disponibles")
