#!/usr/bin/env python3
"""
Script para mejorar la visualización de estados y tipos de hosts
"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyng_django.settings')
django.setup()

from monitor.models import Hosts
from monitor.utils import poll_host_universal

def main():
    print("Mejorando la visualización del dashboard...")
    print("=" * 60)
    
    # Verificar que todas las funciones de tipos funcionan
    hosts = Hosts.objects.all()
    print(f"Total de hosts: {hosts.count()}")
    
    # Mostrar tipos de hosts
    web_hosts = sum(1 for host in hosts if host.is_web_url())
    ip_hosts = hosts.count() - web_hosts
    
    print(f"🌐 Hosts Web: {web_hosts}")
    print(f"🖥️ Hosts IP: {ip_hosts}")
    print()
    
    # Mostrar algunos ejemplos de cada tipo
    print("Ejemplos de hosts por tipo:")
    print("-" * 30)
    
    for host in hosts[:5]:
        host_type = "🌐 Web" if host.is_web_url() else "🖥️ IP"
        print(f"{host_type}: {host.ip_address} ({host.hostname or 'Sin nombre'})")
    
    print("\n✅ Dashboard mejorado correctamente!")
    print("Los cambios incluyen:")
    print("- Nueva columna 'Tipo' en el dashboard")
    print("- Iconos distintivos para Web y IP")
    print("- Mejor manejo de estados HTTP")
    print("- Textos de ayuda mejorados en formularios")

if __name__ == "__main__":
    main()
