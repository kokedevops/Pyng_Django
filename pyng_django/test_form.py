#!/usr/bin/env python3
"""
Script para probar el formulario AddHostsForm
"""
import sys
import os

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

# Importar el formulario
from monitor.forms import AddHostsForm
from monitor.models import Hosts

# Datos de prueba
test_data = {
    'ip_address': '127.0.0.1:8080\n192.168.1.1\n10.0.0.1:3000'
}

print("Probando formulario AddHostsForm:")
print(f"Datos de entrada: {test_data}")

# Crear el formulario
form = AddHostsForm(data=test_data)

if form.is_valid():
    print("✅ Formulario válido!")
    print(f"IP addresses: {form.cleaned_data['ip_address']}")
    
    # Simular el procesamiento como en la vista
    ip_list = form.cleaned_data['ip_address'].splitlines()
    print(f"\nProcesando {len(ip_list)} IPs:")
    
    for ip_str in ip_list:
        ip_str = ip_str.strip()
        if not ip_str:
            continue
            
        try:
            from monitor.utils import validate_ip_port
            ip_only, port = validate_ip_port(ip_str)
            print(f"  ✅ {ip_str} -> IP: {ip_only}, Puerto: {port}")
        except ValueError as e:
            print(f"  ❌ {ip_str} -> Error: {e}")
else:
    print("❌ Formulario inválido!")
    print(f"Errores: {form.errors}")
    
print("\nHosts actuales en la base de datos:")
for host in Hosts.objects.all():
    print(f"  - {host.ip_address} ({host.hostname})")
